import streamlit as st
import os
from agents.resume_analyzer import ResumeAnalyzerAgent

# Initialize the resume analyzer agent
@st.cache_resource
def get_resume_analyzer():
    return ResumeAnalyzerAgent(verbose=True)

def main():
    st.title("📝 Resume Analyzer")
    
    # Initialize the agent
    analyzer = get_resume_analyzer()
    
    st.write("""
    Get detailed feedback on your resume from our AI-powered analyzer. 
    Upload your resume to receive insights on:
    - Professional Summary
    - Key Skills
    - Experience Analysis
    - Areas for Improvement
    - ATS Compatibility
    """)
    
    # File upload
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    
    if uploaded_file:
        # Save uploaded file temporarily
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        try:
            with st.spinner("Analyzing your resume..."):
                # Analyze resume
                analysis = analyzer.process_resume(temp_path)
                st.session_state.resume_analysis = analysis
                
                # Display results
                st.success("Resume Analysis Complete!")
                
                # Professional Summary
                st.header("Professional Summary")
                for item in analysis["structured_data"].get("professional_summary", []):
                    st.write(f"• {item}")
                
                # Skills Analysis
                col1, col2 = st.columns(2)
                with col1:
                    st.header("Technical Skills")
                    skills = analysis["structured_data"].get("skills", [])
                    technical_skills = [s for s in skills if not s.startswith("Soft Skill:")]
                    for skill in technical_skills:
                        st.write(f"• {skill}")
                
                with col2:
                    st.header("Soft Skills")
                    soft_skills = [s.replace("Soft Skill: ", "") for s in skills if s.startswith("Soft Skill:")]
                    for skill in soft_skills:
                        st.write(f"• {skill}")
                
                # Experience Analysis
                st.header("Experience Analysis")
                for exp in analysis["structured_data"].get("work_experience", []):
                    with st.expander(exp.split(" - ")[0]):  # Use company/role as expander title
                        st.write(exp)
                
                # Education
                st.header("Education")
                for edu in analysis["structured_data"].get("education", []):
                    st.write(f"• {edu}")
                
                # Strengths and Improvements
                col3, col4 = st.columns(2)
                with col3:
                    st.header("Key Strengths")
                    for strength in analysis["structured_data"].get("key_strengths", []):
                        st.success(f"✓ {strength}")
                
                with col4:
                    st.header("Areas for Improvement")
                    for improvement in analysis["structured_data"].get("areas_for_improvement", []):
                        st.info(f"↗ {improvement}")
                
                # Update user context if needed
                if not st.session_state.user_context.get("skills"):
                    if st.button("Update Profile with Resume Skills"):
                        if "user_context" not in st.session_state:
                            st.session_state.user_context = {}
                        st.session_state.user_context["skills"] = technical_skills
                        st.success("Profile updated with skills from your resume!")
            
            # Cleanup
            os.remove(temp_path)
            
        except Exception as e:
            st.error(f"Error analyzing resume: {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    main() 