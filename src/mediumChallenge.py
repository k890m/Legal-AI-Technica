import os
import json
import torch
import random
from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import numpy as np


model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../models/roberta-base'))
model = AutoModelForQuestionAnswering.from_pretrained(model_dir)
tokenizer = AutoTokenizer.from_pretrained(model_dir)

IOU_THRESH = 0.5


def load_test_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)['data']


def jaccard_similarity(answer, prediction):
    remove_tokens = [".", ",", ";", ":"]
    for token in remove_tokens:
        answer = answer.replace(token, "")
        prediction = prediction.replace(token, "")
    answer, prediction = answer.lower().split(), prediction.lower().split()

    intersection = set(answer).intersection(prediction)
    union = set(answer).union(prediction)
    return len(intersection) / len(union) if union else 0


def get_random_qa(data):
    contract = random.choice(data)
    para = random.choice(contract['paragraphs'])
    qa = random.choice(para['qas'])
    
    context = para['context']
    question = qa['question']
    is_impossible = qa['is_impossible']
    answers = [answer['text'] for answer in qa['answers']] if not is_impossible else ["None"]
    qa_id = qa['id']
    
    return {'context': context, 'question': question, 'answers': answers, 'id': qa_id, 'is_impossible': is_impossible}


def get_prediction(context, question, max_length=128):
    model.eval()

    inputs = tokenizer(
        question,
        context,
        return_tensors='pt',
        max_length=max_length,
        truncation=True,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)

    answer_start = outputs.start_logits.argmax()
    answer_end = outputs.end_logits.argmax() + 1

    predicted_text = tokenizer.decode(
        inputs['input_ids'][0][answer_start:answer_end],
        skip_special_tokens=True
    ).strip()

    return predicted_text if predicted_text else "None"


def calculate_metrics(prediction, ground_truths):
    match_found = any(
        jaccard_similarity(gt, prediction) >= IOU_THRESH for gt in ground_truths
    )

    if match_found:
        tp, fp, fn = 1, 0, 0
    elif ground_truths == ["None"]:
        tp, fp, fn = 0, 0, 0  
    else:
        tp, fp, fn = 0, 1, 1  

    precision = tp / (tp + fp) if (tp + fp) > 0 else np.nan
    recall = tp / (tp + fn) if (tp + fn) > 0 else np.nan

    return {"precision": precision, "recall": recall}


def evaluate_random_qa(test_data_path):
    test_data = load_test_data(test_data_path)
    qa_sample = get_random_qa(test_data)

    prediction = get_prediction(qa_sample['context'], qa_sample['question'])

    metrics = calculate_metrics(prediction, qa_sample['answers'])
    
    print(f"Question: {qa_sample['question']}")
    print(f"Context: {qa_sample['context']}")
    print(f"Ground Truth Answers: {qa_sample['answers']}")
    print(f"Predicted Answer: {prediction}")
    print(f"Precision: {metrics['precision']:.2f}, Recall: {metrics['recall']:.2f}")
    return metrics


test_data_path = './data/unzipped_data/test.json'
evaluate_random_qa(test_data_path)
