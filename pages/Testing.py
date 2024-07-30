import streamlit as st
import sys
sys.path.append('/Users/orbiszeus/metro_analyst/menu_crawler.py')
import time

st.set_page_config(page_title="Test Hotel Analyst", page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("AI Analysts for Hotels")

st.subheader("Please choose your hotel area.")


with st.form(key='my_form'):  
    # Industry selection
    hotel_area_opt = ["Snob", "Ankara", "İzmir", "Bursa", "Antalya", "Çanakkale"]
    hotel_area = st.selectbox("",hotel_area_opt, index=0 )
    submit_button = st.form_submit_button(label='Submit')
     

     
         
     

               
                
          
          
               
