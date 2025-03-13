import streamlit as st
from agents.career_chatbot import CareerChatbotAgent
from components.styling import apply_custom_styling
from components.common import initialize_page, display_user_profile, styled_container

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
    
    # Initialize page with common styling and components
    if not initialize_page(
        "Career Chatbot", 
        "Ask anything about your career path, skills development, or job search"
    ):
        return  # Exit if profile is not complete
    
    # Two-column layout for better organization
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Enhanced chat interface using styled_container
        container = styled_container(
            "How Can I Help?",
            """
            <p style="color: #4a5568;">I can assist with:</p>
            <ul style="color: #4a5568;">
                <li>Career advice and guidance</li>
                <li>Skill development recommendations</li>
                <li>Industry insights and trends</li>
                <li>Career transition strategies</li>
                <li>Learning resources and tools</li>
            </ul>
            """
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Chat input with a more prominent design
        with st.form("chat_form", clear_on_submit=True):
            user_query = st.text_area(
                "Your question:",
                height=100,
                placeholder="Ask me anything about your career..."
            )
            
            cols = st.columns([1, 6, 1])
            with cols[1]:
                submit_button = st.form_submit_button("Send", use_container_width=True)
        
        # Process chat input
        if submit_button and user_query:
            with st.spinner("Thinking..."):
                try:
                    # Get context for personalized responses
                    user_context = st.session_state.user_context
                    
                    # Get recent history for context (last 5 messages)
                    recent_history = []
                    if st.session_state.chat_history:
                        recent_history = st.session_state.chat_history[-5:]
                    
                    # Get chatbot response
                    response_data = chatbot.get_response(
                        user_query,
                        chat_history=recent_history,
                        user_context=user_context
                    )
                    
                    # Extract the main response text
                    response = response_data.get("raw_response", "")
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "user": user_query,
                        "bot": response
                    })
                    
                    # Rerun to show updated chat
                    st.experimental_rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        # Display user profile using common component
        display_user_profile(st.session_state.user_context)
        
        # Suggested questions for better user experience
        container = styled_container("Suggested Questions")
        
        # Create clickable question buttons
        questions = [
            "How can I improve my skills in my current role?",
            "What career paths are available for someone with my skills?",
            "How should I prepare for a job interview?",
            "What industries are growing in demand for my skills?",
            "How do I negotiate a higher salary?"
        ]
        
        for question in questions:
            if st.button(question, key=f"q_{question}", use_container_width=True):
                # Add question to session state to be processed on rerun
                st.session_state.temp_question = question
                st.experimental_rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Handle temporary question if set by suggestion buttons
    if hasattr(st.session_state, 'temp_question') and st.session_state.temp_question:
        question = st.session_state.temp_question
        st.session_state.temp_question = None  # Clear temp question
        
        with st.spinner("Thinking..."):
            try:
                # Get context for personalized responses
                user_context = st.session_state.user_context
                
                # Get recent history for context (last 5 messages)
                recent_history = []
                if st.session_state.chat_history:
                    recent_history = st.session_state.chat_history[-5:]
                
                # Get chatbot response
                response_data = chatbot.get_response(
                    question,
                    chat_history=recent_history,
                    user_context=user_context
                )
                
                # Extract the main response text
                response = response_data.get("raw_response", "")
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "user": question,
                    "bot": response
                })
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display chat history with a more appealing design
    if st.session_state.chat_history:
        st.markdown("## Conversation History")
        
        for chat in reversed(st.session_state.chat_history[-10:]):  # Show last 10 messages
            # User message with left alignment
            st.markdown(f"""
            <div style="
                background-color: #e2e8f0; 
                border-radius: 12px 12px 12px 0; 
                padding: 1rem; 
                margin-bottom: 0.5rem;
                max-width: 80%;
                color: #2d3748;
            ">
                <strong>You:</strong><br>
                {chat["user"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Bot message with right alignment
            st.markdown(f"""
            <div style="
                background-color: #ebf8ff; 
                border-radius: 12px 12px 0 12px; 
                padding: 1rem; 
                margin-bottom: 1rem;
                margin-left: 20%;
                max-width: 80%;
                color: #2c5282;
            ">
                <strong>Assistant:</strong><br>
                {chat["bot"]}
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 