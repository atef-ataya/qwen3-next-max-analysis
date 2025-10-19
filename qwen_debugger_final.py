"""
Qwen Code Debugger - FINAL WORKING VERSION
For International Alibaba Cloud Model Studio
Uses direct HTTP requests (NO dashscope SDK)
"""

import streamlit as st
import requests
import time

# Page config
st.set_page_config(
    page_title="Qwen Code Debugger",
    page_icon="🔍",
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
        margin: 0;
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'api_tested' not in st.session_state:
    st.session_state.api_tested = False

def test_api_key(api_key: str) -> tuple:
    """Test Model Studio API key using direct HTTP request (international)"""
    url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Qwen-Code-Debugger/1.0"
    }

    payload = {
        "model": "qwen-turbo",
        "input": {
            "messages": [
                {"role": "user", "content": "Say hello"}
            ]
        },
        "parameters": {
            "result_format": "message"
        }
    }
    
    try:
        if not api_key.startswith("sk-"):
            st.warning("⚠️ API key should start with 'sk-'")
        else:
            st.toast("🎉 Analysis complete!", icon="✅")
            
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return True, "✅ API Key is valid!"
        else:
            try:
                error_msg = response.json().get("message", "Unknown error")
            except:
                error_msg = response.text
            return False, f"❌ Error {response.status_code}: {error_msg}"
            
    except Exception as e:
        return False, f"❌ Network/Request Error: {str(e)}"

