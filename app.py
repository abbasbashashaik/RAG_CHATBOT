# import streamlit as st
# from src.rag import RAGPipeline



# def main():
#     st.set_page_config(
#     page_title="Customer Support Agent",
#     page_icon="💬",
#     layout="centered",
#     )
#     st.title("customer support bot")
#     # Initialize the RAG Pipeline once and store it in session state
#     if "rag" not in st.session_state:
#         with st.spinner("Initializing AI Agent..."):
#             rag = RAGPipeline()
#             rag.initialize()
#             st.session_state.rag = rag
#     # Handle the chat input and response
#     if question := st.chat_input("Ask question about the story"):
#         with st.spinner("Thinking..."):
#             answer = st.session_state.rag.ask(question)
#         st.markdown(question)
#         st.markdown(answer)
    


# if __name__ == "__main__":
#     main()


import streamlit as st

from src.rag import RAGPipeline
def get_response(question):

    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]
    thanks = [ "thanks", "thank you", "thx" ]
    goodbye = [ "bye", "goodbye", "see you" ]
    question_lower = question.lower().strip()

    if question_lower in greetings:
        return "Hello! 👋 How can I help you today?" 
# Handle thank you messages 
    elif question_lower in thanks:
        return "You're welcome! 😊 Is there anything else I can help you with?" 
    # Handle goodbye messages 
    elif question_lower in goodbye:
        return "Goodbye! 👋 Have a great day!"
     # Send all other questions to RAG 
    else: return st.session_state.rag.ask(question)
def main():

    st.set_page_config(
        page_title="Customer Support Agent",
        page_icon="💬",
        layout="centered"
    )

    st.title("💬 Customer Support Agent")
    st.caption("I'm an Assistant to help you on troubleshooting")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize RAG Pipeline
    if "rag" not in st.session_state:
        with st.spinner("Initializing AI Agent..."):
            rag = RAGPipeline()
            rag.initialize()
            st.session_state.rag = rag

    # Clear chat button
    with st.sidebar:
        st.header("click here to clear chat....")
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    # Display previous conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if question := st.chat_input("Ask question about the story"):

        # Show and save user message
        with st.chat_message("user"):
            st.markdown(question)

        st.session_state.messages.append(
            {"role": "user", "content": question}
        )


        # Generate and show AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer =get_response(question)

            st.markdown(answer)

        # Save AI response
        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )


if __name__ == "__main__":
    main()