import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from io import StringIO
import streamlit.components.v1 as components

st.set_page_config(page_title="Metro Analyst", layout="wide")

if not st.session_state.get('connected'):
    st.subheader("You must log in to access this page.")
    st.stop()  # Stop the page from loading further
    
with st.container(): 
    st.subheader("This is the menu extractor!")
    st.title("Metro Analyst")
    
    # with stylable_container(
    #     key="input_header",
    #     css_styles="""
    #     div[data-testid="stMarkdownContainer"] > p {
    #         font-size: 18px;
    #         margin-top: 30px;
    #     }
    #     """,
    # ):
    input_text = st.text_input("", key="placeholder")
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
                df = pd.read_json(StringIO(df_json), orient='split')
                st.write(df)
            if "url" in data:
                st.write("Extracted URL: ")
                st.write(data["url"])
                
                # Provide download button
                # excel_file = BytesIO()
                # with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                #     df.to_excel(writer, index=False)
                #     writer.save()
                # excel_file.seek(0)
                
                # st.download_button(
                #     label="Download Excel",
                #     data=excel_file,
                #     file_name=f"{input_text}_menu.xlsx",
                #     mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                # )
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
