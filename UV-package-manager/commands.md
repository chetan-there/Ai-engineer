Complete UV Package Manager Guide (2026)
UV is a modern Python package manager created by Astral. It replaces many tools:
• pip
• virtualenv
• pipx
• pyenv
• poetry (partially)
• pip-tools
It is written in Rust and is significantly faster than pip. (Astral Docs)

---

1. Install UV
   Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   Verify:
   uv --version

---

Alternative
pip install uv
(varac.net)

---

2. Check Commands
   uv --help
   uv help
   List all commands:
   uv
   Main commands available: run, init, add, remove, sync, lock, export, tree, tool, python, pip, venv, build, publish, etc. (Astral Docs)

---

3. Create New Project
   uv init myproject
   Creates:
   myproject/
   │
   ├── pyproject.toml
   ├── .python-version
   ├── README.md
   └── main.py
   (Astral Docs)

---

4. Enter Project
   cd myproject

---

5. Create Virtual Environment
   uv venv
   Creates:
   .venv/
   Specific version:
   uv venv --python 3.12
   (Astral Docs)

---

6. Activate Virtual Environment
   Windows
   .venv\Scripts\activate
   Linux/Mac
   source .venv/bin/activate

---

7. Install Package
   Old pip
   pip install requests
   UV
   uv add requests
   This:
1. Installs package
1. Updates pyproject.toml
1. Updates lock file
1. Syncs environment
   (Astral Docs)

---

8. Install Multiple Packages
   uv add requests pandas numpy

---

9. Install Specific Version
   uv add "django==5.2"
   uv add "numpy>=2.0"

---

10. Install Dev Dependency
    uv add pytest --dev
    uv add black --dev

---

11. Remove Package
    uv remove requests
    Updates:
    pyproject.toml
    uv.lock
    (Astral Docs)

---

12. Run Python File
    Instead of:
    python app.py
    Use:
    uv run app.py
    or
    uv run python app.py
    UV automatically creates/syncs environment before execution. (Astral Docs)

---

13. Run Module
    uv run python -m app.main

---

14. Run Installed Tool
    uv run pytest
    uv run black .

---

15. Sync Dependencies
    Install everything from lock file:
    uv sync
    Most important command after cloning a project. (Reddit)
    Example:
    git clone project-url
    cd project
    uv sync

---

16. Generate Lock File
    uv lock
    Creates:
    uv.lock
    (Astral Docs)

---

17. Export Requirements.txt
    uv export -o requirements.txt
    Useful for deployment.

---

18. Show Dependency Tree
    uv tree
    Example:
    requests
    ├── urllib3
    ├── certifi
    └── charset-normalizer
    (Astral Docs)

---

19. Install Python Versions
    UV can replace pyenv.
    List versions:
    uv python list
    Install:
    uv python install 3.12
    Install latest:
    uv python install
    (Astral Docs)

---

20. Use Specific Python
    uv python pin 3.12
    Creates:
    .python-version

---

21. Show Installed Python Versions
    uv python list

---

22. Install Package Like pip
    UV provides pip-compatible commands.
    Install:
    uv pip install requests
    (Astral Docs)

---

23. Install Requirements File
    uv pip install -r requirements.txt

---

24. Uninstall Package
    uv pip uninstall requests

---

25. List Installed Packages
    uv pip list

---

26. Freeze Packages
    uv pip freeze
    Save:
    uv pip freeze > requirements.txt
    (py-launch-blueprint.readthedocs.io)

---

27. Package Information
    uv pip show requests

---

28. Dependency Tree
    uv pip tree

---

29. Check Broken Dependencies
    uv pip check

---

30. Install Global CLI Tools
    Equivalent of pipx.
    Example:
    uv tool install ruff
    uv tool install black
    uv tool install poetry
    (Astral Docs)

---

31. List Installed Tools
    uv tool list

---

32. Uninstall Tool
    uv tool uninstall ruff

---

33. Run Tool Without Installing
    Like npx.
    uvx ruff check .
    or
    uv tool run ruff
    (Astral Docs)

---

34. Build Python Package
    uv build
    Creates:
    dist/
    ├── package.whl
    └── package.tar.gz
    (Astral Docs)

---

35. Publish Package
    uv publish
    Upload to PyPI.

---

36. Cache Commands
    Show cache:
    uv cache dir
    Clean cache:
    uv cache clean
    (Astral Docs)

---

37. Update UV
    uv self update

---

38. Audit Dependencies
    Check vulnerabilities:
    uv audit
    (Astral Docs)

---

39. Format Code
    uv format

---

40. Check Project
    uv check

---

Most Common Workflow (AI/ML Projects)
Create Project
uv init ai-agent
cd ai-agent
Create Environment
uv venv
Add Libraries
uv add langchain
uv add openai
uv add fastapi
uv add pandas
Run App
uv run main.py
Clone Existing Project
git clone repo-url
cd repo
uv sync
uv run main.py

---

Commands You'll Use Daily
uv init
uv venv
uv add
uv remove
uv sync
uv run
uv tree
uv lock
uv export

uv pip install
uv pip uninstall
uv pip list
uv pip freeze

uv python install
uv python list

uv tool install
uv tool list
uv tool uninstall

uv build
uv publish
uv audit
These 15–20 commands cover about 95% of real-world AI Engineering, Data Science, FastAPI, LangGraph, and Backend projects. (Astral Docs)
