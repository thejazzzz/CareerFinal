import streamlit as st
from agents.job_searcher import JobSearchAgent

# Initialize the job search agent
@st.cache_resource
def get_job_searcher():
    return JobSearchAgent(verbose=True)

def main():
    st.title("🔍 Job Search")
    
    # Initialize the agent
    job_searcher = get_job_searcher()
    
    st.write("""
    Find relevant job opportunities based on your skills and preferences. 
    Our AI-powered job search will:
    - Match jobs with your skills
    - Analyze job requirements
    - Provide fit analysis
    - Suggest skill improvements
    """)
    
    # Search interface
    with st.form("job_search_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            keywords = st.text_input(
                "Job Title or Keywords",
                value=st.session_state.user_context.get("current_role", ""),
                help="Enter job title, skills, or keywords"
            )
            location = st.text_input("Location", help="City, State, or Country")
        
        with col2:
            country = st.selectbox(
                "Search Country",
                ["us", "uk", "au", "ca"],
                help="Select country for job search"
            )
            max_results = st.slider(
                "Maximum Results",
                min_value=5,
                max_value=20,
                value=10,
                help="Number of jobs to display"
            )
        
        # Advanced filters
        with st.expander("Advanced Filters"):
            experience_level = st.selectbox(
                "Experience Level",
                ["Entry Level", "Mid Level", "Senior", "Lead", "Executive"]
            )
            job_type = st.multiselect(
                "Job Type",
                ["Full-time", "Part-time", "Contract", "Remote"],
                default=["Full-time"]
            )
            sort_by = st.selectbox(
                "Sort By",
                ["Relevance", "Date Posted", "Salary"]
            )
        
        search_button = st.form_submit_button("Search Jobs")
    
    # Process search
    if search_button and keywords:
        with st.spinner("Searching for jobs..."):
            try:
                # Search jobs
                jobs = job_searcher.search_jobs(
                    keywords=keywords,
                    location=location,
                    country=country,
                    max_results=max_results
                )
                
                # Store results in session state
                st.session_state.job_search_results = jobs
                
                # Display results
                st.success(f"Found {len(jobs)} matching jobs!")
                
                # Display each job
                for job in jobs:
                    with st.expander(f"{job['title']} at {job['company']}"):
                        # Job details
                        st.write(f"**Location:** {job['location']}")
                        if job['salary_min'] and job['salary_max']:
                            st.write(f"**Salary Range:** ${job['salary_min']:,.2f} - ${job['salary_max']:,.2f}")
                        
                        # Job description
                        st.write("**Description:**")
                        st.write(job['description'])
                        
                        # Application link
                        st.write(f"**Apply Here:** {job['url']}")
                        
                        # Job fit analysis
                        if st.session_state.user_context.get("skills"):
                            if st.button(f"Analyze Fit for {job['title']}", key=f"fit_{jobs.index(job)}"):
                                with st.spinner("Analyzing job fit..."):
                                    fit_analysis = job_searcher.analyze_job_fit(
                                        job_description=job['description'],
                                        user_skills=st.session_state.user_context["skills"]
                                    )
                                    
                                    # Display fit analysis
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric(
                                            "Match Score",
                                            f"{fit_analysis['structured_data']['match_score']}%"
                                        )
                                    
                                    with col2:
                                        st.write("**Matching Skills:**")
                                        for skill in fit_analysis['structured_data']['matching_skills']:
                                            st.success(f"✓ {skill}")
                                    
                                    with col3:
                                        st.write("**Skills to Develop:**")
                                        for skill in fit_analysis['structured_data']['missing_skills']:
                                            st.info(f"↗ {skill}")
                                    
                                    # Recommendations
                                    st.write("**Recommendations:**")
                                    for rec in fit_analysis['structured_data']['recommendations']:
                                        st.write(f"• {rec}")
                        else:
                            st.warning("Complete your profile with skills to get a job fit analysis!")
                
                # Save jobs feature
                if st.button("Save Search Results"):
                    if "saved_jobs" not in st.session_state:
                        st.session_state.saved_jobs = []
                    st.session_state.saved_jobs.extend(jobs)
                    st.success("Jobs saved to your profile!")
                
            except Exception as e:
                st.error(f"Error searching jobs: {str(e)}")
    
    # Saved jobs section in sidebar
    with st.sidebar:
        if "saved_jobs" in st.session_state and st.session_state.saved_jobs:
            st.header("Saved Jobs")
            for job in st.session_state.saved_jobs:
                with st.expander(f"{job['title']} at {job['company']}"):
                    st.write(f"**Location:** {job['location']}")
                    st.write(f"**Apply:** {job['url']}")
                    if st.button("Remove", key=f"remove_{st.session_state.saved_jobs.index(job)}"):
                        st.session_state.saved_jobs.remove(job)
                        st.rerun()

if __name__ == "__main__":
    main() 