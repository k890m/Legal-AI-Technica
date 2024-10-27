# app.py

# Import necessary modules
from flask import Flask, render_template, request, jsonify  # Flask modules for creating web applications and handling requests
import os  # Module for interacting with the operating system
from werkzeug.utils import secure_filename  # Utility to secure file uploads by validating filenames
import logging  # Module for event logging in applications
import PyPDF2  # Library for working with PDF files
import torch  # PyTorch, a deep learning library
from transformers import AutoTokenizer, AutoModelForQuestionAnswering  # Hugging Face Transformers for NLP models

# Initialize the Flask app
app = Flask(__name__)

# Configure upload folder and allowed file extensions
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Folder to save uploaded files
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf'}  # Allowed file types for upload

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load pre-trained model and tokenizer for question-answering
model_path = 'models/roberta-base'  # Specify model directory
tokenizer = AutoTokenizer.from_pretrained(model_path)  # Load tokenizer from the model path
model = AutoModelForQuestionAnswering.from_pretrained(model_path)  # Load the question-answering model

# Function to check if the uploaded file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to read and extract content from text or PDF files
def read_file_content(file_path):
    file_extension = file_path.split('.')[-1].lower()
    content = ""
    
    try:
        # Read content for a text file
        if file_extension == 'txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        
        # Read content for a PDF file
        elif file_extension == 'pdf':
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"  # Concatenate text from each page

        return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")  # Log any errors during file reading
        raise

# Function to find the answer to a question based on the extracted file content
def answer_question(content, question):
    # Tokenize the question and content for the model, truncating if necessary
    inputs = tokenizer(question, content, return_tensors='pt', truncation=True, max_length=512)
    
    with torch.no_grad():  # Run model inference without tracking gradients
        outputs = model(**inputs)  # Get the output from the model
        answer_start = torch.argmax(outputs.start_logits)  # Get the start index of the answer
        answer_end = torch.argmax(outputs.end_logits) + 1  # Get the end index of the answer
        # Convert the tokenized answer back to text
        answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs.input_ids[0][answer_start:answer_end]))
    
    print("Inputs:", inputs)  # Debug: Print inputs
    print("Outputs:", outputs)  # Debug: Print model outputs
    print("Answer Start Index:", answer_start)  # Debug: Start index
    print("Answer End Index:", answer_end)  # Debug: End index

    return answer

# Route to render the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file uploads and question-answering
def upload_file():
    # Check if the file part is present in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400  # Error if no file is selected

    # Create the upload directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Secure the filename and save the file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(file_path)
    
    # Extract content from the file
    content = read_file_content(file_path)
    question = request.form.get('question')  # Get the user's question from the form data
    answer = answer_question(content, question)  # Get the answer based on the file content
    return jsonify({"answer": answer}), 200  # Return the answer as a JSON response

# Run the app if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode for detailed error logs during development
