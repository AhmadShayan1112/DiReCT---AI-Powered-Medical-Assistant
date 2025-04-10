import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
import random
from google import genai
from PIL import Image
import pytesseract
import re
import rag_system as rr
import Patient_data as PD_DATA
# Initialize Gemini client
client = genai.Client(api_key="AIzaSyBN6BqOHbtBVqA9NkeU12M6oVwr5FcHG7Q")

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def clean_ocr_text(text):
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)  
    text = re.sub(r'[=~_•""'']', '', text)     
    text = re.sub(r'[\[\]\{\}\|\\]', '', text)
    text = re.sub(r'[-–—]{2,}', '-', text)
    text = '. '.join(i.strip().capitalize() for i in text.split('.'))
    return text.strip()

# Set page configuration
st.set_page_config(
    page_title="DiReCT - AI-Powered Medical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextInput>div>div>input {
        font-size: 1.1rem;
    }
    .stMarkdown {
        font-size: 1.1rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e6f3ff;
    }
    .chat-message.assistant {
        background-color: #f0f2f6;
    }
    .chat-message .avatar {
        width: 20%;
    }
    .chat-message .avatar img {
        max-width: 78px;
        max-height: 78px;
        border-radius: 50%;
        object-fit: cover;
    }
    .chat-message .message {
        width: 100%;
        padding: 0 1.5rem;
    }
    .body-diagram {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
    .body-diagram img {
        max-width: 100%;
        height: auto;
    }
    .symptom-button {
        margin: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        cursor: pointer;
    }
    .symptom-button:hover {
        background-color: #e0e0e0;
    }
    .symptom-button.selected {
        background-color: #4CAF50;
        color: white;
    }
    .severity-slider {
        margin: 1rem 0;
    }
    .language-selector {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'initial'
if 'symptoms' not in st.session_state:
    st.session_state.symptoms = {}
if 'severity' not in st.session_state:
    st.session_state.severity = {}
if 'duration' not in st.session_state:
    st.session_state.duration = {}
if 'body_parts' not in st.session_state:
    st.session_state.body_parts = []
if 'medical_history' not in st.session_state:
    st.session_state.medical_history = {}
if 'language' not in st.session_state:
    st.session_state.language = 'English'

# Language selector
languages = ['English', 'Spanish', 'French', 'German', 'Chinese']
selected_language = st.selectbox('Select Language', languages, key='language_selector')

# Title and description
st.title("🏥 DiReCT - AI-Powered Medical Assistant")
st.markdown("""
    Welcome to DiReCT, your AI-powered medical assistant. Describe your symptoms or use our interactive tools to get a preliminary assessment.
""")

# Sidebar for medical history and settings
with st.sidebar:
    st.header("Medical History")
    
    # Medical history form
    with st.expander("Add Medical History", expanded=False):
        # Medical Records Upload
        st.subheader("Upload Medical Records")
        
        # Initialize medical history in session state if not exists
        if 'medical_history' not in st.session_state:
            st.session_state.medical_history = {}
        
        # Initialize sub-components if they don't exist
        if 'uploaded_records' not in st.session_state.medical_history:
            st.session_state.medical_history['uploaded_records'] = []
        if 'extracted_text' not in st.session_state.medical_history:
            st.session_state.medical_history['extracted_text'] = []
        if 'conditions' not in st.session_state.medical_history:
            st.session_state.medical_history['conditions'] = []
        if 'medications' not in st.session_state.medical_history:
            st.session_state.medical_history['medications'] = ''
        if 'allergies' not in st.session_state.medical_history:
            st.session_state.medical_history['allergies'] = ''
        
        uploaded_files = st.file_uploader(
            "Upload your medical records",
            type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
            accept_multiple_files=True,
            key="medical_records_uploader"
        )
        
        if uploaded_files:
            # Process only new files
            for uploaded_file in uploaded_files:
                # Check if file is already uploaded (by name and size)
                file_identifier = f"{uploaded_file.name}_{uploaded_file.size}"
                existing_files = [f"{record['filename']}_{record['size_bytes']}" 
                                for record in st.session_state.medical_history['uploaded_records']]
                
                if file_identifier not in existing_files:
                    file_details = {
                        "filename": uploaded_file.name,
                        "type": uploaded_file.type,
                        "size": f"{uploaded_file.size / 1024:.2f} KB",
                        "size_bytes": uploaded_file.size  # Store exact size for comparison
                    }
                    
                    # Extract text from uploaded files
                    if uploaded_file.type.startswith('image'):
                        image = Image.open(uploaded_file)
                        extracted_text = pytesseract.image_to_string(image)
                        cleaned_text = clean_ocr_text(extracted_text)
                        st.session_state.medical_history['extracted_text'].append(cleaned_text)
                    
                    st.session_state.medical_history['uploaded_records'].append(file_details)
                    st.success(f"Uploaded and processed: {uploaded_file.name}")
        
        # Display current uploaded files
        if len(st.session_state.medical_history.get('uploaded_records', [])) > 0:
            st.write("Currently uploaded files:")
            for record in st.session_state.medical_history['uploaded_records']:
                st.write(f"- {record['filename']} ({record['size']})")
        
        st.divider()
        
        # Existing conditions
        conditions = st.multiselect(
            "Previous Conditions",
            ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "Arthritis", "None", "Other"],
            default=st.session_state.medical_history.get('conditions', [])
        )
        
        medications = st.text_area(
            "Current Medications",
            value=st.session_state.medical_history.get('medications', ''),
            placeholder="List your current medications"
        )
        
        allergies = st.text_area(
            "Allergies",
            value=st.session_state.medical_history.get('allergies', ''),
            placeholder="List any allergies"
        )
        
        if st.button("Save Medical History"):
            # Update only the form fields, preserve the uploaded records
            st.session_state.medical_history.update({
                "conditions": conditions,
                "medications": medications,
                "allergies": allergies
            })
            st.success("Medical history saved!")
    
    # Display current medical history
    if st.session_state.medical_history:
        st.subheader("Your Medical History")
        if "uploaded_records" in st.session_state.medical_history:
            st.write("Uploaded Records:")
            for record in st.session_state.medical_history["uploaded_records"]:
                st.write(f"- {record['filename']} ({record['size']})")
        if "conditions" in st.session_state.medical_history:
            st.write("Conditions:", ", ".join(st.session_state.medical_history["conditions"]))
        if "medications" in st.session_state.medical_history:
            st.write("Medications:", st.session_state.medical_history["medications"])
        if "allergies" in st.session_state.medical_history:
            st.write("Allergies:", st.session_state.medical_history["allergies"])
    
    st.header("About")
    st.markdown("""
        DiReCT uses advanced AI to:
        - Analyze your symptoms
        - Provide preliminary assessments
        - Recommend appropriate care
        - Connect you with healthcare providers
    """)

# Main content area
if st.session_state.current_step == 'initial':
    st.session_state.current_step = 'questionnaire'
    st.rerun()

elif st.session_state.current_step == 'questionnaire':
    # Guided questionnaire
    st.subheader("Comprehensive Health Assessment")
    
    if 'questionnaire_step' not in st.session_state:
        st.session_state.questionnaire_step = 1
        st.session_state.medical_history = {}
        st.session_state.symptoms = {}
        st.session_state.lifestyle = {}
        st.session_state.follow_up = {}
    
    # Step 1: Medical History
    if st.session_state.questionnaire_step == 1:
        st.write("Step 1: Medical History")
        
        st.session_state.medical_history['conditions'] = st.multiselect(
            "Do you have any existing medical conditions?",
            ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "Arthritis", "None", "Other"]
        )
        
        if "Other" in st.session_state.medical_history['conditions']:
            st.session_state.medical_history['other_conditions'] = st.text_input("Please specify other conditions")
        
        st.session_state.medical_history['medications'] = st.text_area(
            "Are you currently on any medications?",
            placeholder="List all current medications and dosages"
        )
        
        st.session_state.medical_history['allergies'] = st.text_area(
            "Do you have any allergies, especially to medications?",
            placeholder="List any known allergies"
        )
        
        st.session_state.medical_history['family_history'] = st.text_area(
            "Has anyone in your family had similar health issues?",
            placeholder="Describe any relevant family medical history"
        )
        
        if st.button("Next to Symptom Inquiry"):
            st.session_state.questionnaire_step = 2
            st.rerun()
    
    # Step 2: Symptom Inquiry
    elif st.session_state.questionnaire_step == 2:
        st.write("Step 2: Symptom Inquiry")
        
        st.session_state.symptoms['description'] = st.text_area(
            "Can you describe your symptoms?",
            placeholder="Please describe your symptoms in detail"
        )
        
        st.session_state.symptoms['location'] = st.multiselect(
            "Where does it hurt?",
            ["Head", "Neck", "Chest", "Abdomen", "Back", "Arms", "Legs", "Feet", "Multiple locations"]
        )
        
        st.session_state.symptoms['severity'] = st.slider(
            "On a scale of 1 to 10, how severe is the pain?",
            1, 10, 5
        )
        
        st.session_state.symptoms['triggers'] = st.text_area(
            "Does anything make the symptoms better or worse?",
            placeholder="Describe any factors that affect your symptoms"
        )
        
        if st.button("Next to Lifestyle Questions"):
            st.session_state.questionnaire_step = 3
            st.rerun()
    
    # Step 3: Lifestyle and Habits
    elif st.session_state.questionnaire_step == 3:
        st.write("Step 3: Lifestyle and Habits")
        
        st.session_state.lifestyle['smoking'] = st.selectbox(
            "Do you smoke or use tobacco?",
            ["Never", "Former smoker", "Current smoker", "Occasional use"]
        )
        
        st.session_state.lifestyle['alcohol'] = st.selectbox(
            "How much alcohol do you drink, if any?",
            ["None", "Occasionally (1-2 drinks/week)", "Moderately (3-7 drinks/week)", "Regularly (8+ drinks/week)"]
        )
        
        st.session_state.lifestyle['diet'] = st.text_area(
            "What does your diet typically look like?",
            placeholder="Describe your typical eating habits"
        )
        
        st.session_state.lifestyle['exercise'] = st.selectbox(
            "How active are you, and do you exercise regularly?",
            ["Sedentary", "Light activity", "Moderate activity", "Very active", "Athletic"]
        )
        
        if st.button("Next"):
            if st.session_state.symptoms['severity'] >= 7:
                st.session_state.questionnaire_step = 4
            else:
                st.session_state.questionnaire_step = 5
            st.rerun()
    
    # Step 4: Physical Examination (Only for severe pain)
    elif st.session_state.questionnaire_step == 4:
        st.write("Step 4: Detailed Physical Examination")
        
        for location in st.session_state.symptoms['location']:
            st.subheader(f"Examination for {location}")
            
            if location == "Head":
                st.session_state.symptoms[f'{location}_details'] = st.multiselect(
                    f"Where exactly in your {location.lower()} do you feel the pain?",
                    ["Front", "Back", "Sides", "Temples", "Around eyes", "Jaw"]
                )
            elif location == "Chest":
                st.session_state.symptoms[f'{location}_details'] = st.multiselect(
                    f"Where exactly in your {location.lower()} do you feel the pain?",
                    ["Left side", "Right side", "Center", "Upper", "Lower", "All over"]
                )
            elif location == "Abdomen":
                st.session_state.symptoms[f'{location}_details'] = st.multiselect(
                    f"Where exactly in your {location.lower()} do you feel the pain?",
                    ["Upper right", "Upper left", "Lower right", "Lower left", "Center", "All over"]
                )
            elif location == "Back":
                st.session_state.symptoms[f'{location}_details'] = st.multiselect(
                    f"Where exactly in your {location.lower()} do you feel the pain?",
                    ["Upper back", "Middle back", "Lower back", "Left side", "Right side", "All over"]
                )
            elif location in ["Arms", "Legs"]:
                st.session_state.symptoms[f'{location}_details'] = st.multiselect(
                    f"Where exactly in your {location.lower()} do you feel the pain?",
                    ["Left", "Right", "Both", "Upper", "Lower", "Joints"]
                )
            
            st.session_state.symptoms[f'{location}_character'] = st.multiselect(
                f"How would you describe the pain in your {location.lower()}?",
                ["Sharp", "Dull", "Throbbing", "Burning", "Tingling", "Numbness", "Stiffness"]
            )
            
            st.session_state.symptoms[f'{location}_duration'] = st.selectbox(
                f"How long does the pain in your {location.lower()} typically last?",
                ["Seconds", "Minutes", "Hours", "Days", "Constant"]
            )
        
        if st.button("Next to Follow-up Questions"):
            st.session_state.questionnaire_step = 5
            st.rerun()
    
    # Step 5: Follow-up Questions
    elif st.session_state.questionnaire_step == 5:
        st.write("Step 5: Follow-up Questions")
        
        st.session_state.follow_up['recent_tests'] = st.text_area(
            "Have you had any recent tests or procedures done?",
            placeholder="Describe any recent medical tests or procedures"
        )
        
        st.session_state.follow_up['symptom_changes'] = st.text_area(
            "How have your symptoms changed since they first started?",
            placeholder="Describe how your symptoms have evolved"
        )
        
        st.session_state.follow_up['additional_concerns'] = st.text_area(
            "Are there any other concerns you haven't mentioned?",
            placeholder="Share any additional health concerns"
        )
        
        if st.button("Complete Assessment"):
            # Prepare context for Gemini
            context = """
            Generate a structured and to-the-point prompt for a Retrieval-Augmented Generation (RAG) system using the MIMIC-IV-Ext dataset.

            The output should be **only the prompt** in the following format:
            **Example Output Format:**
            Retrieve clinical information from the MIMIC-IV-Ext dataset relevant to a patient presenting with the following information:
            *   **Medical History:** [Condition]
            *   **Symptoms:** [Symptom]
            *   **Lifestyle:** [Lifestyle Details]
            *   **Other:** [Any Additional Details]
            *   and so on

            previous medical records of patient as well
            *   [Previous medical records]
            *   [Previous medical records]
            *   [Previous medical records]
            *   [Previous medical records]
            *   [Previous medical records]
            *   [Previous medical records]
            *   [Previous medical records]
            *   [Previous medical records]

            Specifically, identify potential causes, diagnostic considerations, and treatment options for [Symptom] in a patient with [Condition]. 
            Prioritize information regarding:
            *   [Key Focus Area 1]
            *   [Key Focus Area 2]
            *   [Key Focus Area 3]
            *   and so on
            

            Ensure that the response **only includes the structured prompt** with no extra explanations or descriptions.
             
            Below is the complete patient information from the questionnaire:

            MEDICAL HISTORY:
            1. Previous medical records: {extracted_text}
            2. Existing medical conditions: {conditions}
            3. Current medications: {medications}
            4. Allergies to medications: {allergies}
            5. Family medical history: {family_history}

            SYMPTOMS AND PAIN ASSESSMENT:
            6. Symptom description: {symptoms_description}
            7. Pain location: {symptoms_location}
            8. Pain severity (1-10): {symptoms_severity}
            9. Pain triggers/relief factors: {symptoms_triggers}

            DETAILED PHYSICAL EXAMINATION:
            {physical_exam_details}

            LIFESTYLE AND HABITS:
            10. Smoking/tobacco use: {smoking}
            11. Alcohol consumption: {alcohol}
            12. Diet description: {diet}
            13. Physical activity level: {exercise}

            FOLLOW-UP INFORMATION:
            14. Recent tests/procedures: {recent_tests}
            15. Symptom progression: {symptom_changes}
            16. Additional concerns: {additional_concerns}

            URGENCY ASSESSMENT:
            Current urgency level: {urgency}
            Recommendation: {recommendation}
            """.format(
                extracted_text="\n".join(st.session_state.medical_history.get('extracted_text', [])),
                conditions=", ".join(st.session_state.medical_history.get('conditions', [])),
                medications=st.session_state.medical_history.get('medications', ''),
                allergies=st.session_state.medical_history.get('allergies', ''),
                family_history=st.session_state.medical_history.get('family_history', ''),
                symptoms_description=st.session_state.symptoms.get('description', ''),
                symptoms_location=", ".join(st.session_state.symptoms.get('location', [])),
                symptoms_severity=st.session_state.symptoms.get('severity', ''),
                symptoms_triggers=st.session_state.symptoms.get('triggers', ''),
                physical_exam_details="\n".join([
                    f"{location}:\n- Location details: {st.session_state.symptoms.get(f'{location}_details', '')}\n"
                    f"- Pain character: {st.session_state.symptoms.get(f'{location}_character', '')}\n"
                    f"- Duration: {st.session_state.symptoms.get(f'{location}_duration', '')}"
                    for location in st.session_state.symptoms.get('location', [])
                    if st.session_state.symptoms.get('severity', 0) >= 7
                ]),
                smoking=st.session_state.lifestyle.get('smoking', ''),
                alcohol=st.session_state.lifestyle.get('alcohol', ''),
                diet=st.session_state.lifestyle.get('diet', ''),
                exercise=st.session_state.lifestyle.get('exercise', ''),
                recent_tests=st.session_state.follow_up.get('recent_tests', ''),
                symptom_changes=st.session_state.follow_up.get('symptom_changes', ''),
                additional_concerns=st.session_state.follow_up.get('additional_concerns', ''),
                urgency=urgency if 'urgency' in locals() else 'Not assessed',
                recommendation=recommendation if 'recommendation' in locals() else 'Not provided'
            )

            # Get Gemini's response
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=context
                )
                print("Gemini Response:")
                print(response.text)
                rag_response = rr.answer_clinical_query(response.text)
                print(rag_response)
                st.session_state.gemini_response = response.text
                st.session_state.rag_response = rag_response
                st.session_state.current_step = 'triage'
                st.rerun()
            except Exception as e:
                st.error(f"Error getting AI analysis: {str(e)}")
                st.session_state.current_step = 'triage'
                st.rerun()

