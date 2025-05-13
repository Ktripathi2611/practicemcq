from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import re
from datetime import datetime, timedelta
import random
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

QUESTIONS_PER_SET = 70

def parse_mcqs(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Split content into individual MCQs
    questions_raw = re.split(r'\n(?=\d+\s+)', content)
    mcqs = []
    
    for question_raw in questions_raw:
        if not question_raw.strip():
            continue
            
        try:
            mcq = {}
            
            # Extract question number and text
            match = re.match(r'(\d+)\s+(.*?)\n', question_raw)
            if match:
                mcq['number'] = int(match.group(1))
                mcq['question'] = match.group(2).strip()
            
            # Extract options
            options = re.findall(r'([A-D])[\.|\)]?\s+(.*?)(?=\n[A-D]|Answer|$)', question_raw, re.DOTALL)
            mcq['options'] = [text.strip() for _, text in options]
            
            # Extract answer
            answer_match = re.search(r'Answer\s+option\s*([A-Da-d])', question_raw, re.IGNORECASE)
            if answer_match:
                answer_letter = answer_match.group(1).upper()
                mcq['answer'] = str(ord(answer_letter) - ord('A') + 1)
            
            mcqs.append(mcq)
        except Exception as e:
            print(f"Error parsing question {mcq.get('number', 'unknown')}: {e}")
            continue
    
    return mcqs

def load_questions():
    return parse_mcqs('question.txt')

class UserProgress:
    def __init__(self):
        self.answers = {}  # {question_id: selected_option}
        self.correct_answers = {}  # {question_id: is_correct}
        self.bookmarks = set()  # set of bookmarked question IDs
        self.times = {}  # {question_id: time_taken}
        self.current_question = 0
        self.total_questions = 0
        self.current_set = 0
        self.set_stats = {}  # {set_id: {attempted: int, correct: int, avg_time: float}}
    
    def add_answer(self, question_id, selected_option, is_correct, time_taken):
        self.answers[question_id] = selected_option
        self.correct_answers[question_id] = is_correct
        self.times[question_id] = time_taken
        
        # Update set statistics
        set_id = question_id // QUESTIONS_PER_SET
        if set_id not in self.set_stats:
            self.set_stats[set_id] = {"attempted": 0, "correct": 0, "total_time": 0}
        
        self.set_stats[set_id]["attempted"] += 1
        if is_correct:
            self.set_stats[set_id]["correct"] += 1
        self.set_stats[set_id]["total_time"] += time_taken
        self.set_stats[set_id]["avg_time"] = self.set_stats[set_id]["total_time"] / self.set_stats[set_id]["attempted"]
    
    def get_stats(self):
        total_attempted = len(self.answers)
        total_correct = sum(1 for is_correct in self.correct_answers.values() if is_correct)
        accuracy = (total_correct / total_attempted * 100) if total_attempted > 0 else 0
        
        return {
            "total_attempted": total_attempted,
            "total_correct": total_correct,
            "accuracy": round(accuracy, 1),
            "bookmarked": len(self.bookmarks),
            "incorrect": total_attempted - total_correct,
            "sets": {
                set_id: {
                    "attempted": stats["attempted"],
                    "correct": stats["correct"],
                    "accuracy": round((stats["correct"] / stats["attempted"] * 100) if stats["attempted"] > 0 else 0, 1),
                    "avg_time": round(stats["avg_time"], 1)
                }
                for set_id, stats in self.set_stats.items()
            }
        }
    
    def toggle_bookmark(self, question_id):
        if question_id in self.bookmarks:
            self.bookmarks.remove(question_id)
            return False
        else:
            self.bookmarks.add(question_id)
            return True
    
    def get_review_questions(self):
        incorrect_questions = [q_id for q_id, is_correct in self.correct_answers.items() if not is_correct]
        return {
            "bookmarked": list(self.bookmarks),
            "incorrect": incorrect_questions
        }

@app.route('/')
def index():
    mcqs = load_questions()
    total_questions = len(mcqs)
    questions_per_set = QUESTIONS_PER_SET
    total_sets = (total_questions + questions_per_set - 1) // questions_per_set
    
    question_sets = []
    for i in range(total_sets):
        start_idx = i * questions_per_set
        end_idx = min((i + 1) * questions_per_set, total_questions)
        question_sets.append({
            'start_num': start_idx + 1,
            'end_num': end_idx,
            'total_questions': end_idx - start_idx
        })
    
    set_number = request.args.get('set')
    if set_number is None:
        return render_template('index.html', 
                            question_sets=question_sets,
                            selected_set=None)
    
    try:
        set_index = int(set_number) - 1
        if 0 <= set_index < len(question_sets):
            start_idx = set_index * questions_per_set
            end_idx = min((set_index + 1) * questions_per_set, total_questions)
            set_questions = mcqs[start_idx:end_idx]
            
            # Mark bookmarked questions
            for q in set_questions:
                q['bookmarked'] = str(q.get('number', '')) in session.get('user_progress', UserProgress()).bookmarks
            
            return render_template('index.html',
                                mcqs=set_questions,
                                selected_set=True,
                                current_set=set_index + 1,
                                total_sets=total_sets)
    except ValueError:
        pass
    
    return "Invalid set number", 404

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'user_progress' not in session:
        session['user_progress'] = UserProgress()
    
    data = request.get_json()
    question_id = data.get('question_id')
    selected_option = data.get('selected_option')
    time_taken = data.get('time_taken', 0)
    question_index = data.get('question_index')  # Get the actual question index
    
    # Get the correct answer for this question
    questions = load_questions()
    if question_id >= len(questions):
        return jsonify({"error": "Invalid question ID"}), 400
    
    question = questions[question_id]
    correct_option = int(question['answer']) - 1  # Convert 1-based to 0-based indexing
    is_correct = selected_option == correct_option
    
    # Update user progress
    progress = session['user_progress']
    progress.add_answer(question_id, selected_option, is_correct, time_taken)
    session['user_progress'] = progress
    
    return jsonify({
        "correct": is_correct,
        "correct_option": correct_option,
        "explanation": question.get('explanation', ''),
        "question_index": question_index  # Return the question index for frontend use
    })

@app.route('/bookmark', methods=['POST'])
def bookmark_question():
    data = request.get_json()
    question_id = data.get('question_id')
    
    if 'bookmarks' not in session:
        session['bookmarks'] = []
    
    bookmarks = session['bookmarks']
    
    if question_id in bookmarks:
        bookmarks.remove(question_id)
        is_bookmarked = False
    else:
        bookmarks.append(question_id)
        is_bookmarked = True
    
    session['bookmarks'] = bookmarks
    return jsonify({
        'success': True,
        'bookmarked': is_bookmarked,
        'message': 'Question bookmarked' if is_bookmarked else 'Bookmark removed'
    })

@app.route('/bookmarks')
def get_bookmarks():
    mcqs = load_questions()
    bookmarks = session.get('bookmarks', [])
    bookmarked_questions = [q for q in mcqs if q['number'] in bookmarks]
    return jsonify({
        'success': True,
        'bookmarks': bookmarked_questions
    })

@app.route('/stats')
def stats():
    progress = session.get('user_progress', UserProgress())
    stats_data = progress.get_stats()
    return render_template('stats.html', stats=stats_data)

@app.route('/review')
def review():
    progress = session.get('user_progress', UserProgress())
    mcqs = load_questions()
    
    # Get bookmarked questions
    bookmarked_questions = [
        q for q in mcqs 
        if str(q['number']) in progress.bookmarks
    ]
    
    # Get incorrect questions
    incorrect_questions = [
        q for q in mcqs 
        if str(q['number']) in progress.get_review_questions()['incorrect']
    ]
    
    return render_template('review.html', 
                         bookmarked=bookmarked_questions,
                         incorrect=incorrect_questions)

@app.route('/start_timer', methods=['POST'])
def start_timer():
    question_id = request.json.get('question_id')
    if 'timer_start' not in session:
        session['timer_start'] = {}
    session['timer_start'][str(question_id)] = datetime.now().isoformat()
    return jsonify({'status': 'success'})

@app.route('/get_time_remaining', methods=['POST'])
def get_time_remaining():
    question_id = request.json.get('question_id')
    time_limit = timedelta(minutes=2)  # 2 minutes per question
    
    if 'timer_start' not in session or str(question_id) not in session['timer_start']:
        return jsonify({'time_remaining': str(time_limit)})
    
    start_time = datetime.fromisoformat(session['timer_start'][str(question_id)])
    current_time = datetime.now()
    elapsed_time = current_time - start_time
    remaining_time = time_limit - elapsed_time
    
    if remaining_time.total_seconds() <= 0:
        return jsonify({'time_remaining': '0:00', 'expired': True})
    
    minutes = int(remaining_time.total_seconds() // 60)
    seconds = int(remaining_time.total_seconds() % 60)
    return jsonify({
        'time_remaining': f'{minutes}:{seconds:02d}',
        'expired': False
    })

@app.route('/start-quiz', methods=['POST'])
def start_quiz():
    mode = request.form.get('mode', 'quiz')
    session['quiz_mode'] = mode
    session['current_question'] = 0
    session['score'] = 0
    session['start_time'] = time.time()
    
    if mode == 'practice':
        session['time_limit'] = None  # No time limit in practice mode
    else:
        session['time_limit'] = 5400  # 90 minutes in seconds
    
    # Redirect to the first question
    return redirect(url_for('index', set=1))

if __name__ == '__main__':
    app.run(debug=True)
