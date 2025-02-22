import streamlit as st
from agents.interview_coach import InterviewCoachAgent

# Initialize the interview coach agent
@st.cache_resource
def get_interview_coach():
    return InterviewCoachAgent(verbose=True)

def main():
    st.title("🎤 Interview Coach")
    
    # Initialize the agent
    coach = get_interview_coach()
    
    # Check if user context exists
    if not st.session_state.user_context:
        st.warning("Please complete your profile in the sidebar of the home page first!")
        return
    
    st.write("""
    Practice your interview skills with our AI-powered Interview Coach.
    Get personalized questions, real-time feedback, and expert advice to help you ace your interviews.
    """)
    
    # Interview preparation form
    with st.form("interview_prep_form"):
        # Role details
        st.header("Interview Details")
        role = st.text_input(
            "Target Role",
            value=st.session_state.user_context.get("career_goals", "").split("\n")[0]
        )
        experience_level = st.selectbox(
            "Experience Level",
            ["Entry Level", "Mid Level", "Senior", "Lead", "Executive"],
            index=1
        )
        
        # Interview type
        interview_type = st.selectbox(
            "Interview Type",
            ["technical", "behavioral", "full"],
            help="Choose the type of interview questions"
        )
        
        # Skills focus
        skills_focus = st.multiselect(
            "Skills to Focus On",
            options=st.session_state.user_context.get("skills", []) + [
                "Problem Solving", "Communication", "Leadership",
                "Technical Skills", "Project Management"
            ],
            default=st.session_state.user_context.get("skills", [])[:3]
        )
        
        # Submit button
        start_button = st.form_submit_button("Start Interview Preparation")
    
    # Generate interview questions
    if start_button:
        with st.spinner("Preparing interview questions..."):
            try:
                # Generate questions
                questions = coach.generate_interview_questions(
                    role=role,
                    experience_level=experience_level,
                    skills=skills_focus,
                    interview_type=interview_type
                )
                
                # Store questions in session state
                if "current_interview" not in st.session_state:
                    st.session_state.current_interview = {
                        "questions": questions["structured_data"],
                        "current_question": 0,
                        "answers": {},
                        "feedback": {}
                    }
                
                st.success("Interview questions ready!")
                
                # Display interview sections
                if interview_type in ["technical", "full"]:
                    st.header("Technical Questions")
                    for i, q in enumerate(questions["structured_data"]["technical_questions"]):
                        with st.expander(f"Question {i+1}"):
                            st.write(q)
                
                if interview_type in ["behavioral", "full"]:
                    st.header("Behavioral Questions")
                    for i, q in enumerate(questions["structured_data"]["behavioral_questions"]):
                        with st.expander(f"Question {i+1}"):
                            st.write(q)
                
                st.header("Scenario-Based Questions")
                for i, q in enumerate(questions["structured_data"]["scenario_questions"]):
                    with st.expander(f"Scenario {i+1}"):
                        st.write(q)
                
                st.header("Questions to Ask the Interviewer")
                for i, q in enumerate(questions["structured_data"]["questions_to_ask"]):
                    st.write(f"{i+1}. {q}")
            
            except Exception as e:
                st.error(f"Error generating questions: {str(e)}")
    
    # Practice interface
    if "current_interview" in st.session_state:
        st.header("Practice Session")
        
        # Get current question
        current_idx = st.session_state.current_interview["current_question"]
        all_questions = (
            st.session_state.current_interview["questions"]["technical_questions"] +
            st.session_state.current_interview["questions"]["behavioral_questions"] +
            st.session_state.current_interview["questions"]["scenario_questions"]
        )
        
        if current_idx < len(all_questions):
            st.subheader(f"Question {current_idx + 1}")
            st.write(all_questions[current_idx])
            
            # Answer input
            answer = st.text_area("Your Answer:", height=150)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("Previous Question") and current_idx > 0:
                    st.session_state.current_interview["current_question"] -= 1
                    st.rerun()
            
            with col2:
                if answer and st.button("Submit Answer"):
                    with st.spinner("Analyzing your response..."):
                        # Get feedback
                        feedback = coach.evaluate_response(
                            question=all_questions[current_idx],
                            answer=answer,
                            role=role,
                            experience_level=experience_level
                        )
                        
                        # Store feedback
                        st.session_state.current_interview["answers"][current_idx] = answer
                        st.session_state.current_interview["feedback"][current_idx] = feedback
                        
                        # Display feedback
                        st.write("**Feedback:**")
                        st.metric(
                            "Response Score",
                            f"{feedback['structured_data']['score']}%"
                        )
                        
                        st.write("**Strengths:**")
                        for strength in feedback['structured_data']['strengths']:
                            st.success(f"✓ {strength}")
                        
                        st.write("**Areas for Improvement:**")
                        for improvement in feedback['structured_data']['improvements']:
                            st.info(f"↗ {improvement}")
                        
                        st.write("**Sample Better Response:**")
                        st.write(feedback['structured_data']['better_response'])
                        
                        with st.expander("Additional Tips"):
                            for tip in feedback['structured_data']['tips']:
                                st.write(f"• {tip}")
            
            with col3:
                if st.button("Next Question") and current_idx < len(all_questions) - 1:
                    st.session_state.current_interview["current_question"] += 1
                    st.rerun()
        
        else:
            st.success("Interview practice complete!")
            
            # Overall feedback
            st.header("Interview Performance Summary")
            total_score = sum(
                feedback['structured_data']['score']
                for feedback in st.session_state.current_interview["feedback"].values()
            ) / len(st.session_state.current_interview["feedback"])
            
            st.metric("Overall Score", f"{total_score:.1f}%")
            
            # Save interview session
            if st.button("Save Interview Session"):
                if "saved_interviews" not in st.session_state:
                    st.session_state.saved_interviews = []
                st.session_state.saved_interviews.append({
                    "role": role,
                    "type": interview_type,
                    "score": total_score,
                    "date": st.session_state.get("current_date", "Today"),
                    "feedback": st.session_state.current_interview["feedback"]
                })
                st.success("Interview session saved to your profile!")
            
            # Start new session
            if st.button("Start New Interview"):
                del st.session_state.current_interview
                st.rerun()
    
    # Previous interviews in sidebar
    with st.sidebar:
        if "saved_interviews" in st.session_state and st.session_state.saved_interviews:
            st.header("Previous Interviews")
            for interview in st.session_state.saved_interviews:
                with st.expander(f"{interview['role']} - {interview['date']}"):
                    st.write(f"**Type:** {interview['type']}")
                    st.write(f"**Score:** {interview['score']:.1f}%")
                    if st.button("Review", key=f"review_{st.session_state.saved_interviews.index(interview)}"):
                        # Show detailed feedback
                        st.write("**Detailed Feedback:**")
                        for q_idx, feedback in interview["feedback"].items():
                            with st.expander(f"Question {int(q_idx) + 1}"):
                                st.write(f"Score: {feedback['structured_data']['score']}%")
                                st.write("Strengths:")
                                for strength in feedback['structured_data']['strengths']:
                                    st.write(f"• {strength}")

if __name__ == "__main__":
    main()