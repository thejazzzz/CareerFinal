import streamlit as st
import os
from agents.resume_analyzer import ResumeAnalyzerAgent
import re
from datetime import datetime
from typing import Dict

# Add this at the top of the file with other constants/globals
important_soft_skills = {
    'leadership', 'communication', 'problem solving', 
    'teamwork', 'project management'
}

# Initialize the resume analyzer agent
@st.cache_resource
def get_resume_analyzer():
    return ResumeAnalyzerAgent(verbose=True)

def initialize_session_state():
    """Initialize session state variables with proper structure"""
    if "user_context" not in st.session_state:
        st.session_state.user_context = {
            "current_role": "",
            "experience": "",
            "skills": [],
            "interests": [],
            "career_goals": "",
            "education": []  # Add education list
        }
    
    if "resume_analysis" not in st.session_state:
        st.session_state.resume_analysis = {
            "success": False,
            "structured_data": {
                "skills": [],
                "current_role": "",
                "experience": "",
                "professional_summary": "",
                "education": []  # Add education list
            },
            "raw_text": "",
            "warnings": [],
            "errors": []
        }

def detect_student_status(text: str) -> bool:
    """Detect if the profile is a student based on resume content"""
    student_indicators = [
        r'student',
        r'pursuing',
        r'currently enrolled',
        r'expected graduation',
        r'semester',
        r'university student',
        r'college student',
        r'bachelor\'s student',
        r'master\'s student',
        r'undergraduate',
        r'graduate student'
    ]
    
    text = text.lower()
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in student_indicators)

def extract_current_role(text: str, is_student: bool) -> Dict[str, any]:
    """Enhanced role detection with better pattern matching"""
    role_info = {
        "role": "",
        "organization": "",
        "confidence": 0.0
    }
    
    # Current role patterns
    role_patterns = [
        # Pattern 1: Current role with organization
        r'(?:currently|presently|now)\s+(?:working\s+as|employed\s+as|serving\s+as)\s+(?:an?\s+)?([^,.\n]+?)(?:\s+at\s+([^,.\n]+))?',
        # Pattern 2: Role with dates including present
        r'([^,\n]*?(?:engineer|developer|analyst|manager|designer|consultant|specialist|director|lead|architect))[^,\n]*?\s+(?:at\s+([^,\n]+))?\s*(?:\(|\s)?(?:\d{4}|present)',
        # Pattern 3: Most recent role entry
        r'^([^,\n]*?)(?:\sat\s|\sin\s|\s-\s)([^,\n]*?)(?:present|current|now)'
    ]
    
    for pattern in role_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            role_info["role"] = match.group(1).strip()
            if len(match.groups()) > 1 and match.group(2):
                role_info["organization"] = match.group(2).strip()
            role_info["confidence"] = 0.9
            return role_info
    
    # If no matches found but is student
    if is_student:
        role_info["role"] = "Student"
        role_info["confidence"] = 0.8
        
        # Try to find educational institution
        edu_pattern = r'(?:studying|enrolled|student)\s+at\s+([^,.\n]+)'
        edu_match = re.search(edu_pattern, text, re.IGNORECASE)
        if edu_match:
            role_info["organization"] = edu_match.group(1).strip()
    
    return role_info

def extract_experience(text: str, is_student: bool) -> Dict[str, any]:
    """Enhanced experience extraction with better pattern matching"""
    experience_info = {
        "years": "0",
        "confidence": 0.0,
        "type": "student" if is_student else "professional"
    }
    
    if is_student:
        # Check for internships or part-time experience
        internship_patterns = [
            r'(\d+)\s*(?:internship|internships)',
            r'(?:completed|done|finished)\s+(\d+)\s*internship',
            r'(\d+)\s*years?\s+(?:of\s+)?(?:part[- ]time|internship)'
        ]
        
        for pattern in internship_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                experience_info["years"] = match.group(1)
                experience_info["confidence"] = 0.8
                experience_info["details"] = "internship experience"
                return experience_info
    else:
        # Professional experience patterns
        experience_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:of\s+)?(?:work\s+)?experience',
            r'(?:experience|working)\s+since\s+(\d{4})',
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:in|at|with)'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if pattern.endswith('(\d{4})'):
                    # Calculate years from year mentioned
                    years = datetime.now().year - int(match.group(1))
                    experience_info["years"] = str(years)
                else:
                    experience_info["years"] = match.group(1)
                experience_info["confidence"] = 0.9
                return experience_info
    
    return experience_info

