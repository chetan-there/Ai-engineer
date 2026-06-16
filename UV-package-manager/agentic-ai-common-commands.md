# UV Cheat Sheet for Agentic AI Engineers

## 1. Create New Project

Command:

```bash
uv init ai-agent
```

Work:
Create a new Python project with pyproject.toml.

Example:

```bash
uv init job-application-agent
```

---

## 2. Enter Project

Command:

```bash
cd ai-agent
```

Work:
Move into project directory.

Example:

```bash
cd job-application-agent
```

---

## 3. Create Virtual Environment

Command:

```bash
uv venv
```

Work:
Create .venv virtual environment.

Example:

```bash
uv venv
```

---

## 4. Install Dependencies

Command:

```bash
uv add <package>
```

Work:
Install package and update pyproject.toml automatically.

Example:

```bash
uv add openai
uv add langchain
uv add fastapi
uv add pydantic
```

---

## 5. Install Multiple Packages

Command:

```bash
uv add package1 package2 package3
```

Work:
Install multiple dependencies together.

Example:

```bash
uv add openai langgraph fastapi uvicorn
```

---

## 6. Install Dev Dependencies

Command:

```bash
uv add --dev <package>
```

Work:
Install development tools.

Example:

```bash
uv add --dev pytest
uv add --dev black
uv add --dev ruff
```

---

## 7. Run Python Script

Command:

```bash
uv run file.py
```

Work:
Run Python file inside project environment.

Example:

```bash
uv run main.py
```

---

## 8. Run FastAPI Server

Command:

```bash
uv run uvicorn main:app --reload
```

Work:
Start FastAPI development server.

Example:

```bash
uv run uvicorn app.main:app --reload
```

---

## 9. Run Any Tool

Command:

```bash
uv run <tool>
```

Work:
Run installed tools.

Example:

```bash
uv run pytest
uv run black .
uv run ruff check .
```

---

## 10. Sync Dependencies

Command:

```bash
uv sync
```

Work:
Install everything from pyproject.toml and uv.lock.

Example:

```bash
uv sync
```

When to use:
After cloning GitHub repositories.

---

## 11. Remove Package

Command:

```bash
uv remove <package>
```

Work:
Remove dependency from project.

Example:

```bash
uv remove openai
```

---

## 12. View Dependency Tree

Command:

```bash
uv tree
```

Work:
Show package dependency hierarchy.

Example:

```bash
uv tree
```

---

## 13. Lock Dependencies

Command:

```bash
uv lock
```

Work:
Generate uv.lock file.

Example:

```bash
uv lock
```

---

## 14. Export Requirements.txt

Command:

```bash
uv export -o requirements.txt
```

Work:
Generate requirements.txt for deployment.

Example:

```bash
uv export -o requirements.txt
```

---

## 15. Install Specific Python Version

Command:

```bash
uv python install <version>
```

Work:
Download Python.

Example:

```bash
uv python install 3.12
```

---

## 16. List Python Versions

Command:

```bash
uv python list
```

Work:
Show available and installed Python versions.

Example:

```bash
uv python list
```

---

## 17. Pin Python Version

Command:

```bash
uv python pin 3.12
```

Work:
Set project Python version.

Example:

```bash
uv python pin 3.12
```

---

## 18. Run Tool Without Installing

Command:

```bash
uvx <tool>
```

Work:
Temporary execution like npx.

Example:

```bash
uvx ruff check .
uvx cowsay hello
```

---

## 19. Install Global Tool

Command:

```bash
uv tool install <tool>
```

Work:
Install CLI tools globally.

Example:

```bash
uv tool install claude-code
uv tool install ruff
uv tool install black
```

---

## 20. List Global Tools

Command:

```bash
uv tool list
```

Work:
Show globally installed tools.

Example:

```bash
uv tool list
```

---

## 21. Update UV

Command:

```bash
uv self update
```

Work:
Update uv package manager.

Example:

```bash
uv self update
```

---

# Real AI Engineer Workflow

## Create Project

```bash
uv init ai-job-agent
cd ai-job-agent
uv venv
```

---

## Install AI Libraries

```bash
uv add openai
uv add langchain
uv add langgraph
uv add fastapi
uv add uvicorn
uv add pydantic
uv add python-dotenv
```

---

## Install Development Tools

```bash
uv add --dev pytest
uv add --dev black
uv add --dev ruff
```

---

## Run Application

```bash
uv run main.py
```

or

```bash
uv run uvicorn app.main:app --reload
```

---

## Clone Existing Project

```bash
git clone repo-url

cd repo

uv sync

uv run main.py
```

---

# Commands Used 95% of the Time

```bash
uv init
uv venv

uv add
uv remove

uv sync

uv run

uv tree

uv lock

uv python install

uv python list

uvx

uv tool install

uv export -o requirements.txt
```

If you are building AI Agents using OpenAI, LangGraph, FastAPI, MCP, RAG, PostgreSQL, Docker, and Agentic workflows, these are the commands you'll use almost every day.
