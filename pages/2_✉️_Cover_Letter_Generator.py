import streamlit as st
from agents.cover_letter_generator import CoverLetterGeneratorAgent

# Initialize the cover letter generator agent
@st.cache_resource
def get_cover_letter_generator():
    return CoverLetterGeneratorAgent(verbose=True)

def main():
    st.title("✉️ Cover Letter Generator")
    
    # Initialize the agent
    generator = get_cover_letter_generator()
    
    # Check if user context exists
    if not st.session_state.user_context:
        st.warning("Please complete your profile in the sidebar of the home page first!")
        return
    
    st.write("""
    Generate a personalized cover letter tailored to your target job and company.
    The generator will use your profile information and customize the letter based on the job requirements.
    """)
    
    # Cover letter generation form
    with st.form("cover_letter_form"):
        # Job details
        st.header("Job Details")
        job_description = st.text_area(
            "Job Description",
            help="Paste the full job description here",
            height=200
        )
        company_name = st.text_input("Company Name")
        
        # Style selection
        style = st.selectbox(
            "Cover Letter Style",
            ["professional", "enthusiastic", "concise"],
            help="Choose the tone for your cover letter"
        )
        
        # Candidate info from session state
        candidate_info = {
            "experience": st.session_state.user_context["experience"],
            "skills": st.session_state.user_context["skills"],
            "achievements": [
                f"Experienced in {', '.join(st.session_state.user_context['skills'][:3])}",
                f"Career goal: {st.session_state.user_context['career_goals']}"
            ]
        }
        
        # Submit button
        generate_button = st.form_submit_button("Generate Cover Letter")
    
    # Generate cover letter
    if generate_button and job_description and company_name:
        with st.spinner("Generating your cover letter..."):
            cover_letter = generator.generate_cover_letter(
                job_description=job_description,
                candidate_info=candidate_info,
                company_name=company_name,
                style=style
            )
            
            # Display the generated cover letter
            st.header("Generated Cover Letter")
            
            # Display structured sections
            st.write(cover_letter["structured_data"]["greeting"])
            st.write("")
            st.write(cover_letter["structured_data"]["opening"])
            st.write("")
            for paragraph in cover_letter["structured_data"]["body"]:
                st.write(paragraph)
                st.write("")
            st.write(cover_letter["structured_data"]["closing"])
            st.write(cover_letter["structured_data"]["signature"])
            
            # Improvement suggestions
            st.header("Want to improve your letter?")
            focus_areas = st.multiselect(
                "Select areas to focus on:",
                [
                    "Stronger emphasis on relevant experience",
                    "Better alignment with job requirements",
                    "More compelling opening",
                    "Clearer value proposition",
                    "More specific achievements",
                    "Better company culture alignment"
                ]
            )
            
            if focus_areas and st.button("Improve Letter"):
                with st.spinner("Improving your cover letter..."):
                    improvements = generator.improve_cover_letter(
                        cover_letter=cover_letter["raw_content"],
                        focus_areas=focus_areas
                    )
                    
                    # Display improvements
                    st.subheader("Improved Version")
                    st.write(improvements["structured_data"]["improved_version"])
                    
                    with st.expander("See Improvements Made"):
                        st.write("**Enhancements:**")
                        for enhancement in improvements["structured_data"]["enhancements"]:
                            st.success(enhancement)
                        
                        st.write("**Additional Suggestions:**")
                        for suggestion in improvements["structured_data"]["suggestions"]:
                            st.info(suggestion)

if __name__ == "__main__":
    main() 