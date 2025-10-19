"""
Distributed Task Queue System - Legacy Implementation
WARNING: This code has deliberate issues for demonstration purposes:
- Uses outdated callback patterns instead of async/await
- Contains race condition in worker pool
- No proper error handling
- Missing tests
- Poor documentation
"""

import threading
import queue
import time
import json
from typing import Callable, Any, Dict, List

# Global state (problematic!)
task_results = {}
active_workers = 0
task_counter = 0

class TaskQueue:
    def __init__(self, num_workers=4):
        self.queue = queue.Queue()
        self.workers = []
        self.num_workers = num_workers
        self.callbacks = {}
        self.is_running = False
        
    def start(self):
        self.is_running = True
        for i in range(self.num_workers):
            w = threading.Thread(target=self._worker_loop, args=(i,))
            w.start()
            self.workers.append(w)
    
    # RACE CONDITION: Multiple threads modifying global state without locks
    def _worker_loop(self, worker_id):
        global active_workers, task_results, task_counter
        active_workers += 1  # NOT THREAD SAFE!
        
        while self.is_running:
            try:
                task = self.queue.get(timeout=1)
            except:
                continue
                
            # Execute task with callback hell
            try:
                result = task['func'](*task['args'])
                task_results[task['id']] = result  # RACE CONDITION HERE!
                
                # Nested callbacks - callback hell pattern
                if task['id'] in self.callbacks:
                    callback = self.callbacks[task['id']]
                    def on_success(r):
                        callback(r)
                        if 'then' in task:
                            task['then'](r)
                    on_success(result)
            except Exception as e:
                # Poor error handling - just print
                print(f"Task failed: {e}")
            
            task_counter += 1  # RACE CONDITION!
            self.queue.task_done()
        
        active_workers -= 1  # RACE CONDITION!
    
    # Callback-based API (outdated pattern)
    def submit_task(self, func: Callable, args: tuple, callback: Callable = None):
        task_id = len(task_results) + 1  # NOT THREAD SAFE!
        task = {
            'id': task_id,
            'func': func,
            'args': args,
        }
        if callback:
            self.callbacks[task_id] = callback
        
        self.queue.put(task)
        return task_id
    
    def get_result(self, task_id):
        # Blocking wait without timeout
        while task_id not in task_results:
            time.sleep(0.1)
        return task_results[task_id]
    
    def stop(self):
        self.is_running = False
        for w in self.workers:
            w.join()

# Task execution functions with no error handling
def process_data(data):
    # Simulate processing
    time.sleep(0.5)
    return {'processed': data, 'count': len(data)}

def fetch_remote_data(url):
    # No error handling for network failures
    time.sleep(1)
    return f"data from {url}"

def aggregate_results(results):
    # No validation of input
    total = 0
    for r in results:
        total += r['count']
    return total

# Orchestration with deeply nested callbacks
class TaskOrchestrator:
    def __init__(self):
        self.queue = TaskQueue(num_workers=4)
        self.queue.start()
        self.pending_tasks = []
    
    def process_batch(self, data_items, on_complete):
        results = []
        completed = 0
        total = len(data_items)
        
        # Callback hell
        def on_item_done(result):
            nonlocal completed
            results.append(result)
            completed += 1
            
            if completed == total:
                # Another nested callback
                def on_aggregate_done(final):
                    on_complete(final)
                
                agg_task_id = self.queue.submit_task(
                    aggregate_results,
                    (results,),
                    on_aggregate_done
                )
        
        # Submit all tasks
        for item in data_items:
            task_id = self.queue.submit_task(
                process_data,
                (item,),
                on_item_done
            )
            self.pending_tasks.append(task_id)
    
    def shutdown(self):
        self.queue.stop()

# Priority queue implementation without proper synchronization
class PriorityTaskQueue(TaskQueue):
    def __init__(self, num_workers=4):
        super().__init__(num_workers)
        self.priority_queue = []  # NOT THREAD SAFE!
        self.lock = None  # No lock implemented!
    
    def submit_priority_task(self, func, args, priority, callback=None):
        task_id = len(task_results) + 1
        task = {
            'id': task_id,
            'func': func,
            'args': args,
            'priority': priority
        }
        
        # RACE CONDITION: Multiple threads accessing list
        self.priority_queue.append(task)
        self.priority_queue.sort(key=lambda x: x['priority'], reverse=True)
        
        if callback:
            self.callbacks[task_id] = callback
        
        return task_id

# Retry logic without exponential backoff
def retry_task(func, args, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            return func(*args)
        except:
            retries += 1
            time.sleep(1)  # Fixed delay, should use exponential backoff
    raise Exception("Max retries exceeded")

# Usage example
if __name__ == "__main__":
    orchestrator = TaskOrchestrator()
    
    # Nested callbacks making code hard to read
    def final_callback(result):
        print(f"Final result: {result}")
        orchestrator.shutdown()
    
    data = [
        ["item1", "item2"],
        ["item3", "item4", "item5"],
        ["item6"]
    ]
    
    orchestrator.process_batch(data, final_callback)
    
    # No proper cleanup
    time.sleep(10)
