import PyPDF2
import openai
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os

# Create a FastAPI instance
app = FastAPI()

# CORS setup
origins = [
    "http://localhost:3000",  # React development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows your frontend to connect
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)



def read_pdf_data(file_name):

    pdf_data = ""

    # Open a PDF file
    with open(file_name, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        text = ''
        
        # Extract text from each page
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text()
        
        pdf_data = text 

    return pdf_data

def convert_text_to_html(text, apiKey):

    openai.api_key = apiKey
    prompt = f"Convert the following resume text to HTML format:\n\n{text}"
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    html_content = response.choices[0].message.content.strip()
    return html_content

# Directory to store uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class HTMLResponse(BaseModel):
    html: str

@app.post("/convert", response_model=HTMLResponse)
async def convert_to_html(apiKey: str = Form(...), file: UploadFile = File(...)):
    #apiKey = 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
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    pdf_data = read_pdf_data(file_path)

    html_data = convert_text_to_html(pdf_data, apiKey)

    os.remove(file_path)

    return HTMLResponse(html = html_data)

