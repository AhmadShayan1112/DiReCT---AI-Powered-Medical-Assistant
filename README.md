# DiReCT - AI-Powered Medical Assistant

![DiReCT Logo](https://img.shields.io/badge/DiReCT-AI%20Medical%20Assistant-blue?style=for-the-badge)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.15+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Overview

DiReCT (Diagnostic Retrieval and Clinical Triage) is an AI-powered medical assistant that helps patients describe their symptoms, provides preliminary assessments, and recommends appropriate care options. The system combines a user-friendly Streamlit interface with advanced AI models to deliver personalized medical insights.

## ✨ Key Features

- **Comprehensive Health Assessment**: Guided questionnaire for collecting detailed medical information
- **Symptom Analysis**: AI-driven analysis of patient symptoms with severity assessment
- **Medical Record Processing**: Upload and extract information from medical documents using OCR
- **RAG System Integration**: Retrieval-Augmented Generation for evidence-based clinical information
- **Multilingual Support**: Available in multiple languages including English, Spanish, French, German, and Chinese
- **Appointment Booking**: Streamlined workflow for scheduling in-person or telemedicine appointments

## 🚀 Technology Stack

- **Frontend**: Streamlit for the interactive web interface
- **AI/ML**:
  - Google Gemini for prompt generation and analysis
  - Hugging Face models for embeddings and text generation
  - OCR with Tesseract for document processing
- **Retrieval System**:
  - FAISS for efficient vector search
  - LangChain for RAG pipeline implementation
- **Models**:
  - Embedding: `sentence-transformers/all-MiniLM-L6-v2`
  - Generation: `mistralai/Mistral-7B-Instruct-v0.2`

## 📊 Architecture

DiReCT follows a multi-stage pipeline:

1. **Data Collection**: Comprehensive questionnaire and medical document parsing
2. **Query Generation**: AI-generated clinical queries based on patient data
3. **Information Retrieval**: Relevant medical knowledge retrieved from MIMIC-IV-Ext dataset
4. **Response Generation**: AI-synthesized clinical information and recommendations
5. **Triage**: Urgency assessment and care recommendations

## 🔧 Installation

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (recommended for optimal performance)
- Tesseract OCR installed on your system

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/direct-medical-assistant.git
cd direct-medical-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create a .env file with your API keys
echo "GOOGLE_API_KEY=your_google_api_key" > .env
echo "HUGGINGFACE_API_KEY=your_huggingface_api_key" >> .env
```

5. Download the FAISS index:
```bash
# Either download it from a shared location or build it using the provided scripts
python scripts/download_faiss_index.py
```

6. Run the application:
```bash
streamlit run app.py
```

## 📝 Usage

1. **Start the Assessment**: Begin by filling out the comprehensive health questionnaire
2. **Upload Medical Records**: Add relevant medical documents for better context
3. **Review Assessment**: Examine the AI-generated symptom analysis and recommendations
4. **Book Appointment**: Schedule an in-person visit or telemedicine consultation as needed

## 🏥 Medical Data Sources

DiReCT uses the MIMIC-IV-Ext dataset for its clinical knowledge base. This dataset is accessed through the RAG system to provide evidence-based medical information. Note that you will need appropriate permissions to access and use the MIMIC-IV dataset for your implementation.

## 🔒 Privacy and Security

- All patient data is processed locally and not permanently stored
- The application does not share sensitive information with external services
- Medical record uploads are processed for information extraction only

## ⚠️ Disclaimer

DiReCT is an AI assistant and not a replacement for professional medical advice. Always consult with a healthcare professional for medical concerns. The system provides preliminary assessments only and should not be used for emergency situations.

## 🧠 RAG System Details

The Retrieval-Augmented Generation (RAG) system combines:

1. **Document Embedding**: Converting clinical documents to vector representations
2. **Semantic Search**: Finding the most relevant information to patient queries
3. **Context-Aware Response**: Generating responses based on retrieved medical knowledge

## 🛠️ Development

### Project Structure

```
direct-medical-assistant/
├── app.py                 # Main Streamlit application
├── rag_system.py          # RAG implementation
├── patient_data.py        # Patient data handling
├── faiss_index/           # Vector store for medical information
├── models/                # Model configurations
├── utils/
│   ├── ocr.py            # OCR utility functions
│   └── preprocessing.py  # Data preprocessing utilities
├── tests/                 # Test suite
└── requirements.txt       # Project dependencies
```

### Extending the System

To add new features:

1. **New Medical Models**: Update the model loaders in `rag_system.py`
2. **Additional Languages**: Extend the language selector in `app.py`
3. **New Symptoms**: Update the symptom lists in the questionnaire sections

## 📈 Future Roadmap

- Integration with electronic health record (EHR) systems
- Enhanced visualization of medical conditions
- Expanded multilingual support
- Mobile application development
- Integration with wearable health devices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
---

Built with ❤️ for better healthcare
