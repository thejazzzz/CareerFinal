
---

# **Career Assistant Multi-Agent System (MAS)**  

## **Overview**  
The **Career Assistant MAS** is an **AI-powered system** that helps users navigate their career journey by analyzing their resumes, finding job opportunities, suggesting skill improvements, preparing for interviews, and optimizing resumes and cover letters. The system consists of **multiple AI agents** using **CrewAI**, integrated into an interactive **Streamlit-based frontend**, leveraging **OpenAI’s GPT models** for NLP and **Adzuna API** for job search.  

## **Technologies Used**  
- **Python** (Primary backend language)  
- **Streamlit** (Frontend framework for UI)  
- **CrewAI** (Multi-agent system framework)  
- **OpenAI API** (NLP and language model capabilities)  
- **Adzuna API** (Job search integration)  
- **LangChain** (Agent reasoning and tool integration)  
- **PostgreSQL / Firebase** (Database for user data storage)  
- **Docker & Cloud Deployment** (For production readiness)  

---

## **System Architecture & Agents**  

The system consists of **10 AI Agents**, each handling a specific career-related task. They are implemented using **CrewAI**, leveraging OpenAI’s GPT models.  

### **1. Resume Analyzer Agent**  
**Function:** Extracts key details (skills, experience, education) from the user's uploaded resume.  

```python
import streamlit as st
import openai
import pdfplumber

openai.api_key = "YOUR_OPENAI_API_KEY"

def extract_resume_text(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def analyze_resume(text):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "Extract skills, experience, and education from the following resume:\n" + text}]
    )
    return response["choices"][0]["message"]["content"]

st.title("Resume Analyzer")
uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
if uploaded_file:
    resume_text = extract_resume_text(uploaded_file)
    analysis = analyze_resume(resume_text)
    st.write("### Extracted Details:", analysis)
```

---

### **2. Job Search Agent**  
**Function:** Uses **Adzuna API** to find job opportunities based on extracted resume details.  

```python
import requests
import json
import os

class JobSearchAgent:
    def search_jobs(self, role, location, num_results=5):
        app_id = os.getenv('ADZUNA_APP_ID')
        api_key = os.getenv('ADZUNA_API_KEY')
        url = f"http://api.adzuna.com/v1/api/jobs/us/search/1?app_id={app_id}&app_key={api_key}&results_per_page={num_results}&what={role}&where={location}&content-type=application/json"

        response = requests.get(url)
        jobs_data = response.json()
        return [
            f"Title: {job['title']}, Company: {job['company']['display_name']}, Location: {job['location']['display_name']}"
            for job in jobs_data.get('results', [])
        ]
```

---

### **3. Skills Development Agent**  
**Function:** Recommends skill improvements based on job requirements.  

```python
from crewai import Agent

skills_agent = Agent(
    role="Skills Development Advisor",
    goal="Identify key skills required and suggest learning resources",
    backstory="Expert in career growth, helping users improve relevant skills.",
    llm=ChatOpenAI(model="gpt-4-turbo-preview")
)
```

---

### **4. Career Navigator Agent**  
**Function:** Builds a **personalized career path** based on current skills and goals.  

```python
career_navigator = Agent(
    role="Career Navigator",
    goal="Create a personalized career path based on user's skills and experience",
    backstory="Guides users on career progression strategies.",
    llm=ChatOpenAI(model="gpt-4-turbo-preview")
)
```

---

### **5. Interview Preparation Agent**  
**Function:** Conducts **mock interviews** and provides feedback.  

```python
interview_coach = Agent(
    role="Interview Coach",
    goal="Enhance interview skills through mock interviews and feedback",
    backstory="Expert in coaching job seekers on common questions and confidence-building.",
    llm=ChatOpenAI(model="gpt-4-turbo-preview")
)
```

---

### **6. Resume Optimization Agent**  
**Function:** Improves the **user’s resume** for better job prospects.  

```python
resume_optimizer = Agent(
    role="Resume Optimizer",
    goal="Suggest improvements to the user's resume",
    backstory="Specialist in resume enhancement and ATS-friendly formatting.",
    llm=ChatOpenAI(model="gpt-4-turbo-preview")
)
```

---

### **7. Cover Letter Generator Agent**  
**Function:** Generates **custom cover letters** for job applications.  

```python
cover_letter_agent = Agent(
    role="Cover Letter Generator",
    goal="Create tailored cover letters based on job descriptions",
    backstory="Expert in professional writing for job seekers.",
    llm=ChatOpenAI(model="gpt-4-turbo-preview")
)
```

---

### **8. Web Research Agent**  
**Function:** Finds **industry trends** and job market insights.  

```python
web_researcher = Agent(
    role="Web Researcher",
    goal="Analyze job market trends and provide insights",
    backstory="Automates data collection from various sources to keep users informed.",
    llm=ChatOpenAI(model="gpt-4-turbo-preview")
)
```

---

### **9. AI-Powered Chatbot Agent**  
**Function:** Answers **career-related queries** via **Streamlit chatbot interface**.  

```python
st.title("Career Assistant Chatbot")

def get_chatbot_response(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": user_input}]
    )
    return response["choices"][0]["message"]["content"]

user_input = st.text_input("Ask a career-related question:")
if user_input:
    response = get_chatbot_response(user_input)
    st.write(response)
```

---

## **Deployment & Production Setup**  
1. **Dockerization:**  
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

2. **Cloud Deployment (Railway, Render, or AWS):**  
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```
- Deploy using **Railway.app, Render, or AWS Lambda**.

---

## **Final Workflow Execution Using CrewAI**  
```python
from crewai import Crew, Process

career_crew = Crew(
    agents=[resume_optimizer, job_searcher_agent, skills_agent, career_navigator, interview_coach, cover_letter_agent],
    tasks=[job_search_task, skills_task, interview_task, resume_task],
    process=Process.hierarchical,
    manager_llm=ChatOpenAI(model="gpt-4-turbo-preview"),
)

crew_result = career_crew.kickoff()
print(crew_result)
```

---

## **Conclusion**  
This system **integrates multiple AI agents** to provide **a seamless career assistance experience**. It is fully modular, scalable, and can be **deployed on cloud platforms** for production use. 🚀  
