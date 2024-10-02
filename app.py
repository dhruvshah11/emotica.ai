import os
import base64  # Import base64
from flask import Flask, render_template, request, jsonify
from transformers import BertTokenizer, TFBertForSequenceClassification
import tensorflow as tf
import cv2
import face_recognition  # Or your preferred facial analysis library
import numpy as np
import json  # For handling JSON data
import requests # For gemini


app = Flask(__name__)

#Load the BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('monologg/bert-base-cased-goemotions-original')
#Use from_pt=True to load PyTorch weights into the TensorFlow model
model = TFBertForSequenceClassification.from_pretrained('monologg/bert-base-cased-goemotions-original', num_labels=28, from_pt=True)

# Emotion labels (Make sure this is defined)
emotion_labels = [
    'admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring', 'confusion', 'curiosity',
    'desire', 'disappointment', 'disapproval', 'disgust', 'embarrassment', 'excitement', 'fear',
    'gratitude', 'grief', 'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization', 'relief',
    'remorse', 'sadness', 'surprise', 'neutral'
]


GEMINI_API_KEY = os.environ.get("AIzaSyACOykGzBxR_SbVC5wuohk3se99clfkL-g")



# Placeholder for microexpression detection function (will be implemented later)
def detect_microexpressions(frame):
    # ... (Implementation for microexpression detection using face_recognition or other library) ...
    # For now, return a dummy stress level
    stress_level = np.random.rand()  # Replace with actual stress level calculation
    return stress_level

def detect_emotion(text, stress_level):
    # ... (Your existing code to get logits) ...

    # Refine the logic here (more specific example)
    if stress_level > 0.7:
        try:  # Add try-except for error handling during indexing
            negative_emotion_indices = [emotion_labels.index(emotion) for emotion in ['anger', 'annoyance', 'fear']]
            for index in negative_emotion_indices:
                logits[0][index] += stress_level * 2  # You'll need to fine-tune these weightings/thresholds!
        except ValueError as e: # If any of those emotions are not present
          print("Error: " + str(e)) # Catch the error


    predicted_class = tf.argmax(logits, axis=-1)
    emotion = emotion_labels[int(predicted_class[0].numpy())] # safer access
    return emotion


advice = {
'admiration': "You're feeling admiration! It’s great to recognize and appreciate others. Consider telling the person or thing you admire how they’ve inspired you.",

'amusement': "You're amused! Laughter is a wonderful way to relieve stress. Share the source of your amusement with a friend or take some time to enjoy the lighter side of life.",

'anger': "You're feeling angry. Take a few moments to breathe deeply and step away from the source of frustration. Physical exercise or writing down your thoughts can help clear your mind.",

'annoyance': "It seems something is bothering you. Acknowledge the feeling but try to focus on a solution. Small irritations can be handled by redirecting your attention or taking a break.",

'approval': "You're feeling approval! Offering genuine feedback can strengthen relationships. Consider letting others know that their efforts are recognized and appreciated.",

'caring': "You're feeling caring! That compassion is powerful. Reach out to someone who may need support or engage in a kind act today.",

'confusion': "You're confused. That's okay. Try breaking the situation into smaller parts to understand what’s unclear. Talking to someone or doing more research can provide clarity.",

'curiosity': "You're feeling curious! Curiosity is the start of all learning. Take this opportunity to explore new topics, read, or experiment with a new hobby or skill.",

'desire': "You're feeling desire. Use this feeling to set clear goals and work toward them. Channel your drive into action steps to make it a reality.",

'disappointment': "You're feeling disappointed. Reflect on what happened and how you can move forward. Tomorrow is another chance.",

'disapproval': "You’re feeling disapproval. Think about why this feeling arose, and if it’s important, express your concerns constructively.",

'disgust': "You're feeling disgusted. Identify the source of this feeling and why it triggered such a reaction. Consider distancing yourself from the cause if it's within your control.",

'embarrassment': "You're feeling embarrassed. Remember, everyone makes mistakes! Laughing at yourself or acknowledging what happened with humility can turn the situation around.",

'excitement': "You're excited! Use that positive energy to fuel your next move. Whether it's starting a new project or sharing your enthusiasm with others, keep that momentum going!",

'fear': "You're feeling scared. Fear is natural, but grounding yourself can help. Focus on deep breathing, positive self-talk, or reaching out to someone who can reassure you.",

'gratitude': "You're feeling grateful. Take a moment to reflect on the things you appreciate. Consider expressing your thanks to those who’ve positively impacted your life.",

'grief': "You're grieving. Allow yourself to feel the pain, and don't rush the process. Reach out to someone you trust or engage in activities that bring you comfort.",

'joy': "You're feeling joyful! Embrace the happiness and spread it to those around you. Take a moment to savor the feeling and think about what made you so happy.",

'love': "You're feeling love. Take time to nurture and express this love in a meaningful way, whether it’s for someone else or something you're passionate about.",

'nervousness': "You're feeling nervous. Remember that nerves show you care about the outcome. Deep breathing exercises, mindfulness, or talking to someone can help ease your anxiety.",

'optimism': "You're feeling optimistic! This is a great mindset for tackling challenges. Use your optimism to set goals, inspire others, and keep pushing forward.",

'pride': "You're feeling proud! Reflect on your accomplishments and enjoy the moment. You've earned it. Use this confidence to continue achieving great things.",

'realization': "You're having an important realization. Take time to understand what this means for you. These moments can be life-changing, so embrace the clarity.",

'relief': "You're feeling relief! Take a deep breath and enjoy the release of tension. Now that the pressure has eased, consider doing something calming or rewarding for yourself.",

'remorse': "You're feeling remorseful. It’s good to recognize mistakes, but don’t dwell in guilt. Apologize if needed and focus on learning from the experience to move forward.",

'sadness': "You're feeling sad. Take time to rest and reflect, and consider reaching out to someone who can provide comfort. Doing something that brings you joy can help too.",

'surprise': "You're surprised! Whether it's good or bad, give yourself a moment to process it. If it's positive, enjoy the excitement. If it's challenging, stay calm and approach it with an open mind.",

'neutral': "You're feeling neutral. It's a steady, balanced emotion. Use this calm moment to focus on your wellbeing, plan your next steps, or simply enjoy the peace of mind."

}

