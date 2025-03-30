import streamlit as st
from components.auth import auth_page, auth_required, is_authenticated
from utils.supabase_client import get_current_user

# Page configuration
st.set_page_config(
    page_title="Supabase Auth Demo",
    page_icon="🔐",
    layout="centered",
)

st.title("Supabase Authentication Demo")

# Display authentication interface in the sidebar
with st.sidebar:
    st.title("Authentication")
    auth_page(key_prefix="sidebar_")

# Main content based on authentication status
if is_authenticated():
    user = get_current_user()
    
    st.success(f"✅ Successfully authenticated as {user.email}")
    
    st.header("User Information")
    st.json({
        "id": user.id,
        "email": user.email,
        "app_metadata": user.app_metadata,
        "user_metadata": user.user_metadata,
        "created_at": user.created_at
    })
    
    # Example of a protected function
    @auth_required
    def protected_function():
        st.header("Protected Content")
        st.write("This content is only visible to authenticated users.")
        st.write("You can use the @auth_required decorator to protect functions and pages.")
    
    # Call the protected function
    protected_function()
    
else:
    st.info("👈 Please log in or sign up using the sidebar.")
    
    st.header("About This Demo")
    st.write("""
    This is a demonstration of Supabase authentication integration with Streamlit.
    
    Features:
    - User registration
    - Email/password login
    - Password reset
    - Session management
    
    After logging in, you'll see your user information and protected content.
    """)
    
    # Example of what happens when calling protected function when not authenticated
    with st.expander("Try accessing protected content"):
        # Instead of directly calling the inaccessible function inside the expander,
        # we'll just show a message explaining what would happen
        st.warning("This content requires authentication")
        st.write("In your real app, the @auth_required decorator will show a login form")
        
        # Button to demonstrate auth protection
        if st.button("Try to access protected content", key="expander_demo_button"):
            # This is a safer way to demonstrate the protected content
            # that won't cause duplicate key errors
            @auth_required
            def demo_protected_function():
                st.write("You shouldn't see this unless you're logged in!")
            
            demo_protected_function()
        
# Footer
st.markdown("---")
st.caption("Powered by Supabase + Streamlit") 