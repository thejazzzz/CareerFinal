from agents.career_navigator import CareerNavigatorAgent
from config.config import Config

def test_career_navigator():
    # Initialize the agent
    agent = CareerNavigatorAgent(verbose=True)
    
    # Test parameters
    current_role = "Junior Software Developer"
    experience = "2 years of experience in web development"
    skills = [
        "Python",
        "JavaScript",
        "React",
        "Node.js",
        "SQL",
        "Git"
    ]
    interests = [
        "Machine Learning",
        "Cloud Computing",
        "System Design",
        "Team Leadership"
    ]
    goals = [
        "Become a Senior Full Stack Developer",
        "Lead a development team",
        "Work on AI/ML projects",
        "Contribute to open source"
    ]
    
    try:
        # Test career path creation
        print("\n=== Career Path Analysis ===\n")
        career_path = agent.create_career_path(
            current_role=current_role,
            experience=experience,
            skills=skills,
            interests=interests,
            goals=goals
        )
        
        print("Career Path Options:")
        for path in career_path["structured_data"]["path_options"]:
            print(f"- {path}")
        
        print("\nRequired Skills:")
        for skill in career_path["structured_data"]["required_skills"]:
            print(f"- {skill}")
        
        print("\nTimeline and Milestones:")
        for milestone in career_path["structured_data"]["timeline"]:
            print(f"- {milestone}")
        
        print("\nPotential Challenges:")
        for challenge in career_path["structured_data"]["challenges"]:
            print(f"- {challenge}")
        
        print("\nIndustry Trends:")
        for trend in career_path["structured_data"]["trends"]:
            print(f"- {trend}")
        
        # Test role analysis
        if career_path["structured_data"]["path_options"]:
            print("\n=== Role Analysis ===\n")
            target_role = career_path["structured_data"]["path_options"][0]
            industry = "Technology"
            
            role_analysis = agent.analyze_role(
                target_role=target_role,
                industry=industry
            )
            
            print(f"Analysis for {target_role} in {industry}:\n")
            
            print("Role Overview:")
            for item in role_analysis["structured_data"]["overview"]:
                print(f"- {item}")
            
            print("\nRequired Skills and Experience:")
            for item in role_analysis["structured_data"]["requirements"]:
                print(f"- {item}")
            
            print("\nIndustry Outlook:")
            for item in role_analysis["structured_data"]["outlook"]:
                print(f"- {item}")
            
            print("\nSalary Range and Growth:")
            for item in role_analysis["structured_data"]["salary"]:
                print(f"- {item}")
            
            print("\nKey Companies:")
            for company in role_analysis["structured_data"]["companies"]:
                print(f"- {company}")
    
    except Exception as e:
        print(f"Error testing Career Navigator: {str(e)}")

if __name__ == "__main__":
    # Validate configuration
    Config.validate_config()
    
    # Run the test
    test_career_navigator() 