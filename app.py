import os
import random
from flask import Flask, render_template, request, jsonify
from ddgs import DDGS

app = Flask(__name__)

# Casual greetings/small-talk that should NOT trigger a web search
GREETINGS = {
    "hi", "hii", "hiii", "hello", "hey", "heya", "yo",
    "good morning", "good afternoon", "good evening", "good night",
    "how are you", "how are you doing", "what's up", "whats up", "sup",
    "who are you", "what are you",
}

GREETING_REPLIES = [
    "Hello! 👋 Ask me anything and I'll search the web for you.",
    "Hi there! What would you like to know?",
    "Hey! I'm ready when you are — ask me a question.",
]


def is_greeting(text):
    cleaned = text.lower().strip().strip("!?.")
    return cleaned in GREETINGS


def ask_ai(question, max_results=5):
    """Run a web search and shape the results into a simple answer + sources."""
    try:
        results = DDGS().text(question, max_results=max_results)
    except Exception as e:
        return {"error": f"Search failed: {e}"}

    if not results:
        return {"error": "No information found."}

    snippets = [r.get("body", "") for r in results if r.get("body")]
    sources = [
        {"title": r.get("title", "Untitled"), "url": r.get("href", "")}
        for r in results
    ]

    return {
        "question": question,
        "snippets": snippets,
        "sources": sources,
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Please type a question."}), 400

    # Casual greeting -> friendly reply, no web search needed
    if is_greeting(question):
        return jsonify({
            "question": question,
            "snippets": [random.choice(GREETING_REPLIES)],
            "sources": [],
        }), 200

    result = ask_ai(question)
    if "error" in result:
        return jsonify(result), 200

    return jsonify(result), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
