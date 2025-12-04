"""
EditorAI - Gemini 3.0 Powered Document Editor
A Streamlit application for intelligent document editing with Greek/English grammar enforcement.
"""

import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="EditorAI",
    page_icon="✒️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Root variables */
    :root {
        --ink-black: #1a1a1a;
        --parchment: #faf8f5;
        --gold-accent: #c9a227;
        --correction-red: #c44536;
        --success-green: #2d5a27;
        --rule-blue: #1e5f8a;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #faf8f5 0%, #f0ebe3 100%);
    }
    
    /* Header styling */
    .editor-header {
        font-family: 'Crimson Pro', Georgia, serif;
        font-size: 3rem;
        font-weight: 600;
        color: var(--ink-black);
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .editor-subtitle {
        font-family: 'Crimson Pro', Georgia, serif;
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        font-style: italic;
        margin-bottom: 2rem;
    }
    
    /* Edit card styling */
    .edit-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 4px solid var(--gold-accent);
    }
    
    .original-text {
        font-family: 'Crimson Pro', Georgia, serif;
        font-size: 1.1rem;
        color: var(--correction-red);
        text-decoration: line-through;
        padding: 0.8rem;
        background: #fff5f5;
        border-radius: 6px;
        margin-bottom: 0.5rem;
    }
    
    .revised-text {
        font-family: 'Crimson Pro', Georgia, serif;
        font-size: 1.1rem;
        color: var(--success-green);
        padding: 0.8rem;
        background: #f5fff5;
        border-radius: 6px;
        font-weight: 500;
    }
    
    .rule-badge {
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 500;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin-bottom: 0.8rem;
    }
    
    .rule-grammar { background: #e3f2fd; color: #1565c0; }
    .rule-style { background: #f3e5f5; color: #7b1fa2; }
    .rule-formatting { background: #fff3e0; color: #ef6c00; }
    .rule-greek-final-nu { background: #e8f5e9; color: #2e7d32; }
    .rule-monotonic { background: #fce4ec; color: #c2185b; }
    .rule-punctuation { background: #fff8e1; color: #f9a825; }
    .rule-spelling { background: #e0f7fa; color: #00838f; }
    .rule-syntax { background: #ede7f6; color: #512da8; }
    
    .reasoning-text {
        font-family: 'Crimson Pro', Georgia, serif;
        font-size: 0.95rem;
        color: #555;
        line-height: 1.6;
        padding: 1rem;
        background: #fafafa;
        border-radius: 6px;
        border-left: 3px solid var(--rule-blue);
    }
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #333 100%);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        color: white;
    }
    
    .stat-number {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 500;
        color: var(--gold-accent);
    }
    
    .stat-label {
        font-family: 'Crimson Pro', Georgia, serif;
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    /* Upload area */
    .upload-zone {
        border: 2px dashed #ccc;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        background: white;
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        border-color: var(--gold-accent);
        background: #fffef8;
    }
    
    /* Streamlit overrides */
    .stButton > button {
        font-family: 'Crimson Pro', Georgia, serif;
        font-weight: 600;
        background: linear-gradient(135deg, #1a1a1a 0%, #333 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .stProgress > div > div {
        background: var(--gold-accent);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #1a1a1a;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Crimson Pro', Georgia, serif;
        font-weight: 600;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Arrow between texts */
    .arrow-divider {
        text-align: center;
        font-size: 1.5rem;
        color: var(--gold-accent);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


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


def render_edit_card(edit, index: int):
    """Render a single edit card with side-by-side comparison."""
    badge_class = get_rule_badge_class(edit.rule_category)
    
    st.markdown(f"""
    <div class="edit-card">
        <span class="rule-badge {badge_class}">{edit.rule_category}</span>
        <div class="original-text">{edit.original_text}</div>
        <div class="arrow-divider">↓</div>
        <div class="revised-text">{edit.revised_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander(f"📖 View Reasoning", expanded=False):
        st.markdown(f"""
        <div class="reasoning-text">
            {edit.reasoning}
        </div>
        """, unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<h1 class="editor-header">✒️ EditorAI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="editor-subtitle">Powered by Gemini 3.0 • Greek & English Grammar Enforcement</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # API Key input
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=os.environ.get("GEMINI_API_KEY", ""),
            help="Your Google Gemini API key"
        )
        
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
        
        st.markdown("---")
        
        # Language preference
        language = st.selectbox(
            "Document Language",
            options=["auto", "greek", "english"],
            format_func=lambda x: {
                "auto": "🔍 Auto-detect",
                "greek": "🇬🇷 Greek",
                "english": "🇬🇧 English"
            }[x]
        )
        
        st.markdown("---")
        
        # Export options
        st.markdown("### 📤 Export Options")
        export_format = st.radio(
            "Export Style",
            options=["highlighted", "summary"],
            format_func=lambda x: {
                "highlighted": "📝 Highlighted Changes",
                "summary": "📋 With Edit Summary"
            }[x]
        )
        
        st.markdown("---")
        
        # Info section
        st.markdown("### 📚 Supported Rules")
        st.markdown("""
        **Greek:**
        - Τελικό Ν (Final Nu)
        - Monotonic System
        
        **English:**
        - Oxford Comma
        - Active Voice
        - Punctuation
        """)
    
    # Main content area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # File upload
        uploaded_file = st.file_uploader(
            "Upload your document",
            type=["docx"],
            help="Upload a .docx file for editing"
        )
    
    if uploaded_file is not None:
        # Check for API key
        if not os.environ.get("GEMINI_API_KEY"):
            st.error("⚠️ Please enter your Gemini API key in the sidebar.")
            return
        
        # Import modules
        from core.llm import EditorLLM
        from core.document import DocumentProcessor, detect_language
        
        # Initialize processor
        processor = DocumentProcessor()
        paragraphs = processor.load_from_bytes(uploaded_file)
        
        # Show document info
        st.markdown("---")
        
        # Stats row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(paragraphs)}</div>
                <div class="stat-label">Paragraphs</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            word_count = sum(len(p.split()) for p in paragraphs)
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{word_count}</div>
                <div class="stat-label">Words</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            detected_lang = detect_language(" ".join(paragraphs[:5]))
            lang_display = {"greek": "🇬🇷", "english": "🇬🇧", "mixed": "🌐", "auto": "🔍"}
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{lang_display.get(detected_lang, '📄')}</div>
                <div class="stat-label">Detected: {detected_lang.title()}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            char_count = sum(len(p) for p in paragraphs)
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{char_count}</div>
                <div class="stat-label">Characters</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Process button
        if st.button("🔍 Analyze Document", use_container_width=True):
            # Initialize LLM
            try:
                llm = EditorLLM()
            except ValueError as e:
                st.error(str(e))
                return
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Store results in session state
            if 'reviews' not in st.session_state:
                st.session_state.reviews = []
            
            reviews = []
            
            # Process each paragraph
            for i, para in enumerate(paragraphs):
                if para.strip():
                    status_text.text(f"Analyzing paragraph {i+1} of {len(paragraphs)}...")
                    try:
                        review = llm.review_segment(para, language)
                        reviews.append(review)
                    except Exception as e:
                        st.warning(f"Error processing paragraph {i+1}: {str(e)}")
                        from core.models import SegmentReview
                        reviews.append(SegmentReview(edits=[]))
                else:
                    from core.models import SegmentReview
                    reviews.append(SegmentReview(edits=[]))
                
                progress_bar.progress((i + 1) / len(paragraphs))
            
            status_text.text("✅ Analysis complete!")
            st.session_state.reviews = reviews
            st.session_state.processor = processor
        
        # Display results if available
        if 'reviews' in st.session_state and st.session_state.reviews:
            reviews = st.session_state.reviews
            
            # Count total edits
            all_edits = []
            for review in reviews:
                all_edits.extend(review.get_actual_changes())
            
            st.markdown("---")
            st.markdown(f"### 📝 Found **{len(all_edits)}** Edit(s)")
            
            if all_edits:
                # Category filter
                categories = list(set(e.rule_category for e in all_edits))
                selected_categories = st.multiselect(
                    "Filter by category:",
                    options=categories,
                    default=categories
                )
                
                # Display edits
                edit_index = 0
                for para_idx, review in enumerate(reviews):
                    changes = review.get_actual_changes()
                    filtered_changes = [c for c in changes if c.rule_category in selected_categories]
                    
                    if filtered_changes:
                        st.markdown(f"#### Paragraph {para_idx + 1}")
                        
                        # Show original paragraph context
                        if para_idx < len(paragraphs):
                            with st.expander("View original paragraph"):
                                st.text(paragraphs[para_idx])
                        
                        for edit in filtered_changes:
                            render_edit_card(edit, edit_index)
                            edit_index += 1
                
                # Export section
                st.markdown("---")
                st.markdown("### 📥 Export Revised Document")
                
                processor = st.session_state.get('processor')
                if processor:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if export_format == "highlighted":
                            doc_bytes = processor.apply_edits_and_export(
                                reviews,
                                add_comments=True,
                                add_highlights=True
                            )
                        else:
                            doc_bytes = processor.export_with_track_changes_summary(reviews)
                        
                        st.download_button(
                            label="⬇️ Download Revised Document",
                            data=doc_bytes,
                            file_name=f"edited_{uploaded_file.name}",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
            else:
                st.success("✨ No edits needed! Your document looks perfect.")
    
    else:
        # Empty state
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #888;">
            <h3>📄 Upload a .docx file to get started</h3>
            <p>EditorAI will analyze your document and suggest improvements with detailed explanations.</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

