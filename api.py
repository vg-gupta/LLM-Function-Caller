from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import subprocess
import os
import shutil
import faiss
import pickle
from sentence_transformers import SentenceTransformer

app = FastAPI()

# ----------------- [ FAISS-based Function Retrieval ] -----------------

# Load FAISS index & function metadata
index = faiss.read_index("function_index.faiss")
with open("function_metadata.pkl", "rb") as f:
    function_metadata = pickle.load(f)

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def retrieve_best_function(user_query):
    """Search FAISS index to get best function match."""
    query_embedding = model.encode([user_query]).astype("float32")
    _, nearest_idx = index.search(query_embedding, 1)
    best_function = function_metadata[nearest_idx[0][0]]
    return best_function

# ----------------- [ Auto-Detect & Open Applications ] -----------------

COMMON_PATHS = [
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    f"C:\\Users\\{os.getlogin()}\\AppData\\Local",
    f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming",
]

def find_executable(app_name):
    """Find the executable path for an application."""
    exe_path = shutil.which(app_name)
    if exe_path:
        return exe_path

    for directory in COMMON_PATHS:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().startswith(app_name.lower()) and file.endswith(".exe"):
                    return os.path.join(root, file)

    return None  # No match found

# ----------------- [ HTML UI for User Input ] -----------------

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Function Executor</title>
        </head>
        <body>
            <h2>Enter a command:</h2>
            <input type="text" id="userInput" placeholder="e.g., open calculator or get time">
            <button onclick="sendRequest()">Execute</button>
            <p id="response"></p>

            <script>
                async function sendRequest() {
                    let userPrompt = document.getElementById("userInput").value;
                    let response = await fetch("/execute", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ prompt: userPrompt })
                    });
                    let data = await response.json();
                    document.getElementById("response").innerText = JSON.stringify(data, null, 2);
                }
            </script>
        </body>
    </html>
    """

# ----------------- [ Function Execution Endpoint ] -----------------
@app.post("/execute")
async def execute_function(request: dict):
    user_prompt = request.get("prompt", "").strip().lower()

    # 🔹 **Handle direct app open requests**
    if user_prompt.startswith("open "):
        app_name = user_prompt.replace("open ", "").strip()
        exe_path = find_executable(app_name)
        if exe_path:
            subprocess.Popen(exe_path, shell=True)
            return {"message": f"{app_name.capitalize()} opened!", "path": exe_path}
        return {"error": "Application not found. Try a valid app name."}

    # 🔹 **Exact function mappings**
    known_commands = {
        "notepad": "open_notepad",
        "chrome": "open_chrome",
        "calculator": "open_calculator",
        "get time": "get_time",
        "hello": "say_hello"
    }

    function_name = known_commands.get(user_prompt) or retrieve_best_function(user_prompt)

    if function_name:
        # 🔹 **Execute the correct function instead of just returning it**
        if function_name == "open_chrome":
            subprocess.Popen("chrome.exe", shell=True)
            return {"function": function_name, "output": "Google Chrome opened!"}
        elif function_name == "open_notepad":
            subprocess.Popen("notepad.exe", shell=True)
            return {"function": function_name, "output": "Notepad opened!"}
        elif function_name == "open_calculator":
            subprocess.Popen("calc.exe", shell=True)
            return {"function": function_name, "output": "Calculator opened!"}
        elif function_name == "get_time":
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {"function": function_name, "output": f"Current time is {current_time}"}
        elif function_name == "say_hello":
            return {"function": function_name, "output": "Hello! How can I help you?"}
        else:
            return {"error": "Function recognized but not yet implemented!"}

    return {"error": "No matching function found."}


# ----------------- [ Dynamic Code Generator ] -----------------

def generate_code(function_name):
    """Generate Python code dynamically for function execution."""
    function_library = {
        "get_time": """
def get_time():
    from datetime import datetime
    global output
    output = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
get_time()
""",
        "say_hello": """
def say_hello():
    global output
    output = "Hello, world!"
say_hello()
""",
        "square_number": """
def square_number():
    global output
    output = 5 * 5  # Example computation
square_number()
"""
    }

    return function_library.get(function_name, "output = 'Function not implemented'")

