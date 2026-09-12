import os
from flask import Flask, render_template, request, jsonify
from groq import Groq

# Load .env file if present
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"\'')

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/simulate", methods=["POST"])
def simulate():
    data = request.json or {}
    prompt = data.get("prompt", "Build a Python FastAPI microservice for user management.")
    
    if not groq_client:
        return jsonify({
            "status": "success",
            "mode": "fallback",
            "logs": [
                f"[ARCHITECT] Analyzing prompt: '{prompt}'",
                "[ARCHITECT] Formulating architectural specification and ticket backlog...",
                "[ARCHITECT] Created 3 implementation tickets under .hermes-swarm/tickets/",
                "[DEVELOPER] Picking up Ticket 1: Database models & FastAPI setup...",
                "[DEVELOPER] Writing clean, documented code to main.py...",
                "[QA_ENGINEER] Discovering test suite and running pytest...",
                "[QA_ENGINEER] Test run passed 100% green!",
                "[TECHNICAL_WRITER] Generating comprehensive README.md documentation...",
                "[SWARM] Swarm execution completed successfully!"
            ]
        })
    
    try:
        system_prompt = (
            "You are Hermes-Swarm Orchestrator. Given a user software project prompt, simulate the step-by-step "
            "execution of 4 agents: [ARCHITECT], [DEVELOPER], [QA_ENGINEER], and [TECHNICAL_WRITER]. "
            "Output 6 to 8 concise, realistic log lines representing their execution steps."
        )
        
        # Use llama-3.1-70b-versatile which is active on Groq API
        completion = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Project Prompt: {prompt}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        response_text = completion.choices[0].message.content
        logs = [line.strip() for line in response_text.split("\n") if line.strip()]
        
        return jsonify({
            "status": "success",
            "model": "llama-3.1-70b-versatile",
            "logs": logs
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "logs": [f"[ERROR] Failed to query Groq API: {str(e)}", "[FALLBACK] Swarm continuing with default simulation sequence..."]
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
