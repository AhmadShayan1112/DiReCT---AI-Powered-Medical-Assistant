import os
from langchain.vectorstores import FAISS
from huggingface_hub import login
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'

# Import torch first to avoid circular imports
import torch
import bitsandbytes as bnb
from transformers import AutoModel, AutoTokenizer, BitsAndBytesConfig, AutoModelForCausalLM, pipeline
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

# Verify CUDA and GPU
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"BitsAndBytes version: {bnb.__version__}")
else:
    print("CUDA is not available. Please install CUDA-compatible PyTorch")

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)

# Load the embedding model
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
embedding = HuggingFaceEmbeddings(
    model_name=embedding_model_name,
    model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"}
)
print("Embedding model loaded successfully!")

# Load the Mistral model for generation
generation_model_name = "mistralai/Mistral-7B-Instruct-v0.2"
generation_tokenizer = AutoTokenizer.from_pretrained(generation_model_name)

if torch.cuda.is_available():
    generation_model = AutoModelForCausalLM.from_pretrained(
        generation_model_name,
        device_map="auto",
        quantization_config=quantization_config,
        trust_remote_code=True
    )
else:
    print("No GPU detected. Loading model with basic configuration...")
    try:
        generation_model = AutoModelForCausalLM.from_pretrained(
            generation_model_name,
            device_map="auto",
            torch_dtype=torch.float32,
            trust_remote_code=True
        )
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        print("Consider using a smaller model or enabling GPU runtime")
        raise

# Load generation pipeline
qa_pipeline = pipeline(
    "text-generation",
    model=generation_model,
    tokenizer=generation_tokenizer,
    device_map="auto"
)

print("Generation model loaded successfully!")

# Load vectorstore and setup retriever
try:
    vectorstore = FAISS.load_local("faiss_index", embedding, allow_dangerous_deserialization=True)
    print("Vectorstore loaded successfully!")
    
    # Login to Hugging Face
    login(token="Your_Hugging_face_token")
    
    # Setup retriever
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    print("Retriever setup complete!")
except Exception as e:
    print(f"Error loading vectorstore or setting up retriever: {str(e)}")

def answer_clinical_query(query):
    try:
        docs = retriever.get_relevant_documents(query)  # Using get_relevant_documents instead of invoke
        context = "\n".join([doc.page_content for doc in docs])
        prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        
        response = qa_pipeline(prompt, max_new_tokens=2000, num_return_sequences=1)
        return response[0]['generated_text']
    except Exception as e:
        print(f"Error in answer_clinical_query: {str(e)}")
        return "Sorry, I encountered an error while processing your query."

# Test the query
# query = input("Enter the query")
# response = answer_clinical_query(query)
# print(response)

