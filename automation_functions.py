import os
import webbrowser
import psutil  # For system monitoring
import subprocess

# Function to open applications
def open_chrome():
    webbrowser.open("https://www.google.com")

def open_calculator():
    os.system("calc" if os.name == "nt" else "gnome-calculator")

def get_cpu_usage():
    return f"CPU Usage: {psutil.cpu_percent()}%"

def get_ram_usage():
    return f"RAM Usage: {psutil.virtual_memory().percent}%"

def run_shell_command(command):
    return subprocess.getoutput(command)
