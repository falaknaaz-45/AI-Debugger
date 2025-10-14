🧠 AI Debugger (LLM-Powered via OpenRouter)
🎯 Overview

AI Debugger is a multi-language intelligent debugging tool that automatically analyzes, explains, and fixes programming and document errors.
It integrates local static analysis with a Large Language Model (LLM) via OpenRouter API for maximum accuracy — covering syntax, logic, style, and grammar across multiple languages.

🧩 Supported Languages

🐍 Python

☕ Java

💻 C++

📝 Text / Markdown Documents

⚙️ Features

✅ Detects syntax & compilation errors using local tools (javac, g++, pylint)
✅ Finds logical issues, style violations, and bad formatting
✅ Suggests and auto-applies fixes
✅ Grammar & spelling corrections for documents
✅ Integrates with OpenRouter LLM for reasoning & corrections
✅ Works on Google Colab or locally (no paid API needed)

🧰 Tech Stack

Python 3.x

OpenRouter API (LLM Integration)

Local tools: javac, g++, pylint, black, language-tool-python

🚀 How to Run

Clone the repository:

git clone https://github.com/<your-username>/AI-Debugger.git
cd AI-Debugger


Install dependencies:

pip install -r requirements.txt


Add your OpenRouter API key:

OPENROUTER_API_KEY = "sk-or-your-key-here"


Run the debugger:

python main.py


Choose language → Paste code → Select Analyze + Auto-Fix

🧪 Example Output
syntax_errors:
  - getTitle is missing parentheses
logical_issues:
  - rentVideo called without arguments
fixed_code:
  public String getTitle() { return title; }

🧠 Architecture

Frontend: CLI (command-line interface)

Backend: Python logic for local static checks and LLM requests

AI Engine: OpenRouter’s Mistral / LLaMA model

Output: JSON + formatted text (with syntax, logic, and style results)

📄 License

MIT License © 2025 Falak Irfan
