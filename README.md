# ✒️ EditorAI

**Gemini 3.0 Powered Document Editor** — Intelligent grammar enforcement for Greek & English documents.

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)
![Gemini 3](https://img.shields.io/badge/Gemini-3.0_Pro-purple.svg)

---

## 🎯 Overview

EditorAI is a sophisticated document editing assistant that:

- **Accepts .docx documents** and analyzes them paragraph by paragraph
- **Uses Gemini 3 Pro** with deep thinking (`thinking_level: high`) for thorough grammar analysis
- **Enforces language-specific rules** for both Greek and English
- **Provides detailed justifications** for every edit
- **Exports revised documents** with highlighted changes and comments

### Greek Language Rules
- **Τελικό Ν (Final Nu)**: Strict enforcement of when to keep/remove the final "n" sound
- **Monotonic System**: Proper accent placement in modern Greek

### English Language Rules
- **Oxford Comma**: Always use serial commas in lists
- **Active Voice**: Prefer active over passive constructions
- **Punctuation**: American English conventions

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
# Activate the Poetry environment
poetry shell

# Run Streamlit
streamlit run app.py
```

Or run directly:
```bash
poetry run streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
editor_ai/
├── app.py                 # Streamlit UI application
├── core/
│   ├── __init__.py       # Module exports
│   ├── models.py         # Pydantic data models
│   ├── llm.py            # Gemini 3 Pro integration
│   └── document.py       # .docx processing & export
├── pyproject.toml        # Poetry dependencies
├── README.md             # This file
└── .env                  # Your API key (create this)
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes |

### Language Detection

EditorAI automatically detects document language but you can override this in the sidebar:
- **Auto-detect**: Let the AI determine the language
- **Greek**: Force Greek grammar rules
- **English**: Force English grammar rules

### Export Options

1. **Highlighted Changes**: Exports with yellow highlights and superscript comment markers
2. **With Edit Summary**: Appends a detailed summary of all changes at the end of the document

---

## 🧠 How It Works

### 1. Document Processing
The document is split into paragraphs to avoid context limits and enable precise editing.

### 2. LLM Analysis
Each paragraph is sent to Gemini 3 Pro with:
- A comprehensive system prompt defining all grammar rules
- `thinking_budget: 10000` for deep reasoning
- Structured output via `response_schema` ensuring valid JSON responses

### 3. Structured Output
Responses conform to Pydantic models:

```python
class EditAction(BaseModel):
    original_text: str      # Exact text to change
    revised_text: str       # Corrected version
    rule_category: Literal[...]  # Type of rule applied
    reasoning: str          # Explanation of the edit

class SegmentReview(BaseModel):
    edits: List[EditAction]  # All edits for a paragraph
```

### 4. Export
The revised document is generated using `python-docx` with:
- Applied corrections
- Visual highlights
- Embedded reasoning (as comments or summary)

---

## 📝 Supported Rule Categories

| Category | Description | Language |
|----------|-------------|----------|
| `Grammar` | General grammatical corrections | Both |
| `Style` | Writing style improvements | Both |
| `Formatting` | Spacing, capitalization, etc. | Both |
| `Greek-Final-Nu` | Τελικό Ν rule enforcement | Greek |
| `Monotonic` | Accent system corrections | Greek |
| `Punctuation` | Commas, periods, quotes | Both |
| `Spelling` | Spelling corrections | Both |
| `Syntax` | Sentence structure | Both |

---

## 🎨 UI Features

- **Side-by-side comparison**: Original vs. revised text with visual distinction
- **Expandable reasoning**: Click to see the full justification for each edit
- **Category filtering**: Focus on specific types of edits
- **Document statistics**: Paragraph count, word count, language detection
- **Progress tracking**: Real-time progress bar during analysis

---

## ⚠️ Important Notes

1. **SDK Version**: This project uses `google-genai` (the new v1 SDK), **not** `google-generativeai` (the old SDK). Do not install both.

2. **Model**: Uses `gemini-3-pro-preview` which requires API access to Gemini 3.

3. **Rate Limits**: Large documents may hit rate limits. The app processes paragraphs sequentially to manage this.

4. **Context Length**: Very long paragraphs may be truncated. Consider breaking them up before upload.

---

## 🛠️ Development

```bash
# Run tests
poetry run pytest

# Format code
poetry run black .

# Type checking
poetry run mypy core/
```

---

## 📄 License

MIT License - feel free to use and modify.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini 3](https://deepmind.google/technologies/gemini/)
- Document handling via [python-docx](https://python-docx.readthedocs.io/)

# editor_ai
