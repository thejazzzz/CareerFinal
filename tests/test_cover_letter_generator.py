from agents.cover_letter_generator import CoverLetterGeneratorAgent
from config.config import Config

def test_cover_letter_generator():
    # Initialize the agent
    agent = CoverLetterGeneratorAgent(verbose=True)
    
    # Test parameters
    job_description = """
    Senior Software Engineer - Python
    
    We are seeking an experienced Python developer to join our growing team. The ideal candidate will have:
    - 5+ years of experience with Python and web frameworks (Django/Flask)
    - Strong background in cloud technologies (AWS/Azure)
    - Experience with microservices architecture
    - Team leadership experience
    - Strong communication skills
    
    Responsibilities:
    - Design and implement scalable backend services
    - Lead a team of junior developers
    - Collaborate with product and design teams
    - Contribute to system architecture decisions
    """
    
    candidate_info = {
        "experience": "6 years of software development experience, specializing in Python and web technologies",
        "skills": [
            "Python",
            "Django",
            "AWS",
            "Microservices",
            "Team Leadership",
            "System Design"
        ],
        "achievements": [
            "Led a team of 5 developers in delivering a major platform upgrade",
            "Reduced system response time by 40% through optimization",
            "Implemented CI/CD pipeline reducing deployment time by 60%"
        ]
    }
    
    company_name = "TechCorp Solutions"
    
    try:
        # Test cover letter generation
        print("\n=== Generated Cover Letter ===\n")
        cover_letter = agent.generate_cover_letter(
            job_description=job_description,
            candidate_info=candidate_info,
            company_name=company_name,
            style="professional"
        )
        
        # Print structured cover letter
        print(cover_letter["structured_data"]["greeting"])
        print()
        print(cover_letter["structured_data"]["opening"])
        print()
        for paragraph in cover_letter["structured_data"]["body"]:
            print(paragraph)
            print()
        print(cover_letter["structured_data"]["closing"])
        print(cover_letter["structured_data"]["signature"])
        
        # Test cover letter improvement
        print("\n=== Cover Letter Improvements ===\n")
        
        focus_areas = [
            "Stronger emphasis on leadership experience",
            "More specific technical achievements",
            "Better company culture alignment"
        ]
        
        improvements = agent.improve_cover_letter(
            cover_letter=cover_letter["raw_content"],
            focus_areas=focus_areas
        )
        
        print("Enhancements Made:")
        for enhancement in improvements["structured_data"]["enhancements"]:
            print(f"- {enhancement}")
        
        print("\nAdditional Suggestions:")
        for suggestion in improvements["structured_data"]["suggestions"]:
            print(f"- {suggestion}")
        
        print("\nImproved Version:")
        print(improvements["structured_data"]["improved_version"])
    
    except Exception as e:
        print(f"Error testing Cover Letter Generator: {str(e)}")

if __name__ == "__main__":
    # Validate configuration
    Config.validate_config()
    
    # Run the test
    test_cover_letter_generator() 