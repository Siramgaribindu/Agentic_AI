import streamlit as st

st.set_page_config(
    page_title="AI Interview Practice Partner",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- MOCK BACKEND LOGIC (In-App) ----------
def get_next_question(stage: str, role_name: str, difficulty: str) -> str:
    stage_responses = {
        "INTRO": f"Welcome! Thank you for joining us today for the {role_name} ({difficulty}) interview. Could you start by introducing yourself and walking me through your professional background?",
        "TECHNICAL_1": "Great presentation. Let's dive into some technical aspects. Can you explain how you handle optimization and system tradeoffs under production-level traffic scale?",
        "TECHNICAL_2": "Interesting approach. Following up on that, how would you design a fault-tolerant system if your core architectural components experience a sudden failure or network split?",
        "BEHAVIORAL": "Excellent instincts. Now, tell me about a time when you disagreed with a manager or coworker on a project tradeoff. How did you handle that communication?",
    }
    return stage_responses.get(stage, "Let's move on to the next segment.")

def get_scorecard(role_name: str, difficulty: str) -> str:
    return f"""### 📊 Performance Assessment Summary
**Position:** {role_name} | **Level:** {difficulty}

---

* **Technical Knowledge:** 🌟 🌟 🌟 🌟 ☆ (8/10)
    * *Strengths:* Strong grasp of structural design and architectural scaling concepts.
    * *Growth Areas:* Can dive deeper into caching architectures and precise error-handling strategies.
* **Communication & Framework Alignment:** 🌟 🌟 🌟 🌟 🌟 (10/10)
    * *Strengths:* Highly articulate structure (STAR method), great professional cadence, and clear problem decomposition.
    
---
### 📝 Interviewer Feedback
"The candidate demonstrated strong foundational knowledge aligned well with the {difficulty} level requirement. Splendid communication loop throughout the session; refining high-concurrency architecture limits will make them an exceptional choice."
"""

# ---------- STYLES ----------
st.markdown("""
<style>
.main { background-color: #0f172a; color: white; }
.header-card {
    background: linear-gradient(135deg, #1e1b4b, #312e81);
    padding: 25px; border-radius: 16px; margin-bottom: 20px; border: 1px solid #4338ca; color: white;
}
.step-pill {
    padding: 6px 14px; border-radius: 20px; display: inline-block; margin-right: 6px; font-size: 0.85rem; font-weight: 600;
}
.active-pill { background: #3b82f6; color: white; }
.inactive-pill { background: #1e293b; color: #94a3b8; }
.interviewer-box {
    background: #1e293b; border-left: 6px solid #8b5cf6; padding: 20px; border-radius: 12px; margin: 15px 0; color: white;
}
.interviewer-title { color: #c084fc; font-weight: bold; margin-bottom: 8px; }
.interviewer-text { color: white; font-size: 1rem; line-height: 1.6; }
.candidate-box {
    background: #111827; border: 1px solid #374151; padding: 18px; border-radius: 12px; margin: 15px 0 15px auto; color: white;
}
.candidate-title { color: #9ca3af; font-weight: bold; margin-bottom: 8px; }
.scorecard-container {
    background: #0b1329; border: 2px solid #10b981; padding: 25px; border-radius: 16px; margin-top: 20px; color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "messages" not in st.session_state: st.session_state.messages = []
if "interview_started" not in st.session_state: st.session_state.interview_started = False
if "job_role" not in st.session_state: st.session_state.job_role = ""
if "difficulty" not in st.session_state: st.session_state.difficulty = ""
if "current_stage" not in st.session_state: st.session_state.current_stage = "INTRO"

STAGES = ["INTRO", "TECHNICAL_1", "TECHNICAL_2", "BEHAVIORAL", "FEEDBACK"]

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 📋 Session Details")
    if st.session_state.interview_started:
        st.metric("Target Role", st.session_state.job_role)
        st.metric("Difficulty", st.session_state.difficulty)
        st.markdown("---")
        if st.button("🔄 Start New Interview", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    else:
        st.info("Configure interview settings to begin.")

# ---------- HEADER ----------
st.markdown("""
<div class="header-card">
    <h1>💼 AI Interview Practice Partner</h1>
    <p>Professional AI Mock Interview Simulator</p>
</div>
""", unsafe_allow_html=True)

# ---------- INTERVIEW SETUP ----------
if not st.session_state.interview_started:
    st.markdown("### Configure Your Interview")
    col1, col2 = st.columns(2)
    
    with col1:
        role = st.text_input("Job Role", placeholder="e.g., Software Engineer")
    with col2:
        difficulty = st.selectbox("Difficulty", ["Internship Level", "Associate / Junior Level", "Mid-Senior Level"])

    if st.button("🚀 Start Interview", use_container_width=True, type="primary"):
        if not role.strip():
            st.warning("Please enter a job role.")
        else:
            st.session_state.job_role = role
            st.session_state.difficulty = difficulty
            st.session_state.interview_started = True
            st.session_state.current_stage = "INTRO"

            initial_question = get_next_question("INTRO", role, difficulty)
            st.session_state.messages.append({"role": "assistant", "content": initial_question})
            st.rerun()

# ---------- INTERVIEW SCREEN ----------
else:
    pills_html = "<div>"
    for stage in STAGES:
        css = "active-pill" if stage == st.session_state.current_stage else "inactive-pill"
        pills_html += f'<span class="step-pill {css}">{stage}</span>'
    pills_html += "</div><br>"
    st.markdown(pills_html, unsafe_allow_html=True)

    last_assistant_idx = -1
    if st.session_state.current_stage != "FEEDBACK":
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "assistant": last_assistant_idx = i

    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "assistant" and "## SCORECARD" in msg["content"]:
            st.markdown(f'<div class="scorecard-container">{msg["content"]}</div>', unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            st.markdown(f"""
            <div class="interviewer-box">
                <div class="interviewer-title">🎙️ Senior Interview Panel</div>
                <div class="interviewer-text">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.current_stage != "FEEDBACK" and idx == last_assistant_idx:
                speech_text = msg["content"].replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
                st.components.v1.html(f"""
                    <script>
                    window.parent.speechSynthesis.cancel();
                    var speech = new SpeechSynthesisUtterance("{speech_text}");
                    speech.rate = 1; speech.pitch = 1;
                    window.parent.speechSynthesis.speak(speech);
                    </script>
                """, height=0)
        else:
            st.markdown(f"""
            <div class="candidate-box">
                <div class="candidate-title">👤 Candidate</div>
                <div>{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

    # ---------- FEEDBACK STAGE ----------
    if st.session_state.current_stage == "FEEDBACK":
        if len(st.session_state.messages) > 0 and "## SCORECARD" not in st.session_state.messages[-1]["content"]:
            with st.spinner("Generating Interview Scorecard..."):
                scorecard_content = get_scorecard(st.session_state.job_role, st.session_state.difficulty)
                st.session_state.messages.append({"role": "assistant", "content": "## SCORECARD\n\n" + scorecard_content})
                st.rerun()

    # ---------- USER INPUT ----------
    else:
        user_input = st.chat_input("Type your answer here...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            current_index = STAGES.index(st.session_state.current_stage)
            if current_index < len(STAGES) - 1:
                st.session_state.current_stage = STAGES[current_index + 1]

            if st.session_state.current_stage != "FEEDBACK":
                next_q = get_next_question(
                    st.session_state.current_stage, 
                    st.session_state.job_role, 
                    st.session_state.difficulty
                )
                st.session_state.messages.append({"role": "assistant", "content": next_q})
                st.rerun()
