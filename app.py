import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from models import db, JournalEntry, Resource
from dotenv import load_dotenv
from textblob import TextBlob
import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mind-care-secret-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mind_care.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Helper for Chatbot Logic
def get_chatbot_response(user_input):
    user_input = user_input.lower()
    blob = TextBlob(user_input)
    sentiment = blob.sentiment.polarity
    
    # Crisis Detection
    crisis_keywords = ['suicide', 'kill myself', 'end my life', 'don\'t want to live', 'harm myself']
    if any(k in user_input for k in crisis_keywords):
        return "I'm very concerned about what you're sharing. Please reach out to a professional or a crisis hotline immediately. You are not alone. (US: 988, UK: 111)"

    # Keyword mapping
    responses = {
        'anxiety': "It sounds like you're feeling anxious. Try a 4-7-8 breathing exercise: inhale for 4, hold for 7, exhale for 8. It can help calm your nervous system.",
        'anxious': "It sounds like you're feeling anxious. Try a 4-7-8 breathing exercise: inhale for 4, hold for 7, exhale for 8. It can help calm your nervous system.",
        'panic': "If you're having a panic attack, try the 5-4-3-2-1 grounding technique: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, and 1 you can taste.",
        'depress': "I'm sorry you're feeling this way. Sometimes when things feel heavy, just focusing on one small task can help. Have you spoken to anyone about these feelings?",
        'sad': "I hear that you're feeling sad. It's okay to let yourself feel that. Would you like to try journaling about it in our Journal section?",
        'stress': "Stress can be overwhelming. Take a moment to step away from what you're doing. A short walk or a glass of water can make a difference.",
        'lonely': "Feeling lonely is tough. Remember that seeking connection is a human need. Is there a friend or family member you could send a quick text to?",
        'sleep': "Struggling with sleep? Try to limit screen time before bed and keep your room cool and dark. Deep breathing can also help ready your body for rest.",
        'help': "I'm here to listen and provide support techniques. If you need medical help, please consult a professional.",
        'hello': "Hello! I'm your Mind Care assistant. How are you feeling today?",
        'hi': "Hi there! I'm here to support you. What's on your mind?",
        'thanks': "You're very welcome. I'm glad I could be here for you.",
        'thank you': "You're very welcome. I'm glad I could be here for you.",
    }

    # Check for keywords
    for key in responses:
        if key in user_input:
            return responses[key]

    # Sentiment-based fallback
    if sentiment < -0.5:
        return "I can feel that you're going through a very hard time. Please be kind to yourself. Would you like to check out some coping techniques?"
    elif sentiment < 0:
        return "I'm sorry you're feeling down. I'm here to listen. Tell me more, or check our resources for support."
    elif sentiment > 0.5:
        return "I'm so glad to hear you're feeling positive! Keep nurturing that mindset."
    
    return "Thank you for sharing that with me. I'm here to support your mental well-being. Have you tried any grounding exercises today?"

# Initial Database Creation
with app.app_context():
    db.create_all()
    # Seed resources if empty
    if not Resource.query.first():
        sample_resources = [
            Resource(title="National Suicide Prevention Lifeline", description="24/7, free and confidential support for people in distress.", link="https://icallhelpline.org/"),
            Resource(title="MindIndia.org", description="Provides advice and support to empower anyone experiencing a mental health problem.", link="https://mindindia.org/home"),
            Resource(title="Headspace", description="Guided meditation and mindfulness for everyday life.", link="https://www.headspace.com/"),
            Resource(title="India Mental Health Alliance (IMHA)", description="Resources for various mental health conditions and support groups.", link="https://indiamentalhealthalliance.org/")
        ]
        db.session.bulk_save_objects(sample_resources)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    # if 'chat_history' not in session:
    #     session['chat_history'] = [
    #         {'role': 'bot', 'content': 'Hello! I am your Mind Care assistant. How can I help you today?'}
    #     ]
    
    # if request.method == 'POST':
        # user_message = request.form.get('message')
        # if user_message:
        #     # Add user message
        #     history = session['chat_history']
        #     history.append({'role': 'user', 'content': user_message})
            
        #     # Get bot response
        #     bot_response = get_chatbot_response(user_message)
        #     history.append({'role': 'bot', 'content': bot_response})
            
        #     session['chat_history'] = history
    
    # return render_template('chatbot.html', chat_history=session['chat_history'])
    return redirect('https://6dadfe40205b5beebf.gradio.live/')

@app.route('/chatbot/clear')
def clear_chat():
    session.pop('chat_history', None)
    return redirect(url_for('chatbot'))

@app.route('/journal', methods=['GET', 'POST'])
def journal():
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            new_entry = JournalEntry(content=content)
            db.session.add(new_entry)
            db.session.commit()
            flash('Journal entry saved successfully!', 'success')
            return redirect(url_for('journal'))
    
    entries = JournalEntry.query.order_by(JournalEntry.created_at.desc()).all()
    return render_template('journal.html', entries=entries)

@app.route('/resources')
def resources():
    all_resources = Resource.query.all()
    return render_template('resources.html', resources=all_resources)

@app.route('/techniques')
def techniques():
    return render_template('techniques.html')

@app.route('/breathing')
def breathing():
    return render_template('breathing.html')

@app.route('/grounding')
def grounding():
    return render_template('grounding.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
