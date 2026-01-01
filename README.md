# 📧 Autonomous Gmail Agent (Production-Ready With Langchain)

**Autonomous Gmail Agent** is not your ordinary email tool — it’s a **fully autonomous AI executive assistant** that securely connects to your Gmail, understands your intent, and actively manages your inbox using natural language.

Unlike standard chatbots, this system leverages **Agentic Workflows**. It doesn't just generate text; it actively **reasons, searches, fetches, and executes** tasks using real-world APIs. It combines the reasoning power of **Google Gemini 2.5 Flash** with the orchestration capabilities of **LangChain** to create a seamless, intelligent email experience.

---

## 🚀 Key Features

### 🧠 **Agentic Reasoning & Function Calling**
The system doesn't just guess; it "thinks." It uses **Function Calling** to translate natural language (e.g., *"Find emails from John about the meeting"*) into precise API execution strategies. It autonomously decides *which* tool to use (search, fetch, send) based on your request.

### 🔐 **Production-Grade Security**
* **OAuth 2.0 Authorization Code Flow:** Implements the official Google Auth flow for secure access.
* **Local Token Persistence:** Safely serializes `token.pickle` for seamless session management without re-login.
* **Zero-Trust Data:** Runs entirely locally; your email data never touches a third-party server (other than Google/Gemini APIs).

### 📥 **Intelligent Inbox Management**
* **Deep Parsing:** It doesn't just read subject lines; it parses complex MIME types and decodes base64 email bodies to understand the full context of threads.
* **Smart Unread Tracking:** Instantly fetches and reports unread counts with a single command.

### 🔍 **Semantic Search**
Forget complex search operators. Just ask:
* *"Show me emails from HR sent last week."*
* *"Find the invoice from Amazon."*
The agent translates these into optimized Gmail queries like `from:hr@company.com newer_than:7d`.

### ⚡ **Autonomous Action**
The system is capable of **drafting and sending emails programmatically**.
* *"Reply to this email saying I agree."*
* *"Send an email to user@example.com with the subject 'Update'."*

### 🎨 **Modern Streamlit Interface**
* **Real-Time Chat UI:** A beautiful, chat-based interface that maintains conversation history.
* **Session State Management:** Remembers previous turns (e.g., *"Read that last email"* refers to the one just found).
* **Connection Dashboard:** Clear sidebar controls for authentication status and quick actions.

---

## 🧩 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Orchestration** | [LangChain](https://langchain.com/) (Agents & Tools) |
| **AI Model** | [Google Gemini 2.5 Flash](https://deepmind.google/technologies/gemini/) |
| **Frontend/UI** | [Streamlit](https://streamlit.io/) |
| **API** | Google Gmail API (REST v1) |
| **Auth** | OAuth 2.0 Client & `google-auth` |
| **Language** | Python 3.10+ |

---

## 🔑 API Key Sources

To use this project, you will need to set up credentials for two services:

| API | Source |
| :--- | :--- |
| **🤖 Google Gemini** | [Get API Key from Google AI Studio](https://aistudio.google.com/app/apikey) |
| **📧 Gmail API** | [Enable via Google Cloud Console](https://console.cloud.google.com/) |

* **Gemini Key:** Store this in a `.env` file (e.g., `GOOGLE_API_KEY=...`).
* **Gmail Credentials:** Download the OAuth 2.0 Client JSON file from Google Cloud and save it as `credentials.json` in the root directory.

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone [https://github.com/yourusername/autonomous-gmail-agent.git](https://github.com/yourusername/autonomous-gmail-agent.git)
cd autonomous-gmail-agent
```
### 2️⃣ Create Virtual Environment
**It is recommended to use a virtual environment to manage dependencies.

# Bash
```
python -m venv venv
```

# Windows
```
venv\Scripts\activate
```
# Mac/Linux
```
source venv/bin/activate
```
### 3️⃣ Install Dependencies
# Bash
```
pip install -r requirements.txt
```
### 4️⃣ Configure Credential
1:Create a .env file in the root folder:
# Code snippet
```
GOOGLE_API_KEY=your_gemini_api_key_here
```
2:Place your downloaded credentials.json file in the root folder.
### 5️⃣ Run the App
# Bash
```
streamlit run app.py
```
Open your browser and navigate to:👉http://localhost:8501💡

---
### 💡How It Works

Connect: Click the "Connect Gmail" button in the sidebar.The app initiates a secure OAuth flow.

Authenticate*: Grant permissions via the Google popup (only needed once; tokens are saved locally).

Command: Type a natural language query (e.g., "Check my inbox").

Reasoning: The Gemini model analyzes the request and determines which tool to call (e.g., check_gmail_inbox).

Execution: LangChain executes the tool, fetches data from the Gmail API, and returns it to the model.

Response: The agent synthesizes the data into a clear, natural language response displayed in the chat.

---
## 📊 Example Queries
```
|User Says 🗣️                           | Agent Does 🤖 |
| :---                                   | :--- |
| `Check my inbox for the last 5 emails` | `check_gmail_inbox(max_results=5)` |
| `Find emails from John sent yesterday` | `search_gmail(query="from:John older_than:1d")` |
| `Read email number 3`                  | `read_email_content(email_number=3)` |
| `How many unread emails do I have?`    | `get_unread_count()` |
| `Send an email to jane@example.com`    | `send_gmail(to="jane@example.com", ...)` |
```
---

### 🔐 Notes & Limitations❌

* Local Use Only: 

This project is designed for local execution.

Deploying to a public server requires additional security configurations for OAuth callback URLs.

---

### ⚠️ Sensitive Data: 

Your credentials.json and token.pickle contain sensitive access keys. 

Never commit these files to GitHub. (They are already added to .gitignore).

---

### 📧 Rate Limits:

Usage is subject to Google Gmail API rate limits.

---

### 📈 Future Enhancements

🗓️ Calendar Integration: Extend the agent to manage Google Calendar events.

🎙️ Voice Mode: Add speech-to-text for a fully hands-free experience.

🧠 RAG (Retrieval Augmented Generation): Chat with your entire email archive using vector embeddings.

📎 Attachment Handling: Add capability to summarize or download email attachments.

---

### 🤝 Contributing

Contributions are welcome! If you want to improve the agent, add new tools, or enhance the UI:

# Bash
```
Fork → Create Branch → Commit → Push → Pull Request
```

---

### 👨‍💻 AuthorDeveloped by: Nofil Ahmed Khan

📧 Email: nofil2012@gmail.com

🌐 LinkedIn: linkedin.com/in/khannofil

💬 Building practical AI projects that merge intelligence, interaction, and innovation.

---

### 📜 License'
This project is open-source under the MIT License.

Created with 💙 by Nofil Ahmed Khan — where AI meets real-world productivity.
