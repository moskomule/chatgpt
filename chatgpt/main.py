import json

import openai
import streamlit as st


# utility functions
def message_too_long(messages: list[dict[str, str]], max_length: int) -> bool:
    length = sum([len(message["content"]) for message in messages])
    return length > max_length


def clear_history():
    st.session_state.generated = []
    st.session_state.past = []
    st.session_state.messages = []
    st.session_state.user_text = ""


def show_text_input():
    st.text_area(label="chat with GPT:", value=st.session_state.user_text, key="user_text")


def chat(model_name: str, messages: list[dict[str, str]]) -> dict:
    with st.spinner("please wait..."):
        return openai.ChatCompletion.create(model=model_name, messages=messages)


def show_chat(response: str, user_text: str):
    if response not in st.session_state.generated:
        st.session_state.past.append(user_text)
        st.session_state.generated.append(response)
    if st.session_state.generated:
        for i, (past, generated) in enumerate(zip(st.session_state.generated, st.session_state.past)):
            st.write(f"user: {past}")
            st.markdown(f"assistant: {generated}")


def show_conversation(model_name: str, system_input: str):
    if len(st.session_state.messages) > 0:
        st.session_state.messages.append({"role": "user", "content": st.session_state.user_text})
    else:
        st.session_state.messages = [{"role": "system", "content": system_input},
                                     {"role": "user", "content": st.session_state.user_text}]
    response = chat(model_name, st.session_state.messages)["choices"][0]["message"]["content"]
    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
        show_chat(response, st.session_state.user_text)
        st.divider()


st.title("ChatGPT")

# initialize
if "generated" not in st.session_state:
    st.session_state.generated = []
if "past" not in st.session_state:
    st.session_state.past = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_text" not in st.session_state:
    st.session_state.user_text = ""

with st.expander("system settings"):
    system_input = st.text_input("inputs to system", "You are a helpful assistant to support researchers.")
    model_name = st.selectbox("GPT backend", ("gpt-3.5-turbo", "gpt-4-0314", "gpt-4-32k-0314"))
    history_length = st.text_input("Max number of characters in history", 40_000)

st.download_button("save chat", json.dumps(st.session_state.messages), mime="application/json")

if st.session_state.user_text:
    show_conversation(model_name, system_input)
    st.session_state.user_text = ""
show_text_input()
