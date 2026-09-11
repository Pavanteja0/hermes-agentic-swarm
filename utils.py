# C:\Users\KALYAN\hermes-swarm\utils.py
"""
Utility functions for the Hermes Multi-Agent Swarm, including
workspace preparation, programmatic Hermes process execution, TUI helpers, and state tracking.
"""

import os
import sys
import json
import subprocess
import glob
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

# Setup Rich Console with custom colors
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "accent": "bold #DA7756",  # Terracotta
    "badge_architect": "bold #F59E0B", # Amber
    "badge_developer": "bold #3B82F6", # Blue
    "badge_qa": "bold #10B981",        # Emerald
    "badge_doc": "bold #8B5CF6",       # Purple
})
console = Console(theme=custom_theme)

def setup_workspace(workspace_dir):
    """Creates the required directories for tracking the swarm state."""
    workspace_dir = os.path.abspath(workspace_dir)
    os.makedirs(workspace_dir, exist_ok=True)
    
    swarm_dir = os.path.join(workspace_dir, ".hermes-swarm")
    os.makedirs(swarm_dir, exist_ok=True)
    os.makedirs(os.path.join(swarm_dir, "tickets"), exist_ok=True)
    os.makedirs(os.path.join(swarm_dir, "logs"), exist_ok=True)
    
    # Write a default state file if not existing
    state_path = os.path.join(swarm_dir, "state.json")
    if not os.path.exists(state_path):
        save_state(workspace_dir, {
            "project_name": os.path.basename(workspace_dir),
            "status": "INIT",
            "current_step": "ARCHITECT_PLAN",
            "completed_tickets": [],
            "failed": False
        })
    return workspace_dir

def save_state(workspace_dir, state_data):
    """Saves the global swarm state file."""
    state_path = os.path.join(workspace_dir, ".hermes-swarm", "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state_data, f, indent=2, ensure_ascii=False)

def load_state(workspace_dir):
    """Loads the global swarm state file."""
    state_path = os.path.join(workspace_dir, ".hermes-swarm", "state.json")
    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def run_hermes_agent(agent_name, prompt, workspace_dir, log_tag):
    """
    Invokes the Hermes CLI programmatically inside the workspace directory.
    Uses --oneshot, -Q (quiet), and --yolo flags to run completely autonomously.
    """
    workspace_dir = os.path.abspath(workspace_dir)
    log_dir = os.path.join(workspace_dir, ".hermes-swarm", "logs")
    log_file_path = os.path.join(log_dir, f"{log_tag}.log")
    
    # We find the hermes command path
    # On Windows, hermes might be in standard path. Let's use 'hermes' directly
    # and default to the current active environment launcher if available.
    cmd_base = "hermes"
    
    cmd = [
        cmd_base, "chat",
        "-q", prompt,
        "--oneshot",
        "-Q",
        "--yolo",
        "--in", workspace_dir
    ]
    
    # Save the prompt to the log first
    with open(log_file_path, "w", encoding="utf-8") as lf:
        lf.write(f"=== AGENT RUN: {agent_name} ===\n")
        lf.write(f"=== PROMPT ===\n{prompt}\n\n")
        lf.write("=== EXECUTION OUTPUT ===\n")
        lf.flush()
        
    try:
        # Use shell=True for Windows safety with MSYS path/commands resolution
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        output_buffer = []
        with open(log_file_path, "a", encoding="utf-8") as lf:
            for line in iter(process.stdout.readline, ""):
                lf.write(line)
                lf.flush()
                output_buffer.append(line)
                
        process.stdout.close()
        return_code = process.wait()
        
        output_text = "".join(output_buffer)
        
        if return_code != 0:
            console.print(f"[danger]Agent {agent_name} failed with return code {return_code}[/danger]")
            return False, output_text
            
        return True, output_text
        
    except Exception as e:
        err_msg = f"Failed to execute Hermes command: {str(e)}"
        console.print(f"[danger]{err_msg}[/danger]")
        with open(log_file_path, "a", encoding="utf-8") as lf:
            lf.write(f"\nEXCEPTION ERROR:\n{err_msg}\n")
        return False, err_msg

def scan_tickets(workspace_dir):
    """Scans and lists all ticket files and parses their current statuses."""
    tickets_dir = os.path.join(workspace_dir, ".hermes-swarm", "tickets")
    files = sorted(glob.glob(os.path.join(tickets_dir, "ticket_*.md")))
    
    tickets = []
    for filepath in files:
        filename = os.path.basename(filepath)
        status = "PENDING"
        
        # Read file to check if status is updated to completed
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                if "STATUS: COMPLETED" in content or "status: completed" in content.lower():
                    status = "COMPLETED"
        except Exception:
            pass
            
        tickets.append({
            "path": filepath,
            "filename": filename,
            "name": filename.replace(".md", "").replace("ticket_", ""),
            "status": status
        })
    return tickets
