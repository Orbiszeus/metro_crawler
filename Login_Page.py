import streamlit as st
from streamlit_google_auth import Authenticate

# Initialize session state for authentication if not already done
if 'connected' not in st.session_state:
    authenticator = Authenticate(
        secret_credentials_path='google_credentials.json',
        cookie_name='my_cookie_name',
        cookie_key='this_is_secret',
        redirect_uri='http://localhost:8501/',
    )
    st.session_state["authenticator"] = authenticator

# Catch the login event
st.session_state["authenticator"].check_authentification()

# Create the login button
st.session_state["authenticator"].login()

# If the user is logged in, show the profile page
if st.session_state.get('connected'):
    st.title('Profile')
    st.image(st.session_state['user_info'].get('picture'))
    st.write('Hello, ' + st.session_state['user_info'].get('name'))
    if st.button('Log Out'):
        st.session_state["authenticator"].logout()
        st.rerun()  # Refresh to reflect the logged-out state
else:
    # If not logged in, redirect to the login page
    # st.write("Please log in to access the application.")
    st.stop()