def filter_and_limit_skills(skills: list) -> list:
    """Filter unnecessary skills and strictly limit to 20 most relevant skills"""
    # Convert input to list if it's a set
    if isinstance(skills, set):
        skills = list(skills)
    
    # Common unnecessary or redundant skills to remove
    unnecessary_skills = {
        # Single letters or numbers
        'r', 'c', 'a', 'b', '1', '2', '3',
        # Common words that aren't really skills
        'the', 'and', 'or', 'in', 'at', 'to', 'of', 'for',
        # Very generic terms
        'computer', 'software', 'programming', 'development', 'technology',
        # Redundant qualifiers
        'basic', 'intermediate', 'advanced', 'proficient', 'experienced',
        # Articles and prepositions
        'a', 'an', 'the', 'in', 'on', 'at', 'by', 'for', 'with',
        # Common file extensions
        'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx',
        # Vague terms
        'etc', 'others', 'various', 'multiple'
    }

    # Essential technical skills to prioritize
    essential_skills = {
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', '.net',
        # Web Development
        'react', 'angular', 'vue', 'node.js', 'html', 'css',
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb',
        # Cloud & DevOps
        'aws', 'azure', 'docker', 'kubernetes',
        # Data Science
        'tensorflow', 'pytorch', 'pandas',
        # Version Control
        'git', 'github',
        # Testing
        'junit', 'pytest', 'selenium'
    }

    filtered_skills = []
    
    # Step 1: Convert all skills to lowercase for comparison
    skills = [skill.lower().strip() for skill in skills]
    
    # Step 2: Remove unnecessary skills
    skills = [skill for skill in skills if skill not in unnecessary_skills]
    
    # Step 3: Prioritize essential technical skills (max 15)
    for skill in essential_skills:
        if skill in skills and len(filtered_skills) < 15:
            filtered_skills.append(skill)
    
    # Step 4: Add important soft skills (max 5)
    soft_skills_added = 0
    for skill in important_soft_skills:
        if skill in skills and soft_skills_added < 5 and len(filtered_skills) < 20:
            filtered_skills.append(skill)
            soft_skills_added += 1
    
    # Step 5: If we still have room, add any remaining valid skills
    remaining_skills = [
        skill for skill in skills 
        if skill not in filtered_skills 
        and skill not in unnecessary_skills
        and len(skill) > 2  # Avoid very short terms
    ]
    
    # Add remaining skills until we hit 20
    for skill in remaining_skills:
        if len(filtered_skills) >= 20:
            break
        filtered_skills.append(skill)
    
    # Step 6: Ensure we have exactly 20 skills
    return filtered_skills[:20]

def update_user_profile(analysis):
    """Update user profile with strict 20-skill limit"""
    try:
        if not analysis.get("success", False):
            st.error("❌ Resume analysis failed. Please check the errors and try again.")
            for error in analysis.get("errors", []):
                st.error(f"- {error}")
            return False
        
        # Get raw text and structured data
        raw_text = analysis.get("raw_text", "")
        structured_data = analysis.get("structured_data", {})
        
        # Filter and limit skills to exactly 20
        skills = []
        if "skills" in structured_data:
            # Convert skills to list if it's a set
            skills_data = structured_data["skills"]
            if isinstance(skills_data, set):
                skills_data = list(skills_data)
            skills = filter_and_limit_skills(skills_data)
        
        # Extract and format role and experience
        role_info = extract_current_role(raw_text, detect_student_status(raw_text))
        experience_info = extract_experience(raw_text, detect_student_status(raw_text))
        
        # Format role display
        current_role = role_info["role"]
        if role_info.get("organization"):
            current_role += f" at {role_info['organization']}"
            
        # Format experience display
        experience = experience_info["years"]
        if experience_info.get("type") == "student" and experience_info.get("details"):
            experience += " (Student with internship experience)"
        
        # Update session state with extracted information
        profile_updates = {
            "current_role": current_role,
            "experience": experience,
            "skills": skills,
            "education": structured_data.get("education", [])  # Add education
        }
        
        # Only update career goals if found in analysis
        if structured_data.get("professional_summary"):
            profile_updates["career_goals"] = structured_data["professional_summary"]
        
        # Update session state
        st.session_state.user_context.update(profile_updates)
        
        # Display what was updated
        st.success("✅ Profile updated with resume information!")
        with st.expander("View Updated Information"):
            st.write("**Current Role:** ", current_role)
            st.write("**Experience:** ", experience)
            
            # Display skills in a structured format
            st.write("**Skills (20):** ")
            
            # Split into technical and soft skills
            technical_skills = [s for s in skills if s not in important_soft_skills]
            soft_skills = [s for s in skills if s in important_soft_skills]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("💻 Technical Skills")
                for skill in technical_skills:
                    st.write(f"• {skill}")
            
            with col2:
                st.write("🤝 Soft Skills")
                for skill in soft_skills:
                    st.write(f"• {skill}")
            
            if "career_goals" in profile_updates:
                st.write("**Career Goals:** ", profile_updates["career_goals"])
            
            # Display any warnings
            if analysis.get("warnings"):
                st.warning("⚠️ Warnings:")
                for warning in analysis["warnings"]:
                    st.warning(f"- {warning}")
        
        return True
        
    except Exception as e:
        st.error(f"Error updating profile: {str(e)}")
        return False

