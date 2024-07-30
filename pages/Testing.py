import streamlit as st
import sys
sys.path.append('/Users/orbiszeus/metro_analyst/menu_crawler.py')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import menu_crawler
from selenium_stealth import stealth
from webdriver_manager.core.os_manager import ChromeType
import time

st.set_page_config(page_title="Test Hotel Analyst", page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("AI Analysts for Hotels")

st.subheader("Please choose your hotel area.")

@st.cache_resource
def get_driver():
     options = Options()
     options.add_argument("--window-size=1920,1200")
     options.add_argument('--disable-gpu')
     options.add_argument('--headless')
     return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

with st.form(key='my_form'):  
    # Industry selection
    hotel_area_opt = ["Snob", "Ankara", "İzmir", "Bursa", "Antalya", "Çanakkale"]
    hotel_area = st.selectbox("",hotel_area_opt, index=0 )
    submit_button = st.form_submit_button(label='Submit')
    if submit_button:
         
     driver = get_driver()
     stealth(driver,
     languages=["tr-TR", "tr"],
     vendor="Google Inc.",
     platform="Win32",
     webgl_vendor="Intel Inc.",
     renderer="Intel Iris OpenGL Engine",
     fix_hairline=True,)         

     
         
     

               
                
          
          
               
