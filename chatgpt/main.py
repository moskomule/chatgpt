import json

import openai
import streamlit as st


def message_too_long(messages, max_length):
    length = sum([len(message["content"]) for message in messages])
    return length > max_length


st.title("ChatGPT")

system_input = st.text_input("inputs to system", "You are a helpful assistant to support researchers.")

messages = [{"role": "system", "content": system_input}]
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_input}]

st.download_button("save chat", json.dumps(st.session_state.messages), mime="application/json")

model = st.selectbox("GPT backend", ("gpt-3.5-turbo", "gpt-4-0314", "gpt-4-32k-0314"))

input = st.text_area("▷user's input", disabled=len(st.session_state.messages) > 1)
key = 0

while True:

    if len(input) > 0:
        st.session_state.messages.append({"role": "user", "content": input})

        with st.spinner("please wait..."):
            while message_too_long(messages, 40_000):
                # to keep system message (index=0)
                messages.pop(1)
            results = openai.ChatCompletion.create(model=model, messages=messages)

        for result in results['choices']:
            st.write("▶assistant's reply")
            st.write(result["message"]["content"])
            messages.append({"role": "assistant", "content": result["message"]["content"]})
            st.session_state.messages.append({"role": "assistant", "content": result["message"]["content"]})

        input = st.text_area("▷user's input", key=key)
        key += 1
