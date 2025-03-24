import streamlit as st
from agents.communication_agent import CommunicationAgent
import json
import os
from datetime import datetime

# Initialize the communication agent
@st.cache_resource
def get_communication_agent():
    return CommunicationAgent(verbose=True)

def initialize_session_state():
    """Initialize required session state variables"""
    if "user_context" not in st.session_state:
        st.session_state.user_context = {
            "name": "",
            "current_role": "",
            "experience": "",
            "skills": [],
            "interests": [],
            "career_goals": ""
        }
    
    if "networking_strategy" not in st.session_state:
        st.session_state.networking_strategy = None

def main():
    st.title("🔗 Networking Strategy")
    
    # Initialize session state and agent
    initialize_session_state()
    agent = get_communication_agent()
    
    display_networking_strategy(agent)

def display_networking_strategy(agent):
    st.header("Networking Strategy")
    
    with st.form("networking_strategy_form"):
        st.subheader("Your Networking Profile")
        
        career_stage = st.selectbox(
            "Career Stage",
            ["Entry-level", "Mid-level", "Senior", "Executive", "Career Transition", "Student/Recent Graduate"]
        )
        
        industry = st.text_input("Industry", 
            help="Your current or target industry")
        
        st.subheader("Networking Goals")
        goals = st.text_area(
            "What are your networking goals?",
            help="Examples: Find a new job, Connect with industry experts, Build a professional community, etc."
        )
        
        current_network = st.text_area(
            "Describe your current professional network",
            help="Size, composition, strengths, and weaknesses of your current network"
        )
        
        create_strategy_button = st.form_submit_button("Create Networking Strategy")
    
    # Process networking strategy creation
    if create_strategy_button:
        if not industry or not goals:
            st.error("Please enter your industry and networking goals.")
            return
            
        with st.spinner("Creating personalized networking strategy..."):
            try:
                # Parse goals into a list
                goals_list = [goal.strip() for goal in goals.split("\n") if goal.strip()]
                
                # Get networking strategy
                strategy = agent.create_networking_strategy(
                    career_stage=career_stage,
                    industry=industry,
                    goals=goals_list,
                    current_network=current_network
                )
                
                # Store in session state
                st.session_state.networking_strategy = strategy
                
                # Display success message
                st.success("Networking strategy created successfully!")
                
            except Exception as e:
                st.error(f"Error creating networking strategy: {str(e)}")
    
    # Display networking strategy results if available
    if st.session_state.networking_strategy:
        strategy = st.session_state.networking_strategy
        
        st.subheader("Your Personalized Networking Strategy")
        
        # Create expandable sections for each component of the strategy
        with st.expander("Target Connections", expanded=True):
            st.write("These are the types of professionals you should focus on connecting with:")
            for item in strategy["structured_data"]["target_connections"]:
                st.write(f"• {item}")
        
        with st.expander("Networking Platforms"):
            st.write("These platforms are most relevant for your networking goals:")
            for item in strategy["structured_data"]["platforms"]:
                st.write(f"• {item}")
        
        with st.expander("Outreach Templates"):
            st.write("Use these templates when reaching out to new connections:")
            for item in strategy["structured_data"]["outreach_templates"]:
                st.write(f"• {item}")
        
        with st.expander("Engagement Strategy"):
            st.write("How to engage with your network effectively:")
            for item in strategy["structured_data"]["engagement_strategy"]:
                st.write(f"• {item}")
        
        with st.expander("In-Person Networking Tactics"):
            st.write("Strategies for face-to-face networking:")
            for item in strategy["structured_data"]["in_person_tactics"]:
                st.write(f"• {item}")
        
        with st.expander("Relationship Nurturing"):
            st.write("How to maintain and strengthen your professional relationships:")
            for item in strategy["structured_data"]["relationship_nurturing"]:
                st.write(f"• {item}")
        
        with st.expander("Metrics to Track"):
            st.write("Key metrics to monitor your networking success:")
            for item in strategy["structured_data"]["metrics"]:
                st.write(f"• {item}")
        
        with st.expander("Weekly Action Plan"):
            st.write("Your weekly networking activities:")
            for item in strategy["structured_data"]["action_plan"]:
                st.write(f"• {item}")
        
        # Add a download button for the strategy
        if st.button("Download Networking Strategy"):
            strategy_text = "# Your Personalized Networking Strategy\n\n"
            
            sections = {
                "Target Connections": strategy["structured_data"]["target_connections"],
                "Networking Platforms": strategy["structured_data"]["platforms"],
                "Outreach Templates": strategy["structured_data"]["outreach_templates"],
                "Engagement Strategy": strategy["structured_data"]["engagement_strategy"],
                "In-Person Networking": strategy["structured_data"]["in_person_tactics"],
                "Relationship Nurturing": strategy["structured_data"]["relationship_nurturing"],
                "Metrics to Track": strategy["structured_data"]["metrics"],
                "Weekly Action Plan": strategy["structured_data"]["action_plan"]
            }
            
            for section_title, items in sections.items():
                strategy_text += f"## {section_title}\n\n"
                for item in items:
                    strategy_text += f"* {item}\n"
                strategy_text += "\n"
            
            # Create a download link
            st.download_button(
                label="Download Strategy",
                data=strategy_text,
                file_name=f"networking_strategy_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main() 