def analyze_code(code: str, api_key: str, model: str = "qwen-turbo") -> str:
    """Analyze code using Model Studio API (international, non-streaming)"""
    
    prompt = f"""You are an expert Python developer and code reviewer.
Analyze the following code and provide:

1. **Problems Identified**: List all issues (circular imports, inefficiency, bad practices)
2. **Explanations**: Clearly explain each issue
3. **Refactored Code**: Provide clean, efficient, production-ready code
4. **Best Practices Applied**: Highlight improvements made

Code to analyze:
```python
{code}
```

Provide your analysis in a clear, structured format with markdown formatting."""

    messages = [
        {"role": "system", "content": "You are an expert Python code reviewer and refactoring specialist."},
        {"role": "user", "content": prompt}
    ]

    # ✅ CORRECT INTERNATIONAL ENDPOINT
    url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Qwen-Code-Debugger/1.0"
    }


    payload = {
        "model": model,  # e.g., "qwen-turbo"
        "input": {
            "messages": messages
        },
        "parameters": {
            "result_format": "message",
            "max_tokens": 3000,
            "temperature": 0.3
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        if response.status_code == 200:
            data = response.json()
            content = data.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
            return content
        else:
            try:
                error_detail = response.json()
                msg = error_detail.get("message", "Unknown error")
                code_err = error_detail.get("code", "N/A")
                return f"❌ API Error {response.status_code} [{code_err}]: {msg}"
            except:
                return f"❌ API Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"❌ Exception: {str(e)}"

def main():
    # Header
    st.markdown("""
        <div class="header-container">
            <h1 class="header-title">🔍 Qwen Code Debugger</h1>
            <p class="header-subtitle">AI-Powered Code Analysis & Refactoring</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
        st.title("⚙️ Configuration")
        
        st.info("""
        **Using Model Studio (International)**
        
        Get your API key from:
        https://modelstudio.console.alibabacloud.com
        """)
        
        # API Key input
        api_key = st.text_input(
            "🔑 API Key",
            type="password",
            value=st.session_state.api_key,
            help="Your Model Studio API key (starts with sk-)"
        )
        
        if api_key and api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
            st.session_state.api_tested = False
        
        # Test API button
        if api_key:
            if st.button("🧪 Test API Connection", use_container_width=True):
                with st.spinner("Testing connection..."):
                    success, message = test_api_key(api_key)
                    st.session_state.api_tested = success
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                        st.warning("💡 Make sure Qwen models are activated in Model Studio!")
            
            if st.session_state.api_tested:
                st.success("✅ API Ready to use!")
        
        st.divider()
        
        # Model selection
        model = st.selectbox(
            "🤖 Select Model",
            ["qwen-turbo", "qwen-plus", "qwen-max"],
            help="turbo: Fast | plus: Balanced | max: Best Quality"
        )
        
        st.divider()
        
        # Example code
        st.subheader("📚 Quick Start")
        
        if st.button("📋 Load Messy Code Example", use_container_width=True):
            example_code = """import json
import time

# Circular Import Pattern
class User:
    def __init__(self,n):
        self.name=n
        self.orders=[]
    
    def add_order(self,id,amt):
        from order import Order
        o=Order(id,amt,self)
        self.orders.append(o)
        return o
    
    def get_total(self):
        t=0
        for i in range(len(self.orders)):
            t=t+self.orders[i].amount
        return t

class Order:
    def __init__(self,id,amt,usr):
        self.id=id
        self.amount=amt
        self.user=usr

# No error handling
def load_data(f):
    file=open(f,'r')
    data=file.read()
    file.close()
    return json.loads(data)

# N+1 query pattern
def process_users(users):
    result=[]
    for u in users:
        orders=get_user_orders(u['id'])
        result.append({'user':u,'orders':orders})
    return result

def get_user_orders(user_id):
    time.sleep(0.1)
    return []

# Global variable + mutable default
total_processed=0
def add_item(item,cart=[]):
    global total_processed
    cart.append(item)
    total_processed+=1
    return cart

# SQL injection vulnerability
def find_user(db,name):
    query=f"SELECT * FROM users WHERE name='{name}'"
    return db.execute(query)"""
            
            st.session_state.example_code = example_code
            st.rerun()
        
        st.divider()
        
        st.markdown("""
        **How to use:**
        1. Enter your API key from Model Studio (International)
        2. Click "Test API Connection"
        3. Load example or paste your code
        4. Click "Analyze Code"
        5. Get AI-powered debugging! ✨
        """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Your Code")
        
        default_code = st.session_state.get('example_code', '')
        
        code_input = st.text_area(
            "Paste your code here:",
            value=default_code,
            height=450,
            placeholder="def my_function():\n    # Your messy code here...\n    pass"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn1:
            analyze_button = st.button("🚀 Analyze Code", use_container_width=True, type="primary")
        
        with col_btn2:
            clear_button = st.button("🗑️ Clear All", use_container_width=True)
        
        with col_btn3:
            if st.session_state.analysis_result:
                st.download_button(
                    "💾 Download",
                    st.session_state.analysis_result,
                    "qwen_analysis.md",
                    use_container_width=True
                )
    
    with col2:
        st.subheader("✨ AI Analysis")
        
        if clear_button:
            st.session_state.analysis_result = None
            st.session_state.example_code = ""
            st.rerun()
        
        if analyze_button:
            if not st.session_state.api_key:
                st.error("⚠️ Please enter your API key in the sidebar!")
            elif not st.session_state.api_tested:
                st.warning("⚠️ Please test your API connection first!")
            elif not code_input.strip():
                st.warning("⚠️ Please enter some code to analyze!")
            else:
                status_text = st.empty()
                status_text.text("🔄 Analyzing your code with Qwen AI...")
                
                try:
                    full_response = analyze_code(code_input, st.session_state.api_key, model)
                    
                    if full_response.startswith("❌"):
                        st.error(full_response)
                    else:
                        st.session_state.analysis_result = full_response
                        st.markdown(full_response)
                        st.success("🎉 Code analysis completed successfully!")
                        
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
                finally:
                    status_text.empty()
        
        elif st.session_state.analysis_result:
            st.markdown(st.session_state.analysis_result)
        else:
            st.info("👈 Paste your code on the left and click **Analyze Code**")
            
            st.markdown("""
            ### 🎯 What You'll Get:
            
            - ✅ **Bug Detection** - Find issues automatically
            - 🔍 **Code Review** - Identify bad practices
            - 🎨 **Clean Refactoring** - Get production-ready code
            - 📚 **Best Practices** - Learn industry standards
            - 💡 **Clear Explanations** - Understand every change
            """)
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>Powered by <strong>Qwen AI</strong> from Alibaba Cloud Model Studio (International)</p>
            <p style='font-size: 0.9rem;'>Built with ❤️ using Streamlit</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()