# app.py
from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import logging
import PyPDF2
import torch 
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/' 
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf'}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model_path = 'models/roberta-base'  
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForQuestionAnswering.from_pretrained(model_path)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def read_file_content(file_path):
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

        return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise

def answer_question(content, question):
    inputs = tokenizer(question, content, return_tensors='pt', truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
        answer_start = torch.argmax(outputs.start_logits)
        answer_end = torch.argmax(outputs.end_logits) + 1
        answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs.input_ids[0][answer_start:answer_end]))
    print("Inputs:", inputs)
    print("Outputs:", outputs)
    print("Answer Start Index:", answer_start)
    print("Answer End Index:", answer_end)

    return answer

@app.route('/')
def index():
    return render_template('index.html')

def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(file_path)
    content = read_file_content(file_path)
    question = request.form.get('question')
    answer = answer_question(content, question)
    return jsonify({"answer": answer}), 200

if __name__ == '__main__':
    app.run(debug=True)
