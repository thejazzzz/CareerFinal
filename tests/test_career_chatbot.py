from agents.career_chatbot import CareerChatbotAgent
from config.config import Config

def test_career_chatbot():
    # Initialize the agent
    agent = CareerChatbotAgent(verbose=True)
    
    # Test parameters
    user_context = {
        "current_role": "Software Developer",
        "experience": "3 years",
        "skills": "Python, JavaScript, React, SQL",
        "interests": "AI/ML, Cloud Computing",
        "career_goals": "Transition to Machine Learning Engineer role"
    }
    
    chat_history = [
        {
            "user": "What skills do I need to become a Machine Learning Engineer?",
            "bot": "To become a Machine Learning Engineer, you'll need strong foundations in:\n1. Python programming\n2. Mathematics and Statistics\n3. Machine Learning frameworks (TensorFlow, PyTorch)\n4. Data preprocessing and analysis\n5. Deep Learning concepts"
        }
    ]
    
    try:
        # Test chat response
        print("\n=== Chat Response Test ===\n")
        user_query = "How should I start learning these ML skills while working as a developer?"
        
        response = agent.get_response(
            user_query=user_query,
            chat_history=chat_history,
            user_context=user_context
        )
        
        print(f"User Query: {user_query}\n")
        print("Main Response:")
        print(response["structured_data"]["main_response"])
        
        print("\nFollow-up Questions:")
        for question in response["structured_data"]["follow_up_questions"]:
            print(f"- {question}")
        
        print("\nActionable Advice:")
        for advice in response["structured_data"]["actionable_advice"]:
            print(f"- {advice}")
        
        print("\nRecommended Resources:")
        for resource in response["structured_data"]["resources"]:
            print(f"- {resource}")
        
        # Test resource suggestions
        print("\n=== Resource Suggestions Test ===\n")
        topic = "Machine Learning Fundamentals"
        
        resources = agent.suggest_resources(
            topic=topic,
            resource_type="all"
        )
        
        print(f"Resources for: {topic}\n")
        
        for resource in resources["structured_data"]["recommended_resources"]:
            print(f"Resource: {resource}")
            if resource in resources["structured_data"]["descriptions"]:
                print(f"Description: {resources['structured_data']['descriptions'][resource]}")
            if resource in resources["structured_data"]["value_props"]:
                print(f"Value: {resources['structured_data']['value_props'][resource]}")
            if resource in resources["structured_data"]["usage_tips"]:
                print(f"Usage Tips: {resources['structured_data']['usage_tips'][resource]}")
            print()
    
    except Exception as e:
        print(f"Error testing Career Chatbot: {str(e)}")

if __name__ == "__main__":
    # Validate configuration
    Config.validate_config()
    
    # Run the test
    test_career_chatbot() 