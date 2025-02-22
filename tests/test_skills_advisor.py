from agents.skills_advisor import SkillsAdvisorAgent
from config.config import Config

def test_skills_advisor():
    # Initialize the agent
    agent = SkillsAdvisorAgent(verbose=True)
    
    # Test parameters
    current_skills = [
        "Python",
        "JavaScript",
        "HTML/CSS",
        "SQL",
        "Git"
    ]
    
    target_role = "Senior Full Stack Developer"
    
    job_requirements = [
        "Python",
        "JavaScript",
        "React",
        "Node.js",
        "Docker",
        "Kubernetes",
        "AWS",
        "System Design",
        "Team Leadership"
    ]
    
    try:
        # Test skill gap analysis
        print("\n=== Skill Gap Analysis ===\n")
        analysis = agent.analyze_skill_gaps(
            current_skills=current_skills,
            target_role=target_role,
            job_requirements=job_requirements
        )
        
        print("Skill Gaps:")
        for gap in analysis["structured_data"]["skill_gaps"]:
            print(f"- {gap}")
        
        print("\nPriority Skills to Develop:")
        for skill in analysis["structured_data"]["priority_skills"]:
            print(f"- {skill}")
        
        print("\nLearning Resources:")
        for resource in analysis["structured_data"]["learning_resources"]:
            print(f"- {resource}")
        
        print("\nTransition Strategy:")
        for strategy in analysis["structured_data"]["transition_strategy"]:
            print(f"- {strategy}")
        
        # Test learning path creation
        if analysis["structured_data"]["priority_skills"]:
            print("\n=== Learning Path for Top Priority Skill ===\n")
            top_skill = analysis["structured_data"]["priority_skills"][0]
            
            learning_path = agent.create_learning_path(
                skill=top_skill,
                current_level="beginner",
                target_level="advanced"
            )
            
            print(f"Learning Path for: {top_skill}\n")
            
            print("Learning Objectives:")
            for obj in learning_path["structured_data"]["objectives"]:
                print(f"- {obj}")
            
            print("\nRecommended Resources:")
            for resource in learning_path["structured_data"]["resources"]:
                print(f"- {resource}")
            
            print("\nTimeline and Milestones:")
            for milestone in learning_path["structured_data"]["timeline"]:
                print(f"- {milestone}")
            
            print("\nPractice Exercises:")
            for exercise in learning_path["structured_data"]["exercises"]:
                print(f"- {exercise}")
            
            print("\nAssessment Criteria:")
            for criteria in learning_path["structured_data"]["assessment"]:
                print(f"- {criteria}")
    
    except Exception as e:
        print(f"Error testing Skills Advisor: {str(e)}")

if __name__ == "__main__":
    # Validate configuration
    Config.validate_config()
    
    # Run the test
    test_skills_advisor() 