def main():
    st.title("📝 Resume Analyzer")
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize the agent
    analyzer = get_resume_analyzer()
    
    st.write("""
    Get detailed feedback on your resume from our AI-powered analyzer. 
    Upload your resume to receive insights on:
    - Professional Summary
    - Key Skills
    - Experience Analysis
    - Areas for Improvement
    """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"],
        accept_multiple_files=False,
        help="Upload a PDF file of your resume"
    )
    
    if uploaded_file:
        try:
            with st.spinner("Analyzing your resume..."):
                # Process resume
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                # Process resume and ensure proper structure
                analysis = analyzer.process_resume(temp_path)
                st.session_state.resume_analysis = analysis
                
                # Ensure skills is a list before processing
                skills = analysis["structured_data"].get("skills", [])
                if isinstance(skills, set):
                    skills = list(skills)
                
                # Update user profile
                if update_user_profile(analysis):
                    st.success("✅ Profile updated with resume information!")
                
                # Display results
                if analysis.get("success", False):
                    st.success("Resume Analysis Complete!")
                    
                    # Display extracted information
                    st.header("📄 Extracted Information")
                    
                    # Skills Analysis
                    st.subheader("🎯 Skills")
                    if skills:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("💻 Technical Skills")
                            tech_skills = [s for s in skills if not s.startswith("soft:")]
                            for skill in tech_skills[:5]:  # Safely limit to 5 skills
                                st.write(f"• {skill}")
                        
                        with col2:
                            st.write("🤝 Soft Skills")
                            soft_skills = [s.replace("soft:", "") for s in skills if s.startswith("soft:")]
                            for skill in soft_skills[:5]:  # Safely limit to 5 skills
                                st.write(f"• {skill}")
                    
                    # Education Analysis
                    st.subheader("📚 Education")
                    education = analysis["structured_data"].get("education", [])
                    if education:
                        for edu in education:
                            st.write(f"• {edu}")
                    else:
                        st.info("No education information extracted from resume")
                    
                    # Profile Information
                    st.subheader("👤 Profile Information")
                    with st.form("profile_form"):
                        # Form fields with safe default values
                        current_role = st.text_input(
                            "Current Role",
                            value=st.session_state.user_context.get("current_role", "")
                        )
                        
                        experience = st.text_input(
                            "Years of Experience",
                            value=st.session_state.user_state.get("experience", "")
                        )
                        
                        # Ensure skills is a list before using in multiselect
                        available_skills = list(analysis["structured_data"].get("skills", []))
                        default_skills = list(st.session_state.user_context.get("skills", []))
                        
                        skills = st.multiselect(
                            "Skills",
                            options=available_skills,
                            default=default_skills
                        )
                        
                        # Additional Skills
                        additional_skills = st.text_input(
                            "Additional Skills (comma-separated)"
                        )
                        
                        # Interests
                        interests = st.text_input(
                            "Interests (comma-separated)",
                            value=",".join(st.session_state.user_context["interests"])
                        )
                        
                        # Career Goals
                        career_goals = st.text_area(
                            "Career Goals",
                            value=st.session_state.user_context["career_goals"]
                        )
                        
                        # Education Section
                        st.write("📚 **Education**")
                        
                        # Display existing education entries
                        existing_education = st.session_state.user_context.get("education", [])
                        if existing_education:
                            st.write("Current Education Entries:")
                            for i, edu in enumerate(existing_education):
                                st.write(f"{i+1}. {edu}")
                        
                        # Add new education entry
                        col1, col2 = st.columns(2)
                        with col1:
                            degree = st.selectbox(
                                "Degree",
                                options=[
                                    "Select Degree",
                                    "Bachelor of Technology",
                                    "Bachelor of Engineering",
                                    "Bachelor of Science",
                                    "Master of Technology",
                                    "Master of Engineering",
                                    "Master of Science",
                                    "Master of Business Administration",
                                    "Doctor of Philosophy",
                                    "Other"
                                ]
                            )
                            
                            if degree == "Other":
                                degree = st.text_input("Specify Degree")
                        
                        with col2:
                            field = st.text_input("Field of Study")
                        
                        col3, col4 = st.columns(2)
                        with col3:
                            institution = st.text_input("Institution")
                        
                        with col4:
                            year = st.text_input("Year of Completion")
                        
                        # GPA/Percentage
                        gpa = st.text_input("GPA/Percentage (Optional)")
                        
                        # Additional Education Details
                        edu_details = st.text_area(
                            "Additional Details (Optional)",
                            placeholder="Enter any additional details about your education..."
                        )
                        
                        # Save button
                        if st.form_submit_button("💾 Save Profile Updates"):
                            # Format new education entry
                            if degree != "Select Degree" and field and institution and year:
                                new_edu = {
                                    "degree": degree,
                                    "field": field,
                                    "institution": institution,
                                    "year": year,
                                    "gpa": gpa if gpa else None,
                                    "details": edu_details if edu_details else None
                                }
                                
                                # Format education string
                                edu_str = f"{degree} in {field} from {institution} ({year})"
                                if gpa:
                                    edu_str += f" - GPA/Percentage: {gpa}"
                                
                                # Update education list
                                current_education = st.session_state.user_context.get("education", [])
                                current_education.append(edu_str)
                                
                                # Update session state
                                st.session_state.user_context.update({
                                    "current_role": current_role,
                                    "experience": experience,
                                    "skills": skills + [s.strip() for s in additional_skills.split(",") if s.strip()],
                                    "interests": [i.strip() for i in interests.split(",") if i.strip()],
                                    "career_goals": career_goals,
                                    "education": current_education
                                })
                                st.success("✅ Profile updated successfully!")
                                st.experimental_rerun()
                    
                    # Education Management
                    st.subheader("📚 Manage Education")
                    with st.expander("Edit/Delete Education Entries"):
                        current_education = st.session_state.user_context.get("education", [])
                        if current_education:
                            for i, edu in enumerate(current_education):
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"{i+1}. {edu}")
                                with col2:
                                    if st.button(f"Delete Entry {i+1}"):
                                        current_education.pop(i)
                                        st.session_state.user_context["education"] = current_education
                                        st.success("Education entry deleted!")
                                        st.experimental_rerun()
                        else:
                            st.info("No education entries to display")
                    
                    # Education Suggestions
                    if education:
                        st.subheader("🎓 Education Suggestions")
                        with st.expander("View Suggestions"):
                            st.write("""
                            Based on your current education profile, consider:
                            
                            1. **Advanced Degrees**: 
                               - Look into advanced degrees in your field
                               - Consider specialized certifications
                            
                            2. **Continuing Education**:
                               - Stay updated with latest technologies
                               - Take relevant online courses
                            
                            3. **Professional Development**:
                               - Join professional associations
                               - Attend workshops and conferences
                            """)
                            
                            # Display specific suggestions based on education level
                            current_education = st.session_state.user_context.get("education", [])
                            if any("Bachelor" in edu for edu in current_education):
                                st.write("""
                                **Master's Degree Opportunities**:
                                - Consider pursuing a Master's degree to advance your career
                                - Look into specialized Master's programs in emerging fields
                                """)
                            
                            if any("Master" in edu for edu in current_education):
                                st.write("""
                                **Doctoral Opportunities**:
                                - Consider PhD programs for research interests
                                - Look into industry research positions
                                """)
                    
                    # Inside the main() function where skills are displayed
                    if "structured_data" in analysis and "skills" in analysis["structured_data"]:
                        skills = analysis["structured_data"]["skills"]
                        if skills:
                            st.subheader("📊 Extracted Skills:")
                            # Display skills in a grid
                            cols = st.columns(3)
                            for i, skill in enumerate(skills):
                                with cols[i % 3]:
                                    confidence = skill.get("confidence", 0.7) 
                                    confidence_color = "#5FD068" if confidence > 0.7 else "#FFD24C" if confidence > 0.4 else "#F87474"
                                    st.markdown(
                                        f"""<div style="background-color: {confidence_color}20; 
                                        padding: 10px; border-radius: 5px; margin: 5px 0px;
                                        border-left: 5px solid {confidence_color}">
                                        <strong>{skill.get('name', '')}</strong>
                                        <div style="font-size: 0.8em; opacity: 0.8;">
                                        {skill.get('category', 'technical')}
                                        </div>
                                        </div>""", 
                                        unsafe_allow_html=True
                                    )
                        else:
                            st.info("No skills were extracted from the resume. Consider adding a dedicated skills section to your resume.")
                    else:
                        st.info("No skills data found in the analysis.")
                else:
                    st.error("❌ Resume analysis failed. Please check the errors below.")
                    for error in analysis.get("errors", []):
                        st.error(f"- {error}")
        
        except Exception as e:
            st.error(f"❌ Error analyzing resume: {str(e)}")
        
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    main() 