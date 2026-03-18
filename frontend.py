import os
import time

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="JobFinder", page_icon="💼")
st.title("JobFinder")

for key, default in [
    ("mode", None),
    ("session_id", None),
    ("is_complete", False),
    ("matches", None),
    ("messages", []),
    ("pending_answer", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def reset() -> None:
    for key in ["mode", "session_id", "matches", "pending_answer"]:
        st.session_state[key] = None
    st.session_state.is_complete = False
    st.session_state.messages = []


def char_stream(text: str):
    for char in text:
        yield char
        time.sleep(0.015)


def show_matches(matches: list) -> None:
    st.subheader("Matchade jobb")
    for job in matches:
        with st.container(border=True):
            st.markdown(f"### {job['title']}")
            st.caption(f"{job['employer_name']} · {job['location']} · {job['score']:.0%} match")
            st.write(job["short_description"])
            st.link_button("Ansök", job["job_url"])


def render_messages() -> None:
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])


if st.session_state.is_complete:
    render_messages()
    if st.session_state.matches:
        show_matches(st.session_state.matches)
    else:
        st.info("Inga matchande jobb hittades för din profil och plats.")
    if st.button("Börja om"):
        reset()
        st.rerun()
    st.stop()

if not st.session_state.mode:
    st.write("Hur vill du söka jobb?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ladda upp CV", use_container_width=True):
            st.session_state.mode = "resume"
            st.rerun()
    with col2:
        if st.button("Starta intervju", use_container_width=True):
            st.session_state.mode = "interview"
            st.rerun()
    st.stop()

if st.session_state.mode == "resume" and not st.session_state.session_id:
    uploaded = st.file_uploader("Ladda upp ditt CV", type=["pdf", "docx"])
    if uploaded:
        with st.spinner("Analyserar CV..."):
            res = requests.post(
                f"{BACKEND_URL}/api/v1/resume",
                files={"file": (uploaded.name, uploaded.read(), uploaded.type)},
            )
        data = res.json()
        st.session_state.session_id = data["session_id"]
        st.session_state.is_complete = data["is_complete"]
        st.session_state.matches = data.get("matches")
        if data.get("next_question"):
            st.session_state.messages.append({"role": "assistant", "content": data["next_question"]})
        st.rerun()
    st.stop()

if st.session_state.mode == "interview" and not st.session_state.session_id:
    with st.spinner("Startar..."):
        res = requests.post(f"{BACKEND_URL}/api/v1/interview/start")
    data = res.json()
    st.session_state.session_id = data["session_id"]
    st.session_state.messages.append({"role": "assistant", "content": data["question"]})
    st.rerun()

render_messages()

if st.session_state.pending_answer:
    answer = st.session_state.pending_answer
    st.session_state.pending_answer = None
    res = requests.post(
        f"{BACKEND_URL}/api/v1/interview/answer",
        json={"session_id": st.session_state.session_id, "answer": answer},
    )
    if not res.ok:
        st.error(f"Fel från backend ({res.status_code}): {res.text}")
        st.stop()
    data = res.json()
    st.session_state.is_complete = data["is_complete"]
    st.session_state.matches = data.get("matches")
    if data.get("next_question"):
        with st.chat_message("assistant"):
            response = st.write_stream(char_stream(data["next_question"]))
        st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

if answer := st.chat_input("Skriv ditt svar..."):
    st.session_state.messages.append({"role": "user", "content": answer})
    st.session_state.pending_answer = answer
    st.rerun()
