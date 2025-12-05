import streamlit as st

from core.document import DocumentProcessor
from core.models import Language
from ui.analysis import analyze_document
from ui.results import render_results
from ui.utils import get_active_api_key


def render_main_content(language: Language, concurrency: int) -> None:
    """Render the main content area."""

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # File upload
        uploaded_file = st.file_uploader(
            "Upload your document", type=["docx"], help="Upload a .docx file for editing"
        )

    if uploaded_file is not None:
        # Check for API key
        active_api_key = get_active_api_key()
        if not active_api_key:
            st.error("⚠️ Please enter your Gemini API key in the sidebar.")
            return

        # Initialize processor
        processor = DocumentProcessor()
        paragraphs = processor.load_from_bytes(uploaded_file)

        # Show document info
        st.markdown("---")

        # Filter out empty paragraphs for accurate count
        non_empty_paragraphs = [p for p in paragraphs if p.strip()]

        # Stats row
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
            <div class="stat-card">
                <div class="stat-number">{len(non_empty_paragraphs)}</div>
                <div class="stat-label">Paragraphs</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            word_count = sum(len(p.split()) for p in non_empty_paragraphs)
            st.markdown(
                f"""
            <div class="stat-card">
                <div class="stat-number">{word_count}</div>
                <div class="stat-label">Words</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            char_count = sum(len(p) for p in non_empty_paragraphs)
            st.markdown(
                f"""
            <div class="stat-card">
                <div class="stat-number">{char_count}</div>
                <div class="stat-label">Characters</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Process button
        if st.button("🔍 Analyze Document", use_container_width=True):
            analyze_document(paragraphs, language, concurrency, active_api_key)
            st.session_state.processor = processor
            st.session_state.paragraphs = paragraphs

        # Display results if available
        render_results(paragraphs, uploaded_file)

    else:
        # Empty state
        st.markdown(
            """
        <div style="text-align: center; padding: 3rem; color: #888;">
            <h3>📄 Upload a .docx file to get started</h3>
            <p>EditorAI will analyze your document and suggest improvements with detailed explanations.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
