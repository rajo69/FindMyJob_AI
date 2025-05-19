import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from openai import OpenAI
import io
from fpdf import FPDF
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random
from datetime import datetime
import warnings

# --------------------------
# Configuration & Constants
# --------------------------
warnings.filterwarnings("ignore")  # Suppress all warnings

# Firebase configuration constants
FIREBASE_CONFIG = {
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

# Application constants
WORD_LIMIT_OPTIONS = [100, 150, 200, 250, 300, 350, 400, 450, 500]
DEFAULT_USER_ID = "unknown_user"
OPENAI_MODEL = "gpt-3.5-turbo"

# --------------------------
# Firebase Initialization
# --------------------------
def initialize_firebase():
    """Initialize Firebase connection using credentials from secrets."""
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CONFIG)
        firebase_admin.initialize_app(cred)
    return firestore.client()

# Initialize Firebase and get Firestore client
db = initialize_firebase()

# --------------------------
# Utility Functions
# --------------------------
def get_user_identifier():
    """
    Generate or retrieve user identifier based on session state.
    Falls back to random ID with timestamp if unavailable.
    """
    if "remote_ip" in st.session_state:
        return st.session_state.remote_ip
    return f"u{random.randint(10000000,99999999)}{datetime.now().timestamp()}"

def create_pdf_content(text):
    """
    Generate PDF bytes from text content using FPDF.
    Returns bytes encoded in ISO-8859-1 for proper PDF formatting.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    pdf.multi_cell(0, 10, text)
    return pdf.output(dest='S').encode('ISO-8859-1')

def extract_text_from_pdf(pdf_file):
    """Extract text content from PDF file using PyPDF2."""
    pdf_reader = PdfReader(pdf_file)
    return "\n".join([page.extract_text() for page in pdf_reader.pages])

def extract_text_from_docx(docx_file):
    """Extract text content from DOCX file using python-docx."""
    doc = Document(docx_file)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)

# --------------------------
# Content Generation Functions
# --------------------------
def create_prompt_content(role, company, word_limit, file_text, additional_text, is_resume):
    """
    Construct the GPT prompt based on user inputs and secret templates.
    Handles both resume and cover letter generation cases.
    """
    base_prompt = (
        f"I am applying for the role of {role} at {company}. "
        f"{st.secrets['pr_1' if is_resume else 'pc_1']} "
        f"under {word_limit} words "
        f"{st.secrets['pr_2' if is_resume else 'pc_2']}"
        "\nHere are my 'Resume:' and 'Job and company description:' for your reference\n"
        f"Resume: {file_text}\n"
        f"Job and company description: {additional_text}"
    )
    return base_prompt

def generate_gpt_content(client, system_prompt, user_prompt):
    """
    Execute OpenAI API call with given prompts.
    Returns generated content from GPT-3.5-turbo.
    """
    return client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    ).choices[0].message.content

# --------------------------
# UI Components
# --------------------------
def show_terms_agreement():
    """Display initial terms agreement screen and handle user consent."""
    st.image('https://openclipart.org/image/2400px/svg_to_png/29833/warning.png', width=200)
    st.write('WARNING !!!\nWE WILL USE YOUR ANONYMIZED DATA TO IMPROVE OUR SERVICES. ALL OF OUR SERVICES WILL FOREVER BE FREE!')
    st.write('CAUTION !!!\nPLEASE UPLOAD YOUR COMPLETE RESUME AND COMPLETE JOB DESCRIPTION TO GET THE BEST RESULT.\nGARBAGE IN GARBAGE OUT.')
    
    st.write('WELCOME!')
    st.write("GENERATE ATS FRIENDLY RESUME AND COVER LETTER WITH SINGLE CLICK!")
    return st.button("Agree to Terms and Conditions")

def get_user_inputs():
    """Collect common user inputs for both resume and cover letter generation."""
    return {
        'role': st.text_input("Job role"),
        'company': st.text_input("Company name"),
        'additional_text': st.text_area('Please enter job description', height=300),
        'word_limit': st.select_slider("Word limit", options=WORD_LIMIT_OPTIONS),
        'rc_choice': st.toggle('Enhanced resume'),
        'generate': st.button('Generate')
    }

# --------------------------
# Main Application Logic
# --------------------------
def main():
    st.title('FindMyJob.AI')
    client = OpenAI(api_key=st.secrets["openai_api_key"])
    user_id = get_user_identifier()

    # Terms agreement handling
    if 'terms_agreed' not in st.session_state:
        st.session_state['terms_agreed'] = False

    if not st.session_state['terms_agreed']:
        if show_terms_agreement():
            st.session_state['terms_agreed'] = True
        return

    # Main application flow
    uploaded_file = st.file_uploader(
        "Upload your resume here (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=False
    )

    if not uploaded_file:
        return

    # File processing
    file_extension = uploaded_file.name.split('.')[-1].lower()
    file_text = ""
    
    try:
        if file_extension == 'pdf':
            file_text = extract_text_from_pdf(uploaded_file)
        elif file_extension == 'docx':
            file_text = extract_text_from_docx(io.BytesIO(uploaded_file.getvalue()))
        elif file_extension == 'txt':
            file_text = str(uploaded_file.read(), "utf-8")
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return

    inputs = get_user_inputs()
    
    if file_text and inputs['additional_text'] and inputs['generate']:
        # Content generation
        is_resume = inputs['rc_choice']
        prompt = create_prompt_content(
            inputs['role'],
            inputs['company'],
            inputs['word_limit'],
            file_text,
            inputs['additional_text'],
            is_resume
        )

        with st.spinner(f'Writing your {"enhanced resume" if is_resume else "cover letter"}...'):
            response = generate_gpt_content(
                client,
                st.secrets["p1"],
                prompt
            )
            
        st.write(response)

        # PDF handling for cover letter
        if not is_resume:
            pdf_bytes = create_pdf_content(response)
            if st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name="Cover_Letter.pdf",
                mime="application/pdf"
            ):
                st.success('Downloaded!')

        # Firestore data storage
        doc_ref = db.collection('user_data').document(user_id)
        doc_ref.set({
            'Consent': st.session_state['terms_agreed'],
            'Resume': file_text,
            'Job description': inputs['additional_text'],
            'Resume or Cover letter': inputs['rc_choice'],
            'Generated content': response,
        })

if __name__ == "__main__":
    main()
