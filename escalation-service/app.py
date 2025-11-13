import time
import json
import pika
from flask import Flask, jsonify

app = Flask(__name__)

RABBITMQ_HOST = "rabbitmq"
QUEUE_NAME = "chatbot_queue"

messages_log = []

def analyze_message(message: str):
    keywords = ["problem", "issue", "error", "help", "urgent"]
    escalate = any(kw in message.lower() for kw in keywords)
    reason = "keyword matched" if escalate else "normal"
    return escalate, reason

def connect_with_retry():
    """Keeps trying to connect until RabbitMQ is ready."""
    while True:
        try:
            print("[INFO] Trying to connect to RabbitMQ...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            print("[INFO] ✅ Connected to RabbitMQ!")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("[WARN] RabbitMQ not ready. Retrying in 5 seconds...")
            time.sleep(5)

def start_consumer():
    """Consume messages from RabbitMQ with auto-reconnect."""
    while True:
        try:
            connection = connect_with_retry()
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            print("[INFO] ✅ Starting consumer on chatbot_queue")

            def callback(ch, method, properties, body):
                data = json.loads(body.decode())
                msg = data.get("message", "")
                print(f"[RECEIVED] {msg}")

                escalate, reason = analyze_message(msg)
                messages_log.append({
                    "message": msg,
                    "escalate": escalate,
                    "reason": reason
                })

                print(f"[RESULT] Escalate={escalate}, Reason={reason}")
                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
            channel.start_consuming()

        except Exception as e:
            print("[ERROR] Consumer crashed, reconnecting...", e)
            time.sleep(5)

# ✅ Home route (no more 404 on /)
@app.route("/")
def home():
    return "Escalation Service is running!"

# ✅ Test route
@app.route("/test")
def test():
    return jsonify({"status": "Escalation service alive"})

# ✅ Recent messages route
@app.route("/recent")
def recent():
    return jsonify(messages_log[-20:])  # last 20 messages

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=start_consumer)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=8081)
