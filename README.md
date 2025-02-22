# Career Assistant Multi-Agent System

An AI-powered career development platform that combines multiple specialized agents to help users navigate their career journey effectively.

## Features

- 💬 **Career Chatbot**: Get instant answers to career-related questions
- 📝 **Resume Analyzer**: Get feedback on your resume
- 🔍 **Job Search**: Find relevant job opportunities
- 📚 **Skills Development**: Personalized learning recommendations
- 🎯 **Career Planning**: Long-term career strategy
- 🌟 **Skills Advisor**: Skill gap analysis and recommendations
- 🧭 **Career Navigator**: Career transition guidance
- 🎤 **Interview Coach**: Interview preparation and feedback
- ✉️ **Cover Letter Generator**: Create tailored cover letters

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Career-project
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
```

## Running the Application

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. Complete your profile in the sidebar of the home page

4. Navigate between different agents using the sidebar menu

## Usage

1. **Career Chatbot**:
   - Ask any career-related questions
   - Get personalized advice based on your profile
   - Access recommended resources

2. **Cover Letter Generator**:
   - Paste the job description
   - Enter company name
   - Choose letter style
   - Generate and improve your cover letter

3. **Other Agents**:
   - Each agent has its own dedicated page
   - Follow the instructions on each page
   - Use your profile information for personalized results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 