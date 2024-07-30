import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from io import StringIO
import pandas as pd
import requests

st.set_page_config(page_title="Metro Analyst", layout="wide")


with st.container():
    
    st.subheader("This is the menu extractor!")
    st.title("Metro Analyst")


    
    with stylable_container(
        key="input_header",
        css_styles="""
        div[data-testid="stMarkdownContainer"] > p {
            font-size: 18px;
            margin-top: 30px;
        }
        """,
    ):
        input_text = st.text_input("Please type your desired restaurant area or restaurant name.", key="disabled")
    single_restaurant = st.checkbox("I want a single restaurant")

    if st.button("Search"):
        if single_restaurant:
            payload = {
                "restaurant": input_text
            }
        else:
            payload = {
                "area": input_text
            }
        
        response = requests.post("http://127.0.0.1:8581/crawl_menu", json=payload)
        if response.status_code == 200:
            data = response.json()
            st.write(data)
        else:
            st.write("An error occurred. Please try again.")

with st.container():
    with stylable_container(
        key="input_header",
        css_styles="""
        div[data-testid="stMarkdownContainer"] > p {
            font-size: 18px;
            margin-top: 30px;
        }
        """,
    ):
        uploaded_file = st.file_uploader("Insert your menu here." ,type="pdf")

        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            st.write(bytes_data)
            
            response = requests.post(
            "http://localhost:8581/upload_pdf",  # Adjust to your FastAPI endpoint
            files={"file": uploaded_file})
            
            if response.status_code == 200:
                st.write("File processed successfully!")
                st.write(response.json())
            else:
                st.write("File processing failed.")
                
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            string_data = stringio.read()
            
            dataframe = pd.read_csv(uploaded_file)
        
