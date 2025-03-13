from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from langchain.prompts import PromptTemplate
import re

class CommunicationAgent(BaseAgent):
    def __init__(self, verbose: bool = False):
        super().__init__(
            role="Communication Expert",
            goal="Help users optimize their professional networking and LinkedIn profiles",
            backstory="Specialist in professional communication, networking strategies, and social media optimization for career advancement",
            verbose=verbose
        )
        
        # LinkedIn profile optimization prompt
        self.linkedin_prompt = PromptTemplate(
            input_variables=["profile_data", "target_role", "industry"],
            template="""
            Analyze the following LinkedIn profile information and provide optimization recommendations:
            
            Profile Data:
            {profile_data}
            
            Target Role:
            {target_role}
            
            Industry:
            {industry}
            
            Please provide detailed recommendations for the following sections:
            1. Profile Photo & Banner
            2. Headline
            3. About/Summary
            4. Experience Descriptions
            5. Skills & Endorsements
            6. Education
            7. Recommendations
            8. Additional Sections (Projects, Certifications, etc.)
            9. Content Strategy
            10. Overall Profile Strength
            
            For each section, include:
            - Current assessment
            - Specific improvement suggestions
            - Examples or templates where applicable
            - Best practices for the target role and industry
            """
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
        
        # Communication templates prompt
        self.templates_prompt = PromptTemplate(
            input_variables=["template_type", "context", "tone"],
            template="""
            Create professional communication templates for the following scenario:
            
            Template Type:
            {template_type}
            
            Context:
            {context}
            
            Tone:
            {tone}
            
            Please provide:
            1. 3 different template variations
            2. Guidance on when to use each variation
            3. Customization tips for personalizing the templates
            4. Follow-up suggestions
            5. Best practices for this type of communication
            
            Ensure the templates are concise, professional, and effective for the specified context.
            """
        )
        
        # Social media audit prompt
        self.social_audit_prompt = PromptTemplate(
            input_variables=["platforms", "career_goals", "target_audience"],
            template="""
            Conduct a professional social media audit strategy based on the following information:
            
            Platforms to Audit:
            {platforms}
            
            Career Goals:
            {career_goals}
            
            Target Audience:
            {target_audience}
            
            Please provide a comprehensive audit framework including:
            1. Platform-specific assessment criteria
            2. Content evaluation guidelines
            3. Professional image consistency check
            4. Privacy and security review
            5. Engagement analysis approach
            6. Red flags to look for
            7. Improvement opportunities
            8. Platform-specific optimization tips
            
            For each platform, include specific elements to review and best practices for professional presence.
            """
        )
    
    def optimize_linkedin_profile(
        self,
        profile_data: Dict[str, Any],
        target_role: str,
        industry: str
    ) -> Dict:
        """
        Provide recommendations to optimize a LinkedIn profile
        
        Args:
            profile_data (Dict): User's current LinkedIn profile information
            target_role (str): User's target job role
            industry (str): User's industry
            
        Returns:
            Dict: LinkedIn profile optimization recommendations
        """
        try:
            # Format profile data
            profile_text = "\n".join([
                f"{key}: {value}"
                for key, value in profile_data.items()
            ])
            
            # Get optimization recommendations from LLM
            response = self.llm.invoke(
                self.linkedin_prompt.format(
                    profile_data=profile_text,
                    target_role=target_role,
                    industry=industry
                )
            ).content
            
            # Parse and structure the response
            optimization = {
                "raw_recommendations": response,
                "structured_data": self._parse_linkedin_recommendations(response)
            }
            
            self._log(f"Generated LinkedIn optimization recommendations for {target_role} in {industry}")
            return optimization
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
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
    
    def generate_communication_templates(
        self,
        template_type: str,
        context: str,
        tone: str = "professional"
    ) -> Dict:
        """
        Generate professional communication templates
        
        Args:
            template_type (str): Type of template (e.g., "connection request", "follow-up", "introduction")
            context (str): Specific context for the template
            tone (str): Desired tone (e.g., "professional", "friendly", "formal")
            
        Returns:
            Dict: Communication templates and usage guidance
        """
        try:
            # Get templates from LLM
            response = self.llm.invoke(
                self.templates_prompt.format(
                    template_type=template_type,
                    context=context,
                    tone=tone
                )
            ).content
            
            # Parse and structure the response
            templates = {
                "raw_content": response,
                "structured_data": self._parse_templates(response)
            }
            
            self._log(f"Generated {template_type} templates with {tone} tone")
            return templates
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def create_social_media_audit(
        self,
        platforms: List[str],
        career_goals: List[str],
        target_audience: str
    ) -> Dict:
        """
        Create a professional social media audit strategy
        
        Args:
            platforms (List[str]): Social media platforms to audit
            career_goals (List[str]): User's career goals
            target_audience (str): Description of target audience
            
        Returns:
            Dict: Social media audit strategy
        """
        try:
            # Format platforms and goals
            platforms_text = ", ".join(platforms)
            goals_text = "\n".join([f"- {goal}" for goal in career_goals])
            
            # Get audit strategy from LLM
            response = self.llm.invoke(
                self.social_audit_prompt.format(
                    platforms=platforms_text,
                    career_goals=goals_text,
                    target_audience=target_audience
                )
            ).content
            
            # Parse and structure the response
            audit = {
                "raw_strategy": response,
                "structured_data": self._parse_social_audit(response)
            }
            
            self._log(f"Created social media audit strategy for {platforms_text}")
            return audit
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def _parse_linkedin_recommendations(self, response: str) -> Dict:
        """Parse LinkedIn profile optimization recommendations"""
        sections = {
            "profile_photo": [],
            "headline": [],
            "summary": [],
            "experience": [],
            "skills": [],
            "education": [],
            "recommendations": [],
            "additional_sections": [],
            "content_strategy": [],
            "overall_strength": []
        }
        
        current_section = None
        
        # Split by numbered sections and process
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if re.match(r'^1\..*Photo', line, re.IGNORECASE):
                current_section = "profile_photo"
                continue
            elif re.match(r'^2\..*Headline', line, re.IGNORECASE):
                current_section = "headline"
                continue
            elif re.match(r'^3\..*About|Summary', line, re.IGNORECASE):
                current_section = "summary"
                continue
            elif re.match(r'^4\..*Experience', line, re.IGNORECASE):
                current_section = "experience"
                continue
            elif re.match(r'^5\..*Skills', line, re.IGNORECASE):
                current_section = "skills"
                continue
            elif re.match(r'^6\..*Education', line, re.IGNORECASE):
                current_section = "education"
                continue
            elif re.match(r'^7\..*Recommendations', line, re.IGNORECASE):
                current_section = "recommendations"
                continue
            elif re.match(r'^8\..*Additional', line, re.IGNORECASE):
                current_section = "additional_sections"
                continue
            elif re.match(r'^9\..*Content', line, re.IGNORECASE):
                current_section = "content_strategy"
                continue
            elif re.match(r'^10\..*Overall|Strength', line, re.IGNORECASE):
                current_section = "overall_strength"
                continue
                
            # Add content to current section
            if current_section and line:
                # Clean the line by removing bullets and numbers
                cleaned_line = re.sub(r'^[\-\*•\d\.]+\s*', '', line).strip()
                if cleaned_line:
                    sections[current_section].append(cleaned_line)
        
        return sections
    
    def _parse_networking_strategy(self, response: str) -> Dict:
        """Parse networking strategy response"""
        strategy = {
            "target_connections": [],
            "platforms": [],
            "outreach_templates": [],
            "engagement_strategy": [],
            "in_person_tactics": [],
            "relationship_nurturing": [],
            "metrics": [],
            "action_plan": []
        }
        
        current_section = None
        
        # Process each line
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if re.match(r'^1\..*Target|Connections', line, re.IGNORECASE):
                current_section = "target_connections"
                continue
            elif re.match(r'^2\..*Platforms', line, re.IGNORECASE):
                current_section = "platforms"
                continue
            elif re.match(r'^3\..*Outreach|Templates', line, re.IGNORECASE):
                current_section = "outreach_templates"
                continue
            elif re.match(r'^4\..*Engagement', line, re.IGNORECASE):
                current_section = "engagement_strategy"
                continue
            elif re.match(r'^5\..*In-Person|Events', line, re.IGNORECASE):
                current_section = "in_person_tactics"
                continue
            elif re.match(r'^6\..*Relationship|Nurturing', line, re.IGNORECASE):
                current_section = "relationship_nurturing"
                continue
            elif re.match(r'^7\..*Metrics', line, re.IGNORECASE):
                current_section = "metrics"
                continue
            elif re.match(r'^8\..*Action|Plan', line, re.IGNORECASE):
                current_section = "action_plan"
                continue
                
            # Add content to current section
            if current_section and line:
                # Clean the line by removing bullets and numbers
                cleaned_line = re.sub(r'^[\-\*•\d\.]+\s*', '', line).strip()
                if cleaned_line:
                    strategy[current_section].append(cleaned_line)
        
        return strategy
    
    def _parse_templates(self, response: str) -> Dict:
        """Parse communication templates response"""
        templates = {
            "variations": [],
            "usage_guidance": [],
            "customization_tips": [],
            "follow_up_suggestions": [],
            "best_practices": []
        }
        
        current_section = None
        current_template = None
        
        # Process each paragraph
        paragraphs = response.split('\n\n')
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check for template variations
            if re.search(r'template|variation', paragraph.lower()) and re.search(r'1:|2:|3:', paragraph):
                templates["variations"].append(paragraph)
                continue
                
            # Check for section headers
            if re.search(r'when to use|usage|guidance', paragraph.lower()):
                current_section = "usage_guidance"
            elif re.search(r'customization|personaliz', paragraph.lower()):
                current_section = "customization_tips"
            elif re.search(r'follow-up|follow up', paragraph.lower()):
                current_section = "follow_up_suggestions"
            elif re.search(r'best practices|tips', paragraph.lower()):
                current_section = "best_practices"
            else:
                # If no clear section, add to the appropriate one based on content
                if re.search(r'template|email|message', paragraph.lower()):
                    templates["variations"].append(paragraph)
                elif re.search(r'customize|personalize|adapt', paragraph.lower()):
                    templates["customization_tips"].append(paragraph)
                elif re.search(r'follow|response', paragraph.lower()):
                    templates["follow_up_suggestions"].append(paragraph)
                elif re.search(r'practice|effective|professional', paragraph.lower()):
                    templates["best_practices"].append(paragraph)
                else:
                    # Default to usage guidance if unclear
                    templates["usage_guidance"].append(paragraph)
        
        return templates
    
    def _parse_social_audit(self, response: str) -> Dict:
        """Parse social media audit response"""
        audit = {
            "assessment_criteria": {},
            "content_evaluation": [],
            "image_consistency": [],
            "privacy_security": [],
            "engagement_analysis": [],
            "red_flags": [],
            "improvement_opportunities": [],
            "platform_specific_tips": {}
        }
        
        current_section = None
        current_platform = None
        
        # Process each line
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check for platform-specific content
            platform_match = re.match(r'^(LinkedIn|Twitter|Facebook|Instagram|GitHub|Medium|YouTube):', line)
            if platform_match:
                current_platform = platform_match.group(1)
                if current_platform not in audit["platform_specific_tips"]:
                    audit["platform_specific_tips"][current_platform] = []
                if current_platform not in audit["assessment_criteria"]:
                    audit["assessment_criteria"][current_platform] = []
                continue
                
            # Check for section headers
            if re.search(r'assessment|criteria', line.lower()):
                current_section = "assessment_criteria"
            elif re.search(r'content|evaluation', line.lower()):
                current_section = "content_evaluation"
            elif re.search(r'image|consistency|branding', line.lower()):
                current_section = "image_consistency"
            elif re.search(r'privacy|security', line.lower()):
                current_section = "privacy_security"
            elif re.search(r'engagement|analysis', line.lower()):
                current_section = "engagement_analysis"
            elif re.search(r'red flags|warning', line.lower()):
                current_section = "red_flags"
            elif re.search(r'improvement|opportunities', line.lower()):
                current_section = "improvement_opportunities"
            elif re.search(r'tips|optimization', line.lower()):
                current_section = "platform_specific_tips"
                
            # Add content to current section
            if line:
                # Clean the line by removing bullets and numbers
                cleaned_line = re.sub(r'^[\-\*•\d\.]+\s*', '', line).strip()
                if cleaned_line:
                    if current_section == "assessment_criteria" and current_platform:
                        audit["assessment_criteria"][current_platform].append(cleaned_line)
                    elif current_section == "platform_specific_tips" and current_platform:
                        audit["platform_specific_tips"][current_platform].append(cleaned_line)
                    elif current_section:
                        audit[current_section].append(cleaned_line)
        
        return audit
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for communication agent"""
        return ["communication_type"]  # Basic requirement to determine which function to use 