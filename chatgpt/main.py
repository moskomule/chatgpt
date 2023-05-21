# chatgpt client
# inspired by https://blog.streamlit.io/ai-talks-chatgpt-assistant-via-streamlit/

import json
import warnings

import openai
import streamlit as st


# utility functions
def message_too_long(messages: list[dict[str, str]], max_length: int) -> bool:
    length = sum([len(message["content"]) for message in messages])
    return length > max_length


def clear_history():
    warnings.warn('clear history')
    st.session_state.generated_texts = []
    st.session_state.past_user_texts = []
    st.session_state.messages = []
    st.session_state.current_user_text = ""


def show_text_input():
    st.text_area(label="Chat with GPT:", value=st.session_state.current_user_text, key="current_user_text")


def chat(model_name: str, messages: list[dict[str, str]]) -> dict:
    with st.spinner(f"Asking ..."):
        return openai.ChatCompletion.create(model=model_name, messages=messages)


def show_chat(response: str, user_text: str):
    if response not in st.session_state.generated_texts:
        st.session_state.past_user_texts.append(user_text)
        st.session_state.generated_texts.append(response)
    if st.session_state.generated_texts:
        for user, generated in zip(st.session_state.past_user_texts, st.session_state.generated_texts):
            st.write(f"▷User")
            st.write(user)
            st.write("▶Assistant")
            st.markdown(generated)


def show_conversation(model_name: str, system_input: str):
    if len(st.session_state.messages) > 0:
        st.session_state.messages.append({"role": "user", "content": st.session_state.current_user_text})
    else:
        st.session_state.messages = [{"role": "system", "content": system_input},
                                     {"role": "user", "content": st.session_state.current_user_text}]
    response = chat(model_name, st.session_state.messages)["choices"][0]["message"]["content"]
    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
        show_chat(response, st.session_state.current_user_text)
        st.divider()


# contents from here
st.title("ChatGPT")

# initialize
if "generated_texts" not in st.session_state:
    st.session_state.generated_texts = []
if "past_user_texts" not in st.session_state:
    st.session_state.past_user_texts = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_user_text" not in st.session_state:
    st.session_state.current_user_text = ""

with st.expander("System settings"):
    system_input = st.text_input("inputs to system", "You are a helpful assistant to support researchers.")
    model_name = st.selectbox("GPT backend", ("gpt-3.5-turbo", "gpt-4-0314", "gpt-4-32k-0314"))

with st.expander("Debug info"):
    st.write(st.session_state.messages)

col0, col1 = st.columns(2)
with col0, col1:
    col0.download_button("Save chat", json.dumps(st.session_state.messages), mime="application/json")
    col1.button("Clear history", on_click=clear_history)

if st.session_state.current_user_text:
    show_conversation(model_name, system_input)
    st.session_state.current_user_text = ""
show_text_input()
