import os
from agents.resume_analyzer import ResumeAnalyzerAgent
from config.config import Config

def test_resume_analyzer():
    # Initialize the agent
    agent = ResumeAnalyzerAgent(verbose=True)
    
    # Test with a sample resume
    test_resume_path = "test_resume.pdf"  # You'll need to provide a test resume
    
    try:
        # Process the resume
        result = agent.process_resume(test_resume_path)
        
        # Print results
        print("\n=== Resume Analysis Results ===\n")
        
        print("Professional Summary:")
        for item in result["structured_data"]["professional_summary"]:
            print(f"- {item}")
        
        print("\nSkills:")
        for item in result["structured_data"]["skills"]:
            print(f"- {item}")
        
        print("\nKey Strengths:")
        for item in result["structured_data"]["key_strengths"]:
            print(f"- {item}")
        
        print("\nAreas for Improvement:")
        for item in result["structured_data"]["areas_for_improvement"]:
            print(f"- {item}")
        
    except Exception as e:
        print(f"Error testing Resume Analyzer: {str(e)}")

if __name__ == "__main__":
    # Validate configuration
    Config.validate_config()
    
    # Run the test
    test_resume_analyzer() 