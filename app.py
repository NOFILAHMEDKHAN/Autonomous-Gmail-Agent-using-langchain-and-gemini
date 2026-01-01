# ==================== FILE 1: app.py ====================
"""
Production Gmail Agent with Real API Integration
Author: NOFIL AHMED KHAN
Date: 01-01-26
"""

import os
import streamlit as st
from dotenv import load_dotenv
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os.path
from datetime import datetime

# ==================== ENV ====================
load_dotenv()

# ==================== LANGCHAIN IMPORTS ====================
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

# ==================== GMAIL SCOPES ====================
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="📧 Production Gmail Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .status-connected {
        color: #28a745;
        font-weight: bold;
    }
    .status-disconnected {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==================== GMAIL AUTHENTICATION ====================
def get_gmail_service():
    """Authenticate and return Gmail API service"""
    creds = None
    
    # Token file stores user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                st.error(f"Token refresh failed: {str(e)}")
                if os.path.exists('token.pickle'):
                    os.remove('token.pickle')
                return None
        else:
            # You need to create credentials.json from Google Cloud Console
            if not os.path.exists('credentials.json'):
                st.error("❌ credentials.json not found!")
                st.info("""
                Please follow these steps:
                1. Go to Google Cloud Console
                2. Create OAuth 2.0 credentials
                3. Download as credentials.json
                4. Place in project folder
                """)
                return None
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")
                return None
        
        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    try:
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        st.error(f"Failed to build service: {str(e)}")
        return None

def get_user_email():
    """Get the authenticated user's email address"""
    try:
        service = st.session_state.get('gmail_service')
        if service:
            profile = service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress', 'Unknown')
    except:
        return 'Unknown'
    return 'Unknown'

# ==================== GMAIL TOOLS ====================
@tool
def check_gmail_inbox(max_results: int = 10) -> str:
    """Check real Gmail inbox and return recent emails
    
    Args:
        max_results: Number of emails to fetch (default 10, max 50)
    """
    try:
        service = st.session_state.get('gmail_service')
        if not service:
            return "❌ Gmail not connected. Please authenticate first."
        
        # Limit max results
        max_results = min(max_results, 50)
        
        # Get messages
        results = service.users().messages().list(
            userId='me', 
            maxResults=max_results,
            labelIds=['INBOX']
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            return "📭 No emails found in inbox."
        
        email_list = [f"📧 **GMAIL INBOX** ({len(messages)} emails)\n"]
        
        for i, msg in enumerate(messages, 1):
            # Get message details
            message = service.users().messages().get(
                userId='me', 
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            
            headers = message['payload']['headers']
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
            
            # Check if unread
            labels = message.get('labelIds', [])
            unread_marker = "🔵 " if 'UNREAD' in labels else ""
            
            email_list.append(f"\n{unread_marker}**{i}. From:** {from_email}")
            email_list.append(f"   **Subject:** {subject}")
            email_list.append(f"   **Date:** {date}")
            email_list.append("   " + "-" * 50)
        
        return "\n".join(email_list)
    
    except Exception as e:
        return f"❌ Error fetching emails: {str(e)}"

@tool
def send_gmail(to: str, subject: str, body: str) -> str:
    """Send a real email via Gmail
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
    """
    try:
        service = st.session_state.get('gmail_service')
        if not service:
            return "❌ Gmail not connected. Please authenticate first."
        
        # Validate email
        if '@' not in to:
            return "❌ Invalid email address format."
        
        # Create message
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send message
        send_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return f"""✅ **Email sent successfully!**

**To:** {to}
**Subject:** {subject}
**Body Preview:** {body[:100]}{'...' if len(body) > 100 else ''}
**Message ID:** {send_message['id']}
**Sent at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"

@tool
def search_gmail(query: str, max_results: int = 10) -> str:
    """Search Gmail with a query
    
    Args:
        query: Search query (e.g., 'from:john@example.com', 'subject:meeting', 'is:unread')
        max_results: Number of results to return (default 10, max 50)
    """
    try:
        service = st.session_state.get('gmail_service')
        if not service:
            return "❌ Gmail not connected. Please authenticate first."
        
        max_results = min(max_results, 50)
        
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            return f"📭 No emails found matching: '{query}'"
        
        email_list = [f"🔍 **Search Results** for '{query}' ({len(messages)} found)\n"]
        
        for i, msg in enumerate(messages, 1):
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            
            headers = message['payload']['headers']
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
            
            email_list.append(f"\n**{i}. From:** {from_email}")
            email_list.append(f"   **Subject:** {subject}")
            email_list.append(f"   **Date:** {date}")
            email_list.append("   " + "-" * 50)
        
        return "\n".join(email_list)
    
    except Exception as e:
        return f"❌ Error searching emails: {str(e)}"

@tool
def get_unread_count() -> str:
    """Get count of unread emails"""
    try:
        service = st.session_state.get('gmail_service')
        if not service:
            return "❌ Gmail not connected."
        
        results = service.users().messages().list(
            userId='me',
            labelIds=['UNREAD']
        ).execute()
        
        count = results.get('resultSizeEstimate', 0)
        return f"📬 You have **{count}** unread emails."
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

@tool
def read_email_content(email_number: int) -> str:
    """Read the full content of a specific email from the inbox
    
    Args:
        email_number: The number of the email from the inbox list (1-based)
    """
    try:
        service = st.session_state.get('gmail_service')
        if not service:
            return "❌ Gmail not connected."
        
        # Get recent messages
        results = service.users().messages().list(
            userId='me',
            maxResults=50,
            labelIds=['INBOX']
        ).execute()
        
        messages = results.get('messages', [])
        
        if email_number < 1 or email_number > len(messages):
            return f"❌ Invalid email number. Please choose between 1 and {len(messages)}."
        
        # Get the specific message
        msg_id = messages[email_number - 1]['id']
        message = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()
        
        # Extract headers
        headers = message['payload']['headers']
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
        
        # Extract body
        def get_body(payload):
            if 'body' in payload and 'data' in payload['body']:
                return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            elif 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            return "No readable content"
        
        body = get_body(message['payload'])
        
        return f"""📧 **Email #{email_number}**

**From:** {from_email}
**Subject:** {subject}
**Date:** {date}

**Content:**
{body[:1000]}{'...' if len(body) > 1000 else ''}"""
    
    except Exception as e:
        return f"❌ Error reading email: {str(e)}"

# ==================== AGENT ====================
def create_gmail_agent():
    """Create agent with Gmail tools"""
    
    tools = [check_gmail_inbox, send_gmail, search_gmail, get_unread_count, read_email_content]
    
    system_message = """You are a helpful Gmail assistant with access to real Gmail functionality.

Available tools:
- check_gmail_inbox: View recent emails in inbox
- send_gmail: Send emails to recipients
- search_gmail: Search emails with queries (e.g., 'from:someone@example.com', 'is:unread')
- get_unread_count: Check number of unread emails
- read_email_content: Read full content of a specific email by number

Always use tools when users ask about their emails. Be helpful and provide clear responses."""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3
    )
    
    llm_with_tools = llm.bind_tools(tools)
    
    return llm_with_tools, tools, system_message

def run_agent(user_input: str, chat_history: list):
    """Run the agent with Gmail tools"""
    try:
        llm_with_tools, tools, system_message = create_gmail_agent()
        
        tool_map = {tool.name: tool for tool in tools}
        
        messages = [{"role": "system", "content": system_message}]
        
        for role, content in chat_history:
            if role == "human":
                messages.append({"role": "user", "content": content})
            else:
                messages.append({"role": "assistant", "content": content})
        
        messages.append({"role": "user", "content": user_input})
        
        response = llm_with_tools.invoke(messages)
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_results = []
            
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                
                if tool_name in tool_map:
                    tool = tool_map[tool_name]
                    result = tool.invoke(tool_args)
                    tool_results.append(result)
            
            return "\n\n".join(tool_results)
        else:
            return response.content
    
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease try again or rephrase your request."

# ==================== STREAMLIT UI ====================
def main():
    # Header
    st.markdown('<p class="main-header">🤖 Production Gmail Agent</p>', unsafe_allow_html=True)
    st.markdown("**AI-Powered Email Management with Real Gmail Integration**")
    st.markdown("---")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "gmail_connected" not in st.session_state:
        st.session_state.gmail_connected = False
    
    # Sidebar
    with st.sidebar:
        st.header("🔐 Gmail Connection")
        
        if st.session_state.gmail_connected:
            user_email = get_user_email()
            st.success("✅ Gmail Connected")
            st.info(f"**Email:** {user_email}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
            with col2:
                if st.button("🔓 Logout", use_container_width=True):
                    st.session_state.gmail_connected = False
                    st.session_state.gmail_service = None
                    if os.path.exists('token.pickle'):
                        os.remove('token.pickle')
                    st.success("Logged out!")
                    st.rerun()
        else:
            st.warning("🔒 Gmail Not Connected")
            
            if st.button("🔐 Connect Gmail", use_container_width=True, type="primary"):
                with st.spinner("🔄 Connecting to Gmail..."):
                    service = get_gmail_service()
                    if service:
                        st.session_state.gmail_service = service
                        st.session_state.gmail_connected = True
                        st.success("✅ Connected!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Connection failed. Check credentials.json")
        
        st.markdown("---")
        st.header("⚡ Quick Actions")
        
        if st.session_state.gmail_connected:
            if st.button("📥 Check Inbox", use_container_width=True):
                with st.spinner("📧 Fetching emails..."):
                    result = run_agent("Check my inbox", st.session_state.messages)
                    st.session_state.messages.append(("human", "Check my inbox"))
                    st.session_state.messages.append(("assistant", result))
                st.rerun()
            
            if st.button("🔵 Unread Count", use_container_width=True):
                with st.spinner("🔢 Counting..."):
                    result = run_agent("How many unread emails do I have?", st.session_state.messages)
                    st.session_state.messages.append(("human", "Unread count"))
                    st.session_state.messages.append(("assistant", result))
                st.rerun()
            
            if st.button("🔍 Search Unread", use_container_width=True):
                with st.spinner("🔎 Searching..."):
                    result = run_agent("Search for unread emails", st.session_state.messages)
                    st.session_state.messages.append(("human", "Search unread"))
                    st.session_state.messages.append(("assistant", result))
                st.rerun()
        else:
            st.info("Connect Gmail to use quick actions")
        
        st.markdown("---")
        
        # Statistics
        if st.session_state.gmail_connected:
            st.header("📊 Session Stats")
            st.metric("Messages", len(st.session_state.messages))
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        
        # Setup guide
        with st.expander("📖 Setup Guide"):
            st.markdown("""
**First Time Setup:**

1. **Google Cloud Console**
   - Visit console.cloud.google.com
   - Create new project

2. **Enable Gmail API**
   - Go to APIs & Services → Library
   - Search "Gmail API" → Enable

3. **Create Credentials**
   - APIs & Services → Credentials
   - Create OAuth 2.0 Client ID
   - Type: Desktop app
   - Download as `credentials.json`

4. **Place File**
   - Put `credentials.json` in project folder
   - Click "Connect Gmail" button
            """)
    
    # Main chat area
    st.subheader("💬 Chat with Your Gmail Agent")
    
    if not st.session_state.gmail_connected:
        st.warning("⚠️ Please connect your Gmail account using the sidebar to start chatting.")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for role, content in st.session_state.messages:
            if role == "human":
                with st.chat_message("user"):
                    st.write(content)
            else:
                with st.chat_message("assistant"):
                    st.markdown(content)
    
    # Chat input
    if prompt := st.chat_input("💬 Ask about your emails... (e.g., 'Check my inbox', 'Send email to john@example.com')"):
        if not st.session_state.gmail_connected:
            st.error("❌ Please connect Gmail first!")
            return
        
        st.session_state.messages.append(("human", prompt))
        
        with st.spinner("🤔 Processing your request..."):
            result = run_agent(prompt, st.session_state.messages[:-1])
            st.session_state.messages.append(("assistant", result))
        
        st.rerun()
    
    # Examples section
    with st.expander("💡 Example Commands"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
**Reading Emails:**
- "Check my inbox"
- "Show me last 20 emails"
- "How many unread emails?"
- "Read email number 3"
- "Search emails from john@example.com"
            """)
        
        with col2:
            st.markdown("""
**Sending Emails:**
- "Send email to jane@example.com"
- "Send meeting invite to team@company.com"

**Searching:**
- "Search for emails about project"
- "Find unread emails from last week"
            """)

# ==================== RUN ====================
if __name__ == "__main__":
    main()
