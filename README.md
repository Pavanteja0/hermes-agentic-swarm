# Hermes-Swarm: Autonomous Multi-Agent Software Engineering Swarm 🐝💻

**Hermes-Swarm** is a production-grade, state-persisting Multi-Agent Software Engineering Swarm designed to autonomously **design, write, test, debug, and document** entire applications from a single high-level user prompt.

It is built specifically on top of the **Hermes Agent Framework (by Nous Research)**, leveraging programmatic tool-assisted runs, CLI subprocess wrappers, and the beautiful terminal rendering capabilities of `rich`.

---

## 🏗️ System Architecture

```
                                  +-------------------+
                                  |    User Prompt    |
                                  +---------+---------+
                                            |
                                            v
                                  +---------+---------+
                                  | Swarm Orchestrator| <====== (state.json database)
                                  +---------+---------+
                                            |
         +----------------------------------+----------------------------------+
         |                                  |                                  |
         v                                  v                                  v
+-------------------+              +-------------------+              +-------------------+
|  Lead Architect   |              | Senior Developer  |              |    QA Engineer    |
| ----------------- |              | ----------------- |              | ----------------- |
| • Formulates Spec |              | • Pulls Next      |              | • Discovers Tests |
| • Compiles Tech   |              |   Pending Ticket  |              | • Runs test cmd   |
|   Folder Tree     | ------------>| • Writes Clean,   | ------------>| • Recursive Bug-  |
| • Spawns Markdown |              |   Documented Code |              |   Patch Loop      |
|   Tickets Backlog |              | • Verifies Files  |              | • Certifies green |
+-------------------+              +-------------------+              +-------------------+
                                                                                |
                                                                                v
                                                                      +-------------------+
                                                                      | Technical Writer  |
                                                                      | ----------------- |
                                                                      | • Scans Codebase  |
                                                                      | • Formulates Docs |
                                                                      | • Writes elegant  |
                                                                      |   README.md       |
                                                                      +-------------------+
```

---

## 🌟 Core Engineering Features

### 1. Robust Workspace Separation & File-Driven State
Instead of managing state inside high-risk in-memory LLM structures, the orchestrator utilizes **file-driven state isolation**.
- It creates `.hermes-swarm/` inside the target project workspace.
- The **Lead Architect** creates structural tickets under `.hermes-swarm/tickets/`.
- The **Developer** picks up tickets, writes code, and appends `# STATUS: COMPLETED` directly to the ticket files. This ensures high robustness: if an agent execution crashes or is aborted, it can resume **exactly where it left off** because states are persisted to disk.

### 2. Quiet, Autonomous Run-Configurations
The swarm leverages custom options from the `hermes chat` CLI to execute tasks 100% autonomously:
```bash
hermes chat -q "{PROMPT}" --oneshot -Q --yolo --in {WORKSPACE_DIR}
```
- `--oneshot`: Runs the query and exits non-interactively.
- `-Q` (Quiet Mode): Suppresses terminal spinners, console headers, and decorative elements to output pure, parseable responses.
- `--yolo`: Bypasses all dangerous system command approval gates, letting agents build, install, and execute test commands freely.

### 3. Recursive Debugging Loop (QA Agent Self-Correction)
The **QA Engineer** doesn't just run tests and report errors. It runs a **recursive correction loop**:
1. Scans codebase for test configurations (`pytest.ini`, `setup.cfg`, `test_*.py`).
2. Discovers and runs the test suite.
3. If test failure tracebacks occur, it captures the raw logs, reads them, edits the file contents using targeted write/patch tools, and re-runs the tests.
4. Repeat until the suite passes 100% green.

### 4. Rich Terminal Dashboard (TUI)
An enterprise-grade, color-coded, live terminal dashboard keeps the user updated on the swarm's activity, displaying:
- Target workspace path, swarm phase, and global execution status.
- **Active Node Card**: Describing the current agent personality and what action it is running.
- **Ticket Backlog Table**: Showing list of all architectural tickets and real-time status updates (`PENDING` or `COMPLETED`).

---

## 🚀 Quick Start Guide

### Prerequisites
1. **Python 3.10+**
2. **Hermes Agent Framework**:
   ```bash
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
   ```
3. Set your preferred AI model provider API key (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or local setup).

### Installation
Clone this repository to your system:
```bash
git clone https://github.com/yourusername/hermes-swarm.git
cd hermes-swarm
pip install rich python-pptx
```

### Running the Swarm
To run the swarm, call `swarm.py` with your product prompt and the output directory:
```bash
python swarm.py "Build a Python FastAPI microservice for user management, with SQLite DB, password hashing via bcrypt, and basic unit tests using pytest" --dir ./my_api
```

---

## 📁 Repository Structure

```
hermes-swarm/
├── README.md               # Enterprise-grade project documentation
├── swarm.py                # Main state-machine Orchestrator & Rich TUI Console
├── agents.py               # Custom System Prompts & Prompts for specialized Agents
├── utils.py                # File managers, Ticket scanners, & Subprocess Hermes wrappers
```

---

## 💼 Why this is a Powerful Portfolio Piece

Hiring managers for **Agentic AI Engineer** roles look for tangible expertise in workflow design, prompt engineering, and subprocess control. This project stands out because:
- **No Heavy Libraries**: Avoids complex, opinionated agent frameworks (like LangChain or CrewAI) by utilizing the native CLI features of a highly reliable agent core (`hermes`).
- **Resilience**: The system design expects errors and handles them gracefully via state persistence (`state.json` + markdown files).
- **Practical Utility**: Produces fully working, compiled code, complete with passing tests and structural documentation rather than simple text descriptions.
