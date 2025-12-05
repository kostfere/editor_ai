"""
EditorAI - Document Editor with Grammar Enforcement
A Streamlit application for intelligent document editing with Greek/English grammar rules.
"""

import streamlit as st
from dotenv import load_dotenv

from ui.main_content import render_main_content
from ui.sidebar import render_sidebar
from ui.styles import CUSTOM_CSS
from ui.utils import init_edit_decisions

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="EditorAI", page_icon="✒️", layout="wide", initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def main() -> None:
    # Initialize session state
    init_edit_decisions()

    # Initialize API key session state
    if "use_custom_key" not in st.session_state:
        st.session_state.use_custom_key = False
    if "custom_api_key" not in st.session_state:
        st.session_state.custom_api_key = ""

    # Header
    st.markdown('<h1 class="editor-header">✒️ EditorAI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="editor-subtitle">Editor Style Enforcement</p>', unsafe_allow_html=True)

    # Sidebar
    language, concurrency = render_sidebar()

    # Main content area
    render_main_content(language, concurrency)


if __name__ == "__main__":
    main()
