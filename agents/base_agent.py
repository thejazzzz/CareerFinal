from crewai import Agent
from langchain_openai import ChatOpenAI
from config.config import Config

class BaseAgent:
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        verbose: bool = False
    ):
        """
        Initialize a base agent with common properties.
        
        Args:
            role (str): The role of the agent
            goal (str): The main goal/objective of the agent
            backstory (str): The agent's backstory for context
            verbose (bool): Whether to enable verbose logging
        """
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        
        # Initialize the language model
        self.llm = ChatOpenAI(
            model_name=Config.DEFAULT_GPT_MODEL,
            temperature=0.7,
            api_key=Config.OPENAI_API_KEY
        )
    
    def _log(self, message: str) -> None:
        """Log messages if verbose mode is enabled"""
        if self.verbose:
            print(f"[{self.role}] {message}")
    
    def _format_error(self, error: Exception) -> str:
        """Format error messages consistently"""
        return f"Error in {self.role}: {str(error)}"
    
    def create_agent(self) -> Agent:
        """
        Create and return a CrewAI agent instance.
        
        Returns:
            Agent: A CrewAI agent instance
        """
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            verbose=self.verbose,
            llm=self.llm
        )
    
    def validate_input(self, input_data: dict) -> bool:
        """
        Validate input data for the agent.
        
        Args:
            input_data (dict): Input data to validate
            
        Returns:
            bool: True if valid, raises ValueError if invalid
        """
        required_fields = self.get_required_fields()
        missing_fields = [field for field in required_fields if field not in input_data]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        return True
    
    def get_required_fields(self) -> list:
        """
        Get required fields for the agent. Override in subclasses.
        
        Returns:
            list: List of required field names
        """
        return [] 