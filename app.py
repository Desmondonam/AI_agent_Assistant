import streamlit as st
import openai
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key_configured" not in st.session_state:
    st.session_state.api_key_configured = False

# Application header
st.title("🤖 Personal AI Assistant")
st.markdown("Your AI-powered assistant with customizable capabilities")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # API key input
    api_key = st.text_input("Enter your OpenAI API Key", type="password")
    if api_key:
        openai.api_key = api_key
        st.session_state.api_key_configured = True
    
    # Agent personality configuration
    st.subheader("Agent Personality")
    agent_name = st.text_input("Assistant name", value="Assistant")
    agent_role = st.selectbox(
        "Role",
        ["General Assistant", "Research Helper", "Creative Writer", "Code Expert", "Business Consultant"]
    )
    
    # Agent capabilities
    st.subheader("Capabilities")
    capabilities = {
        "answer_questions": st.checkbox("Answer questions", value=True),
        "generate_content": st.checkbox("Create content", value=True),
        "analyze_text": st.checkbox("Analyze text", value=True),
        "code_assistance": st.checkbox("Provide code help", value=True)
    }
    
    # Temperature slider for response randomness
    temperature = st.slider("Response creativity", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    
    # Clear conversation button
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Input area
    if user_input := st.chat_input("Type your message here..."):
        if not st.session_state.api_key_configured:
            st.error("Please configure your OpenAI API key in the sidebar first.")
        else:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Display user message
            with st.chat_message("user"):
                st.write(user_input)
            
            # Create system message based on configuration
            system_prompt = f"""
            You are {agent_name}, a helpful {agent_role}.
            
            Capabilities:
            - {"Answer questions with accurate information" if capabilities["answer_questions"] else "Politely decline to answer questions"}
            - {"Generate creative content when requested" if capabilities["generate_content"] else "Decline requests to generate content"}
            - {"Analyze and summarize text" if capabilities["analyze_text"] else "Decline text analysis requests"}
            - {"Provide code examples and explanations" if capabilities["code_assistance"] else "Decline coding assistance"}
            
            Current date: {datetime.now().strftime("%Y-%m-%d")}
            """
            
            # Prepare messages for API call
            messages = [{"role": "system", "content": system_prompt}]
            for msg in st.session_state.messages:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Show a spinner while generating response
            with st.spinner("Thinking..."):
                try:
                    # Call OpenAI API
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=temperature,
                    )
                    
                    # Extract response text
                    assistant_response = response.choices[0].message.content
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    
                    # Display assistant response
                    with st.chat_message("assistant"):
                        st.write(assistant_response)
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with col2:
    # Agent status and information
    st.subheader("Agent Status")
    
    # Display configuration summary
    st.info(f"""
    **Name:** {agent_name}
    **Role:** {agent_role}
    **Creativity Level:** {temperature}
    
    **Active Capabilities:**
    {"- Question answering" if capabilities["answer_questions"] else ""}
    {"- Content generation" if capabilities["generate_content"] else ""}
    {"- Text analysis" if capabilities["analyze_text"] else ""}
    {"- Code assistance" if capabilities["code_assistance"] else ""}
    """)
    
    # Display conversation metrics
    if st.session_state.messages:
        user_messages = sum(1 for msg in st.session_state.messages if msg["role"] == "user")
        assistant_messages = sum(1 for msg in st.session_state.messages if msg["role"] == "assistant")
        
        st.metric("Messages Exchanged", len(st.session_state.messages))
        st.metric("Your Messages", user_messages)
        st.metric("Assistant Responses", assistant_messages)
    
    # Display API key status
    if st.session_state.api_key_configured:
        st.success("API Key Configured ✅")
    else:
        st.warning("API Key Not Configured ⚠️")
    
    # Help section
    with st.expander("Help & Instructions"):
        st.markdown("""
        ### How to use this AI Assistant
        
        1. Enter your OpenAI API key in the sidebar
        2. Configure the agent's personality and capabilities
        3. Start chatting in the input box
        
        ### Tips
        - Adjust the temperature slider to control response creativity
        - Clear the conversation to start fresh
        - Enable/disable capabilities as needed
        
        ### Requirements
        - OpenAI API key
        - Python 3.7+
        - Streamlit 1.8+
        """)