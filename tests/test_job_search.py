from agents.job_searcher import JobSearchAgent
from config.config import Config

def test_job_search():
    # Initialize the agent
    agent = JobSearchAgent(verbose=True)
    
    # Test parameters
    test_keywords = "Python Developer"
    test_location = "New York"
    test_max_results = 5
    
    try:
        # Search for jobs
        print("\n=== Job Search Results ===\n")
        jobs = agent.search_jobs(
            keywords=test_keywords,
            location=test_location,
            max_results=test_max_results
        )
        
        # Print results
        print(f"Found {len(jobs)} jobs matching '{test_keywords}' in {test_location}\n")
        
        for job in jobs:
            print(f"Title: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}")
            if job['salary_min'] and job['salary_max']:
                print(f"Salary Range: ${job['salary_min']:,.2f} - ${job['salary_max']:,.2f}")
            print(f"URL: {job['url']}")
            print("\nDescription:")
            print(job['description'][:200] + "...")  # Show first 200 chars
            print("\n---\n")
        
        # Test job fit analysis
        if jobs:
            print("\n=== Job Fit Analysis ===\n")
            # Sample user skills
            test_skills = [
                "Python",
                "Django",
                "JavaScript",
                "SQL",
                "Git"
            ]
            
            # Analyze first job
            first_job = jobs[0]
            fit_analysis = agent.analyze_job_fit(
                job_description=first_job['description'],
                user_skills=test_skills
            )
            
            print(f"Analyzing fit for: {first_job['title']}\n")
            print(f"Match Score: {fit_analysis['structured_data']['match_score']}%")
            
            print("\nMatching Skills:")
            for skill in fit_analysis['structured_data']['matching_skills']:
                print(f"- {skill}")
            
            print("\nSkills to Develop:")
            for skill in fit_analysis['structured_data']['missing_skills']:
                print(f"- {skill}")
            
            print("\nRecommendations:")
            for rec in fit_analysis['structured_data']['recommendations']:
                print(f"- {rec}")
        
    except Exception as e:
        print(f"Error testing Job Search: {str(e)}")

if __name__ == "__main__":
    # Validate configuration
    Config.validate_config()
    
    # Run the test
    test_job_search() 