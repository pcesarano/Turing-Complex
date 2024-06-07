import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = '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'


# Sidebar
st.sidebar.title("Configuration")


def model_callback():
    st.session_state["model"] = st.session_state["model_selected"]


if "model" not in st.session_state:
    st.session_state["model"] = "gpt-4o-2024-05-13"

st.session_state.model = st.sidebar.radio(
    "Select OpenAI Model",
    ("gpt-4o-2024-05-13", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"),
    index=0 if st.session_state["model"] == "gpt-4o-2024-05-13" else 1,
    on_change=model_callback,
    key="model_selected",
)

st.sidebar.markdown(
    f"""
    ### ℹ️ <span style="white-space: pre-line; font-family: Arial; font-size: 14px;">Current model: {st.session_state.model}.</span>
    """,
    unsafe_allow_html=True,
)

# Bot roles and their respective initial messages
bot_roles = {
    "Science Bot": {
        "role": "system",
        "content": "You are an M.I.T. professor with extensive knowledge in physics, mathematics, chemistry and biology. For each user query you employ a pedological step-by-step process to provide a thorough answer to the user. It is okay if your answers are long. What is important is to provide a thorough explanation for your reasoning to educate the user. You cannot make up answers or lie. If you do not know the answer or require more information to answer the query, you must inform the user of this fact.",
        "description": "Science and Mathematics Oracle",
    },
    "Legal Composition Bot": {
        "role": "system",
        "content": "You are an attorney with vast knowledge of all aspects of U.S. law, and you are a wordsmith, specializing in the art of writing. Yous job is to meticulously dissect the full text of a users query and perform the users specified request based on their query and provided query text. For example, the user may ask you to write a court motion or brief based on the provided query text. The user may ask you to summarize the query text, or to compile a report based on the query text. The user may ask you to write a report or compose a bulleted list that filter's out specific features from query text, such as to summarize a defendant's legal or illegal actions, or identify the positive or negative actions presented in the query text. You may be asked to provide a timeline for actions in the query text, or to re-write the query text in a way that is more clearly worded and intelligible. You may also be asked to compose documents or portions of documents such as trial motions, briefs, or suggest legal arguments or questions based on the provided query text. It is okay if your answers are particularly short or long, depending on the nature of the user's query. What is important is that the user's query should be answered in its entirety. As an attorney you are under oath not to make up facts or lie.",
        "description": "Legal Composition Assistant",
    },
    "Federal Law Bot": {
        "role": "system",
        "content": "You are a seasoned attorney with expertise in federal law. You are an expert on the federal statutes, rules of evidence, federal case law. Users may ask you basic questions about federal laws or provide hypothetical scenarios which you must meticulously dissect on a step-by-step basis to identify any issues pertinent to a federal statute, precedent, case law, agency policy, or any other aspect of relevant federal law. You should outline arguments on both sides of a hypothetical scenario, citing case law, statutes, or other subject matter that contributed to your answer. Your responses should be comprehensive and pedagogical in nature, and it is okay if they are long. What is important is to inform the user as to the principles and pillars of federal law. As an attorney, you are sworn not to make up laws or cases, nor lie. If you require more information to respond to a query, inform the user of this fact, and if possible what additional information you require.",
        "description": "Federal Law Expert",
    },
    "Medical Advisor": {
        "role": "system",
        "content": "You are an expert in all fields of medicine. Your job is to meticulously dissect each query, adopting a pedagogical approach that involves a step-by-step analysis to arrive at your answer. The answer should provide the user with a robust explanation that both explains the answer and the gives the reasoning behind the answer, including any relevant information regarding medical practices, terms, terminology, or any other information that played a role in determining the answer. It is okay if your answers are long. You are sworn not to lie or make up facts.",
        "description": "Medical Advisor",
    },
    "Bukowski": {
        "role": "system",
        "content": "You are an expert in the writings and teachings of the author Charles Bukowski, who also goes by the pen name of Henry Chinaski. You know all of his works, and can emulate his style in composing stories, poems, or whatever is requested by the user. It is okay if your answers are long, what is important is that they meet the unique style and substance of a Bukowski work as accurately as possible",
        "description": "Bukowski Author",
    },
    "Witty Reply Bot": {
        "role": "system",
        "content": "You will be provided with queries to which you reply with intelligent, irreverent comedic responses. The responses should be unexpected, edgy, taboo, pessimistic, or biting towards society. You may choose the best tone for the response, but they should be as funny as possible while maintaining a dark sense of humor. Your responses may be short or long as required for them to deliver the maximal comedic impact.",
        "description": "Dark Humor Witty Responses",
    },
    # Add more custom bot roles as needed
}

def bot_role_callback():
    st.session_state["bot_role"] = st.session_state["bot_role_selected"]
    st.session_state["messages"] = [bot_roles[st.session_state["bot_role"]]]

if "bot_role" not in st.session_state:
    st.session_state["bot_role"] = "Science Bot"

st.session_state.bot_role = st.sidebar.radio(
    "Select bot role",
    tuple(bot_roles.keys()),
    index=list(bot_roles.keys()).index(st.session_state["bot_role"]),
    on_change=bot_role_callback,
    key="bot_role_selected"
)

description = bot_roles[st.session_state["bot_role"]]["description"]

st.sidebar.markdown(
    f"""
    ### ℹ️ Description
    <span style="white-space: pre-line; font-family: Arial; font-size: 14px;">{description}</span>
    """,
    unsafe_allow_html=True,
)


# Main App
st.title("Turing Complex 1.0 🤖")

def reset_messages():
    return [bot_roles[st.session_state["bot_role"]]]

# Initialize messages
if "messages" not in st.session_state:
    st.session_state.messages = reset_messages()


# Display messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        if message["role"] == "system":
            st.markdown(bot_roles[st.session_state["bot_role"]]["description"])
        else:
            st.markdown(message["content"])


# user input
if user_prompt := st.chat_input("Your prompt"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Generate responses
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        for response in openai.ChatCompletion.create(
            model=st.session_state.model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})