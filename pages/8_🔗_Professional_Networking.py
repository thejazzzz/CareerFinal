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
    
    if "linkedin_optimization" not in st.session_state:
        st.session_state.linkedin_optimization = None
    
    if "networking_strategy" not in st.session_state:
        st.session_state.networking_strategy = None
    
    if "communication_templates" not in st.session_state:
        st.session_state.communication_templates = {}
    
    if "social_media_audit" not in st.session_state:
        st.session_state.social_media_audit = None

def main():
    st.title("🔗 Professional Networking")
    
    # Initialize session state and agent
    initialize_session_state()
    agent = get_communication_agent()
    
    # Create tabs for different functionalities
    tabs = ["LinkedIn Profile Optimization", "Networking Strategy", "Communication Templates", "Social Media Audit"]
    active_tab = st.radio("Select Functionality", tabs, horizontal=True)
    
    if active_tab == "LinkedIn Profile Optimization":
        display_linkedin_optimization_tab(agent)
    elif active_tab == "Networking Strategy":
        display_networking_strategy_tab(agent)
    elif active_tab == "Communication Templates":
        display_communication_templates_tab(agent)
    else:
        display_social_media_audit_tab(agent)

def display_linkedin_optimization_tab(agent):
    st.header("LinkedIn Profile Optimization")
    
    with st.form("linkedin_profile_form"):
        st.subheader("Current LinkedIn Profile Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            profile_headline = st.text_input("Profile Headline", 
                help="Your current LinkedIn headline")
            
            profile_summary = st.text_area("About/Summary", 
                help="Your current LinkedIn summary or about section")
            
            profile_photo = st.selectbox("Do you have a professional profile photo?", 
                ["Yes", "No", "Not sure if it's professional enough"])
        
        with col2:
            experience_description = st.text_area("Experience Description", 
                help="Brief description of your current role and responsibilities")
            
            skills = st.text_area("Skills & Endorsements", 
                help="List your current LinkedIn skills (comma-separated)")
            
            education = st.text_input("Education", 
                help="Your highest education level and institution")
        
        st.subheader("Target Information")
        target_role = st.text_input("Target Role", 
            value=st.session_state.user_context.get("career_goals", "").split("\n")[0] if st.session_state.user_context.get("career_goals") else "",
            help="The job role you're targeting")
        
        industry = st.text_input("Industry", 
            help="The industry you're in or targeting")
        
        optimize_button = st.form_submit_button("Optimize LinkedIn Profile")
    
    # Process LinkedIn profile optimization
    if optimize_button:
        if not target_role or not industry:
            st.error("Please enter both a target role and industry for optimization.")
            return
            
        with st.spinner("Analyzing LinkedIn profile and generating recommendations..."):
            try:
                # Prepare profile data
                profile_data = {
                    "headline": profile_headline,
                    "summary": profile_summary,
                    "photo_status": profile_photo,
                    "experience": experience_description,
                    "skills": skills,
                    "education": education
                }
                
                # Get optimization recommendations
                optimization = agent.optimize_linkedin_profile(
                    profile_data=profile_data,
                    target_role=target_role,
                    industry=industry
                )
                
                # Store in session state
                st.session_state.linkedin_optimization = optimization
                
                # Display success message
                st.success("LinkedIn profile optimization complete!")
                
            except Exception as e:
                st.error(f"Error optimizing LinkedIn profile: {str(e)}")
                if st.checkbox("Show detailed error"):
                    st.exception(e)
    
    # Display optimization results if available
    if st.session_state.linkedin_optimization:
        optimization = st.session_state.linkedin_optimization
        
        st.subheader("LinkedIn Profile Optimization Recommendations")
        
        # Create expandable sections for each profile component
        with st.expander("Profile Photo & Banner", expanded=True):
            for recommendation in optimization["structured_data"]["profile_photo"]:
                st.write(f"• {recommendation}")
        
        with st.expander("Headline"):
            for recommendation in optimization["structured_data"]["headline"]:
                st.write(f"• {recommendation}")
        
        with st.expander("About/Summary"):
            for recommendation in optimization["structured_data"]["summary"]:
                st.write(f"• {recommendation}")
        
        with st.expander("Experience Descriptions"):
            for recommendation in optimization["structured_data"]["experience"]:
                st.write(f"• {recommendation}")
        
        with st.expander("Skills & Endorsements"):
            for recommendation in optimization["structured_data"]["skills"]:
                st.write(f"• {recommendation}")
        
        with st.expander("Education"):
            for recommendation in optimization["structured_data"]["education"]:
                st.write(f"• {recommendation}")
        
        with st.expander("Recommendations"):
            for recommendation in optimization["structured_data"]["recommendations"]:
                st.write(f"• {recommendation}")
        
        with st.expander("Additional Sections"):
            for recommendation in optimization["structured_data"]["additional_sections"]:
                st.write(f"• {recommendation}")
        
        with st.expander("Content Strategy"):
            for recommendation in optimization["structured_data"]["content_strategy"]:
                st.write(f"• {recommendation}")
        
        with st.expander("Overall Profile Strength"):
            for recommendation in optimization["structured_data"]["overall_strength"]:
                st.write(f"• {recommendation}")
        
        # Add a download button for the recommendations
        if st.button("Download Recommendations as Text"):
            recommendations_text = "# LinkedIn Profile Optimization Recommendations\n\n"
            
            for section, items in optimization["structured_data"].items():
                if items:
                    section_title = section.replace("_", " ").title()
                    recommendations_text += f"## {section_title}\n\n"
                    for item in items:
                        recommendations_text += f"* {item}\n"
                    recommendations_text += "\n"
            
            # Create a download link
            st.download_button(
                label="Download Recommendations",
                data=recommendations_text,
                file_name=f"linkedin_recommendations_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

def display_networking_strategy_tab(agent):
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
                if st.checkbox("Show detailed error"):
                    st.exception(e)
    
    # Display networking strategy if available
    if st.session_state.networking_strategy:
        strategy = st.session_state.networking_strategy
        
        st.subheader("Your Personalized Networking Strategy")
        
        # Create expandable sections for each strategy component
        with st.expander("Target Connections", expanded=True):
            st.write("**Who you should connect with:**")
            for connection in strategy["structured_data"]["target_connections"]:
                st.write(f"• {connection}")
        
        with st.expander("Networking Platforms"):
            st.write("**Where you should network:**")
            for platform in strategy["structured_data"]["platforms"]:
                st.write(f"• {platform}")
        
        with st.expander("Outreach Templates"):
            st.write("**How to reach out effectively:**")
            for template in strategy["structured_data"]["outreach_templates"]:
                st.write(f"• {template}")
        
        with st.expander("Engagement Strategy"):
            st.write("**How to engage with your network:**")
            for tactic in strategy["structured_data"]["engagement_strategy"]:
                st.write(f"• {tactic}")
        
        with st.expander("In-Person Networking Tactics"):
            st.write("**Face-to-face networking opportunities:**")
            for tactic in strategy["structured_data"]["in_person_tactics"]:
                st.write(f"• {tactic}")
        
        with st.expander("Relationship Nurturing"):
            st.write("**How to maintain and strengthen connections:**")
            for tip in strategy["structured_data"]["relationship_nurturing"]:
                st.write(f"• {tip}")
        
        with st.expander("Metrics to Track"):
            st.write("**How to measure your networking success:**")
            for metric in strategy["structured_data"]["metrics"]:
                st.write(f"• {metric}")
        
        with st.expander("Weekly Action Plan"):
            st.write("**Your networking schedule:**")
            for action in strategy["structured_data"]["action_plan"]:
                st.write(f"• {action}")
        
        # Add a download button for the strategy
        if st.button("Download Networking Strategy"):
            strategy_text = "# Your Personalized Networking Strategy\n\n"
            
            for section, items in strategy["structured_data"].items():
                if items:
                    section_title = section.replace("_", " ").title()
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

def display_communication_templates_tab(agent):
    st.header("Professional Communication Templates")
    
    with st.form("communication_templates_form"):
        template_type = st.selectbox(
            "Template Type",
            [
                "LinkedIn Connection Request",
                "Follow-up After Meeting",
                "Informational Interview Request",
                "Thank You Note",
                "Job Application Follow-up",
                "Introduction Email",
                "Recommendation Request",
                "Event Invitation",
                "Networking Check-in",
                "Other (specify below)"
            ]
        )
        
        if template_type == "Other (specify below)":
            custom_template_type = st.text_input("Specify Template Type")
        
        context = st.text_area(
            "Context",
            help="Provide specific details about your situation (e.g., who you're contacting, why, your relationship)"
        )
        
        tone = st.selectbox(
            "Tone",
            ["Professional", "Friendly", "Formal", "Casual but Professional", "Enthusiastic", "Grateful"]
        )
        
        generate_button = st.form_submit_button("Generate Templates")
    
    # Process template generation
    if generate_button:
        if not context:
            st.error("Please provide context for your communication templates.")
            return
            
        with st.spinner("Generating professional communication templates..."):
            try:
                # Use custom template type if specified
                final_template_type = custom_template_type if template_type == "Other (specify below)" else template_type
                
                # Generate templates
                templates = agent.generate_communication_templates(
                    template_type=final_template_type,
                    context=context,
                    tone=tone.lower()
                )
                
                # Store in session state
                st.session_state.communication_templates[final_template_type] = templates
                
                # Display success message
                st.success(f"{final_template_type} templates generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating templates: {str(e)}")
                if st.checkbox("Show detailed error"):
                    st.exception(e)
    
    # Display generated templates if available
    if st.session_state.communication_templates:
        st.subheader("Your Communication Templates")
        
        # If multiple template types have been generated, let the user select which to view
        if len(st.session_state.communication_templates) > 1:
            template_to_view = st.selectbox(
                "Select template type to view",
                list(st.session_state.communication_templates.keys())
            )
            templates = st.session_state.communication_templates[template_to_view]
        else:
            # Just use the first (and only) template
            template_to_view = list(st.session_state.communication_templates.keys())[0]
            templates = st.session_state.communication_templates[template_to_view]
        
        # Display template variations
        st.write("### Template Variations")
        for i, variation in enumerate(templates["structured_data"]["variations"], 1):
            with st.expander(f"Template Variation {i}", expanded=i==1):
                st.write(variation)
                if st.button(f"Copy Template {i}", key=f"copy_{i}"):
                    st.code(variation, language="")
        
        # Display usage guidance
        if templates["structured_data"]["usage_guidance"]:
            with st.expander("When to Use These Templates"):
                for guidance in templates["structured_data"]["usage_guidance"]:
                    st.write(f"• {guidance}")
        
        # Display customization tips
        if templates["structured_data"]["customization_tips"]:
            with st.expander("How to Customize"):
                for tip in templates["structured_data"]["customization_tips"]:
                    st.write(f"• {tip}")
        
        # Display follow-up suggestions
        if templates["structured_data"]["follow_up_suggestions"]:
            with st.expander("Follow-up Suggestions"):
                for suggestion in templates["structured_data"]["follow_up_suggestions"]:
                    st.write(f"• {suggestion}")
        
        # Display best practices
        if templates["structured_data"]["best_practices"]:
            with st.expander("Best Practices"):
                for practice in templates["structured_data"]["best_practices"]:
                    st.write(f"• {practice}")

def display_social_media_audit_tab(agent):
    st.header("Professional Social Media Audit")
    
    with st.form("social_media_audit_form"):
        st.subheader("Platforms to Audit")
        
        platforms = st.multiselect(
            "Select platforms to include in your audit",
            [
                "LinkedIn",
                "Twitter",
                "Facebook",
                "Instagram",
                "GitHub",
                "Medium",
                "YouTube",
                "Personal Website/Blog"
            ],
            default=["LinkedIn"]
        )
        
        st.subheader("Career Information")
        
        career_goals = st.text_area(
            "What are your career goals?",
            help="Short and long-term professional objectives"
        )
        
        target_audience = st.text_area(
            "Who is your target audience?",
            help="Describe the professionals, recruiters, or companies you want to impress"
        )
        
        audit_button = st.form_submit_button("Create Audit Strategy")
    
    # Process social media audit
    if audit_button:
        if not platforms or not career_goals or not target_audience:
            st.error("Please complete all fields to create your audit strategy.")
            return
            
        with st.spinner("Creating social media audit strategy..."):
            try:
                # Parse career goals into a list
                goals_list = [goal.strip() for goal in career_goals.split("\n") if goal.strip()]
                
                # Generate audit strategy
                audit = agent.create_social_media_audit(
                    platforms=platforms,
                    career_goals=goals_list,
                    target_audience=target_audience
                )
                
                # Store in session state
                st.session_state.social_media_audit = audit
                
                # Display success message
                st.success("Social media audit strategy created successfully!")
                
            except Exception as e:
                st.error(f"Error creating audit strategy: {str(e)}")
                if st.checkbox("Show detailed error"):
                    st.exception(e)
    
    # Display audit strategy if available
    if st.session_state.social_media_audit:
        audit = st.session_state.social_media_audit
        
        st.subheader("Your Social Media Audit Strategy")
        
        # Display platform-specific assessment criteria
        st.write("### Platform-Specific Assessment")
        for platform, criteria in audit["structured_data"]["assessment_criteria"].items():
            with st.expander(f"{platform} Assessment Criteria"):
                for item in criteria:
                    st.write(f"• {item}")
        
        # Display general audit sections
        audit_sections = [
            ("Content Evaluation", "content_evaluation", "How to evaluate your content"),
            ("Professional Image Consistency", "image_consistency", "Ensuring a consistent professional image"),
            ("Privacy and Security", "privacy_security", "Protecting your professional reputation"),
            ("Engagement Analysis", "engagement_analysis", "Analyzing your engagement metrics"),
            ("Red Flags to Address", "red_flags", "Issues that could harm your professional image"),
            ("Improvement Opportunities", "improvement_opportunities", "Ways to enhance your professional presence")
        ]
        
        for title, key, description in audit_sections:
            if audit["structured_data"][key]:
                with st.expander(title, expanded=key=="improvement_opportunities"):
                    st.write(f"**{description}:**")
                    for item in audit["structured_data"][key]:
                        st.write(f"• {item}")
        
        # Display platform-specific optimization tips
        st.write("### Platform-Specific Optimization Tips")
        for platform, tips in audit["structured_data"]["platform_specific_tips"].items():
            with st.expander(f"{platform} Optimization"):
                for tip in tips:
                    st.write(f"• {tip}")
        
        # Add a download button for the audit strategy
        if st.button("Download Audit Strategy"):
            audit_text = "# Your Professional Social Media Audit Strategy\n\n"
            
            # Add platform-specific assessment criteria
            audit_text += "## Platform-Specific Assessment Criteria\n\n"
            for platform, criteria in audit["structured_data"]["assessment_criteria"].items():
                audit_text += f"### {platform}\n\n"
                for item in criteria:
                    audit_text += f"* {item}\n"
                audit_text += "\n"
            
            # Add general audit sections
            for title, key, _ in audit_sections:
                if audit["structured_data"][key]:
                    audit_text += f"## {title}\n\n"
                    for item in audit["structured_data"][key]:
                        audit_text += f"* {item}\n"
                    audit_text += "\n"
            
            # Add platform-specific optimization tips
            audit_text += "## Platform-Specific Optimization Tips\n\n"
            for platform, tips in audit["structured_data"]["platform_specific_tips"].items():
                audit_text += f"### {platform}\n\n"
                for tip in tips:
                    audit_text += f"* {tip}\n"
                audit_text += "\n"
            
            # Create a download link
            st.download_button(
                label="Download Audit Strategy",
                data=audit_text,
                file_name=f"social_media_audit_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main() 