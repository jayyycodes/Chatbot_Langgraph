import streamlit as st
from backend import workflow,retrive_all_theards
from langchain_core.messages import HumanMessage
import uuid
import sqlite3

def genarate_threadid():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = genarate_threadid()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []
    st.rerun()  # force clean re-render after reset

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_convos(thread_id):
    state = workflow.get_state(config={
        "configurable": {
            "thread_id": thread_id
        }
    })
    return state.values.get('messages', [])


# ── Session state init ────────────────────────────────────────────────────────
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = genarate_threadid()
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrive_all_theards()

add_thread(st.session_state['thread_id'])

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title('Ez Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('Past Chats')

for t_id in st.session_state['chat_threads']:
    # Show a short label (last 8 chars of UUID) so buttons aren't huge
    label = f"Chat ...{str(t_id)[-8:]}"
    if st.sidebar.button(label, key=str(t_id)):
        st.session_state['thread_id'] = t_id
        messages = load_convos(t_id)

        temp_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role': role, 'content': message.text})

        st.session_state['message_history'] = temp_messages
        st.rerun()  # BUG FIX 2: force re-render so loaded messages display cleanly

# ── Config is built HERE, after sidebar has potentially updated thread_id ─────
# BUG FIX 1: was placed before sidebar, so it captured stale thread_id
config = {
    "configurable": {
        "thread_id": st.session_state['thread_id']
    }
}

# ── Chat UI ───────────────────────────────────────────────────────────────────
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('type here...')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('assistant'):
        # BUG FIX 3: AIMessageChunk uses .content, not .text
        ai_message = st.write_stream(
            message_chunk.text
            for message_chunk, metadata in workflow.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=config,
                stream_mode='messages'
            )
            if message_chunk.text  # skip empty chunks
        )
        st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
