from vertexai.generative_models import GenerativeModel, Part
import vertexai
import os
import pandas as pd
import re
from openai import OpenAI
import json
import PyPDF2
import gcsfs

class VertexAI:     
     
     
     ''' This function is a back-up method that will get files from 
     local storage if Google Data Storage fails to load items. '''
     
     def read_pdf(file_path):
          pdf_content = ""
          with open(file_path, "rb") as file:
               reader = PyPDF2.PdfReader(file)
               for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    pdf_content += page.extract_text()
               
          return pdf_content
     
     
     ''' Ingredient founder function tries to fill the missing ingredients 
     from the given menu using OpenAI's GPT. '''
     
     def ingredient_founder(json_data):
          client = OpenAI()
          OpenAI.api_key = os.getenv('OPENAI_API_KEY')
          completion = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": f"Here is the menu data in JSON format with missing ingredients: {json.dumps(json_data)}. Please fill in the missing ingredients and return the data in JSON format."}
          ],
          response_format={"type": "json_object"}
          )
          
          return completion.choices[0].message.content
     
     def vertex_ai(self, pdf_file_uri):

          # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/orbiszeus/metro_analyst/metro_analsyt_google_key.json"

          PROJECT_ID = "recursive-summary"
          # gcs_file_system = gcsfs.GCSFileSystem(project=PROJECT_ID)
          # f_object = gcs_file_system.open(pdf_file_uri, "rb")
          # pdf_cont = ""
          # reader = PyPDF2.PdfReader(f_object)
          # for num in range(len(reader.pages)):
          #      page = reader.pages[num]
          #      pdf_cont += page.extract_text()
          # f_object.close()


          vertexai.init(project=PROJECT_ID, location="us-central1")

          model = GenerativeModel(model_name="gemini-1.5-flash-001")


          prompt = """
          You are a very professional document summarization specialist in these menus from restaurants.
          Please only extract the menu items and it's ingredients in a form that could later be written to an excel with the columns always in this format like this: "Menu Item" : "Ingredients".
          For just as an example if the Menu Item is "Tacos" and the ingredients are "Chicken, Rice, Cheese", the output always should be in this format:
          "Menu Item" : "Tacos" | "Ingredients": "Chicken, Rice, Cheese"
          
          """

          pdf_file = Part.from_uri(pdf_file_uri, mime_type="application/pdf")
          # pdf_content = VertexAI.read_pdf("/Users/orbiszeus/metro_analyst/restaurant_menus/bs_yemek_2501.pdf")

          chunk_size = 1000
          response_text = ""
          for i in range(0, len(prompt), chunk_size):
               chunk = prompt[i:i + chunk_size]
               contents = [pdf_file, chunk]
               print(contents)
               response = model.generate_content(contents, stream=True)
               for r in response:
                    print(r.text, end="")
                    response_text += r.text
          # contents = [pdf_content, prompt]
          # response_text = model.generate_content(contents)
          # print(response.text)

          data = []
          for line in response_text.split('\n'):
               if "|" in line and "Menu Item" not in line and "-------" not in line:
                    menu_item, ingredients = line.split("|", 1)
                    data.append({"Menu Item": menu_item.strip(), "Ingredients": ingredients.strip()})
          
          df = pd.DataFrame(data)
          match = re.search(r"gs://[^/]+/([^/]+)\.pdf", pdf_file_uri)
          empty_ingredients = df[(df['Ingredients'] == '-') | (df['Ingredients'] == '')]
          
          if not empty_ingredients.empty:
              print("boş menü itemi var!!")
              json_data = df.to_dict(orient='records')
              
              filled_menu = VertexAI.ingredient_founder(json_data)
              data = json.loads(filled_menu)
              menu = data.get("menu", [])
              cleaned_menu = []
              for item in menu: 
                   menu_item = item["Menu Item"]
                   ingredients = item["Ingredients"]
                   cleaned_menu.append({"Menu Item": menu_item.strip(), "Ingredients": ingredients.strip()})
              df_filled = pd.DataFrame(cleaned_menu)
              
              if match:
                   file_id = match.group(1)
                   output_file = f"{file_id}.xlsx"
              else:
                   output_file = "menu_items.xlsx"
              df_filled.to_excel(output_file, index=False, sheet_name='Menu')
              return 
              
          else:
               if match:
                    file_id = match.group(1)
                    output_file = f"{file_id}.xlsx"
               else:
                    output_file = "menu_items.xlsx" 

               df.to_excel(output_file, index=False)



     ''' Ask Gemini is the main function that is taking the ocr text output
     of the given gcs url pdf item in raw text form and converting
     it into a readable excel file holding menu items and it's ingredients. '''
     
     def ask_gemini(self, input_text, pdf_file_uri):
          
          # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/orbiszeus/metro_analyst/metro_analsyt_google_key.json"
          PROJECT_ID = "recursive-summary"         

          vertexai.init(project=PROJECT_ID, location="us-central1")
          model = GenerativeModel(model_name="gemini-1.5-flash-001")
          
          prompt = """
          You are a very professional document summarization specialist in these menus from restaurants.
          Please only extract the menu items and it's ingredients in a form that could later be written to an excel with the columns always in this format like this: "Menu Item" : "Ingredients".
          For just as an example if the Menu Item is "Tacos" and the ingredients are "Chicken, Rice, Cheese", the output always should be in this format:
          "Menu Item" : "Tacos" | "Ingredients": "Chicken, Rice, Cheese"  
          """         
             
          chunk_size = 1000
          response_text = ""
          for i in range(0, len(prompt), chunk_size):
               chunk = prompt[i:i + chunk_size]
               contents = [input_text, chunk]
               print(contents)
               response = model.generate_content(contents, stream=True)
               for r in response:
                    print(r.text, end="")
                    response_text += r.text
                    
          data = []
          # for line in response_text.split('\n'):
          #      if " | " in line and "Menu Item" not in line and "-------" not in line:
          #           menu_item, ingredients = line.split(" | ", 1)
          #           data.append({"Menu Item": menu_item.strip(), "Ingredients": ingredients.strip()})
          for line in response_text.split('\n'):
               if " | " in line:
                    parts = line.split(" | ")
                    menu_item = parts[0].split(' : ')[1].strip(' "')
                    ingredients = parts[1].split(': ')[1].strip(' "')
                    data.append({"Menu Item": menu_item, "Ingredients": ingredients})
          print("Parsed data:", data)
          df = pd.DataFrame(data)
          match = re.search(r"gs://[^/]+/([^/]+)\.pdf", pdf_file_uri)
          empty_ingredients = df[(df['Ingredients'] == '-') | (df['Ingredients'] == '')]
          
          # if not empty_ingredients.empty:
          #     print("boş menü itemi var!!")
          #     json_data = df.to_dict(orient='records')
              
          #     filled_menu = VertexAI.ingredient_founder(json_data)
          #     data = json.loads(filled_menu)
          #     menu = data.get("menu", [])
          #     cleaned_menu = []
          #     for item in menu: 
          #          menu_item = item["Menu Item"]
          #          ingredients = item["Ingredients"]
          #          cleaned_menu.append({"Menu Item": menu_item.strip(), "Ingredients": ingredients.strip()})
          #     df_filled = pd.DataFrame(cleaned_menu)
              
          #     if match:
          #          file_id = match.group(1)
          #          output_file = f"{file_id}.xlsx"
          #     else:
          #          output_file = "menu_items.xlsx"
          #     df_filled.to_excel(output_file, index=False, sheet_name='Menu')
          #     return 
              
          # else:
          if match:
               file_id = match.group(1)
               output_file = f"{file_id}.xlsx"
          else:
               output_file = "menu_items.xlsx" 

          df.to_excel(output_file, index=False)