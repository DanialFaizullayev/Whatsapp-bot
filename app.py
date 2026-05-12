import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

user_histories = {}

SYSTEM_PROMPT = """You are a helpful AI assistant for a local business in Shymkent, Kazakhstan.
Answer customer questions clearly and politely.
Reply in the same language the customer writes in (Kazakh, Russian, or English).
Be concise — this is WhatsApp, keep answers short and clear."""

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    if sender not in user_histories:
        user_histories[sender] = []

    user_histories[sender].append({"role": "user", "content": incoming_msg})
    history = user_histories[sender][-10:]

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history
        )
        reply = response.choices[0].message.content
        user_histories[sender].append({"role": "assistant", "content": reply})

    except Exception as e:
        reply = "Извините, произошла ошибка. Попробуйте позже."
        print(f"Error: {e}")

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)