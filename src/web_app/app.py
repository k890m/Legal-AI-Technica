# app.py
from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import re
from datetime import datetime
import PyPDF2
import docx
import logging

app = Flask(__name__, static_folder='static')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def read_file_content(file_path):
    """Read content from different file types."""
    file_extension = file_path.split('.')[-1].lower()
    content = ""
    
    try:
        if file_extension == 'txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        
        elif file_extension == 'pdf':
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
        
        elif file_extension == 'docx':
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
        
        return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise

def extract_info(content):
    """Extract relevant information from the contract text."""
    info = {
        "dates": [],
        "amounts": [],
        "parties": [],
        "emails": [],
        "phone_numbers": [],
        "key_clauses": {}
    }
    
    # Regular expressions for pattern matching
    patterns = {
        'dates': r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',
        'amounts': r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?',
        'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phones': r'\b\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        'parties': r'(?:between|party|client|contractor|vendor|supplier|customer)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
    }
    
    # Extract patterns
    for key, pattern in patterns.items():
        matches = re.findall(pattern, content)
        if key == 'parties':
            info['parties'] = list(set([m.strip() for m in matches if m.strip()]))
        else:
            info[key if key != 'phones' else 'phone_numbers'] = list(set(matches))
    
    # Extract key clauses
    clauses = {
        'termination': r'(?i)(?:termination|terminate).*?(?:\.|$)',
        'payment': r'(?i)(?:payment terms?|compensation).*?(?:\.|$)',
        'confidentiality': r'(?i)(?:confidential|confidentiality).*?(?:\.|$)',
        'liability': r'(?i)(?:liability|indemnification).*?(?:\.|$)'
    }
    
    for clause_type, pattern in clauses.items():
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        if matches:
            info['key_clauses'][clause_type] = [m.strip() for m in matches[:2]]  # Limit to first 2 matches
    
    return info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        # Create upload folder if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save and process file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Read content and extract information
            content = read_file_content(file_path)
            extracted_info = extract_info(content)
            
            # Clean up - delete the uploaded file
            os.remove(file_path)
            
            return jsonify(extracted_info)
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"error": "Error processing file content"}), 500
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
