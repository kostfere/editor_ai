# ✒️ EditorAI

**Gemini Powered Document Editor** — Intelligent grammar enforcement for Greek & English documents.

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)
![Gemini](https://img.shields.io/badge/Gemini-purple.svg)
---

## 🎯 Overview

EditorAI is a sophisticated document editing assistant that:

- **Accepts .docx documents** and analyzes them paragraph by paragraph
- **Enforces language-specific rules** for both Greek and English
- **Provides detailed justifications** for every edit
- **Exports revised documents** with highlighted changes and comments

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Poetry (package manager)
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### Installation

```bash
# Clone or navigate to the project
cd editor_ai

# Install dependencies with Poetry
poetry install

# Create your .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### Running the App

```bash
# Run with Make (recommended)
make run
```

Or manually with Poetry:
```bash
poetry run streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---
