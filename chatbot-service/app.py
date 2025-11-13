from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ Import CORS
import pika
import os
import json

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])  # ✅ Enable CORS for your React frontend

# RabbitMQ env
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = "chatbot_queue"


def send_to_rabbitmq(message):
    """Sends user message to RabbitMQ queue."""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        channel = connection.channel()

        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps({"message": message}),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        connection.close()
    except Exception as e:
        print("RabbitMQ Error:", e)


def get_response(message):
    """Basic rule-based NLP logic."""
    msg = message.lower()

    if "course" in msg:
        return "You can find all course details here: https://university.edu/courses"
    elif "exam" in msg:
        return "Exam schedule: https://university.edu/exams"
    elif "timetable" in msg:
        return "Timetable link: https://university.edu/timetable"
    elif "fee" in msg:
        return "Fee details: https://university.edu/fees"
    elif "library" in msg:
        return "Library information: https://university.edu/library"
    else:
        return "Sorry, I didn't understand. Please ask about courses, fees, exams or timetable."


@app.route('/')
def home():
    return "✅ University Chatbot API is running!"


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"]

    # Send to RabbitMQ for escalation-service
    send_to_rabbitmq(user_message)

    # Local bot response
    reply = get_response(user_message)

    return jsonify({"reply": reply})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
