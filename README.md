# FindMyJob.AI

FindMyJob.AI is a **Streamlit-based application** that helps users generate a customized **cover letter** or **enhanced resume** by uploading a resume (PDF, DOCX, or TXT) along with the job description. It utilizes **OpenAI GPT-3.5** to generate high-quality cover letters based on user inputs. The data is anonymized and securely stored in **Google Firestore** using **Firebase**.

## Features

- **Customized Cover Letters:** Generate personalized cover letters based on your resume and job description.
- **Enhanced Resumes:** Optionally enhance your resume with an AI-generated version that highlights relevant skills and experiences.
- **PDF Output:** Download the generated cover letter in PDF format.
- **Firebase Integration:** Secure storage of user data in Firebase Firestore.
- **Resume Upload Support:** Accepts resumes in PDF, DOCX, and TXT formats.

## Use the App

Go to: https://findmyjobai-rajo.streamlit.app/

## Installation

### Prerequisites

Make sure you have the following installed:

- Python 3.8+
- Streamlit
- Firebase Admin SDK
- OpenAI API key

### Clone the Repository

```bash
git clone https://github.com/yourusername/findmyjob-ai.git
cd findmyjob-ai
```

### Install Dependencies

Install all necessary dependencies listed in the `requirements.txt` file using pip:

```bash
pip install -r requirements.txt
```

### Firebase Setup

1. Create a Firebase project in the [Firebase Console](https://console.firebase.google.com/).
2. Download the service account key (JSON file) and store it in a secure location.
3. Set up Firebase Firestore for data storage.
4. Update your Streamlit secrets by adding your Firebase configuration and OpenAI API key in `secrets.toml` as follows:

```toml
type = "service_account"
project_id = "your_project_id"
private_key_id = "your_private_key_id"
private_key = "your_private_key"
client_email = "your_client_email"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your_cert_url"
openai_api_key = "your_openai_api_key"

# You can also include other required strings like:
pc_1 = " .... "
pr_1 = " .... "
```

## Usage

### Running the App

Once everything is set up, you can run the application locally by executing:

```bash
streamlit run findmyjob_t1.py
```

### Application Workflow

1. **Terms & Conditions:** First, agree to the terms and conditions for data processing.
2. **Upload Resume:** Upload your resume in PDF, DOCX, or TXT format.
3. **Enter Job Information:** Input the job role, company name, and job description.
4. **Generate:** Click the 'Generate' button to produce a customized cover letter or enhanced resume.
5. **Download:** Optionally, download the generated cover letter in PDF format.

## File Structure

```bash
findmyjob-ai/
│
├── findmyjob_t1.py           # Main Python script that runs the Streamlit app
├── requirements.txt          # Lists all dependencies required for the app
└── .streamlit/secrets.toml    # Configuration file for storing secrets like Firebase and OpenAI API keys
```

## Technologies Used

- **Streamlit:** For building the web interface.
- **PyPDF2:** For extracting text from PDF resumes.
- **python-docx:** For processing DOCX resumes.
- **OpenAI GPT-3.5:** For generating personalized cover letters and enhanced resumes.
- **FPDF:** For generating PDF output files.
- **Firebase Firestore:** For securely storing anonymized user data.

## Future Improvements

- Add multi-language support for non-English job descriptions and resumes.
- Implement more resume enhancement features.
- Improve the AI model's ability to handle varying job descriptions.

## License

This project is licensed under the MIT License.

## Contribution

Feel free to submit a pull request or open an issue for suggestions, bug fixes, or improvements.
