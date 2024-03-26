import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from openai import OpenAI
import io
from fpdf import FPDF

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
    pdf_bytes = pdf.output(dest='S').encode('windows-1252')  # Correct encoding for PDF data
    return pdf_bytes

# Function to extract text from a DOCX
def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

# Popup mechanism to agree terms
if not st.session_state['terms_agreed']:
    st.write('WELCOME!')
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
    comp_role = "I am appling for the role of " + role + " at " + Company + "."
    word = "under " + str(word_limit) + " words"
    content_c = comp_role + " I have given my resume under the section 'Resume:' and the job and company description under the section 'Job and company description:' later in this prompt. I want you to analyze both the information thoroughly and write me a cover letter with proper word formatting" + word + "relating my experiences and skills mentioned under 'Resume:' with that of the the required skills and responsibilities mentioned under ' Job and company description:'. Don't forget to mention my achievements and how my career goals aligns with the company objective and how I can uniuqely add value to the company's growth. Remember to only give either an entire cover letter as output or no output at all and the cover letter should have no place holders and it should have a subject line. Here are my 'Resume:' and 'Job and company description:' for your reference\nResume:" + file_text +"\nJob and company description:" + additional_text
    content_r = comp_role + " I have given my resume under the section 'Resume:' and the job and company description under the section 'Job and company description:' later in this prompt. I want you to analyze both the information thoroughly and write me an enhanced resume with proper word formatting" + word + "modifying my experiences and skills mentioned under 'Resume:' in accordance with that of the the required skills and responsibilities mentioned under ' Job and company description:'. Remember to only give either an entire resume as output or no output at all, remember to just give resume and no other information and the resume should have no place holders and it should have made up metrics if my 'Resume:' does not already have any and strong action words and ATS friendly words. Here are my 'Resume:' and 'Job and company description:' for your reference\nResume:" + file_text +"\nJob and company description:" + additional_text

    if rc_choice:
        with st.spinner('Writing your enahanced resume...'):
            completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert recruitment consultant having 20 years of experience and specializes in writing cover letters and resumes by analyzing the resume of candidates and relating their experience with the required skills and responsibilities given in the job description and alligning candidate goals to the company objectives with creative flair."},
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
                {"role": "system", "content": "You are an expert recruitment consultant having 20 years of experience and specializes in writing cover letters and resumes by analyzing the resume of candidates and relating their experience with the required skills and responsibilities given in the job description and alligning candidate goals to the company objectives with creative flair."},
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
    # Optionally, remove the generated PDF file after downloading
    # os.remove(pdf_path)
