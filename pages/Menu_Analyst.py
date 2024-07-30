import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import requests
from io import BytesIO

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
        
        response = requests.post("http://0.0.0.0:8000/crawl_menu", json=payload)
        if response.status_code == 200:
            data = response.json()
            if "dataframe" in data:
                df_json = data["dataframe"]
                df = pd.read_json(df_json, orient='split')
                st.write(df)
                
                # Provide download button
                excel_file = BytesIO()
                df.to_excel(excel_file, index=False)
                excel_file.seek(0)
                
                st.download_button(
                    label="Download Excel",
                    data=excel_file,
                    file_name=f"{input_text}_menu.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                st.write("An error occurred. Please try again.")
        else:
            st.write("An error occurred. Please try again.")

# with st.container():
#     with stylable_container(
#         key="input_header",
#         css_styles="""
#         div[data-testid="stMarkdownContainer"] > p {
#             font-size: 18px;
#             margin-top: 30px;
#         }
#         """,
#     ):
#         uploaded_file = st.file_uploader("Insert your menu here.", type="pdf")

#         if uploaded_file is not None:
#             bytes_data = uploaded_file.getvalue()
            
#             response = requests.post(
#                 "http://localhost:8581/upload_pdf",  # Adjust to your FastAPI endpoint
#                 files={"file": uploaded_file})
            
#             if response.status_code == 200:
#                 st.write("File processed successfully!")
#                 st.write(response.json())
#             else:
#                 st.write("File processing failed.")
