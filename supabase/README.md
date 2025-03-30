# Setting Up Supabase Authentication for Career Assistant

This guide will walk you through the steps to set up authentication for your Career Assistant project using Supabase.

## Prerequisites

- A Supabase account and project (already created: "Mutli agent career assistant")
- Supabase URL and API Key (already added to your `.env` file)

## Step 1: Enable Email Authentication in Supabase

1. **Log in to your Supabase Dashboard**: Go to [Supabase Dashboard](https://app.supabase.com/)
2. **Select your project**: Click on your "Mutli agent career assistant" project
3. **Navigate to Authentication**: In the left sidebar, click on "Authentication"
4. **Go to Providers**: Click on the "Providers" tab
5. **Configure Email Provider**:
   - Ensure "Email" is enabled
   - You can choose to enable "Confirm email" if you want users to confirm their email
   - Save your changes

## Step 2: Set Up Database Tables and Security

1. **Navigate to SQL Editor**: In the Supabase dashboard, click on "SQL Editor" in the left sidebar
2. **Create a New Query**: Click on "New Query"
3. **Paste the Setup SQL**: Copy the content from `setup.sql` in this folder and paste it into the SQL editor
4. **Run the Query**: Click "Run" to execute the SQL and set up your tables and security policies

## Step 3: Configure Site URL (for Password Reset)

1. **Navigate to Authentication Settings**: In the Supabase dashboard, go to "Authentication" and then click on "URL Configuration"
2. **Set Site URL**: Enter the URL of your application (e.g., `http://localhost:8501` for local development)
3. **Save Changes**: Click "Save" to apply the URL settings

## Step 4: Test Authentication

1. **Run the Auth Demo**: In your terminal, navigate to your project directory and run:
   ```bash
   streamlit run auth_demo.py
   ```
2. **Test Sign-Up**: Create a new account using the sign-up form
3. **Test Login**: Log in with your newly created account
4. **Test Password Reset**: Try the password reset functionality

## Step 5: Integrating with the Main App

The authentication functions have already been integrated into the main application (`app.py`). The integration includes:

- A sidebar for authentication
- Protected content that only appears for authenticated users
- User session management
- Data persistence connected to the authenticated user

## Additional Configuration

### Email Templates

You can customize email templates for authentication emails (confirmation, password reset, etc.):

1. **Go to Authentication Settings**: In Supabase dashboard, navigate to "Authentication" > "Email Templates"
2. **Customize Templates**: Edit the templates for confirmation and recovery emails
3. **Save Changes**: Click "Save" to apply your customized templates

### Advanced Settings

For advanced authentication settings:

1. **Go to Authentication Settings**: Navigate to "Authentication" > "Settings"
2. **Configure Options**: Adjust settings like:
   - Session duration
   - User sign-up options
   - Security settings
3. **Save Changes**: Click "Save" to apply your settings

## Troubleshooting

If you encounter issues with authentication:

1. **Check API Keys**: Ensure your Supabase URL and API Key in `.env` are correct
2. **Inspect Network Requests**: Use browser developer tools to inspect network requests
3. **Check Supabase Logs**: Review logs in the Supabase dashboard under "Database" > "Logs"
4. **Verify SQL Setup**: Ensure the SQL setup script ran correctly by checking tables in the "Table Editor" 