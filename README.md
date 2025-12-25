# 🧠 DevinLikeClone – AI Software Engineer with LangGraph

- DevinLikeClone is an experimental AI software engineering application inspired by Devin.
- It uses LangGraph-based AI agents to plan, reason, and generate complete applications from natural language prompts.

- The system can take a user request like “Build a calculator app” and orchestrate multiple agents (planner, architect, coder, reviewer, etc.) to produce working code.

## 🚀 Features

- 🧩 Agent-based architecture using LangGraph

- 🧠 Task planning, decomposition, and execution

- 🛠 Tool-augmented reasoning

- 🧑‍💻 Software-engineering style workflow (like Devin)

- ⚡ Fast dependency management using uv

- 🧪 Easy to extend with new agents and tools

## 📂 Project Structure
``` 
DEVINLIKECLONE/
│
├── agent/
│ ├── init.py
│ ├── graph.py # LangGraph agent workflow
│ ├── prompts.py # System + agent prompts
│ ├── states.py # LangGraph state definitions
│ ├── tools.py # Tools used by agents
│ └── pycache/
│
├── main.py # Entry point
├── pyproject.toml # Project dependencies
├── uv.lock # Locked dependencies (uv)
├── .env # Environment variables (API keys)
├── .gitignore
├── .python-version
└── README.md
```

## 🛠️ Requirements

- Python 3.10+

- OpenAI API Key

- uv package manager

## 🔧 Setup Instructions
1️⃣ Clone the Repository
2️⃣ Create & Activate Virtual Environment
3️⃣ Install Dependencies

## 🔑 Environment Variables

- Create a .env file in the root directory:

- OPENAI_API_KEY=your_openai_api_key_here

## ▶️ Running the Application
- python main.py
- This will start the AI agent pipeline.

## 💡 Example Prompts

- “Create a calculator application using HTML, CSS, and JavaScript.”
- “Build a TODO app with a modern UI.”
- “Create a random quote generator with a button to generate a new quote.”

