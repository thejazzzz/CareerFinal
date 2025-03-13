import streamlit as st

def apply_custom_styling():
    """Apply custom CSS styling to make the UI more modern and user-friendly"""
    
    # Custom CSS for a more polished, modern UI
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Overall page styling */
        .main {
            background-color: #ffffff;
            font-family: 'Inter', sans-serif;
        }
        
        /* Headers and typography */
        h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            color: #1a202c;
            letter-spacing: -0.5px;
        }
        
        h1, .stMarkdown h1 {
            font-size: 2.5rem;
            letter-spacing: -1px;
        }
        
        h2, .stMarkdown h2 {
            font-size: 1.75rem;
            margin-top: 1.5rem;
        }
        
        p, li, .stMarkdown p {
            font-size: 1rem;
            line-height: 1.6;
            color: #2d3748;  /* Darker text for better contrast */
        }
        
        /* Sidebar styling - ensure consistent color across all pages */
        .css-1lcbmhc.e1fqkh3o0, [data-testid="stSidebar"], .css-1d391kg, .css-1wrcr25 {
            background-color: #2d3748 !important;
            border-right: 1px solid #4a5568 !important;
        }
        
        /* Sidebar navigation links */
        .css-1wrcr25 button, .css-1wrcr25 p, .css-1wrcr25 span, 
        [data-testid="stSidebar"] button, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
        .css-1d391kg button, .css-1d391kg p, .css-1d391kg span {
            color: #e2e8f0 !important;
        }
        
        /* Active sidebar item */
        .css-1wrcr25 [data-testid="stSidebarNavLink"].css-1aehpvj, 
        [data-testid="stSidebar"] [data-testid="stSidebarNavLink"].css-1aehpvj,
        .css-1d391kg [data-testid="stSidebarNavLink"].css-1aehpvj {
            background-color: #4a5568 !important;
            color: white !important;
        }
        
        /* Form inputs */
        div[data-baseweb="input"], div[data-baseweb="textarea"] {
            border-radius: 8px;
            border: 1px solid #cbd5e0;  /* Darker border */
            transition: all 0.3s ease;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        
        div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within {
            border-color: #3182ce;  /* Darker blue for better visibility */
            box-shadow: 0 0 0 2px rgba(49,130,206,0.25);
        }
        
        /* Buttons */
        button[kind="primary"], .stButton button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(49,130,206,0.15);
            background-color: #2b6cb0;  /* Darker blue for better contrast */
            border: none;
            padding: 0.5rem 1.5rem;
            color: white;
        }
        
        button[kind="primary"]:hover, .stButton button:hover {
            background-color: #2c5282;  /* Even darker on hover */
            box-shadow: 0 4px 6px rgba(49,130,206,0.25);
            transform: translateY(-1px);
        }
        
        /* Containers and cards */
        .stContainer, .element-container, .stExpander {
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            padding: 1rem;
            margin-bottom: 1.5rem;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }
        
        .stContainer:hover, .element-container:hover {
            box-shadow: 0 8px 12px rgba(0,0,0,0.1);
        }
        
        /* File uploader */
        .uploadedFile {
            border-radius: 8px;
            border: 1px dashed #3182ce;
            background-color: rgba(49,130,206,0.05);
        }
        
        /* Progress bars and indicators */
        .stProgress > div > div {
            background-color: #3182ce;
            border-radius: 999px;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            border-radius: 12px;
            background-color: #f8fafc;
            padding: 4px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Hide Resume Analyzer from sidebar */
        [data-testid="stSidebarNavLink"][href="/Resume_Analyzer"],
        [data-testid="stSidebarNavLink"][href*="Resume_Analyzer"],
        [data-testid="stSidebarNavLink"][href*="3_"],
        [data-testid="stSidebarNavLink"][href*="resume"],
        [data-testid="stSidebarNavLink"][aria-label*="Resume"],
        [data-testid="stSidebarNavLink"][aria-label*="resume"] {
            display: none !important;
        }
        
        /* Container for the resume upload area */
        .resume-upload-container {
            background-color: #ebf8ff;  /* Light blue background for emphasis */
            border: 2px dashed #3182ce;  /* Darker blue border */
            border-radius: 12px;
            padding: 2.5rem;  /* More padding */
            text-align: center;
            transition: all 0.3s ease;
            margin-bottom: 2rem;
            margin-top: 1rem;
        }
        
        .resume-upload-container:hover {
            border-color: #2b6cb0;
            background-color: rgba(49,130,206,0.1);
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        }
        
        .resume-upload-container h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #2c5282;
        }
        
        .resume-upload-container .upload-icon {
            font-size: 2.5rem;
            color: #3182ce;
            margin-bottom: 1rem;
        }
        
        /* Custom card layouts */
        .feature-card {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            padding: 1.5rem;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .feature-card:hover {
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
            color: #3182ce;
        }
        
        /* Custom hero section */
        .hero-section {
            padding: 3rem 2rem;
            background: linear-gradient(135deg, #f8fafc 0%, #e6f7ff 100%);  /* Lighter gradient */
            border-radius: 12px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
        }
        
        /* User profile completion indicator */
        .profile-completion-indicator {
            width: 100%;
            height: 8px;
            background-color: #edf2f7;
            border-radius: 999px;
            overflow: hidden;
            margin: 1rem 0;
        }
        
        .profile-completion-indicator-fill {
            height: 100%;
            background-color: #3182ce;
            border-radius: 999px;
            transition: width 0.5s ease;
        }
        
        /* Loading spinner */
        .stSpinner > div {
            border-color: #3182ce transparent transparent transparent;
        }
        
        /* Chat bubbles */
        .chat-bubble-user {
            background-color: #e2e8f0; 
            border-radius: 12px 12px 12px 0; 
            padding: 1rem; 
            margin-bottom: 0.5rem;
            max-width: 80%;
            color: #2d3748;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            display: inline-block;
        }
        
        .chat-bubble-assistant {
            background-color: #e6f7ff; 
            border-radius: 12px 12px 0 12px; 
            padding: 1rem; 
            margin-bottom: 1rem;
            margin-left: 20%;
            max-width: 80%;
            color: #2c5282;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            display: inline-block;
        }
        
        /* Fix for some mobile-specific issues */
        @media (max-width: 768px) {
            .hero-section {
                padding: 2rem 1rem;
            }
            
            h1, .stMarkdown h1 {
                font-size: 2rem;
            }
        }
    </style>
    
    <script>
        // Function to hide Resume Analyzer from sidebar
        function hideResumeAnalyzer() {
            // Wait for the sidebar to load
            setTimeout(function() {
                // Get all sidebar links
                var sidebarLinks = document.querySelectorAll('[data-testid="stSidebarNavLink"]');
                
                // Loop through each link
                sidebarLinks.forEach(function(link) {
                    // Check if the link text contains "Resume" or "resume"
                    var linkText = link.textContent.toLowerCase();
                    if (linkText.includes('resume')) {
                        // Hide the link
                        link.style.display = 'none';
                    }
                });
            }, 1000); // Wait 1 second for the sidebar to load
        }
        
        // Run the function when the page loads
        window.addEventListener('load', hideResumeAnalyzer);
        
        // Also run it when the DOM content is loaded
        document.addEventListener('DOMContentLoaded', hideResumeAnalyzer);
    </script>
    """, unsafe_allow_html=True)

def custom_hero_section(title, subtitle, cta_text=None, cta_link=None):
    """
    Creates a modern, visually appealing hero section
    
    Args:
        title: The main headline
        subtitle: The subheadline text
        cta_text: Call to action button text (optional)
        cta_link: Link for the CTA button (optional)
    """
    
    st.markdown(f"""
    <style>
    .hero-container {{
        background: linear-gradient(135deg, #4299e1 0%, #667eea 100%);
        border-radius: 12px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }}
    .hero-title {{
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }}
    .hero-subtitle {{
        font-size: 1.25rem;
        font-weight: 400;
        margin-bottom: 2rem;
        opacity: 0.9;
    }}
    .hero-cta {{
        display: inline-block;
        background-color: white;
        color: #4299e1;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 9999px;
        text-decoration: none;
        transition: all 0.2s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    .hero-cta:hover {{
        background-color: #f7fafc;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }}
    </style>
    
    <div class="hero-container">
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle">{subtitle}</div>
        {f'<a href="{cta_link}" class="hero-cta">{cta_text}</a>' if cta_text and cta_link else ''}
    </div>
    """, unsafe_allow_html=True)

def feature_card(icon, title, description, button_text, button_link):
    """
    Creates a feature card with icon, title, description, and button
    
    Args:
        icon: Emoji or icon to display
        title: Card title
        description: Card description
        button_text: Text for the card button
        button_link: Link for the button
    
    Returns:
        HTML string for the feature card
    """
    
    return f"""
    <div style="
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">{icon}</div>
        <h3 style="margin-top: 0; margin-bottom: 0.75rem; color: #2d3748;">{title}</h3>
        <p style="color: #4a5568; margin-bottom: 1.5rem; font-size: 0.95rem;">{description}</p>
        <a href="{button_link}" style="
            display: inline-block;
            background-color: #ebf8ff;
            color: #3182ce;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            text-decoration: none;
            font-size: 0.875rem;
            transition: all 0.2s;
        ">{button_text}</a>
    </div>
    """

def resume_upload_area(file_uploader_func):
    """
    Creates an enhanced file uploader area specifically for resume files
    
    Args:
        file_uploader_func: The streamlit file_uploader function
    
    Returns:
        The uploaded file object if a file was uploaded, None otherwise
    """
    
    # Create a visually appealing upload zone
    st.markdown("""
    <style>
    .resume-upload-container {
        background-color: #ebf8ff;
        border: 2px dashed #3182ce;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
        transition: all 0.3s;
    }
    .resume-upload-container:hover {
        background-color: #bee3f8;
        border-color: #2b6cb0;
    }
    .upload-icon {
        font-size: 3rem;
        color: #3182ce;
        margin-bottom: 1rem;
    }
    .upload-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    .upload-subtitle {
        color: #4a5568;
        margin-bottom: 1.5rem;
    }
    </style>
    
    <div class="resume-upload-container">
        <div class="upload-icon">📄</div>
        <div class="upload-title">Upload Your Resume</div>
        <div class="upload-subtitle">PDF, DOCX, or TXT formats accepted</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add the actual file uploader
    uploaded_file = file_uploader_func(
        label="Upload your resume",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
        help="Upload your resume to automatically extract your skills and experience"
    )
    
    return uploaded_file

def profile_completion_indicator(completion_percentage):
    """
    Displays a visual progress indicator for profile completion
    
    Args:
        completion_percentage: Integer percentage of profile completion (0-100)
    """
    # Ensure percentage is within bounds
    completion_percentage = max(0, min(100, completion_percentage))
    
    # Determine status color based on completion percentage
    if completion_percentage < 40:
        status_color = "#f56565"  # Red
        message = "Just getting started"
    elif completion_percentage < 70:
        status_color = "#ed8936"  # Orange
        message = "Making good progress"
    else:
        status_color = "#48bb78"  # Green
        message = "Almost there!"
    
    # Display progress bar with percentage
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="color: white; font-size: 0.875rem; font-weight: 500;">Profile Completion</span>
            <span style="color: {status_color}; font-weight: 600;">{completion_percentage}%</span>
        </div>
        <div style="background-color: #4a5568; border-radius: 9999px; height: 8px; overflow: hidden;">
            <div style="width: {completion_percentage}%; height: 100%; background-color: {status_color};"></div>
        </div>
        <div style="text-align: right; margin-top: 0.25rem;">
            <span style="color: #e2e8f0; font-size: 0.75rem;">{message}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def apply_custom_css():
    """
    Applies custom CSS to improve overall UI appearance
    """
    
    st.markdown("""
    <style>
    /* Import better fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Apply better font */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Improve text colors for better readability */
    p, li, div:not(.streamlit-expanderHeader) {
        color: white;
    }
    
    /* Enhance button styling */
    .stButton > button {
        background-color: #4299e1;
        color: white;
        border-radius: 0.375rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #3182ce;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Improve form styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stMultiselect > div > div > div {
        border-color: #a0aec0;
        border-radius: 0.375rem;
        color: white;
        background-color: rgba(0, 0, 0, 0.1);
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #4299e1;
        box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.2);
    }
    
    /* Enhance sidebar styling */
    .css-1d391kg, .css-12oz5g7 {
        background-color: #2d3748;
        border-right: 1px solid #4a5568;
    }
    
    /* Style expander headers */
    .streamlit-expanderHeader {
        background-color: #4a5568;
        border-radius: 0.375rem;
        border: 1px solid #2d3748;
        color: white;
    }
    .streamlit-expanderHeader:hover {
        background-color: #3c4758;
    }
    
    /* Style dataframes and tables */
    .stDataFrame {
        border-radius: 0.375rem;
        overflow: hidden;
        border: 1px solid #4a5568;
    }
    .dataframe {
        border-collapse: collapse;
    }
    .dataframe thead tr th {
        background-color: #4a5568;
        color: white;
        font-weight: 600;
    }
    
    /* Overall app background */
    .main .block-container {
        background-color: #1a202c;
        padding: 2rem;
        border-radius: 1rem;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    /* Labels */
    label {
        color: white !important;
    }
    
    /* Custom styling for markdown */
    .element-container div.stMarkdown {
        color: white;
    }
    
    /* Adjust for dark theme */
    .stMarkdown p, .stMarkdown li {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True) 