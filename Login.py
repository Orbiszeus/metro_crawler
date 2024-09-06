import streamlit as st
# from streamlit_google_auth import Authenticate
from st_login_form import login_form

st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
# st.title("AI ANALYST")

supabase_url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
supabase_key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]

client = login_form()
    
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

if st.session_state['authenticated']:
    st.subheader('Hello, ' + st.session_state['username'])
    
# # Initialize session state for authentication if not already done
# if 'connected' not in st.session_state:
#     authenticator = Authenticate(
#         secret_credentials_path='google_credentials.json',
#         cookie_name='my_cookie_name',
#         cookie_key='this_is_secret',
#         redirect_uri='http://localhost:8501/',
#     )
#     st.session_state["authenticator"] = authenticator

# # Catch the login event
# st.session_state["authenticator"].check_authentification()

# # Create the login button
# st.session_state["authenticator"].login()

# # If the user is logged in, show the profile page
# if st.session_state.get('connected'):
#     st.header('My Profile')
#     st.image(st.session_state['user_info'].get('picture'))
#     st.subheader('Hello, ' + st.session_state['user_info'].get('name'))
#     st.write('Email: ' + st.session_state['user_info'].get('email'))
#     if st.button('Log Out'):
#         st.session_state["authenticator"].logout()
#         st.rerun()  # Refresh to reflect the logged-out state
# else:
#     # If not logged in, redirect to the login page
#     # st.write("Please log in to access the application.")
#     st.stop()
