import streamlit as st
from dotenv import load_dotenv
import os
from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

# Load environment variables from .env file
load_dotenv()

def chat_application():
    """
    Main application function for handling the Groq chatbot with conversational memory
    and Streamlit interface.
    """

    # Retrieve the Groq API key from environment variables
    groq_api_key = os.getenv("GROQ")
    if not groq_api_key:
        st.error("Groq API key is not set. Please configure the environment variable 'GROQ'.")
        return

    # Streamlit App Title
    st.title("Chat with Groq!")
    st.write("Welcome to the Groq-powered chatbot. Ask anything, and enjoy lightning-fast responses!")

    # Sidebar for customization
    st.sidebar.title('Customization')
    system_prompt = st.sidebar.text_input("System prompt:")
    model_selection = st.sidebar.selectbox(
        'Choose a model',
        ['llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it']
    )
    conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value=5)

    # Initialize conversational memory
    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)

    # User input for the chatbot
    user_question = st.text_input("Ask a question:")

    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # If there is previous chat history, load it into memory
    for message in st.session_state.chat_history:
        memory.save_context(
            {'input': message['human']},
            {'output': message['AI']}
        )

    # Validate that the Groq API key and model are properly set
    try:
        # Initialize the Groq Chat Model with the selected model
        groq_chat_model = ChatGroq(
            groq_api_key=groq_api_key, 
            model_name=model_selection
        )

        # If a question is asked by the user
        if user_question:
            # Define the chat prompt template
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=system_prompt),  # System message for context
                MessagesPlaceholder(variable_name="chat_history"),  # Chat history placeholder
                HumanMessagePromptTemplate.from_template("{human_input}")  # User's current input
            ])

            # Create conversation chain with LLM and memory
            conversation = LLMChain(
                llm=groq_chat_model,  # Use the Groq model
                prompt=prompt,        # Constructed prompt
                verbose=True,         # Verbose output for debugging
                memory=memory         # Conversational memory for context
            )

            # Generate response from the chatbot
            response = conversation.predict(human_input=user_question)
            
            # Store the human and AI conversation in session state
            st.session_state.chat_history.append({'human': user_question, 'AI': response})

            # Display the AI's response in the chat interface
            st.write("Chatbot:", response)

    except Exception as e:
        # In case of any errors, display the error message
        st.error(f"An error occurred: {str(e)}")


# Start the application
if __name__ == "__main__":
    chat_application()
