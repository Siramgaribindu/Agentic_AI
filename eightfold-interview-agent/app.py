import streamlit as st
import requests
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="AI Interview Practice Partner",
    page_icon="💼",
    layout="wide"
)

# ---------- DATABASE STORAGE HELPER ----------
USER_DB_FILE = "user_database.json"

def load_user_db():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    return {"users": {}, "history": {}}

def save_user_db(db):
    with open(USER_DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

db = load_user_db()

# ---------- GROQ AI COMPLETION LAYER ----------
def call_groq_ai(system_prompt: str, user_message: str, chat_history: list = None) -> str:
    """Queries the ultra-fast Llama-3 model on Groq for realistic AI interaction."""
    api_key = st.secrets.get("GROQ_API_KEY", "") if "GROQ_API_KEY" in st.secrets else os.environ.get("GROQ_API_KEY", "")
    
    if not api_key:
        return "⚠️ [Configuration Error]: Please add your GROQ_API_KEY to Streamlit Secrets to activate real conversation layers."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = [{"role": "system", "content": system_prompt}]
    if chat_history:
        for msg in chat_history:
            # Strip custom markdown headers to pass clean text to context window
            clean_content = msg["content"].replace("## SCORECARD\n\n", "")
            messages.append({"role": msg["role"], "content": clean_content})
            
    messages.append({"role": "user", "content": user_message})
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI Generation Error: Please verify your connection or API parameters. Details: {e}"

# ---------- INITIALIZE GLOBAL SESSION STATES ----------
if "authenticated_user" not in st.session_state: st.session_state.authenticated_user = None
if "messages" not in st.session_state: st.session_state.messages = []
if "interview_started" not in st.session_state: st.session_state.interview_started = False
if "current_stage" not in st.session_state: st.session_state.current_stage = "INTRO"
if "job_role" not in st.session_state: st.session_state.job_role = ""
if "difficulty" not in st.session_state: st.session_state.difficulty = ""

STAGES = ["INTRO", "TECHNICAL_1", "TECHNICAL_2", "BEHAVIORAL", "FEEDBACK"]

# ---------- CSS DESIGN OVERHAUL ----------
st.markdown("""
<style>
.main { background-color: #0f172a; color: white; }
.header-card {
    background: linear-gradient(135deg, #1e1b4b, #312e81);
    padding: 25px; border-radius: 16px; margin-bottom: 20px; border: 1px solid #4338ca; color: white;
}
.step-pill { padding: 6px 14px; border-radius: 20px; display: inline-block; margin-right: 6px; font-size: 0.85rem; font-weight: 600; }
.active-pill { background: #3b82f6; color: white; }
.inactive-pill { background: #1e293b; color: #94a3b8; }
.interviewer-box { background: #1e293b; border-left: 6px solid #8b5cf6; padding: 20px; border-radius: 12px; margin: 15px 0; color: white; }
.interviewer-title { color: #c084fc; font-weight: bold; margin-bottom: 8px; }
.interviewer-text { color: white; font-size: 1rem; line-height: 1.6; }
.candidate-box { background: #111827; border: 1px solid #374151; padding: 18px; border-radius: 12px; margin: 15px 0 15px auto; color: white; }
.candidate-title { color: #9ca3af; font-weight: bold; margin-bottom: 8px; }
.scorecard-container { background: #0b1329; border: 2px solid #10b981; padding: 25px; border-radius: 16px; margin-top: 20px; color: white; }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# VIEW 1: AUTHENTICATION (LOGIN / REGISTER)
# ==============================================================================
def render_login_page():
    st.markdown('<div class="header-card"><h1>🔐 Access Portal</h1><p>Sign in or register to start your simulation history profiles.</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
    
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", type="primary"):
            if username in db["users"] and db["users"][username] == password:
                st.session_state.authenticated_user = username
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid credential details. Please check again.")
                
    with tab2:
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        if st.button("Register Account"):
            if not new_user.strip() or not new_pass.strip():
                st.warning("Fields cannot remain blank.")
            elif new_user in db["users"]:
                st.error("Username already taken!")
            else:
                db["users"][new_user] = new_pass
                if new_user not in db["history"]: db["history"][new_user] = []
                save_user_db(db)
                st.success("Account initialized successfully! Please jump to the login tab.")


# ==============================================================================
# VIEW 2: INTERVIEW SIMULATOR WORKSPACE
# ==============================================================================
def render_simulator_page():
    st.markdown('<div class="header-card"><h1>💼 AI Interview Practice Partner</h1><p>Professional AI Mock Interview Simulator</p></div>', unsafe_allow_html=True)
    
    if not st.session_state.interview_started:
        st.markdown("### Configure Your Interview Session")
        col1, col2 = st.columns(2)
        with col1:
            role = st.text_input("Job Role Target", placeholder="e.g., Frontend Web Developer")
        with col2:
            difficulty = st.selectbox("Experience Level", ["Internship Level", "Associate / Junior Level", "Mid-Senior Level"])

        if st.button("🚀 Begin Assessment", use_container_width=True, type="primary"):
            if not role.strip():
                st.warning("Please define your target job role.")
                return
                
            st.session_state.job_role = role
            st.session_state.difficulty = difficulty
            st.session_state.interview_started = True
            st.session_state.current_stage = "INTRO"
            st.session_state.messages = []
            
            system_prompt = f"You are an executive interviewer assessing a candidate for a {role} position at the {difficulty} level. This is the INTRO stage. Greet them, remain highly realistic, and ask them to introduce themselves based on the target profile requirements."
            with st.spinner("Panel connecting..."):
                initial_q = call_groq_ai(system_prompt, "Hello, I am ready to start my interview.")
                st.session_state.messages.append({"role": "assistant", "content": initial_q})
                st.rerun()
    else:
        # Step Progress Pills
        pills_html = "<div>"
        for stage in STAGES:
            css = "active-pill" if stage == st.session_state.current_stage else "inactive-pill"
            pills_html += f'<span class="step-pill {css}">{stage}</span>'
        pills_html += "</div><br>"
        st.markdown(pills_html, unsafe_allow_html=True)

        # Print history dialogue boxes
        last_assistant_idx = -1
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "assistant": last_assistant_idx = i

        for idx, msg in enumerate(st.session_state.messages):
            if msg["role"] == "assistant" and "## SCORECARD" in msg["content"]:
                st.markdown(f'<div class="scorecard-container">{msg["content"]}</div>', unsafe_allow_html=True)
            elif msg["role"] == "assistant":
                st.markdown(f'<div class="interviewer-box"><div class="interviewer-title">🎙️ Senior Interview Panel</div><div class="interviewer-text">{msg["content"]}</div></div>', unsafe_allow_html=True)
                
                if st.session_state.current_stage != "FEEDBACK" and idx == last_assistant_idx:
                    speech_text = msg["content"].replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
                    st.components.v1.html(f'<script>window.parent.speechSynthesis.cancel(); var s = new SpeechSynthesisUtterance("{speech_text}"); s.rate=1; window.parent.speechSynthesis.speak(s);</script>', height=0)
            else:
                st.markdown(f'<div class="candidate-box"><div class="candidate-title">👤 Candidate ({st.session_state.authenticated_user})</div><div>{msg["content"]}</div></div>', unsafe_allow_html=True)

        # Dynamic Evaluator Script trigger
        if st.session_state.current_stage == "FEEDBACK":
            if len(st.session_state.messages) > 0 and "## SCORECARD" not in st.session_state.messages[-1]["content"]:
                with st.spinner("Compiling structural scores & final metrics..."):
                    system_prompt = f"Analyze the following conversation context. Generate a final professional, structural evaluation scorecard for a {st.session_state.job_role} position at a {st.session_state.difficulty} level. Format your response clearly starting with '## SCORECARD', giving numerical marks out of 10 for technical depth and communication framework matching, plus clear direct bullet summaries."
                    scorecard_content = call_groq_ai(system_prompt, "Evaluate our entire conversation transcript history.", st.session_state.messages)
                    
                    full_scorecard = "## SCORECARD\n\n" + scorecard_content
                    st.session_state.messages.append({"role": "assistant", "content": full_scorecard})
                    
                    # PERSIST TO FILE DB HISTORY LOGGER
                    record = {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "role": st.session_state.job_role,
                        "difficulty": st.session_state.difficulty,
                        "scorecard": full_scorecard
                    }
                    if st.session_state.authenticated_user in db["history"]:
                        db["history"][st.session_state.authenticated_user].append(record)
                    else:
                        db["history"][st.session_state.authenticated_user] = [record]
                    save_user_db(db)
                    st.rerun()
        else:
            user_input = st.chat_input("Provide your interview reply here...")
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                current_index = STAGES.index(st.session_state.current_stage)
                next_stage = STAGES[current_index + 1] if current_index < len(STAGES) - 1 else "FEEDBACK"
                st.session_state.current_stage = next_stage
                
                if next_stage != "FEEDBACK":
                    sys_instructions = f"You are a realistic corporate recruiter interviewing the candidate for a {st.session_state.job_role} profile ({st.session_state.difficulty}). We are now moving to the {next_stage} round. Acknowledge their prior answer organically, challenge any weak statements, and shift professionally to a question fitting the {next_stage} category."
                    next_q = call_groq_ai(sys_instructions, user_input, st.session_state.messages[:-1])
                    st.session_state.messages.append({"role": "assistant", "content": next_q})
                st.rerun()


# ==============================================================================
# VIEW 3: PAST PERFORMANCE ARCHIVE LOGS
# ==============================================================================
def render_history_page():
    st.markdown('<div class="header-card"><h1>📜 Your Past Performance Logs</h1><p>Review metrics, growth tracking history, and panel remarks from past sessions.</p></div>', unsafe_allow_html=True)
    
    user_records = db["history"].get(st.session_state.authenticated_user, [])
    
    if not user_records:
        st.info("No completed interview history sessions found yet. Wrap up an interview session first!")
    else:
        for idx, item in enumerate(reversed(user_records)):
            with st.expander(f"💼 {item['role']} ({item['difficulty']}) — Completed on {item['date']}"):
                st.markdown(item["scorecard"])


# ==============================================================================
# DYNAMIC MULTIPAGE NAVIGATION CONTROLLER
# ==============================================================================
if not st.session_state.authenticated_user:
    render_login_page()
else:
    # Build sidebar controller links
    with st.sidebar:
        st.markdown(f"### 👤 Profile: **{st.session_state.authenticated_user}**")
        st.markdown("---")
        
        # Navigation parameters
        nav_selection = st.radio("Navigate Workspace", ["🎙️ Live Simulator", "📜 Performance History"])
        
        st.markdown("---")
        if st.session_state.interview_started:
            st.caption(f"🎯 Target: {st.session_state.job_role}")
            if st.button("🔄 Reset / Start New"):
                st.session_state.interview_started = False
                st.session_state.messages = []
                st.session_state.current_stage = "INTRO"
                st.rerun()
                
        if st.button("🚪 System Logout"):
            st.session_state.authenticated_user = None
            st.session_state.interview_started = False
            st.rerun()
            
    if nav_selection == "🎙️ Live Simulator":
        render_simulator_page()
    elif nav_selection == "📜 Performance History":
        render_history_page()
