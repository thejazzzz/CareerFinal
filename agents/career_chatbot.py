from typing import Dict, List, Optional
from .base_agent import BaseAgent
from langchain.prompts import PromptTemplate

class CareerChatbotAgent(BaseAgent):
    def __init__(self, verbose: bool = False):
        super().__init__(
            role="Career Advisor Chatbot",
            goal="Provide helpful career advice and answer career-related questions",
            backstory="AI career counselor with expertise in professional development and career guidance",
            verbose=verbose
        )
        
        self.chat_prompt = PromptTemplate(
            input_variables=["chat_history", "user_query", "user_context"],
            template="""
            Previous conversation:
            {chat_history}
            
            User Context:
            {user_context}
            
            User Query:
            {user_query}
            
            Please provide:
            1. A helpful and informative response
            2. Any relevant follow-up questions
            3. Specific actionable advice when applicable
            4. References to reliable resources when relevant
            """
        )
        
        self.resource_prompt = PromptTemplate(
            input_variables=["topic", "resource_type"],
            template="""
            Suggest high-quality resources for:
            
            Topic: {topic}
            Resource Type: {resource_type}
            
            Please provide:
            1. Top recommended resources
            2. Brief description of each resource
            3. Why it's valuable for this topic
            4. How to best utilize the resource
            """
        )
    
    def get_response(
        self,
        user_query: str,
        chat_history: List[Dict] = None,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate a response to a user's career-related query
        
        Args:
            user_query (str): User's question or input
            chat_history (List[Dict]): Previous conversation history
            user_context (Dict): User's background information
            
        Returns:
            Dict: Chatbot response and suggestions
        """
        try:
            # Format chat history
            history_text = ""
            if chat_history:
                history_text = "\n".join([
                    f"User: {msg['user']}\nBot: {msg['bot']}"
                    for msg in chat_history[-5:]  # Keep last 5 messages for context
                ])
            
            # Format user context
            context_text = ""
            if user_context:
                context_text = "\n".join([
                    f"{key}: {value}"
                    for key, value in user_context.items()
                ])
            
            # Generate response using LLM
            response = self.llm.invoke(
                self.chat_prompt.format(
                    chat_history=history_text,
                    user_query=user_query,
                    user_context=context_text
                )
            ).content
            
            # Parse and structure the response
            chat_response = {
                "raw_response": response,
                "structured_data": self._parse_chat_response(response)
            }
            
            self._log("Generated chat response")
            return chat_response
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def suggest_resources(
        self,
        topic: str,
        resource_type: str = "all"  # Options: courses, books, websites, tools, all
    ) -> Dict:
        """
        Suggest resources for career development topics
        
        Args:
            topic (str): Career-related topic
            resource_type (str): Type of resources to suggest
            
        Returns:
            Dict: Suggested resources and guidance
        """
        try:
            # Get resource suggestions from LLM
            response = self.llm.invoke(
                self.resource_prompt.format(
                    topic=topic,
                    resource_type=resource_type
                )
            ).content
            
            # Parse and structure the response
            resources = {
                "raw_content": response,
                "structured_data": self._parse_resources(response)
            }
            
            self._log(f"Generated resource suggestions for {topic}")
            return resources
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def _parse_chat_response(self, response: str) -> Dict:
        """Parse the chatbot response"""
        sections = response.split("\n\n")
        parsed_data = {
            "main_response": "",
            "follow_up_questions": [],
            "actionable_advice": [],
            "resources": []
        }
        
        current_section = "main_response"
        for section in sections:
            if "?" in section:
                parsed_data["follow_up_questions"].extend(
                    q.strip() for q in section.split("\n") if "?" in q
                )
            elif "resource" in section.lower() or "reference" in section.lower():
                parsed_data["resources"].extend(
                    r.strip("- ") for r in section.split("\n") if r.strip("- ")
                )
            elif any(action_word in section.lower() for action_word in ["should", "could", "try", "consider", "recommend"]):
                parsed_data["actionable_advice"].extend(
                    a.strip("- ") for a in section.split("\n") if a.strip("- ")
                )
            else:
                if not parsed_data["main_response"]:
                    parsed_data["main_response"] = section.strip()
        
        return parsed_data
    
    def _parse_resources(self, response: str) -> Dict:
        """Parse the resource suggestions"""
        sections = response.split("\n\n")
        parsed_data = {
            "recommended_resources": [],
            "descriptions": {},
            "value_props": {},
            "usage_tips": {}
        }
        
        current_resource = None
        for section in sections:
            if section.startswith("1.") or section.startswith("-"):
                # This is a resource name
                resource = section.strip("1.- ").split("\n")[0]
                parsed_data["recommended_resources"].append(resource)
                current_resource = resource
            elif current_resource:
                if "why" in section.lower():
                    parsed_data["value_props"][current_resource] = section.split("\n", 1)[1].strip()
                elif "how" in section.lower():
                    parsed_data["usage_tips"][current_resource] = section.split("\n", 1)[1].strip()
                else:
                    parsed_data["descriptions"][current_resource] = section.strip()
        
        return parsed_data
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for chatbot interaction"""
        return ["user_query"] 