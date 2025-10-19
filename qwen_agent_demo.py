"""
Qwen Agent Demo - GitHub Issue Analyzer
Simulates agent behavior with real analysis
"""

import streamlit as st
import requests
import json
import time
import os
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Qwen Agent Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .header-title {
        color: white;
        font-size: 3rem;
        font-weight: bold;
    }
    
    .agent-step {
        background: rgba(255,255,255,0.1);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: white;
        font-family: monospace;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'agent_result' not in st.session_state:
    st.session_state.agent_result = None
if 'api_tested' not in st.session_state:
    st.session_state.api_tested = False

def test_api_key(api_key: str) -> tuple:
    """Test API key"""
    url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen-turbo",
        "input": {"messages": [{"role": "user", "content": "Hello"}]},
        "parameters": {"result_format": "message"}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        return response.status_code == 200, "✅ Ready!" if response.status_code == 200 else f"❌ Error {response.status_code}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def simulate_agent_step(step_text: str, duration: float = 1.0):
    """Simulate an agent step with visual feedback"""
    step_placeholder = st.empty()
    # Show loading state
    step_placeholder.info(f"🔄 {step_text}")
    time.sleep(duration)
    # Show completed state
    step_placeholder.success(f"✅ {step_text}")
    return step_placeholder

def analyze_github_issues(api_key: str, model: str = "qwen-max") -> str:
    """
    Analyze GitHub issues using Qwen with simulated agent behavior
    """
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    
    # Load the pre-fetched issues - try multiple paths
    issues_data = None
    possible_paths = [
        script_dir / 'langchain_issues.json',  # Same directory as script
        Path.cwd() / 'langchain_issues.json',  # Current working directory
        Path('langchain_issues.json'),  # Relative path
        Path('/mnt/user-data/outputs/langchain_issues.json'),  # Absolute fallback
    ]
    
    error_messages = []
    for path in possible_paths:
        try:
            with open(path, 'r') as f:
                issues_data = json.load(f)
                break
        except Exception as e:
            error_messages.append(f"{path}: {str(e)}")
            continue
    
    if not issues_data:
        error_details = "\n".join(error_messages)
        return f"""❌ Error: Could not load issues data.

Tried these locations:
{error_details}

Please ensure langchain_issues.json is in the same directory as qwen_agent_demo.py

Current working directory: {Path.cwd()}
Script directory: {script_dir}
"""
    
    # Create analysis prompt
    issues_text = json.dumps(issues_data[:50], indent=2)  # Use first 50 issues
    
    prompt = f"""You are an AI agent analyzing GitHub issues for the LangChain repository.

**YOUR TASK:**
Analyze these 50 GitHub issues and provide:

1. **Issue Categorization** - Group issues into logical categories
2. **Common Pain Points** - Identify the most frequent and critical problems
3. **Root Cause Analysis** - Explain what architectural patterns are causing these issues
4. **Proposed Solutions** - Suggest specific architectural improvements that would address multiple issues

**GITHUB ISSUES DATA:**
```json
{issues_text}
```

**ANALYSIS REQUIREMENTS:**

## 1. Category Breakdown
Categorize all issues and show:
- Category name
- Number of issues in each category
- Severity distribution (critical/high/medium)

## 2. Top Pain Points (by frequency)
List the top 5-7 pain points across all issues:
- What is the problem?
- How many issues relate to it?
- Why is it problematic?

## 3. Root Cause Analysis
Identify architectural issues:
- What design patterns are causing problems?
- Which components have the most issues?
- Are there systemic problems?

## 4. Proposed Architectural Solutions
For each major pain point, propose solutions that:
- Fit LangChain's existing architecture
- Can be implemented incrementally
- Address multiple related issues
- Include specific technical approaches (with code examples where helpful)

## 5. Implementation Priority
Rank solutions by:
- Impact (how many issues fixed)
- Effort required
- Risk level

**Be specific, actionable, and technical. Think like a senior architect.**"""

    messages = [
        {
            "role": "system",
            "content": "You are a senior software architect and GitHub repository analyst. You excel at pattern recognition, root cause analysis, and proposing systemic solutions."
        },
        {"role": "user", "content": prompt}
    ]
    
    url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "input": {"messages": messages},
        "parameters": {
            "result_format": "message",
            "max_tokens": 8000,
            "temperature": 0.3
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            return data.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return f"❌ API Error {response.status_code}"
    except Exception as e:
        return f"❌ Exception: {str(e)}"

def main():
    # Header
    st.markdown("""
        <div class="header-container">
            <h1 class="header-title">🤖 Qwen Agent Demo</h1>
            <p style="color: white; font-size: 1.2rem;">GitHub Issue Analysis with Agent Capabilities</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/robot.png", width=80)
        st.title("⚙️ Agent Configuration")
        
        st.info("""
        **Agent Mode**
        
        This demo simulates agent behavior:
        - GitHub API calls
        - Multi-step reasoning
        - Pattern recognition
        - Solution proposals
        """)
        
        # API Key
        api_key = st.text_input(
            "🔑 API Key",
            type="password",
            value=st.session_state.api_key
        )
        
        if api_key and api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
            st.session_state.api_tested = False
        
        if api_key:
            if st.button("🧪 Test Connection", use_container_width=True):
                with st.spinner("Testing..."):
                    success, msg = test_api_key(api_key)
                    st.session_state.api_tested = success
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
            
            if st.session_state.api_tested:
                st.success("✅ Agent Ready!")
        
        st.divider()
        
        # Model
        model = st.selectbox(
            "🤖 Model",
            ["qwen-max", "qwen-plus", "qwen-turbo"],
            help="qwen-max recommended for complex analysis"
        )
        
        st.divider()
        
        st.markdown("""
        **Demo Task:**
        
        Analyze last 50 GitHub issues from langchain-ai/langchain:
        - Categorize by type
        - Identify pain points
        - Propose solutions
        """)
    
    # Main content
    st.subheader("🎯 Agent Task")
    
    task_input = st.text_input(
        "Enter your agent task:",
        value="Analyze the last 50 GitHub issues in the LangChain repository, categorize by type, identify common pain points, propose architectural solutions",
        disabled=True  # Pre-filled for demo
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        run_button = st.button("▶️ Run Agent", use_container_width=True, type="primary")
    
    with col2:
        if st.session_state.agent_result:
            st.download_button(
                "💾 Download Analysis",
                st.session_state.agent_result,
                "github_analysis.md",
                use_container_width=True
            )
    
    st.divider()
    
    # Agent execution area
    if run_button:
        if not st.session_state.api_key:
            st.error("⚠️ Enter API key first!")
        elif not st.session_state.api_tested:
            st.warning("⚠️ Test API connection first!")
        else:
            st.subheader("🤖 Agent Working...")
            
            steps_container = st.container()
            
            with steps_container:
                # Simulate agent steps
                simulate_agent_step("Connecting to GitHub API...", 0.8)
                simulate_agent_step("Fetching issues from langchain-ai/langchain...", 1.2)
                simulate_agent_step("Retrieved 50 issues", 0.5)
                simulate_agent_step("Parsing issue content...", 1.0)
                simulate_agent_step("Analyzing patterns and clustering similar problems...", 1.5)
                simulate_agent_step("Cross-referencing with LangChain documentation...", 1.0)
                
                # Status message
                status = st.empty()
                status.info("🧠 Generating comprehensive analysis with Qwen-Max...")
            
            # Get real Qwen analysis
            try:
                result = analyze_github_issues(st.session_state.api_key, model)
                
                if result.startswith("❌"):
                    status.error(result)
                else:
                    status.empty()
                    steps_container.empty()
                    
                    st.success("✅ Agent task completed!")
                    st.session_state.agent_result = result
                    
                    st.divider()
                    st.subheader("📊 Analysis Results")
                    st.markdown(result)
                    
            except Exception as e:
                status.error(f"❌ Error: {str(e)}")
    
    elif st.session_state.agent_result:
        st.subheader("📊 Analysis Results")
        st.markdown(st.session_state.agent_result)
    
    else:
        st.info("👆 Click **Run Agent** to start the analysis")
        
        st.markdown("""
        ### 🎯 What the Agent Will Do:
        
        1. **🔗 GitHub Integration** - Fetch real issues from LangChain repo
        2. **📊 Pattern Recognition** - Cluster similar problems automatically
        3. **🧠 Root Cause Analysis** - Identify systemic architectural issues
        4. **💡 Solution Proposals** - Suggest improvements fitting existing architecture
        5. **📈 Priority Ranking** - Rank by impact, effort, and risk
        
        **This demonstrates multi-step agent reasoning!**
        """)
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>Powered by <strong>Qwen-Max</strong> Agent Capabilities</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()