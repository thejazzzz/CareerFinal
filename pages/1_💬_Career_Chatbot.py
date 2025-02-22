import streamlit as st
from agents.career_chatbot import CareerChatbotAgent

# Initialize the chatbot agent
@st.cache_resource
def get_chatbot():
    return CareerChatbotAgent(verbose=True)

def main():
    st.title("💬 Career Chatbot")
    
    # Initialize the agent
    chatbot = get_chatbot()
    
    # Check if user context exists
    if not st.session_state.user_context:
        st.warning("Please complete your profile in the sidebar of the home page first!")
        return
    
    # Chat interface
    st.write("""
    Ask me anything about your career! I can help you with:
    - Career advice and guidance
    - Skill development recommendations
    - Industry insights
    - Career transition strategies
    - Learning resources
    """)
    
    # Chat input
    with st.form("chat_form"):
        user_query = st.text_area("Your question:", height=100)
        cols = st.columns([1, 6, 1])
        with cols[1]:
            submit_button = st.form_submit_button("Send", use_container_width=True)
    
    # Process chat input
    if submit_button and user_query:
        with st.spinner("Thinking..."):
            # Get chatbot response
            response = chatbot.get_response(
                user_query=user_query,
                chat_history=st.session_state.chat_history,
                user_context=st.session_state.user_context
            )
            
            # Update chat history
            st.session_state.chat_history.append({
                "user": user_query,
                "bot": response["structured_data"]["main_response"]
            })
            
            # Display response
            st.write("**Response:**")
            st.write(response["structured_data"]["main_response"])
            
            # Display follow-up questions if any
            if response["structured_data"]["follow_up_questions"]:
                st.write("**Follow-up Questions to Consider:**")
                for question in response["structured_data"]["follow_up_questions"]:
                    st.info(question)
            
            # Display actionable advice if any
            if response["structured_data"]["actionable_advice"]:
                st.write("**Actionable Advice:**")
                for advice in response["structured_data"]["actionable_advice"]:
                    st.success(advice)
            
            # Display resources if any
            if response["structured_data"]["resources"]:
                with st.expander("📚 Recommended Resources"):
                    for resource in response["structured_data"]["resources"]:
                        st.markdown(f"- {resource}")
    
    # Display chat history
    if st.session_state.chat_history:
        st.header("Chat History")
        for chat in reversed(st.session_state.chat_history):
            with st.container():
                st.write("**You:**")
                st.write(chat["user"])
                st.write("**Assistant:**")
                st.write(chat["bot"])
                st.divider()
    
    # Resource search
    with st.sidebar:
        st.header("Resource Search")
        st.write("Search for specific learning resources:")
        topic = st.text_input("Topic:")
        resource_type = st.selectbox(
            "Resource Type:",
            ["all", "courses", "books", "websites", "tools"]
        )
        if st.button("Search Resources"):
            with st.spinner("Searching resources..."):
                resources = chatbot.suggest_resources(
                    topic=topic,
                    resource_type=resource_type
                )
                
                st.write(f"**Resources for {topic}:**")
                for resource in resources["structured_data"]["recommended_resources"]:
                    with st.expander(resource):
                        if resource in resources["structured_data"]["descriptions"]:
                            st.write("**Description:**")
                            st.write(resources["structured_data"]["descriptions"][resource])
                        if resource in resources["structured_data"]["value_props"]:
                            st.write("**Value:**")
                            st.write(resources["structured_data"]["value_props"][resource])
                        if resource in resources["structured_data"]["usage_tips"]:
                            st.write("**Usage Tips:**")
                            st.write(resources["structured_data"]["usage_tips"][resource])

if __name__ == "__main__":
    main() 