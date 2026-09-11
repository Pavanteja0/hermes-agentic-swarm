# C:\Users\KALYAN\hermes-swarm\swarm.py
"""
Hermes Multi-Agent Swarm Orchestrator.
Orchestrates Architect, Developer, QA, and Technical Writer agents to autonomously
build, debug, test, and document software systems from high-level user prompts.
"""

import os
import sys
import argparse
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Group

from utils import setup_workspace, load_state, save_state, run_hermes_agent, scan_tickets, console
import agents

def make_header_panel(project_name, status, step):
    """Generates the main title and status bar panel."""
    status_colors = {
        "INIT": "yellow",
        "RUNNING": "bold blue",
        "SUCCESS": "bold green",
        "FAILED": "bold red"
    }
    col = status_colors.get(status, "white")
    
    status_text = f"[{col}]{status}[/{col}]"
    step_text = f"[accent]{step}[/accent]"
    
    header_content = (
        f"[bold accent]HERMES MULTI-AGENT SWARM ORCHESTRATOR[/bold accent]\n"
        f"Target Project: [bold white]{project_name}[/bold white] | Swarm Status: {status_text} | Current Phase: {step_text}"
    )
    return Panel(Align.center(header_content), border_style="accent")

def make_agent_card(agent_name, role_badge, task_desc, status_msg="Idle"):
    """Generates a styled panel describing the active agent and what it is doing."""
    card_text = (
        f"Active Agent: {role_badge}\n"
        f"Task Description: [italic]{task_desc}[/italic]\n"
        f"Live Status: {status_msg}"
    )
    return Panel(card_text, title="Active Swarm Node", border_style="white")

def make_ticket_table(tickets):
    """Generates a beautifully styled table of design/implementation tickets."""
    table = Table(title="Software Implementation Backlog", expand=True)
    table.add_column("Ticket ID/File", justify="left", style="cyan")
    table.add_column("Feature Description", justify="left")
    table.add_column("Status", justify="center")
    
    if not tickets:
        table.add_row("-", "No design tickets generated yet.", "[yellow]WAITING ON ARCHITECT[/yellow]")
        return table
        
    for t in tickets:
        color = "green" if t["status"] == "COMPLETED" else "yellow"
        badge = f"[{color}]{t['status']}[/{color}]"
        table.add_row(t["filename"], t["name"].replace("_", " ").title(), badge)
    return table

def render_dashboard(project_name, state, tickets, active_agent=None, agent_badge="", agent_task="", agent_status=""):
    """Constructs the composite TUI layout of all panels."""
    header = make_header_panel(project_name, state.get("status", "INIT"), state.get("current_step", "N/A"))
    
    if active_agent:
        agent_card = make_agent_card(active_agent, agent_badge, agent_task, agent_status)
    else:
        agent_card = Panel("All agents currently idling. Waiting for state transition...", title="Active Swarm Node", border_style="dim white")
        
    backlog = make_ticket_table(tickets)
    
    # Bundle all components into a group
    return Group(header, agent_card, backlog)

