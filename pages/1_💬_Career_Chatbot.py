import streamlit as st
from agents.career_chatbot import CareerChatbotAgent

# Initialize the chatbot agent
@st.cache_resource
def get_chatbot():
    return CareerChatbotAgent(verbose=True)

def initialize_session_state():
    """Initialize required session state variables"""
    # Initialize user context if not exists
    if "user_context" not in st.session_state:
        st.session_state.user_context = {
            "user_role": "",
            "experience": "",
            "skills": [],
            "interests": [],
            "career_goals": ""
        }
    
    # Initialize chat history if not exists
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

def main():
    # Initialize session state and agent
    initialize_session_state()
    chatbot = get_chatbot()
    
    # Basic CSS with improved visibility
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1E3A8A;
    }
    .profile-item {
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        color: #111827;
    }
    .chat-area {
        margin-top: 1rem;
        margin-bottom: 1rem;
        background-color: #FFFFFF;
    }
    .user-message {
        background-color: #E5E7EB;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin-bottom: 0.8rem;
        color: #111827;
        border: 1px solid #D1D5DB;
    }
    .bot-message {
        background-color: #DBEAFE;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin-bottom: 1.2rem;
        color: #1E3A8A;
        border: 1px solid #BFDBFE;
    }
    .message-sender {
        font-weight: bold;
        margin-bottom: 0.3rem;
        color: #111827;
    }
    .message-content {
        color: #1F2937;
    }
    .stButton>button {
        background-color: #F3F4F6;
        color: #111827;
        border: 1px solid #D1D5DB;
    }
    .stButton>button:hover {
        background-color: #E5E7EB;
        color: #111827;
        border: 1px solid #9CA3AF;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main heading
    st.markdown('<h1 class="main-header">Career Chatbot</h1>', unsafe_allow_html=True)
    st.markdown("Ask anything about your career path, skills development, or job search")
    
    # Two-column layout
    col1, col2 = st.columns([2, 1])
    
    with col2:
        # Simple profile section
        st.markdown("### Your Profile")
        
        user_context = st.session_state.user_context
        
        if user_context.get("user_role"):
            st.markdown(f'<div class="profile-item" style="color: white;"><b>Current Role:</b> {user_context["user_role"]}</div>', 
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="profile-item" style="color: white;"><b>Current Role:</b> Not specified</div>', 
                        unsafe_allow_html=True)
        
        if user_context.get("career_goals"):
            st.markdown(f'<div class="profile-item" style="color: white;"><b>Target Role:</b> {user_context["career_goals"]}</div>', 
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="profile-item" style="color: white;"><b>Target Role:</b> Not specified</div>', 
                        unsafe_allow_html=True)
        
        # Suggested questions
        st.markdown("### Suggested Questions")
        
        # Simple question buttons
        questions = [
            "How can I improve my skills in my current role?",
            "What career paths are available for someone with my skills?",
            "How should I prepare for a job interview?",
            "What industries are growing in demand for my skills?",
            "How do I negotiate a higher salary?"
        ]
        
        for question in questions:
            if st.button(question, key=f"q_{question}", use_container_width=True):
                st.session_state.temp_question = question
                st.rerun()
    
    with col1:
        # Chat history with better visibility
        chat_container = st.container(height=400, border=True)
        
        with chat_container:
            st.markdown("### Conversation")
            
            if st.session_state.chat_history:
                for chat in reversed(st.session_state.chat_history[-10:]):
                    # User message with better visibility
                    user_msg = """
                    <div class="user-message">
                        <div class="message-sender">You</div>
                        <div class="message-content">{0}</div>
                    </div>
                    """
                    st.markdown(user_msg.format(chat["user"]), unsafe_allow_html=True)
                    
                    # Bot message with better visibility
                    bot_msg = """
                    <div class="bot-message">
                        <div class="message-sender">Assistant</div>
                        <div class="message-content">{0}</div>
                    </div>
                    """
                    # Convert newlines to <br> tags and handle formatting
                    formatted_response = chat["bot"].replace("\n", "<br>")
                    st.markdown(bot_msg.format(formatted_response), unsafe_allow_html=True)
        
        # Simple chat input
        with st.form("chat_form", clear_on_submit=True):
            user_query = st.text_area(
                "Your question:",
                height=80,
                placeholder="Ask me anything about your career..."
            )
            
            submit_button = st.form_submit_button("Send", use_container_width=True)
    
    # Process user input
    if submit_button and user_query:
        # Process the input
        process_user_input(user_query, chatbot)
        # Rerun after processing to show new messages immediately
        st.rerun()
    
    # Process suggested question if selected
    if hasattr(st.session_state, 'temp_question') and st.session_state.temp_question:
        question = st.session_state.temp_question
        st.session_state.temp_question = None
        # Process the input
        process_user_input(question, chatbot)
        # Rerun after processing to show new messages immediately
        st.rerun()

def process_user_input(user_input, chatbot):
    """Process user input and get chatbot response"""
    with st.spinner("Thinking..."):
        try:
            # Get context for personalized responses
            user_context = st.session_state.user_context
            
            # Get recent history
            recent_history = []
            if st.session_state.chat_history:
                recent_history = st.session_state.chat_history[-5:]
            
            # Get chatbot response
            response_data = chatbot.get_response(
                user_input,
                chat_history=recent_history,
                user_context=user_context
            )
            
            # Extract response text
            response = response_data.get("raw_response", "")
            
            # Add to chat history
            st.session_state.chat_history.append({
                "user": user_input,
                "bot": response
            })
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 