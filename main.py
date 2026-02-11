# =======================================================
# 🧠 AI Debugger & QA Assistant (Interactive Interface)
# Author: Zumer & ChatGPT
# Description: Multi-language intelligent debugger with color-coded UI
# =======================================================

import os, json, subprocess, textwrap, requests, gradio as gr
from shutil import which

# =======================================================
# 🔑 OPENROUTER API KEY (HARD-CODE YOURS HERE)
# =======================================================
OPENROUTER_API_KEY = "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"   # <--- 🔐 Replace with your real key
MODEL = "gpt-4o-mini"                         # ✅ Use GPT-4o-mini for best balance

# =======================================================
# 🧩 Helper: Run Commands
# =======================================================
def run_cmd(cmd, timeout=20):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

# =======================================================
# 🔍 Local Checks
# =======================================================
def python_checks(code):
    fname = "__tmp.py"
    open(fname, "w").write(code)
    result = {}
    try:
        compile(code, fname, "exec")
        result["syntax_ok"] = True
    except SyntaxError as e:
        result["syntax_ok"] = False
        result["error"] = f"SyntaxError (line {e.lineno}): {e.msg}"
    if which("pylint"):
        rc, out, err = run_cmd(f"pylint --disable=R,C --score=no {fname}")
        result["pylint"] = out.strip()
    else:
        result["pylint"] = "pylint not installed"
    os.remove(fname)
    return result

def java_checks(code):
    fname = "Main.java"
    open(fname, "w").write(code)
    rc, out, err = run_cmd("javac -Xlint Main.java")
    result = {"javac_output": (out + "\n" + err).strip(), "returncode": rc}
    try: os.remove("Main.class")
    except: pass
    return result

def cpp_checks(code):
    fname = "__tmp.cpp"
    open(fname, "w").write(code)
    rc, out, err = run_cmd("g++ -std=c++17 -fsyntax-only __tmp.cpp")
    return {"gpp_output": (out + "\n" + err).strip(), "returncode": rc}

def doc_checks(text):
    import language_tool_python
    tool = language_tool_python.LanguageTool("en-US")
    matches = tool.check(text)
    issues = [
        {"message": m.message, "suggestions": m.replacements, "context": m.context}
        for m in matches
    ]
    return {"issue_count": len(matches), "details": issues}

# =======================================================
# 🧠 Prompt Builder
# =======================================================
def build_prompt(language, code, checks):
    return f"""
You are an **AI Debugger and QA Expert**.
Your job is to analyze and improve the following {language} code or document.

You MUST always respond in **valid JSON** with these sections:
- syntax_errors
- logical_issues
- style_issues
- explanation
- fixed_code_or_text
- suggested_tests
- confidence

🧩 LOCAL CHECK RESULTS:
{json.dumps(checks, indent=2)}

🔍 CODE TO ANALYZE:
{code}

⚠️ RULES:
1. Always explain *why* each error occurs and *how* to fix it in 'explanation'.
2. Always include a full corrected version in 'fixed_code_or_text'.
3. Always use valid JSON. Nothing outside the JSON.
"""

# =======================================================
# 🌐 OpenRouter API Call
# =======================================================
def call_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2500,
        "temperature": 0.1
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if response.status_code != 200:
        return {"error": f"Request failed: {response.text}"}

    try:
        text = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return {"error": f"Response parse error: {e}", "raw": response.text}

    # extract JSON safely
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        json_str = text[start:end+1]
        try:
            return json.loads(json_str)
        except:
            import re
            cleaned = re.sub(r",\s*}", "}", json_str)
            cleaned = re.sub(r",\s*]", "]", cleaned)
            try:
                return json.loads(cleaned)
            except:
                return {"raw_output": text}
    return {"raw_output": text}

# =======================================================
# 🧩 Analyzer Function
# =======================================================
def analyze_code(language, code, autofix):
    if not code.strip():
        return "⚠️ Please paste your code!", "", ""

    # Local checks
    if language == "python":
        checks = python_checks(code)
    elif language == "java":
        checks = java_checks(code)
    elif language == "cpp":
        checks = cpp_checks(code)
    else:
        checks = doc_checks(code)

    prompt = build_prompt(language, code, checks)
    response = call_openrouter(prompt)

    # 🎨 Formatting for UI
    local_md = f"### 🧩 Local Checks\n```json\n{json.dumps(checks, indent=2)}\n```"

    if "error" in response:
        return local_md, f"❌ **Error:** {response['error']}", ""

    # Create colorful formatted sections
    model_md = "### 🤖 Model Analysis\n"
    if "syntax_errors" in response:
        model_md += "#### 🔴 Syntax Errors\n"
        for err in response["syntax_errors"]:
            model_md += f"- {err}\n"
    if "logical_issues" in response:
        model_md += "\n#### 🟡 Logical Issues\n"
        for issue in response["logical_issues"]:
            model_md += f"- {issue}\n"
    if "style_issues" in response:
        model_md += "\n#### 🔵 Style Issues\n"
        for style in response["style_issues"]:
            model_md += f"- {style}\n"
    if "explanation" in response:
        model_md += f"\n#### 🧠 Explanation\n{response['explanation']}\n"
    if "suggested_tests" in response:
        model_md += "\n#### 🧪 Suggested Tests\n"
        for test in response["suggested_tests"]:
            model_md += f"- {test}\n"
    if "confidence" in response:
        model_md += f"\n#### 📊 Confidence: {response['confidence']}%\n"

    fixed_md = ""
    if "fixed_code_or_text" in response:
        fixed_md = f"### ✅ Fixed Code / Text\n```{language}\n{response['fixed_code_or_text']}\n```"

    return local_md, model_md, fixed_md

# =======================================================
# 🎨 Gradio Interface
# =======================================================
title = "🧠 AI Debugger & QA Assistant"
desc = """
### 👋 Welcome to the Interactive AI Debugger  
Upload or paste your **Python / Java / C++ / Text** code to automatically:  
🔍 Detect errors, 💬 Explain them, and 🧩 Provide the fixed version.
"""

iface = gr.Interface(
    fn=analyze_code,
    inputs=[
        gr.Dropdown(["python", "java", "cpp", "doc"], label="Language", value="python"),
        gr.Textbox(label="Paste your code here", lines=15, placeholder="Paste your code..."),
        gr.Radio(["Analyze Only", "Analyze + Auto-Fix"], label="Action", value="Analyze + Auto-Fix")
    ],
    outputs=[
        gr.Markdown(label="Local Checks"),
        gr.Markdown(label="Model Analysis"),
        gr.Markdown(label="Fixed Code")
    ],
    title=title,
    description=desc,
    theme="soft",
    examples=[
        ["python", "print('Hello Word')", "Analyze + Auto-Fix"],
        ["java", "public clas Main { public static void main(String[] args) { System.out.println('Hi'); } }", "Analyze + Auto-Fix"]
    ],
)

iface.launch(share=True, debug=True)