def main():
    parser = argparse.ArgumentParser(description="Run the Hermes Multi-Agent Swarm.")
    parser.add_argument("prompt", type=str, help="High-level description of what you want the swarm to build.")
    parser.add_argument("--dir", type=str, default="./workspace", help="Target output workspace directory.")
    args = parser.parse_args()
    
    workspace_dir = setup_workspace(args.dir)
    state = load_state(workspace_dir)
    
    state["project_prompt"] = args.prompt
    state["status"] = "RUNNING"
    save_state(workspace_dir, state)
    
    tickets = scan_tickets(workspace_dir)
    
    console.print(f"[success]Workspace initialized at: {workspace_dir}[/success]")
    console.print(f"[info]Swarm state loaded. Starting orchestrator state machine...[/info]")
    
    # -------------------------------------------------------------------------
    # STATE MACHINE LOOP
    # -------------------------------------------------------------------------
    with Live(render_dashboard(state["project_name"], state, tickets), console=console, refresh_per_second=4) as live:
        
        # 1. ARCHITECT_PLAN
        if state["current_step"] == "ARCHITECT_PLAN":
            live.update(render_dashboard(
                state["project_name"], state, tickets,
                active_agent="Lead Architect",
                agent_badge="[badge_architect]ARCHITECT[/badge_architect]",
                agent_task="Analyzing requirements, planning folder hierarchy and drafting technical tickets.",
                agent_status="[yellow]Executing tool-assisted system architecture planning...[/yellow]"
            ))
            
            # Format the full prompt with high-level requirement
            prompt = agents.SYSTEM_PROMPT_HEADER.format(role="Lead System Architect") + agents.ARCHITECT_PROMPT.format(request=args.prompt)
            success, output = run_hermes_agent("Lead Architect", prompt, workspace_dir, "01_architect_plan")
            
            if not success:
                state["status"] = "FAILED"
                save_state(workspace_dir, state)
                live.update(render_dashboard(state["project_name"], state, tickets, agent_status="[danger]Architecture Phase Failed[/danger]"))
                console.print("[danger]Lead Architect run encountered an error. Check logs for details.[/danger]")
                return
                
            # Scan newly generated tickets
            tickets = scan_tickets(workspace_dir)
            state["current_step"] = "DEVELOPER_IMPLEMENT"
            save_state(workspace_dir, state)
            
        # 2. DEVELOPER_IMPLEMENT
        if state["current_step"] == "DEVELOPER_IMPLEMENT":
            while True:
                tickets = scan_tickets(workspace_dir)
                pending_tickets = [t for t in tickets if t["status"] == "PENDING"]
                
                if not pending_tickets:
                    # All tickets are finished, advance step
                    state["current_step"] = "QA_TEST"
                    save_state(workspace_dir, state)
                    break
                    
                active_ticket = pending_tickets[0]
                live.update(render_dashboard(
                    state["project_name"], state, tickets,
                    active_agent="Senior Developer",
                    agent_badge="[badge_developer]DEVELOPER[/badge_developer]",
                    agent_task=f"Implementing: {active_ticket['filename']}",
                    agent_status=f"[yellow]Coding feature files and implementing criteria for {active_ticket['name'].replace('_', ' ').title()}...[/yellow]"
                ))
                
                prompt = (
                    agents.SYSTEM_PROMPT_HEADER.format(role="Senior Software Developer") +
                    agents.DEVELOPER_PROMPT.format(
                        ticket_path=active_ticket["path"],
                        ticket_name=active_ticket["filename"]
                    )
                )
                
                # Run the developer on this ticket
                log_tag = f"02_develop_{active_ticket['name']}"
                success, output = run_hermes_agent("Senior Developer", prompt, workspace_dir, log_tag)
                
                if not success:
                    state["status"] = "FAILED"
                    save_state(workspace_dir, state)
                    live.update(render_dashboard(state["project_name"], state, tickets, agent_status=f"[danger]Developer failed on ticket: {active_ticket['filename']}[/danger]"))
                    console.print(f"[danger]Developer encountered error implementing {active_ticket['filename']}. Check logs for details.[/danger]")
                    return
                    
                # Read output / check files to ensure status updated
                tickets = scan_tickets(workspace_dir)
                live.update(render_dashboard(state["project_name"], state, tickets))
                
        # 3. QA_TEST
        if state["current_step"] == "QA_TEST":
            live.update(render_dashboard(
                state["project_name"], state, tickets,
                active_agent="Senior QA & Debugger",
                agent_badge="[badge_qa]QA ENGINEER[/badge_qa]",
                agent_task="Running full verification test suites, diagnosing issues, and patching codebase bugs.",
                agent_status="[yellow]Executing test suites and running recursive automated debugging loops...[/yellow]"
            ))
            
            prompt = agents.SYSTEM_PROMPT_HEADER.format(role="Senior QA & Debugger") + agents.QA_PROMPT
            success, output = run_hermes_agent("Senior QA", prompt, workspace_dir, "03_qa_verification")
            
            if not success:
                state["status"] = "FAILED"
                save_state(workspace_dir, state)
                live.update(render_dashboard(state["project_name"], state, tickets, agent_status="[danger]QA Phase Failed[/danger]"))
                console.print("[danger]QA Engineer run encountered an error. Check logs for details.[/danger]")
                return
                
            state["current_step"] = "TECHNICAL_WRITER"
            save_state(workspace_dir, state)
            
        # 4. TECHNICAL_WRITER
        if state["current_step"] == "TECHNICAL_WRITER":
            live.update(render_dashboard(
                state["project_name"], state, tickets,
                active_agent="Documentation Lead",
                agent_badge="[badge_doc]DOCUMENTATION[/badge_doc]",
                agent_task="Writing clean developer documentation, usage instructions, and polishing README.",
                agent_status="[yellow]Writing README.md, technical API references, and completing software handoff...[/yellow]"
            ))
            
            prompt = agents.SYSTEM_PROMPT_HEADER.format(role="Technical Writer") + agents.DOCUMENTER_PROMPT
            success, output = run_hermes_agent("Technical Writer", prompt, workspace_dir, "04_documentation_writer")
            
            if not success:
                state["status"] = "FAILED"
                save_state(workspace_dir, state)
                live.update(render_dashboard(state["project_name"], state, tickets, agent_status="[danger]Documentation Phase Failed[/danger]"))
                console.print("[danger]Technical Writer run encountered an error. Check logs for details.[/danger]")
                return
                
            # Finish complete run
            state["current_step"] = "COMPLETED"
            state["status"] = "SUCCESS"
            save_state(workspace_dir, state)
            live.update(render_dashboard(state["project_name"], state, tickets))
            
    # Final message outside the TUI loop
    console.print("\n[success]====================================================================[/success]")
    console.print(f"[success]🎉 CONGRATULATIONS! SWARM EXECUTION COMPLETED WITH 100% SUCCESS! 🎉[/success]")
    console.print(f"[success]====================================================================[/success]\n")
    console.print(f"Your project is fully designed, implemented, tested, and documented under:")
    console.print(f"📂 [bold cyan]{workspace_dir}[/bold cyan]\n")
    console.print(f"Detailed execution traces and logs can be audited inside:")
    console.print(f"📝 [bold cyan]{os.path.join(workspace_dir, '.hermes-swarm', 'logs')}[/bold cyan]")

if __name__ == "__main__":
    main()
