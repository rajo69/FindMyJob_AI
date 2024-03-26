import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from openai import OpenAI
import io
from fpdf import FPDF
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Firebase service account key as a Python dictionary
firebase_config = {
  "type": st.secrets["type"],
  "project_id": st.secrets["project_id"],
  "private_key_id": st.secrets["private_key_id"],
  "private_key": st.secrets["private_key"],
  "client_email": st.secrets["client_email"],
  "client_id": st.secrets["client_id"],
  "auth_uri":  st.secrets["auth_uri"],
  "token_uri": st.secrets["token_uri"],
  "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
  "client_x509_cert_url": st.secrets["client_x509_cert_url"]
}

# Initialize the app with the credentials
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Generate a unique user identifier (for demonstration, using the session's client IP)
user_id = st.session_state.remote_ip if "remote_ip" in st.session_state else "unknown_user"

if user_id == "unknown_user":
    # Attempting to fetch the client's IP (Streamlit Cloud method)
    st.session_state.remote_ip = st.experimental_get_query_params().get("client_ip", ["unknown_user"])[0]
    user_id = st.session_state.remote_ip 

file_text, additional_text, generate, Company, role, word_limit = '', '', '', '', '', 200

OPENAI_API_KEY = st.secrets["openai_api_key"]

st.title('FindMyJob.AI')

client = OpenAI(api_key = OPENAI_API_KEY)

# Initialize session state for terms agreement
if 'terms_agreed' not in st.session_state:
    st.image('https://openclipart.org/image/2400px/svg_to_png/29833/warning.png', width=200)
    st.write('WARNING !!!\nWE WILL USE YOUR ANONYMIZED DATA TO IMPROVE OUR SERVICES. ALL OF OUR SERVICES WILL FOREVER BE FREE!')
    st.write('CAUTION !!!\nPLEASE UPLOAD YOUR COMPLETE RESUME AND COMPLETE JOB DESCRIPTION TO GET THE BEST RESULT.\nGARBAGE IN GARBAGE OUT.')
    st.session_state['terms_agreed'] = False

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    count = len(pdf_reader.pages)
    text = ""
    for i in range(count):
        page = pdf_reader.pages[i]
        text += page.extract_text()
    return text

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    pdf.multi_cell(0, 10, text)
    # Use 'S' to get the PDF as a string, then encode to 'latin-1' to get bytes
    pdf_bytes = pdf.output(dest='S').encode('ISO-8859-1')  # Correct encoding for PDF data
    return pdf_bytes

# Function to extract text from a DOCX
def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

# Popup mechanism to agree terms
if not st.session_state['terms_agreed']:
    st.write('WELCOME!')
    st.write("GENERATE ATS FRIENDLY RESUME AND COVER LETTER WITH SINGLE CLICK!")
    agree = st.button("Agree to Terms and Conditions")
    if agree:
        st.session_state['terms_agreed'] = True
else:
    # File uploader
    uploaded_file = st.file_uploader("Upload your resume here (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    
    file_text = ""
    # Check if there is a file uploaded
    if uploaded_file is not None:
        # Extract file extension
        file_type = uploaded_file.name.split('.')[-1]
        
        # Process PDF file
        if file_type.lower() == 'pdf':
            file_text = extract_text_from_pdf(uploaded_file)
            role = st.text_input("Job role")
            Company = st.text_input("Company name")
            additional_text = st.text_area('Please enter job description', height=300)
            word_limit = st.select_slider("Word limit", options = [100, 150, 200, 250, 300, 350, 400, 450, 500])
            rc_choice = st.toggle('Enhanced resume')
            generate = st.button('Generate')
        
        # Process DOCX file
        elif file_type.lower() == 'docx':
            file_text = extract_text_from_docx(io.BytesIO(uploaded_file.getvalue()))
            role = st.text_input("Job role")
            Company = st.text_input("Company name")
            additional_text = st.text_area('Please enter job description', height=300)
            word_limit = st.select_slider("Word limit", options = [100, 150, 200, 250, 300, 350, 400, 450, 500])
            rc_choice = st.toggle('Enhanced resume')
            generate = st.button('Generate')
        
        # Process TXT file
        elif file_type.lower() == 'txt':
            file_text = str(uploaded_file.read(), "utf-8")
            role = st.text_input("Job role")
            Company = st.text_input("Company name")
            additional_text = st.text_area('Please enter job description', height=300)
            word_limit = st.select_slider("Word limit", options = [100, 150, 200, 250, 300, 350, 400, 450, 500])
            rc_choice = st.toggle('Enhanced resume')
            generate = st.button('Generate')

# Display both texts
if file_text and additional_text and generate:
    response = ""
    comp_role = "I am appling for the role of " + role + " at " + Company + "."
    word = "under " + str(word_limit) + " words"
    content_c = comp_role + st.secrets["pc_1"] + word + st.secrets["pc_2"] +  "Here are my 'Resume:' and 'Job and company description:' for your reference\nResume:" + file_text +"\nJob and company description:" + additional_text
    content_r = comp_role + st.secrets["pr_1"] + word + st.secrets["pr_2"] +  " Here are my 'Resume:' and 'Job and company description:' for your reference\nResume:" + file_text +"\nJob and company description:" + additional_text

    if rc_choice:
        with st.spinner('Writing your enahanced resume...'):
            completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": st.secrets["p1"]},
                {"role": "user", "content":  content_r}
            ]
        )
        response = completion.choices[0].message.content
        st.write(response)

    else:
        with st.spinner('Writing your cover letter...'):
            completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": st.secrets["p1"]},
                {"role": "user", "content":  content_c}
            ]
        )
        response = completion.choices[0].message.content
        st.write(response)
        pdf_bytes = create_pdf(response)
        if st.download_button(label="Download PDF",
                        data=pdf_bytes,
                        file_name="Cover_Letter.pdf",
                        mime="application/pdf"):
            st.success('Downloaded!')
    # Add a new document
    doc_ref = db.collection('user_data').document(user_id)
    doc_ref.set({
        'Concent': st.session_state['terms_agreed'],
        'Rsume': file_text,
        'Job description': additional_text,
        'Resume or Cover letter': rc_choice,
        'Generated content': response,
    })
    # Optionally, remove the generated PDF file after downloading
    # os.remove(pdf_path)