def get_gemini_response(text, stress_level):
    if GEMINI_API_KEY is None:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return "I'm having trouble processing your request right now."

    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = { #Refine the prompt further if needed
        "text": f"User: {text}\n(Stress Level: {stress_level:.2f})\nSupportive and helpful Bot:"
    }
    try:
      response = requests.post(
            "https://api.generativeai.google.com/v1beta2/models/gemini-pro:generateText",  # Correct Gemini endpoint
            headers=headers,
            json={"prompt": prompt} # Check Gemini API documentation for exact required format
        ).json()
      gemini_text = response['candidates'][0]['output']
      return gemini_text
    except Exception as e:
        print(f"Error in Gemini API call: {e}")
        return "I'm having trouble processing your request right now." # Fallback


@app.route("/", methods=["GET"])  # Use only one home() route - methods should be ["GET"]
def home():
    return render_template("index.html")



@app.route('/get_emotion', methods=['POST'])
def get_emotion():
    try:
      data = request.get_json()
      user_message = data.get('message') # Handle possibly missing data in the requests.
      image_data = data.get('image_data')
      # Ensure the incoming request has the correct structure


        # Error handling: make sure to convert byte string into utf-8 or ascii first
      decoded_data = base64.b64decode(image_data.split(',')[1]) if image_data and ',' in image_data else None
      
        # Convert base64 to image (error handling here too)
      if decoded_data is not None:
          nparr = np.frombuffer(decoded_data, np.uint8)
          img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
          stress_level = detect_microexpressions(img)

      else:
        stress_level = 0



      emotion_detected = detect_emotion(user_message, stress_level)
      gemini_advice = get_gemini_response(user_message, stress_level)

      response = {
          'emotion': emotion_detected,
          'advice': gemini_advice if gemini_advice is not None else  "Working on it..." # Avoid sending advice if it does not exist.
      }
      return jsonify(response)


    except (KeyError, json.JSONDecodeError) as e: #Catching errors while processing the request, particularly KeyError: 'message'
      return jsonify({"error": "Invalid request format. Please provide both 'message' and 'image_data'."}), 400 # Status code 400 for bad request
    except Exception as e: # All other Exceptions
        print(f"An error occurred: {str(e)}") #Printing for your reference. 
        return jsonify({"error": "An internal server error occurred."}), 500 # Internal Server Error


if __name__ == '__main__':
    app.run(debug=True)

















