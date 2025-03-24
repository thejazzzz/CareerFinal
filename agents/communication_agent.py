from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from langchain.prompts import PromptTemplate
import re

class CommunicationAgent(BaseAgent):
    def __init__(self, verbose: bool = False):
        super().__init__(
            role="Communication Expert",
            goal="Help users develop effective networking strategies",
            backstory="Specialist in professional networking strategies for career advancement",
            verbose=verbose
        )
        
        # Networking strategy prompt
        self.networking_prompt = PromptTemplate(
            input_variables=["career_stage", "industry", "goals", "current_network"],
            template="""
            Create a personalized networking strategy based on the following information:
            
            Career Stage:
            {career_stage}
            
            Industry:
            {industry}
            
            Networking Goals:
            {goals}
            
            Current Network Description:
            {current_network}
            
            Please provide a comprehensive networking strategy including:
            1. Target Connections (types of professionals to connect with)
            2. Networking Platforms (LinkedIn, industry-specific platforms, events)
            3. Outreach Templates (connection requests, follow-ups, informational interviews)
            4. Engagement Strategy (content sharing, commenting, group participation)
            5. In-Person Networking Tactics (events, conferences, meetups)
            6. Relationship Nurturing (maintaining and strengthening connections)
            7. Metrics to Track (connection growth, engagement rates, opportunities generated)
            8. Weekly Networking Action Plan
            
            Make all recommendations specific to the industry, career stage, and goals.
            """
        )
    
    def create_networking_strategy(
        self,
        career_stage: str,
        industry: str,
        goals: List[str],
        current_network: str
    ) -> Dict:
        """
        Create a personalized networking strategy
        
        Args:
            career_stage (str): User's current career stage
            industry (str): User's industry
            goals (List[str]): User's networking goals
            current_network (str): Description of user's current network
            
        Returns:
            Dict: Personalized networking strategy
        """
        try:
            # Format goals
            goals_text = "\n".join([f"- {goal}" for goal in goals])
            
            # Get networking strategy from LLM
            response = self.llm.invoke(
                self.networking_prompt.format(
                    career_stage=career_stage,
                    industry=industry,
                    goals=goals_text,
                    current_network=current_network
                )
            ).content
            
            # Parse and structure the response
            strategy = {
                "raw_strategy": response,
                "structured_data": self._parse_networking_strategy(response)
            }
            
            self._log(f"Created networking strategy for {career_stage} professional in {industry}")
            return strategy
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def _parse_networking_strategy(self, response: str) -> Dict:
        """Parse networking strategy response"""
        strategy_data = {
            "target_connections": [],
            "platforms": [],
            "outreach_templates": [],
            "engagement_strategy": [],
            "in_person_tactics": [],
            "relationship_nurturing": [],
            "metrics": [],
            "action_plan": []
        }
        
        # Split into sections and extract content
        sections = re.split(r'\d+\.\s+', response)
        
        # The first element is usually empty after splitting
        if sections and not sections[0].strip():
            sections = sections[1:]
        
        # Map sections to data structure
        section_mapping = {
            "target connections": "target_connections",
            "networking platforms": "platforms",
            "outreach templates": "outreach_templates",
            "engagement strategy": "engagement_strategy",
            "in-person networking": "in_person_tactics",
            "relationship nurturing": "relationship_nurturing",
            "metrics to track": "metrics",
            "weekly networking": "action_plan"
        }
        
        # Parse each section
        current_section = None
        for i, section in enumerate(sections):
            # Identify which section this is
            for key, value in section_mapping.items():
                if i < len(sections) - 1 and any(key in title.lower() for title in [sections[i], sections[i+1]]):
                    current_section = value
                    break
            
            if current_section:
                # Extract content (remove potential headers)
                content = section.strip()
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                # Remove lines that look like headers
                filtered_lines = []
                for line in lines:
                    if not any(key in line.lower() for key in section_mapping.keys()):
                        # If line starts with a bullet or number, clean it up
                        if line.startswith('-') or line.startswith('•'):
                            line = line[1:].strip()
                        elif re.match(r'^\d+\.\s+', line):
                            line = re.sub(r'^\d+\.\s+', '', line).strip()
                        
                        if line:
                            filtered_lines.append(line)
                
                # Add to structured data
                if filtered_lines:
                    strategy_data[current_section].extend(filtered_lines)
        
        # Ensure all sections have at least one item
        for key in strategy_data:
            if not strategy_data[key]:
                strategy_data[key] = ["No specific information provided"]
        
        return strategy_data
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for the communication agent"""
        return ["career_stage", "industry", "goals"] 