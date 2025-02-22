from agents.interview_coach import InterviewCoachAgent
from config.config import Config

def test_interview_coach():
    # Initialize the agent
    agent = InterviewCoachAgent(verbose=True)
    
    # Test parameters
    role = "Senior Python Developer"
    experience_level = "5+ years"
    skills = [
        "Python",
        "Django",
        "FastAPI",
        "SQL",
        "System Design",
        "Team Leadership",
        "AWS"
    ]
    
    try:
        # Test question generation
        print("\n=== Interview Questions ===\n")
        questions = agent.generate_interview_questions(
            role=role,
            experience_level=experience_level,
            skills=skills,
            interview_type="full"
        )
        
        print("Technical Questions:")
        for q in questions["structured_data"]["technical_questions"]:
            print(f"- {q}")
        
        print("\nBehavioral Questions:")
        for q in questions["structured_data"]["behavioral_questions"]:
            print(f"- {q}")
        
        print("\nScenario Questions:")
        for q in questions["structured_data"]["scenario_questions"]:
            print(f"- {q}")
        
        print("\nQuestions to Ask Interviewer:")
        for q in questions["structured_data"]["questions_to_ask"]:
            print(f"- {q}")
        
        # Test response evaluation
        print("\n=== Response Evaluation ===\n")
        
        # Sample question and answer for testing
        test_question = "Can you explain how you would design a scalable web application?"
        test_answer = """
        I would start by understanding the requirements and constraints, such as expected traffic, 
        data volume, and performance goals. Then, I would design a microservices architecture 
        using containerization with Docker and Kubernetes for scalability. The system would use 
        a load balancer, caching layer with Redis, and a distributed database like PostgreSQL 
        with read replicas. For monitoring and logging, I would implement tools like Prometheus 
        and ELK stack.
        """
        
        evaluation = agent.evaluate_response(
            question=test_question,
            answer=test_answer,
            role=role,
            experience_level=experience_level
        )
        
        print(f"Question: {test_question}\n")
        print(f"Answer: {test_answer}\n")
        print(f"Score: {evaluation['structured_data']['score']}%\n")
        
        print("Strengths:")
        for strength in evaluation["structured_data"]["strengths"]:
            print(f"- {strength}")
        
        print("\nAreas for Improvement:")
        for improvement in evaluation["structured_data"]["improvements"]:
            print(f"- {improvement}")
        
        print("\nBetter Response Example:")
        print(evaluation["structured_data"]["better_response"])
        
        print("\nAdditional Tips:")
        for tip in evaluation["structured_data"]["tips"]:
            print(f"- {tip}")
    
    except Exception as e:
        print(f"Error testing Interview Coach: {str(e)}")

if __name__ == "__main__":
    # Validate configuration
    Config.validate_config()
    
    # Run the test
    test_interview_coach() 