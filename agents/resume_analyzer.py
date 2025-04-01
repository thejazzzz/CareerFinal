import re
import os
from typing import Dict, List, Set, Any
import pdfplumber
from langchain.prompts import PromptTemplate
from .base_agent import BaseAgent
from config.config import Config
import traceback
from collections import OrderedDict

class ResumeAnalyzerAgent(BaseAgent):
    def __init__(self, verbose: bool = False, cache_size: int = 100):
        super().__init__(
            role="Resume Analyzer",
            goal="Analyze resumes for key information",
            backstory="I help extract and analyze information from resumes",
            verbose=verbose
        )
        
        # Initialize both pattern-based and LLM-based analyzers
        self.invalid_skills = {
            # Single letters
            'r', 'go', 'a', 'c', 'in', 
            # Common words
            'of', 'to', 'the', 'and', 'for', 'on', 'at', 'in', 'by', 'or',
            # Common short terms
            'api', 'app', 'web', 'gui', 'css', 'db', 'qa', 'ui', 'ux',
            # Others
            'etc', 'eg', 'ie', 'ex', 'vs'
        }
        
        self.valid_short_skills = {
            'c++', 'c#', '.net', 'php', 'ios', 'api', 'css', 'aws', 'gcp',
            'sql', 'r&d', 'ui', 'ux', 'qa'
        }
        self.tech_skills_patterns = {
            'programming': [
                r'python|java|javascript|typescript|c\+\+|ruby|php|swift|kotlin|rust',
                r'html|css|sql|nosql|golang|scala|perl|shell|bash|powershell',
                r'react|angular|vue|node\.js|express|django|flask|spring|laravel',
                r'tensorflow|pytorch|scikit-learn|pandas|numpy|matplotlib'
            ],
            'databases': [
                r'mysql|postgresql|mongodb|redis|elasticsearch|cassandra|oracle|sql server',
                r'dynamodb|firebase|neo4j|graphql|mariadb|sqlite'
            ],
            'cloud': [
                r'aws|azure|gcp|docker|kubernetes|terraform|jenkins|circleci|gitlab',
                r'cloud computing|devops|ci/cd|containerization|microservices'
            ],
            'tools': [
                r'git|jira|confluence|bitbucket|maven|gradle|npm|yarn|webpack|babel',
                r'visual studio|intellij|eclipse|postman|swagger|junit|selenium'
            ]
        }
        self.soft_skills_patterns = [
            r'leadership|communication|teamwork|problem.solving|analytical|critical.thinking',
            r'project.management|time.management|agile|scrum|collaboration|presentation',
            r'negotiation|stakeholder.management|strategic.thinking|decision.making'
        ]
        
        # Enhanced section detection patterns
        self.section_patterns = {
            'summary': {
                'headers': [
                    r'(?i)^(?:professional\s+)?summary$',
                    r'(?i)^profile$',
                    r'(?i)^objective$',
                    r'(?i)^about\s+me$'
                ],
                'indicators': [
                    r'(?i)years of experience',
                    r'(?i)professional with expertise',
                    r'(?i)seeking a position'
                ]
            },
            'experience': {
                'headers': [
                    r'(?i)^(?:work\s+)?experience$',
                    r'(?i)^employment(?:\s+history)?$',
                    r'(?i)^professional\s+background$'
                ],
                'indicators': [
                    r'(?i)\d{4}\s*[-–]\s*(?:\d{4}|present)',
                    r'(?i)^[A-Z][a-zA-Z\s]+\s*[|,]\s*[A-Z][a-zA-Z\s]+$'
                ]
            },
            'education': {
                'headers': [
                    r'(?i)^education(?:al)?(?:\s+background)?$',
                    r'(?i)^academic\s+qualifications?$',
                    r'(?i)^degrees?$'
                ],
                'indicators': [
                    r'(?i)bachelor|master|phd|degree|university|college',
                    r'(?i)graduated|major|minor'
                ]
            },
            'skills': {
                'headers': [
                    r'(?i)^(?:technical\s+)?skills$',
                    r'(?i)^competencies$',
                    r'(?i)^expertise$'
                ],
                'indicators': [
                    r'(?i)proficient in',
                    r'(?i)experience with',
                    r'(?i)knowledge of'
                ]
            }
        }

        # Pre-compile regular expressions for better performance
        self.skills_pattern = re.compile(r'your_pattern_here', re.IGNORECASE)
        self.education_pattern = re.compile(r'your_pattern_here', re.IGNORECASE)
        
        # Cache for expensive operations
        self.cache_size = cache_size
        self._section_pattern_cache = OrderedDict()  # Use OrderedDict for LRU cache
        self._skill_confidence_cache = OrderedDict()

    # Group 1: File and Text Processing
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from a PDF resume with better handling"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
            
            # Clean the extracted text
            text = self.clean_extracted_text(text)
            
            return text
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")

    def clean_extracted_text(self, text: str) -> str:
        """Enhanced text cleaning with comprehensive character mappings"""
        # Extended special character mappings
        replacements = {
            # Bullets and Dashes
            '\u2022': '-',  # bullet
            '\u2023': '-',  # triangular bullet
            '\u2043': '-',  # hyphen bullet
            '\u2012': '-',  # figure dash
            '\u2013': '-',  # en dash
            '\u2014': '-',  # em dash
            '\u2015': '-',  # horizontal bar
            '\u2053': '-',  # swung dash
            '\u2043': '-',  # hyphen bullet
            
            # Quotes and Apostrophes
            '\u2018': "'",  # left single quotation
            '\u2019': "'",  # right single quotation
            '\u201C': '"',  # left double quotation
            '\u201D': '"',  # right double quotation
            '\u2032': "'",  # prime
            '\u2033': '"',  # double prime
            
            # Spaces and Breaks
            '\u00A0': ' ',  # non-breaking space
            '\u200B': '',   # zero-width space
            '\u200C': '',   # zero-width non-joiner
            '\u200D': '',   # zero-width joiner
            '\u2028': '\n', # line separator
            '\u2029': '\n', # paragraph separator
            
            # Symbols
            '\u2022': '•',  # bullet
            '\u2023': '•',  # triangular bullet
            '\u25CF': '•',  # black circle
            '\u25CB': '○',  # white circle
            '\u25AA': '▪',  # black small square
            '\u25AB': '▫',  # white small square
            '\u2212': '-',  # minus sign
            
            # Common PDF artifacts
            '\uf0b7': '-',  # PDF bullet
            '\uf0a7': '-',  # PDF bullet variant
            '\uf0d8': '-',  # PDF up arrow
            '\uf0d9': '-',  # PDF left arrow
            '\uf0da': '-',  # PDF right arrow
            
            # Typography
            '\u2026': '...',  # horizontal ellipsis
            '\u2122': '(TM)',  # trade mark sign
            '\u00AE': '(R)',   # registered sign
            '\u00A9': '(C)',   # copyright sign
            
            # Currency
            '\u20AC': 'EUR',  # euro
            '\u00A3': 'GBP',  # pound
            '\u00A5': 'JPY',  # yen
            '\u20B9': 'INR',  # rupee
        }
        
        # Apply replacements
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text

    def preprocess_text(self, text: str) -> str:
        """Enhanced text preprocessing"""
        # Clean special characters first
        text = self.clean_extracted_text(text)
        
        # Advanced date normalization
        date_patterns = {
            r'(jan|january|Jan|January)': '01',
            r'(feb|february|Feb|February)': '02',
            r'(mar|march|Mar|March)': '03',
            r'(apr|april|Apr|April)': '04',
            r'(may|May)': '05',
            r'(jun|june|Jun|June)': '06',
            r'(jul|july|Jul|July)': '07',
            r'(aug|august|Aug|August)': '08',
            r'(sep|september|Sep|September)': '09',
            r'(oct|october|Oct|October)': '10',
            r'(nov|november|Nov|November)': '11',
            r'(dec|december|Dec|December)': '12'
        }
        
        for pattern, replacement in date_patterns.items():
            text = re.sub(pattern, replacement, text)
        
        # Normalize education degrees
        degree_patterns = {
            r'b\.?tech\.?': 'Bachelor of Technology',
            r'm\.?tech\.?': 'Master of Technology',
            r'b\.?e\.?': 'Bachelor of Engineering',
            r'm\.?e\.?': 'Master of Engineering',
            r'b\.?sc\.?': 'Bachelor of Science',
            r'm\.?sc\.?': 'Master of Science',
            r'ph\.?d\.?': 'Doctor of Philosophy',
            r'mba': 'Master of Business Administration'
        }
        
        for pattern, replacement in degree_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Normalize job titles
        title_patterns = {
            r'sr\.?\s*': 'Senior ',
            r'jr\.?\s*': 'Junior ',
            r'mgr\.?\s*': 'Manager ',
            r'dir\.?\s*': 'Director ',
            r'exec\.?\s*': 'Executive ',
            r'asst\.?\s*': 'Assistant ',
            r'assoc\.?\s*': 'Associate '
        }
        
        for pattern, replacement in title_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newline
        text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)  # Trim lines
        
        return text.strip()

    # Group 2: Section Processing
    def extract_sections(self, text: str) -> Dict:
        """Enhanced section extraction with better text processing"""
        # Preprocess text first
        text = self.preprocess_text(text)
        sections = {
            'education': [],
            'experience': [],
            'skills': set(),
            'summary': '',
            'projects': [],
            'certifications': []
        }
        
        # Debug log
        self._log("Starting section extraction")
        
        # Split text into lines for processing
        lines = text.split('\n')
        current_section = None
        in_skills_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Debug log
            self._log(f"Processing line: {line[:50]}...")
            
            # Check for section headers
            for section, pattern in self.section_patterns.items():
                if re.search(pattern['headers'][0], line, re.I):
                    current_section = section
                    if section == 'skills':
                        in_skills_section = True
                    else:
                        in_skills_section = False
                    self._log(f"Found section header: {section}")
                    break
            
            # Process line based on current section
            if current_section:
                if current_section == 'summary':
                    sections['summary'] += ' ' + line
                elif current_section == 'skills' or in_skills_section:
                    # Extract skills using pattern matching
                    self._extract_skills(line, sections['skills'])
                    # Also store the raw line for debugging
                    if not line.lower().startswith(('skill', 'technical', 'competencies')):
                        sections['skills'].add(line.strip('•-→⚫⚪▪▫■□●○').strip())
                else:
                    sections[current_section].append(line)
        
        # Additional skill extraction from entire text
        # Split text into chunks and look for skills
        chunks = text.split()
        for i in range(len(chunks)):
            chunk = ' '.join(chunks[max(0, i-2):min(len(chunks), i+3)])  # Context window
            self._extract_skills(chunk, sections['skills'])
        
        # Debug log final results
        self._log(f"Final extracted sections: {sections}")
        
        return sections

    def detect_sections(self, text: str) -> Dict[str, Dict]:
        """Enhanced section detection with confidence scores and caching"""
        # Check if we've already processed this text
        cache_key = hash(text)
        if cache_key in self._section_pattern_cache:
            return self._section_pattern_cache[cache_key]
        
        sections = {}
        lines = text.split('\n')
        current_section = None
        section_content = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            for section, patterns in self.section_patterns.items():
                # Check header patterns
                header_match = any(re.match(pattern, line) for pattern in patterns['headers'])
                # Check indicators
                indicator_match = any(re.search(pattern, line) for pattern in patterns['indicators'])
                
                if header_match or indicator_match:
                    # Save previous section if exists
                    if current_section:
                        sections[current_section] = {
                            'content': '\n'.join(section_content),
                            'start_line': section_start,
                            'end_line': i,
                            'confidence': self._calculate_section_confidence(
                                current_section, '\n'.join(section_content)
                            )
                        }
                    
                    current_section = section
                    section_content = []
                    section_start = i
                    break
            
            if current_section:
                section_content.append(line)
        
        # Save last section
        if current_section and section_content:
            sections[current_section] = {
                'content': '\n'.join(section_content),
                'start_line': section_start,
                'end_line': len(lines),
                'confidence': self._calculate_section_confidence(
                    current_section, '\n'.join(section_content)
                )
            }
        
        # Cache the result before returning
        self._section_pattern_cache[cache_key] = sections
        return sections

    # Group 3: Skills Analysis
    def _extract_skills_pattern(self, text: str) -> Set[str]:
        """Extract skills from text using regex patterns with enhanced patterns"""
        skills = set()
        
        # Common technical skills patterns - expanded list
        tech_patterns = [
            # Programming languages
            r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Ruby|PHP|Swift|Kotlin|R|Scala|Go|Rust|Perl|Shell|Bash|PowerShell|SQL|HTML|CSS|XML|JSON|YAML)\b',
            
            # Frameworks and libraries
            r'\b(React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|Laravel|ASP\.NET|Ruby on Rails|TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy|Matplotlib|Seaborn|Bootstrap|jQuery|D3\.js)\b',
            
            # Databases
            r'\b(MySQL|PostgreSQL|MongoDB|SQLite|Oracle|SQL Server|Redis|Cassandra|DynamoDB|Firebase|Elasticsearch|Neo4j)\b',
            
            # Cloud and DevOps
            r'\b(AWS|Azure|GCP|Docker|Kubernetes|Jenkins|GitLab CI|GitHub Actions|Terraform|Ansible|Puppet|Chef|Prometheus|Grafana|ELK Stack)\b',
            
            # Tools and platforms
            r'\b(Git|SVN|Jira|Confluence|Trello|Slack|Microsoft Office|Google Workspace|Figma|Sketch|Adobe|Photoshop|Illustrator|InDesign|Premiere|After Effects)\b',
            
            # Concepts and methodologies
            r'\b(Agile|Scrum|Kanban|DevOps|CI/CD|TDD|BDD|OOP|Functional Programming|Microservices|RESTful API|GraphQL|SOAP|Machine Learning|Deep Learning|NLP|Computer Vision|Data Science|Big Data|Blockchain)\b',
            
            # Soft skills - common in resumes
            r'\b(Leadership|Communication|Teamwork|Problem Solving|Critical Thinking|Time Management|Project Management|Creativity|Adaptability|Collaboration|Presentation|Negotiation|Conflict Resolution)\b'
        ]
        
        # Extract skills using patterns
        print("\n--- SKILLS EXTRACTION USING PATTERN MATCHING ---")
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                print(f"Pattern matches: {matches}")
                skills.update([match.lower() for match in matches])
        
        # Look for skills in context (e.g., "proficient in X", "experience with Y")
        context_patterns = [
            r'(?:proficient|skilled|experienced|expertise|knowledge|familiar)\s+(?:in|with|of)\s+([A-Za-z0-9\+\#\.\s]+?)(?:,|\.|and|;|\n)',
            r'(?:worked|experience|using)\s+(?:with|in)\s+([A-Za-z0-9\+\#\.\s]+?)(?:,|\.|and|;|\n)',
            r'(?:knowledge|understanding)\s+of\s+([A-Za-z0-9\+\#\.\s]+?)(?:,|\.|and|;|\n)'
        ]
        
        for pattern in context_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Split by common separators and clean up
                potential_skills = re.split(r',|\sand\s|;|\s+', match)
                for skill in potential_skills:
                    skill = skill.strip().lower()
                    if skill and len(skill) > 2 and skill not in ['and', 'the', 'in', 'with', 'of', 'for', 'to', 'on', 'at']:
                        skills.add(skill)
                        print(f"Context pattern match: {skill}")
        
        # Print final results
        print(f"Total skills found: {len(skills)}")
        print(f"Skills: {skills}")
        print("-------------------------------------------\n")
        
        return skills

    def _extract_skills(self, text: str, skills_set: set) -> None:
        """Extract skills from text using pattern matching"""
        text = text.lower()
        self._log(f"Extracting skills from text: {text[:100]}...")  # Log first 100 chars
        
        # Check for skills in each category
        for category, skill_list in self.tech_skills_patterns.items():
            for skill in skill_list:
                if skill in text:
                    skills_set.add(skill)
                    self._log(f"Found skill: {skill} in category: {category}")
        
        self._log(f"Current skills set: {skills_set}")

    def extract_skills_with_context(self, text: str) -> Dict[str, List[Dict]]:
        """Enhanced skill extraction with context"""
        skills = {category: [] for category in self.tech_skills_patterns.keys()}
        
        # Process text line by line
        lines = text.split('\n')
        for i, line in enumerate(lines):
            # Get context (previous and next lines)
            context_before = lines[i-1] if i > 0 else ""
            context_after = lines[i+1] if i < len(lines)-1 else ""
            
            for category, skill_list in self.tech_skills_patterns.items():
                # Check patterns
                for pattern in skill_list:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        skill = match.group(0)
                        skills[category].append({
                            'skill': skill,
                            'context': {
                                'line': line.strip(),
                                'before': context_before.strip(),
                                'after': context_after.strip()
                            },
                            'confidence': self._calculate_skill_confidence(skill, line, category)
                        })
        
        return skills

    def _calculate_skill_confidence(self, skill: str, context: str, category: str) -> float:
        """Calculate confidence score for a skill with caching and optimization"""
        # Create a cache key from the input parameters
        cache_key = (skill, hash(context), category)
        if hasattr(self, '_skill_confidence_cache') and cache_key in self._skill_confidence_cache:
            return self._skill_confidence_cache[cache_key]
        
        # Base confidence based on skill category
        confidence = 0.5
        if category == "technical":
            confidence = 0.7
        elif category == "soft":
            confidence = 0.4
        
        # Context indicators (using pre-compiled patterns for efficiency)
        context_indicators = {
            'strong': [
                re.compile(r'proficient\s+in', re.IGNORECASE),
                re.compile(r'expert\s+in', re.IGNORECASE),
                # More patterns...
            ],
            'medium': [
                re.compile(r'experience\s+with', re.IGNORECASE),
                re.compile(r'knowledge\s+of', re.IGNORECASE),
                # More patterns...
            ],
            'weak': [
                re.compile(r'familiar\s+with', re.IGNORECASE),
                re.compile(r'basic\s+understanding', re.IGNORECASE),
                # More patterns...
            ]
        }
        
        # Check indicators using more efficient pre-compiled patterns
        for indicator in context_indicators['strong']:
            if indicator.search(context):
                confidence += 0.2
                break
        
        for indicator in context_indicators['medium']:
            if indicator.search(context):
                confidence += 0.1
                break
        
        for indicator in context_indicators['weak']:
            if indicator.search(context):
                confidence -= 0.1
                break
        
        result = min(1.0, max(0.0, confidence))
        
        # Cache the result
        if not hasattr(self, '_skill_confidence_cache'):
            self._skill_confidence_cache = OrderedDict()
        self._skill_confidence_cache[cache_key] = result
        
        return result

    # Group 4: Education Analysis
    def _extract_education_pattern(self, text: str) -> List[str]:
        """Extract education information using pattern matching"""
        education = []
        lines = text.split('\n')
        in_education_section = False
        
        education_keywords = [
            r'bachelor|master|phd|degree|diploma|certification',
            r'university|college|institute|school',
            r'graduated|major|minor'
        ]
        
        for line in lines:
            # Check if we're entering education section
            if re.search(r'(?i)^education|academic|qualifications?$', line):
                in_education_section = True
                continue
            
            # Check if we're leaving education section
            if in_education_section and re.search(r'(?i)^(experience|skills|projects)', line):
                in_education_section = False
                continue
            
            # Extract education details
            if in_education_section or any(re.search(pattern, line, re.IGNORECASE) for pattern in education_keywords):
                if len(line.strip()) > 10:  # Avoid short lines
                    education.append(line.strip())
        
        return education

    # Group 5: Validation Methods
    def _validate_skills(self, skills: Set[str]) -> Set[str]:
        """Validate and clean skills"""
        validated = set()
        for skill in skills:
            skill = skill.strip().lower()
            if (
                len(skill) > 2 and  # Longer than 2 characters
                skill not in self.invalid_skills and  # Not in invalid list
                not skill.isnumeric() and  # Not just numbers
                not all(c.isdigit() or c.isspace() for c in skill)  # Not just digits and spaces
            ):
                validated.add(skill)
        return validated

    def validate_sections(self, sections: Dict) -> List[str]:
        """Validate extracted sections and return warnings"""
        warnings = []
        
        # Check for empty or missing sections
        if not sections['summary'].strip():
            warnings.append("No professional summary found")
        
        if not sections['skills']:
            warnings.append("No skills were extracted")
        
        if not sections['experience']:
            warnings.append("No work experience entries found")
        
        if not sections['education']:
            warnings.append("No education details found")
        
        # Validate content length and quality
        if len(sections['summary'].split()) < 10:
            warnings.append("Professional summary seems too short")
        
        if len(sections['skills']) < 5:
            warnings.append("Limited number of skills detected")
        
        # Check for potential data quality issues
        for exp in sections['experience']:
            if len(exp.split()) < 5:
                warnings.append(f"Short work experience entry found: '{exp}'")
        
        return warnings

    def validate_extracted_text(self, text: str) -> Dict[str, any]:
        """Enhanced validation with detailed reporting"""
        validation_report = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "stats": {
                "total_length": len(text),
                "word_count": len(text.split()),
                "line_count": len(text.splitlines()),
                "special_chars_found": set()
            }
        }
        
        try:
            if not text:
                validation_report["is_valid"] = False
                validation_report["errors"].append("No text was extracted from the resume")
                raise ValueError("Empty text content")
            
            # Content length checks
            if len(text.split()) < 50:
                validation_report["is_valid"] = False
                validation_report["errors"].append(
                    f"Text content too short: {len(text.split())} words (minimum 50 required)"
                )
            
            # Section identification check
            required_sections = ['education', 'experience', 'skills']
            found_sections = []
            for section in required_sections:
                if re.search(self.section_patterns[section]['headers'][0], text, re.I):
                    found_sections.append(section)
            
            missing_sections = set(required_sections) - set(found_sections)
            if missing_sections:
                validation_report["warnings"].append(
                    f"Missing sections: {', '.join(missing_sections)}"
                )
            
            # Check for potential formatting issues
            if text.count('\n\n\n') > 5:
                validation_report["warnings"].append(
                    "Multiple excessive line breaks detected - possible formatting issues"
                )
            
            # Identify special characters
            special_chars = set(char for char in text if not char.isascii())
            if special_chars:
                validation_report["stats"]["special_chars_found"] = special_chars
                validation_report["warnings"].append(
                    f"Special characters found: {', '.join(special_chars)}"
                )
            
            return validation_report
            
        except Exception as e:
            validation_report["is_valid"] = False
            validation_report["errors"].append(str(e))
            return validation_report

    def analyze_resume(self, text: str) -> Dict[str, Any]:
        """Analyze resume text and extract structured information"""
        try:
            # Get pattern-based analysis results
            pattern_results = self._pattern_based_analysis(text)
            
            # Only use LLM for current role if pattern matching didn't find it
            if not pattern_results.get("current_role"):
                # Use a simplified LLM prompt just for current role
                current_role = self._extract_current_role_llm(text)
                if current_role:
                    pattern_results["current_role"] = current_role
            
            # Skip full LLM analysis to save costs
            return pattern_results
        except Exception as e:
            self._log(f"Resume analysis error: {str(e)}")
            return {"error": str(e)}

    def _extract_current_role_llm(self, text: str) -> str:
        """Extract current role using LLM with a minimal prompt"""
        try:
            prompt = f"""
            From the following resume text, extract ONLY the person's current or most recent job role/title.
            Return just the role title without any additional text.

            Resume:
            {text}
            """
            
            response = self._llm_client.generate_text(prompt)
            # Clean up the response to get just the role
            role = response.strip()
            
            print(f"LLM Extracted Current Role: {role}")
            return role
        except Exception as e:
            self._log(f"LLM current role extraction error: {str(e)}")
            return ""

    def _pattern_based_analysis(self, text: str) -> Dict[str, Any]:
        """Pattern-based analysis with enhanced reliability"""
        try:
            results = {
                "current_role": self._extract_current_role(text),
                "experience": self._extract_experience(text),
                "skills": self._extract_skills_pattern(text),
                "education": self._extract_education_pattern(text),
                "confidence": "pattern"
            }
            
            # Print the results to the console
            print("Pattern Matching Results:")
            print(f"Current Role: {results['current_role']}")
            print(f"Experience: {results['experience']}")
            print(f"Skills: {results['skills']}")
            print(f"Education: {results['education']}")
            
            return results
        except Exception as e:
            self._log(f"Pattern analysis error: {str(e)}")
            return {"confidence": "pattern", "error": str(e)}

    def _llm_based_analysis(self, text: str) -> Dict[str, Any]:
        """LLM-based analysis with structured output"""
        try:
            prompt = f"""
            Analyze the following resume text and extract key information in a structured format:

            {text}

            Please provide the following information in a structured format:
            1. Current Role: [Most recent/current position]
            2. Years of Experience: [Total years of professional experience]
            3. Skills: [List of technical and soft skills, excluding single letters or common words]
            4. Education: [List of educational qualifications]
            5. Professional Summary: [Brief professional summary]

            Format the response as:
            CURRENT_ROLE: [role]
            EXPERIENCE: [years]
            SKILLS: [skill1, skill2, ...]
            EDUCATION: [edu1, edu2, ...]
            SUMMARY: [summary]
            """

            response = self.llm.invoke(prompt).content
            parsed_results = self._parse_llm_response(response)
            parsed_results["confidence"] = "llm"
            return parsed_results
        except Exception as e:
            self._log(f"LLM analysis error: {str(e)}")
            return {"confidence": "llm", "error": str(e)}

    def _combine_analyses(self, pattern_results: Dict, llm_results: Dict) -> Dict:
        """Combine and validate results from both analyses"""
        combined = {
            "current_role": "",
            "experience": "",
            "skills": set(),
            "education": [],
            "professional_summary": "",
            "confidence_scores": {}
        }

        # Combine current role
        if pattern_results.get("current_role") and llm_results.get("current_role"):
            # Use the longer, more detailed role description
            combined["current_role"] = max(
                [pattern_results["current_role"], llm_results["current_role"]], 
                key=len
            )
            combined["confidence_scores"]["current_role"] = "high"
        else:
            # Use whatever is available
            combined["current_role"] = pattern_results.get("current_role") or llm_results.get("current_role")
            combined["confidence_scores"]["current_role"] = "medium"

        # Combine experience
        pattern_exp = self._normalize_experience(pattern_results.get("experience", ""))
        llm_exp = self._normalize_experience(llm_results.get("experience", ""))
        if pattern_exp and llm_exp:
            # Use the average if both are available
            combined["experience"] = str(round((float(pattern_exp) + float(llm_exp)) / 2))
            combined["confidence_scores"]["experience"] = "high"
        else:
            combined["experience"] = pattern_exp or llm_exp
            combined["confidence_scores"]["experience"] = "medium"

        # Combine and validate skills
        pattern_skills = set(pattern_results.get("skills", []))
        llm_skills = set(llm_results.get("skills", []))
        
        # Skills that appear in both analyses have higher confidence
        high_confidence_skills = pattern_skills.intersection(llm_skills)
        medium_confidence_skills = pattern_skills.union(llm_skills) - high_confidence_skills
        
        # Filter out invalid skills
        validated_skills = self._validate_skills(high_confidence_skills.union(medium_confidence_skills))
        combined["skills"] = validated_skills
        combined["confidence_scores"]["skills"] = {
            skill: "high" if skill in high_confidence_skills else "medium"
            for skill in validated_skills
        }

        # Combine education
        combined["education"] = list(set(
            pattern_results.get("education", []) + 
            llm_results.get("education", [])
        ))
        
        # Use LLM summary if available, otherwise generate from pattern results
        combined["professional_summary"] = (
            llm_results.get("professional_summary") or 
            self._generate_summary(pattern_results)
        )

        return combined

    def _normalize_experience(self, exp: str) -> str:
        """Normalize experience to years"""
        try:
            # Extract numbers from string
            numbers = re.findall(r'\d+', str(exp))
            if numbers:
                return numbers[0]
            return ""
        except:
            return ""

    def _get_best_available_results(self, pattern_results: Dict, llm_results: Dict) -> Dict:
        """Return best available results if either analysis fails"""
        if not pattern_results.get("error") and pattern_results.get("confidence") == "pattern":
            return pattern_results
        if not llm_results.get("error") and llm_results.get("confidence") == "llm":
            return llm_results
            
        # If both have errors, combine whatever data is available
        combined = {}
        for key in ["current_role", "experience", "skills", "education", "professional_summary"]:
            combined[key] = pattern_results.get(key) or llm_results.get(key) or ""
        return combined

    def _format_experience(self, experience_lines: List[str]) -> List[Dict]:
        """Format experience data into structured format"""
        formatted_experience = []
        current_entry = {}
        
        for line in experience_lines:
            # Check for date pattern (e.g., "2020 - Present" or "Jan 2020 - Dec 2023")
            date_match = re.search(r'(?i)(\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\s*[-–]\s*(\d{4}|Present)', line)
            
            if date_match:
                # If we have a previous entry, save it
                if current_entry:
                    formatted_experience.append(current_entry)
                
                # Start new entry
                current_entry = {
                    'dates': line.strip(),
                    'title': '',
                    'company': '',
                    'description': []
                }
            elif current_entry:
                # If we're in an entry, check for title/company pattern
                title_company_match = re.search(r'^([A-Z][a-zA-Z\s]+)\s*[|,]\s*([A-Z][a-zA-Z\s]+)$', line)
                if title_company_match:
                    current_entry['title'] = title_company_match.group(1).strip()
                    current_entry['company'] = title_company_match.group(2).strip()
                else:
                    # Add to description if not empty
                    if line.strip():
                        current_entry['description'].append(line.strip())
        
        # Add the last entry if exists
        if current_entry:
            formatted_experience.append(current_entry)
        
        return formatted_experience

    def process_resume(self, file_path: str) -> Dict:
        """Process resume and return structured data"""
        try:
            # Extract text from PDF
            text = self.extract_text_from_pdf(file_path)
            
            # Extract sections
            sections = self.extract_sections(text)
            
            # Format experience data
            formatted_experience = self._format_experience(sections.get('experience', []))
            
            # Extract skills with context
            skills_with_context = self.extract_skills_with_context(text)
            
            # Calculate total years of experience
            total_years = 0
            for entry in formatted_experience:
                dates = entry.get('dates', '')
                if dates:
                    # Extract years from date range
                    years = re.findall(r'\d{4}', dates)
                    if len(years) >= 2:
                        total_years += int(years[1]) - int(years[0])
            
            # Create structured data
            structured_data = {
                'user_role': self._extract_current_role(sections.get('experience', [])),
                'work_experience': formatted_experience,
                'total_years_experience': total_years,
                'skills': [
                    {'name': skill['skill'], 'category': category}
                    for category, skills in skills_with_context.items()
                    for skill in skills
                ],
                'education': sections.get('education', []),
                'projects': sections.get('projects', []),
                'certifications': sections.get('certifications', [])
            }
            
            # Generate feedback
            feedback = self._generate_feedback(structured_data)
            
            return {
                'structured_data': structured_data,
                'feedback': feedback
            }
            
        except Exception as e:
            self._log(f"Error processing resume: {str(e)}")
            raise

    def analyze_sections(self, sections: Dict) -> Dict:
        """Enhanced LLM analysis with more specific prompts"""
        try:
            prompt = f"""
            Analyze the following resume sections and provide detailed insights:
            
            PROFESSIONAL SUMMARY:
            {sections['summary']}
            
            WORK EXPERIENCE:
            {' | '.join(sections['experience'])}
            
            EDUCATION:
            {' | '.join(sections['education'])}
            
            SKILLS:
            {', '.join(sections['skills'])}
            
            Please provide a structured analysis in the following format:
            
            PROFESSIONAL_SUMMARY:
            [Write a compelling 2-3 sentence summary highlighting key experience, skills, and career trajectory]
            
            KEY_STRENGTHS:
            - [Strength 1: Specific example from experience]
            - [Strength 2: Specific example from experience]
            - [Strength 3: Technical expertise demonstration]
            
            CAREER_PROGRESSION:
            - [Analysis of career growth and progression]
            - [Pattern in role changes and responsibilities]
            
            TECHNICAL_ASSESSMENT:
            - [Evaluation of technical skills relevance]
            - [Identification of skill gaps]
            - [Technology stack analysis]
            
            AREAS_FOR_IMPROVEMENT:
            - [Specific improvement 1 with actionable suggestion]
            - [Specific improvement 2 with actionable suggestion]
            - [Skill gap closure recommendation]
            
            RECOMMENDATIONS:
            - [Career development suggestion 1]
            - [Skill enhancement priority 1]
            - [Industry-specific recommendation]
            """
            
            response = self.llm.invoke(prompt).content
            
            # Enhanced response parsing
            analysis = {
                "summary": "",
                "strengths": [],
                "career_progression": [],
                "technical_assessment": [],
                "improvements": [],
                "recommendations": []
            }
            
            current_section = None
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Enhanced section matching
                section_matches = {
                    "PROFESSIONAL_SUMMARY": "summary",
                    "KEY_STRENGTHS": "strengths",
                    "CAREER_PROGRESSION": "career_progression",
                    "TECHNICAL_ASSESSMENT": "technical_assessment",
                    "AREAS_FOR_IMPROVEMENT": "improvements",
                    "RECOMMENDATIONS": "recommendations"
                }
                
                for marker, section in section_matches.items():
                    if marker in line:
                        current_section = section
                        break
                
                if current_section and not any(marker in line for marker in section_matches):
                    if current_section == "summary":
                        analysis["summary"] += line + " "
                    else:
                        analysis[current_section].append(line.lstrip('- '))
            
            return analysis
            
        except Exception as e:
            self._log(f"Error in LLM analysis: {str(e)}")
            return {}

    def _calculate_section_confidence(self, section: str, content: str) -> float:
        """Calculate confidence score for section detection"""
        confidence = 0.5  # Base confidence
        
        # Check for section-specific indicators
        indicators = self.section_patterns[section]['indicators']
        indicator_matches = sum(1 for indicator in indicators if re.search(indicator, content, re.IGNORECASE))
        confidence += 0.1 * indicator_matches
        
        # Check content length
        words = len(content.split())
        if words > 50:
            confidence += 0.2

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse structured response from LLM"""
        parsed = {
            "current_role": "",
            "experience": "",
            "skills": set(),
            "education": [],
            "professional_summary": ""
        }
        
        current_section = None
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if line.startswith('CURRENT_ROLE:'):
                current_section = "current_role"
                parsed["current_role"] = line.replace('CURRENT_ROLE:', '').strip()
            elif line.startswith('EXPERIENCE:'):
                current_section = "experience"
                parsed["experience"] = line.replace('EXPERIENCE:', '').strip()
            elif line.startswith('SKILLS:'):
                current_section = "skills"
                skills = line.replace('SKILLS:', '').strip()
                parsed["skills"] = {s.strip() for s in skills.split(',') if s.strip()}
            elif line.startswith('EDUCATION:'):
                current_section = "education"
                education = line.replace('EDUCATION:', '').strip()
                parsed["education"] = [e.strip() for e in education.split(',') if e.strip()]
            elif line.startswith('SUMMARY:'):
                current_section = "professional_summary"
                parsed["professional_summary"] = line.replace('SUMMARY:', '').strip()
            elif current_section == "professional_summary":
                parsed["professional_summary"] += " " + line
        
        return parsed

    def _manage_cache_size(self, cache_dict):
        """Keep cache size under control"""
        while len(cache_dict) > self.cache_size:
            cache_dict.popitem(last=False)  # Remove oldest item (LRU)

    def _extract_current_role(self, text: str) -> str:
        """Extract the current role from resume text"""
        # Common patterns for current role
        patterns = [
            r'(?:currently|presently|now)\s+(?:working\s+as|employed\s+as|serving\s+as)\s+(?:an?\s+)?([^,.\n]+)',
            r'([^,\n]*?(?:engineer|developer|analyst|manager|designer|consultant|specialist|director|lead|architect))[^,\n]*?\s+(?:at\s+[^,\n]+)?\s*(?:\(|\s)?(?:\d{4}|present)',
            r'^([^,\n]*?)(?:\sat\s|\sin\s|\s-\s)([^,\n]*?)(?:present|current|now)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no match found, try to find the most recent job title
        lines = text.split('\n')
        for line in lines:
            if re.search(r'\b\d{4}\s*-\s*(?:present|current|now)\b', line, re.IGNORECASE):
                # Extract the job title from this line
                title_match = re.search(r'^([^,\n]*?)(?:\sat\s|\sin\s|\s-\s)', line, re.IGNORECASE)
                if title_match:
                    return title_match.group(1).strip()
        
        return ""

    def _extract_experience(self, text: str) -> str:
        """Extract years of experience from resume text"""
        # Common patterns for years of experience
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:of\s+)?(?:work\s+)?experience',
            r'(?:experience|working)\s+since\s+(\d{4})',
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:in|at|with)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if pattern.endswith('(\d{4})'):
                    # Calculate years from year mentioned
                    import datetime
                    years = datetime.datetime.now().year - int(match.group(1))
                    return str(years)
                else:
                    return match.group(1)
        
        return ""