import streamlit as st
import requests

# Title of the application
st.title("Learnify AI")
st.markdown("PDF Summarizer and Chat with PDF")

# Upload PDF file
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# Button to summarize the PDF
if st.button("Summarize"):
    if uploaded_file is not None:
        with st.spinner("Summarizing the PDF..."):
            files = {"file": uploaded_file}
            response = requests.post("http://127.0.0.1:8000/summarize", files=files)

            if response.status_code == 200:
                summary = response.json().get("summary")
                st.write("**Summary:**")
                st.write(summary)  # Display the summary
            else:
                st.error("Error summarizing the PDF: " + response.text)
    else:
        st.warning("Please upload a PDF file first.")

# Chat with PDF functionality
st.subheader("Chat with PDF")

# Text input for user question
user_question = st.text_input("Ask a question about the PDF:")
if st.button("Submit Question"):
    if uploaded_file is not None and user_question:
        with st.spinner("Getting answer..."):
            # Send POST request to the FastAPI endpoint for chat
            data = {"question": user_question}
            response = requests.post("http://127.0.0.1:8000/chat", json=data)

            if response.status_code == 200:
                answers = response.json().get("answers", [])
                st.write("**Answers:**")
                for answer in answers:
                    st.write("- " + answer)  # Display each answer
            else:
                st.error("Error getting answer: " + response.text)
    else:
        st.warning("Please upload a PDF file and enter a question.")
