import streamlit as st
from agents.interview_coach import InterviewCoachAgent
from typing import List, Dict

# Initialize the interview coach agent
@st.cache_resource
def get_interview_coach():
    return InterviewCoachAgent(verbose=True)

def initialize_session_state():
    """Initialize all required session state variables"""
    # Initialize user context if not exists
    if "user_context" not in st.session_state:
        st.session_state.user_context = {
            "current_role": "",
            "experience": "",
            "skills": [],
            "interests": [],
            "career_goals": ""
        }
    
    # Initialize interview-related states
    default_interview_state = {
        "questions": {
            "technical_questions": [],
            "behavioral_questions": [],
            "scenario_questions": [],
            "questions_to_ask": []
        },
        "current_question": 0,
        "answers": {},
        "feedback": {}
    }
    
    # If current_interview doesn't exist or is None, initialize it with default state
    if not st.session_state.get("current_interview"):
        st.session_state.current_interview = default_interview_state
    else:
        # If it exists but questions is None, initialize questions
        if not st.session_state.current_interview.get("questions"):
            st.session_state.current_interview["questions"] = default_interview_state["questions"]
    
    if "saved_interviews" not in st.session_state:
        st.session_state.saved_interviews = []

def main():
    st.title("🎤 Interview Coach")
    
    # Initialize all session state variables
    initialize_session_state()
    
    # Initialize the agent
    coach = get_interview_coach()
    
    # Check if profile is completed
    if not any(st.session_state.user_context.values()):
        st.warning("Please complete your profile in the home page first!")
        st.write("Go to the home page and fill out your profile information to get personalized interview practice.")
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
            value=st.session_state.user_context.get("career_goals", "").split("\n")[0] if st.session_state.user_context.get("career_goals") else ""
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
        default_skills = st.session_state.user_context.get("skills", [])[:3] if st.session_state.user_context.get("skills") else []
        skills_focus = st.multiselect(
            "Skills to Focus On",
            options=st.session_state.user_context.get("skills", []) + [
                "Problem Solving", "Communication", "Leadership",
                "Technical Skills", "Project Management"
            ],
            default=default_skills
        )
        
        # Submit button
        start_button = st.form_submit_button("Start Interview Preparation")
    
    # Generate interview questions
    if start_button:
        if not role:
            st.error("Please enter a target role to begin the interview preparation.")
            return
            
        with st.spinner("Preparing interview questions..."):
            try:
                # Generate questions
                questions = coach.generate_interview_questions(
                    role=role,
                    experience_level=experience_level,
                    skills=skills_focus,
                    interview_type=interview_type
                )
                
                # Display questions
                if questions and "structured_data" in questions:
                    structured_data = questions["structured_data"]
                    
                    # Technical Questions
                    st.subheader("Technical Questions")
                    tech_questions = structured_data.get("technical_questions", [])
                    if tech_questions:
                        for i, q in enumerate(tech_questions, 1):
                            st.write(f"{i}. {q}")
                    else:
                        st.write("No technical questions generated")
                    
                    # Behavioral Questions
                    st.subheader("Behavioral Questions")
                    behav_questions = structured_data.get("behavioral_questions", [])
                    if behav_questions:
                        for i, q in enumerate(behav_questions, 1):
                            st.write(f"{i}. {q}")
                    else:
                        st.write("No behavioral questions generated")
                    
                    # Scenario Questions
                    st.subheader("Scenario Questions")
                    scen_questions = structured_data.get("scenario_questions", [])
                    if scen_questions:
                        for i, q in enumerate(scen_questions, 1):
                            st.write(f"{i}. {q}")
                    else:
                        st.write("No scenario questions generated")
                    
                    # Questions to Ask
                    st.subheader("Questions to Ask Interviewer")
                    ask_questions = structured_data.get("questions_to_ask", [])
                    if ask_questions:
                        for i, q in enumerate(ask_questions, 1):
                            st.write(f"{i}. {q}")
                    else:
                        st.write("No questions to ask generated")
                    
                    # Update session state
                    st.session_state.current_interview = {
                        "questions": structured_data,
                        "current_question": 0,
                        "answers": {},
                        "feedback": {}
                    }
                    
                    if any(structured_data.values()):
                        st.success("Interview questions generated successfully!")
                    else:
                        st.error("No questions were generated. Please try again.")
                
            except Exception as e:
                st.error(f"Error generating questions: {str(e)}")

    # Add a separator between question generation and practice session
    st.divider()

    # Practice interface
    if (st.session_state.get("current_interview") and 
        isinstance(st.session_state.current_interview.get("questions", {}), dict)):
        
        questions = st.session_state.current_interview.get("questions", {})
        
        has_questions = bool(
            questions.get("technical_questions", []) or
            questions.get("behavioral_questions", []) or
            questions.get("scenario_questions", [])
        )
        
        if has_questions:
            # Create a two-column layout for practice session
            practice_col, feedback_col = st.columns([3, 2])
            
            with practice_col:
                st.header("Practice Session")
                
                # Get all questions in a single list
                all_questions = (
                    questions.get("technical_questions", []) +
                    questions.get("behavioral_questions", []) +
                    questions.get("scenario_questions", [])
                )
                
                # Get current question index
                current_idx = st.session_state.current_interview.get("current_question", 0)
                
                if current_idx < len(all_questions):
                    st.subheader(f"Question {current_idx + 1} of {len(all_questions)}")
                    st.write(all_questions[current_idx])
                    
                    # Show previous answer as default value in text area if it exists
                    previous_answer = ""
                    if current_idx in st.session_state.current_interview.get("answers", {}):
                        previous_answer = st.session_state.current_interview["answers"][current_idx]
                    
                    # Answer input with previous answer as default value
                    answer = st.text_area("Your Answer:", value=previous_answer, height=150)
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        if st.button("Previous Question") and current_idx > 0:
                            st.session_state.current_interview["current_question"] -= 1
                            st.rerun()
                    
                    with col2:
                        if answer and st.button("Submit Answer"):
                            # Store the answer
                            st.session_state.current_interview["answers"][current_idx] = answer
                            
                            # Just save the answer and show a message
                            st.success("Answer saved! Feedback will be provided at the end.")
                            
                            # Automatically move to the next question if not the last one
                            if current_idx < len(all_questions) - 1:
                                st.session_state.current_interview["current_question"] += 1
                                st.rerun()
                    
                    with col3:
                        if st.button("Next Question") and current_idx < len(all_questions) - 1:
                            st.session_state.current_interview["current_question"] += 1
                            st.rerun()
                    
                    # Add button to force generate feedback if answer exists
                    if current_idx in st.session_state.current_interview.get("answers", {}):
                        st.markdown("---")
                        if st.button("Generate Feedback Now", type="primary"):
                            with st.spinner("Analyzing your response..."):
                                try:
                                    # Get feedback
                                    feedback = coach.evaluate_response(
                                        question=all_questions[current_idx],
                                        answer=st.session_state.current_interview["answers"][current_idx],
                                        role=role,
                                        experience_level=experience_level
                                    )
                                    
                                    # Store feedback
                                    st.session_state.current_interview["feedback"][current_idx] = feedback
                                    st.success("Feedback generated! Check the feedback panel.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error generating feedback: {str(e)}")
                
                else:
                    st.success("Interview practice complete!")
                    
                    # Process batch feedback if not already done
                    if (st.session_state.current_interview.get("answers") and
                        not st.session_state.current_interview.get("feedback")):
                        
                        with st.spinner("Processing all your answers... This may take a moment."):
                            for q_idx, ans in st.session_state.current_interview["answers"].items():
                                # Get feedback for each answer
                                feedback = coach.evaluate_response(
                                    question=all_questions[int(q_idx)],
                                    answer=ans,
                                    role=role,
                                    experience_level=experience_level
                                )
                                # Store feedback
                                st.session_state.current_interview["feedback"][q_idx] = feedback
                            
                            st.success("All responses evaluated! See feedback in the sidebar.")
                    
                    # Overall feedback
                    st.header("Interview Performance Summary")
                    if st.session_state.current_interview["feedback"]:
                        total_score = sum(
                            feedback.get('structured_data', {}).get('score', 0) or 0
                            for feedback in st.session_state.current_interview["feedback"].values()
                        ) / len(st.session_state.current_interview["feedback"])
                        
                        st.metric("Overall Score", f"{total_score:.1f}%")
                        
                        # Save interview session
                        if st.button("Save Interview Session"):
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
                        initialize_session_state()
                        st.rerun()
            
            # Feedback column - always displayed on the right side
            with feedback_col:
                st.markdown("### Feedback")
                
                # Get current feedback if available
                current_idx = st.session_state.current_interview.get("current_question", 0)
                current_feedback = None
                
                # Get feedback for current question
                if current_idx in st.session_state.current_interview.get("feedback", {}):
                    current_feedback = st.session_state.current_interview["feedback"][current_idx]
                
                # Display feedback if available
                if current_feedback:
                    # Use a container with custom styling for the feedback
                    st.markdown("""
                    <style>
                    .feedback-container {
                        background-color: #f8f9fa;
                        border-radius: 10px;
                        padding: 15px;
                        margin-bottom: 20px;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # Feedback container
                    with st.container():
                        # Safely extract score with default value
                        score = current_feedback.get('structured_data', {}).get('score')
                        if score is not None:
                            st.metric("Response Score", f"{score}%")
                        
                        # Strengths section with better error handling
                        st.subheader("Strengths")
                        strengths = current_feedback.get('structured_data', {}).get('strengths', [])
                        if strengths:
                            for strength in strengths:
                                st.success(f"✓ {strength}")
                        else:
                            st.info("Your answer contains relevant information that addresses the question.")
                        
                        # Areas for improvement with better error handling
                        st.subheader("Areas for Improvement")
                        improvements = current_feedback.get('structured_data', {}).get('improvements', [])
                        if improvements:
                            for improvement in improvements:
                                st.info(f"↗ {improvement}")
                        else:
                            st.info("Try to be more specific and provide concrete examples in your response.")
                        
                        # Better response with fallback option
                        st.subheader("Sample Better Response")
                        better_response = current_feedback.get('structured_data', {}).get('better_response', '')
                        if better_response:
                            st.write(better_response)
                        else:
                            st.write("""
                            A stronger answer would include:
                            - Specific examples from your experience
                            - Quantifiable results where possible
                            - Clear structure (problem, action, result)
                            - Connection to the role requirements
                            """)
                        
                        # Tips with fallback
                        with st.expander("Additional Tips"):
                            tips = current_feedback.get('structured_data', {}).get('tips', [])
                            if tips:
                                for tip in tips:
                                    st.write(f"• {tip}")
                            else:
                                st.write("""
                                • Prepare several examples from your experience that demonstrate key skills
                                • Use the STAR method (Situation, Task, Action, Result) for behavioral questions
                                • Research the company and position thoroughly beforehand
                                • Practice with common questions in your field
                                • Focus on being concise but thorough in your responses
                                """)
                elif current_idx in st.session_state.current_interview.get("answers", {}):
                    # Show message when answer exists but feedback doesn't
                    st.write("Click 'Generate Feedback Now' if you want immediate feedback for this question.")
                else:
                    # Show placeholder when no feedback is available
                    st.write("Submit your answer to enable feedback generation.")
        else:
            st.info("No interview questions generated yet. Please fill out the form above to start.")
    
    # Previous interviews in sidebar
    with st.sidebar:
        if st.session_state.saved_interviews:
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