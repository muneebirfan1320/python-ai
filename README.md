
# Python for AI

**Student:** Muneeb Irfan

**Course:** Python for AI — Module 1

## My AI Goal

I want to become an AI Engineer and build useful GenAI applications and AI agents.

## How to Run

Make sure Python and uv are installed.

Run the main program from the project root:

```bash
uv run main.py
```

Run the introduction task:

```bash
uv run python code/lesson_01_intro.py
```

## Lessons Completed

- [x] Lesson 1.1 — AI Career Introduction
- [ ] Lesson 1.2 — AI Development Toolkit
- [ ] Lesson 1.3 — Client-Ready Repository
- [ ] Lesson 1.4 — Business Prompt Builder

## Module 2 Project: AI Content Studio

A local AI content studio for Sweet Crumbs Bakery in Lahore. It generates menu descriptions in batches, streams social media posts, answers prices from verified business data, and chats with customers using conversation memory.

### How to run

Requirements: Python project managed with `uv`, Ollama running, and the `llama3.2` model installed.

```powershell
uv sync
uv run code/project_m2_content_studio.py
```

### Commands

- `/menu` — Generate product descriptions.
- `/post fun` — Generate a fun social media post.
- `/post premium` — Generate a premium-style post.
- `/post urgent` — Generate an urgent-style post.
- `/price cupcake` — Look up a product's price.
- `/reset` — Clear chat history.
- `bye` — End the session and show the report.

### Screenshot

After running a full session, save the terminal screenshot as `docs/project-m2-cp1-run.png`.

![AI Content Studio screenshot](docs/project-m2-cp1-run.png)

### Business value

The studio can save the owner hours of repetitive menu writing and social media preparation by generating multiple pieces of content in one session, while keeping price lookups tied to the business's own data.

## AI Business Assistant

- **Description:** An agentic AI business assistant that reads business data from JSON, executes custom Python tools for prices and order status, places approved orders, parses messy WhatsApp orders via Pydantic schemas, and logs errors reliably.
- **Run Command:**
  ```bash
  cd code
  uv run project_m2_business_assistant.py