elif st.session_state.current_step == 'triage':
    # AI-driven triage system
    st.subheader("Symptom Assessment")
    
    # Display collected symptoms
    st.write("Based on your reported symptoms:")
    
    # Determine urgency level (simplified logic)
    if "Chest" in st.session_state.symptoms and "Pain" in st.session_state.symptoms.get("Chest", []):
        urgency = "Emergency"
        recommendation = "Seek immediate medical attention. Chest pain could indicate a serious condition."
    elif "Head" in st.session_state.symptoms and "Severe headache" in st.session_state.symptoms.get("Head", []):
        urgency = "Urgent"
        recommendation = "You should see a doctor within 24 hours."
    else:
        urgency = "Non-Urgent"
        recommendation = "You can try home remedies or book an online consultation."
    
    # Display urgency level
    if urgency == "Emergency":
        st.error(f"**{urgency}**: {recommendation}")
    elif urgency == "Urgent":
        st.warning(f"**{urgency}**: {recommendation}")
    else:
        st.success(f"**{urgency}**: {recommendation}")
    
    # Display Gemini Response
    st.subheader("Patient Query")
    if 'gemini_response' in st.session_state:
        st.markdown(st.session_state.gemini_response)
    else:
        st.info("No query response available yet.")
    
    # Display RAG Response with buttons
    st.subheader("Clinical Information")
    if 'rag_response' in st.session_state:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Associated Document (Context)"):
                st.session_state.show_context = True
                st.session_state.show_answer = False
        
        with col2:
            if st.button("💡 Answer"):
                st.session_state.show_context = False
                st.session_state.show_answer = True
        
        st.markdown("---")
        
        if 'show_context' not in st.session_state:
            st.session_state.show_context = False
        if 'show_answer' not in st.session_state:
            st.session_state.show_answer = False
        
        # Display Context
        if st.session_state.show_context:
            st.markdown("### Associated Document (Context)")
            context = st.session_state.rag_response.split("Answer:")[0].strip()
            st.markdown(context)
            
            # Download button for context
            if st.download_button(
                label="📥 Download Context",
                data=context,
                file_name="clinical_context.txt",
                mime="text/plain"
            ):
                st.success("Context downloaded successfully!")
        
        # Display Answer
        if st.session_state.show_answer:
            st.markdown("### Answer")
            answer = st.session_state.rag_response.split("Answer:")[1].strip()
            st.markdown(answer)
    else:
        st.info("No clinical information available yet.")
    
    # Appointment booking
    st.subheader("Book an Appointment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Book In-Person Visit"):
            st.info("Redirecting to appointment booking system...")
            # Add actual booking logic here
    
    with col2:
        if st.button("Schedule Telemedicine"):
            st.info("Redirecting to telemedicine scheduling...")
            # Add actual telemedicine scheduling logic here
    
    # Reset button
    if st.button("Start New Assessment"):
        st.session_state.current_step = 'initial'
        st.session_state.symptoms = {}
        st.session_state.severity = {}
        st.session_state.duration = {}
        st.session_state.body_parts = []
        st.session_state.chat_history = []
        st.session_state.gemini_response = None
        st.session_state.rag_response = None
        st.session_state.show_context = False
        st.session_state.show_answer = False
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>DiReCT - AI-Powered Medical Assistant</p>
        <p>Built with ❤️ for better healthcare</p>
        <p>Disclaimer: This is an AI assistant and not a replacement for professional medical advice.</p>
    </div>
""", unsafe_allow_html=True)