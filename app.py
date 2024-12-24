from flask import Flask, render_template, request
import re
import math
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

def parse_mcqs(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Split content into individual MCQs
    questions_raw = re.split(r'\n(?=\d+\s+)', content)
    mcqs = []
    
    for question_raw in questions_raw:
        if not question_raw.strip() or question_raw.strip().lower() == 'evs questions':
            continue
            
        try:
            mcq = {}
            
            # Extract question number and text
            match = re.match(r'(\d+)\s+(.*?)\n', question_raw)
            if match:
                mcq['question'] = match.group(2).strip()
            
            # Extract options
            options = re.findall(r'([A-D])[\.|\)]?\s+(.*?)(?=\n[A-D]|Answer|$)', question_raw, re.DOTALL)
            mcq['options'] = []
            for letter, text in options:
                mcq['options'].append(text.strip())
            
            # Extract answer
            answer_match = re.search(r'Answer\s+option\s*([A-Da-d])', question_raw, re.IGNORECASE)
            if answer_match:
                # Convert answer letter to index (0-based)
                answer_letter = answer_match.group(1).upper()
                mcq['answer'] = str(ord(answer_letter) - ord('A') + 1)
            
            mcqs.append(mcq)
        except Exception as e:
            print(f"Error parsing question: {e}")
            continue
    
    return mcqs

def get_question_sets(mcqs, questions_per_set=70):
    total_questions = len(mcqs)
    total_sets = math.ceil(total_questions / questions_per_set)
    question_sets = []
    
    for i in range(total_sets):
        start_idx = i * questions_per_set
        end_idx = min((i + 1) * questions_per_set, total_questions)
        
        # Calculate total questions in this set
        set_questions = mcqs[start_idx:end_idx]
        
        question_sets.append({
            'questions': set_questions,
            'start_num': start_idx + 1,
            'end_num': end_idx,
            'total_questions': len(set_questions)
        })
    
    return question_sets

@app.route('/')
def index():
    try:
        questions_file = os.path.join(os.path.dirname(__file__), 'EVS Questions.txt')
        all_mcqs = parse_mcqs(questions_file)
        question_sets = get_question_sets(all_mcqs)
        
        # Get the requested set number from query parameters
        set_number = request.args.get('set')
        
        if set_number is None:
            return render_template('index.html', 
                                question_sets=question_sets,
                                selected_set=None)
        else:
            try:
                set_index = int(set_number) - 1
                if 0 <= set_index < len(question_sets):
                    current_set = question_sets[set_index]
                    return render_template('index.html',
                                        mcqs=current_set['questions'],
                                        selected_set=True,
                                        current_set=set_index + 1,
                                        total_sets=len(question_sets))
                else:
                    return "Invalid set number", 404
            except ValueError:
                return "Invalid set number", 404
    except Exception as e:
        return f"Error loading questions: {str(e)}", 500

# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
