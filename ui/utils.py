import os

import streamlit as st


def get_default_api_key() -> str:
    """Get API key from Streamlit secrets or environment variable."""
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass
    # Fall back to environment variable
    return os.environ.get("GEMINI_API_KEY", "")


def get_active_api_key() -> str:
    """Get the active API key (user's custom key or default)."""
    if st.session_state.get("use_custom_key") and st.session_state.get("custom_api_key"):
        return st.session_state.custom_api_key
    return get_default_api_key()


def get_rule_badge_class(category: str) -> str:
    """Get CSS class for rule category badge."""
    mapping = {
        "Grammar": "rule-grammar",
        "Style": "rule-style",
        "Formatting": "rule-formatting",
        "Greek-Final-Nu": "rule-greek-final-nu",
        "Monotonic": "rule-monotonic",
        "Punctuation": "rule-punctuation",
        "Spelling": "rule-spelling",
        "Syntax": "rule-syntax",
    }
    return mapping.get(category, "rule-grammar")


def get_edit_key(para_idx: int, edit_idx: int) -> str:
    """Generate a unique key for an edit."""
    return f"{para_idx}_{edit_idx}"


def init_edit_decisions() -> None:
    """Initialize session state for edit decisions."""
    if "edit_decisions" not in st.session_state:
        st.session_state.edit_decisions = {}  # key -> {"status": "pending"|"accepted"|"rejected", "custom_text": None}
