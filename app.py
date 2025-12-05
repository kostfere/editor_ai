"""
EditorAI - Document Editor with Grammar Enforcement
A Streamlit application for intelligent document editing with Greek/English grammar rules.
"""

import os

import streamlit as st
from dotenv import load_dotenv

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
    
    .edit-card.accepted {
        border-left-color: var(--success-green);
        background: #f8fff8;
    }
    
    .edit-card.rejected {
        border-left-color: #999;
        background: #f5f5f5;
        opacity: 0.6;
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
    
    /* Bulk action buttons */
    .bulk-actions {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Streamlit overrides */
    .stButton > button {
        font-family: 'Crimson Pro', Georgia, serif;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .stProgress > div > div {
        background: var(--gold-accent);
    }
    
    /* Status badges */
    .status-accepted {
        color: var(--success-green);
        font-weight: 600;
    }
    
    .status-rejected {
        color: #999;
        font-weight: 600;
    }
    
    .status-pending {
        color: var(--gold-accent);
        font-weight: 600;
    }
    
    /* Arrow between texts */
    .arrow-divider {
        text-align: center;
        font-size: 1.5rem;
        color: var(--gold-accent);
        margin: 0.5rem 0;
    }
    
    /* Highlighted edit text */
    mark {
        background: linear-gradient(180deg, transparent 60%, #ffd54f 60%);
        padding: 0 2px;
        border-radius: 2px;
        cursor: help;
    }
    
    mark:hover {
        background: linear-gradient(180deg, transparent 40%, #ffca28 40%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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


def get_edit_key(para_idx: int, edit_idx: int) -> str:
    """Generate a unique key for an edit."""
    return f"{para_idx}_{edit_idx}"


def init_edit_decisions():
    """Initialize session state for edit decisions."""
    if 'edit_decisions' not in st.session_state:
        st.session_state.edit_decisions = {}  # key -> {"status": "pending"|"accepted"|"rejected", "custom_text": None}


def highlight_edits_in_text(text: str, edits: list, para_idx: int) -> str:
    """
    Create HTML with highlighted portions where edits were identified.
    
    Args:
        text: Original paragraph text
        edits: List of edit info dicts with 'edit' containing the EditAction
        para_idx: Paragraph index for generating anchor IDs
        
    Returns:
        HTML string with highlighted edit portions
    """
    import html

    if not edits:
        return html.escape(text)

    # Find all edit positions
    highlights = []
    for edit_num, info in enumerate(edits, 1):
        edit = info["edit"]
        original = edit.original_text
        start = text.find(original)
        if start != -1:
            highlights.append({
                "start": start,
                "end": start + len(original),
                "text": original,
                "edit_num": edit_num
            })

    # Sort by position
    highlights.sort(key=lambda x: x["start"])

    # Remove overlapping highlights (keep first)
    filtered = []
    last_end = 0
    for h in highlights:
        if h["start"] >= last_end:
            filtered.append(h)
            last_end = h["end"]

    # Build HTML
    result = []
    pos = 0
    for h in filtered:
        # Add text before highlight
        if h["start"] > pos:
            result.append(html.escape(text[pos:h["start"]]))

        # Add highlighted text with tooltip
        highlighted_text = html.escape(h["text"])
        result.append(
            f'<mark style="background: linear-gradient(180deg, transparent 60%, #ffd54f 60%); '
            f'padding: 0 2px; border-radius: 2px; cursor: pointer;" '
            f'title="Edit {h["edit_num"]}">{highlighted_text}</mark>'
        )
        pos = h["end"]

    # Add remaining text
    if pos < len(text):
        result.append(html.escape(text[pos:]))

    return "".join(result)


def render_edit_card(edit, para_idx: int, edit_idx: int, original_paragraph: str):
    """Render a single edit card with accept/reject controls."""
    key = get_edit_key(para_idx, edit_idx)
    badge_class = get_rule_badge_class(edit.rule_category)

    # Get current decision
    decision = st.session_state.edit_decisions.get(key, {"status": "pending", "custom_text": None})
    status = decision["status"]
    custom_text = decision.get("custom_text")

    # Card class based on status
    card_class = "edit-card"
    if status == "accepted":
        card_class += " accepted"
    elif status == "rejected":
        card_class += " rejected"

    # Display the edit card
    st.markdown(f"""
    <div class="{card_class}">
        <span class="rule-badge {badge_class}">{edit.rule_category}</span>
        <div class="original-text">{edit.original_text}</div>
        <div class="arrow-divider">↓</div>
        <div class="revised-text">{custom_text if custom_text else edit.revised_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # Reasoning expander
    with st.expander("📖 View Reasoning", expanded=False):
        st.markdown(f"""
        <div class="reasoning-text">
            {edit.reasoning}
        </div>
        """, unsafe_allow_html=True)

    # Action buttons
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])

    with col1:
        if st.button("✅ Accept", key=f"accept_{key}", disabled=(status == "accepted")):
            st.session_state.edit_decisions[key] = {"status": "accepted", "custom_text": custom_text}
            st.rerun()

    with col2:
        if st.button("❌ Reject", key=f"reject_{key}", disabled=(status == "rejected")):
            st.session_state.edit_decisions[key] = {"status": "rejected", "custom_text": None}
            st.rerun()

    with col3:
        # Custom text input
        new_custom = st.text_input(
            "Custom edit:",
            value=custom_text if custom_text else "",
            key=f"custom_{key}",
            placeholder="Enter your own text...",
            label_visibility="collapsed"
        )

        with col4:
            if st.button("💾 Use Custom", key=f"save_custom_{key}"):
                if new_custom.strip():
                    st.session_state.edit_decisions[key] = {"status": "accepted", "custom_text": new_custom.strip()}
                    st.rerun()

    # Status indicator
    status_class = f"status-{status}"
    status_text = {"pending": "⏳ Pending", "accepted": "✅ Accepted", "rejected": "❌ Rejected"}
    st.markdown(f'<small class="{status_class}">{status_text[status]}</small>', unsafe_allow_html=True)

    st.markdown("---")


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


def main():
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
    with st.sidebar:
        st.markdown("### 🔑 API Key")

        # Check if default key exists
        default_key = get_default_api_key()
        has_default_key = bool(default_key)

        if has_default_key:
            st.success("✓ Default API key configured")
            use_own = st.checkbox(
                "Use my own API key instead",
                value=st.session_state.use_custom_key,
                key="use_own_key_checkbox"
            )
            st.session_state.use_custom_key = use_own

            if use_own:
                custom_key = st.text_input(
                    "Your API Key",
                    type="password",
                    value=st.session_state.custom_api_key,
                    help="Enter your own Gemini API key"
                )
                st.session_state.custom_api_key = custom_key
        else:
            st.warning("No default API key configured")
            custom_key = st.text_input(
                "Gemini API Key",
                type="password",
                value=st.session_state.custom_api_key,
                help="Enter your Gemini API key"
            )
            st.session_state.custom_api_key = custom_key
            st.session_state.use_custom_key = True

        st.markdown("---")

        st.markdown("### ⚙️ Settings")

        # Language preference
        language = st.selectbox(
            "Document Language",
            options=["greek", "english"],
            format_func=lambda x: {
                "greek": "🇬🇷 Greek",
                "english": "🇬🇧 English"
            }[x]
        )

        st.markdown("---")

        # Rules file management
        st.markdown("### 📄 Rules")

        from core.llm import get_rules_dir, load_rules

        try:
            current_rules = load_rules(language)
        except FileNotFoundError:
            current_rules = ""
            st.error(f"Rules file not found for {language}")

        # View rules
        with st.expander("📖 View Current Rules"):
            st.code(current_rules, language="markdown")

        # Download rules
        st.download_button(
            label="⬇️ Download Rules",
            data=current_rules,
            file_name=f"{language}_rules.txt",
            mime="text/plain",
            use_container_width=True
        )

        # Upload custom rules
        uploaded_rules = st.file_uploader(
            "📤 Upload Custom Rules",
            type=["txt"],
            key=f"rules_upload_{language}",
            help="Upload a .txt file to replace the current rules"
        )

        if uploaded_rules is not None:
            new_rules_content = uploaded_rules.read().decode("utf-8")
            rules_path = get_rules_dir() / f"{language}.txt"
            try:
                rules_path.write_text(new_rules_content, encoding="utf-8")
                st.success(f"✅ Rules updated for {language}!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save rules: {e}")

        st.markdown("---")

        # Advanced settings
        with st.expander("⚡ Advanced Settings"):
            concurrency = st.slider(
                "Parallel Requests",
                min_value=1,
                max_value=50,
                value=15,
                help="Number of paragraphs to analyze simultaneously. Higher = faster."
            )

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
        active_api_key = get_active_api_key()
        if not active_api_key:
            st.error("⚠️ Please enter your Gemini API key in the sidebar.")
            return

        # Import modules
        from core.document import AcceptedEdit, DocumentProcessor
        from core.llm import EditorLLM

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
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(non_empty_paragraphs)}</div>
                <div class="stat-label">Paragraphs</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            word_count = sum(len(p.split()) for p in non_empty_paragraphs)
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{word_count}</div>
                <div class="stat-label">Words</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            char_count = sum(len(p) for p in non_empty_paragraphs)
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{char_count}</div>
                <div class="stat-label">Characters</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Process button
        if st.button("🔍 Analyze Document", use_container_width=True):
            import concurrent.futures

            from core.models import SegmentReview

            # Reset edit decisions for new analysis
            st.session_state.edit_decisions = {}

            # Initialize LLM with the active API key
            try:
                llm = EditorLLM(api_key=active_api_key)
            except ValueError as e:
                st.error(str(e))
                return

            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Build list of (index, paragraph) for non-empty paragraphs
            para_tasks = [(i, para) for i, para in enumerate(paragraphs) if para.strip()]
            total_to_analyze = len(para_tasks)

            # Initialize results dict (to maintain order)
            results_dict = {}
            completed = 0

            def analyze_paragraph(task):
                """Analyze a single paragraph."""
                idx, para = task
                try:
                    return idx, llm.review_segment(para, language)
                except Exception:
                    return idx, SegmentReview(edits=[])

            # Process with concurrency
            status_text.text(f"Analyzing {total_to_analyze} paragraphs (concurrency: {concurrency})...")

            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = {executor.submit(analyze_paragraph, task): task for task in para_tasks}

                for future in concurrent.futures.as_completed(futures):
                    idx, review = future.result()
                    results_dict[idx] = review
                    completed += 1
                    progress_bar.progress(completed / total_to_analyze)
                    status_text.text(f"Analyzed {completed} of {total_to_analyze} paragraphs...")

            # Build final reviews list maintaining original paragraph order
            reviews = []
            for i, _para in enumerate(paragraphs):
                if i in results_dict:
                    reviews.append(results_dict[i])
                else:
                    # Empty paragraph
                    reviews.append(SegmentReview(edits=[]))

            status_text.text("✅ Analysis complete!")
            st.session_state.reviews = reviews
            st.session_state.processor = processor
            st.session_state.paragraphs = paragraphs

        # Display results if available
        if 'reviews' in st.session_state and st.session_state.reviews:
            reviews = st.session_state.reviews
            paragraphs = st.session_state.get('paragraphs', paragraphs)

            # Collect all edits with their indices
            all_edits_info = []
            for para_idx, review in enumerate(reviews):
                for edit_idx, edit in enumerate(review.get_actual_changes()):
                    all_edits_info.append({
                        "para_idx": para_idx,
                        "edit_idx": edit_idx,
                        "edit": edit
                    })

            st.markdown("---")

            # Count stats
            total_edits = len(all_edits_info)
            accepted_count = sum(
                1 for info in all_edits_info
                if st.session_state.edit_decisions.get(
                    get_edit_key(info["para_idx"], info["edit_idx"]), {}
                ).get("status") == "accepted"
            )
            rejected_count = sum(
                1 for info in all_edits_info
                if st.session_state.edit_decisions.get(
                    get_edit_key(info["para_idx"], info["edit_idx"]), {}
                ).get("status") == "rejected"
            )
            pending_count = total_edits - accepted_count - rejected_count

            st.markdown(f"### 📝 Found **{total_edits}** Edit(s)")
            st.markdown(f"✅ Accepted: **{accepted_count}** | ❌ Rejected: **{rejected_count}** | ⏳ Pending: **{pending_count}**")

            if all_edits_info:
                # Bulk action buttons
                st.markdown("#### Quick Actions")
                col1, col2, col3 = st.columns([1, 1, 2])

                with col1:
                    if st.button("✅ Accept All", use_container_width=True):
                        for info in all_edits_info:
                            key = get_edit_key(info["para_idx"], info["edit_idx"])
                            current = st.session_state.edit_decisions.get(key, {})
                            # Preserve custom text if already set
                            st.session_state.edit_decisions[key] = {
                                "status": "accepted",
                                "custom_text": current.get("custom_text")
                            }
                        st.rerun()

                with col2:
                    if st.button("❌ Reject All", use_container_width=True):
                        for info in all_edits_info:
                            key = get_edit_key(info["para_idx"], info["edit_idx"])
                            st.session_state.edit_decisions[key] = {
                                "status": "rejected",
                                "custom_text": None
                            }
                        st.rerun()

                with col3:
                    if st.button("🔄 Reset All", use_container_width=True):
                        for info in all_edits_info:
                            key = get_edit_key(info["para_idx"], info["edit_idx"])
                            st.session_state.edit_decisions[key] = {
                                "status": "pending",
                                "custom_text": None
                            }
                        st.rerun()

                st.markdown("---")

                # Category filter
                categories = list({info["edit"].rule_category for info in all_edits_info})
                selected_categories = st.multiselect(
                    "Filter by category:",
                    options=categories,
                    default=categories
                )

                # Build a mapping from para_idx to display number (only non-empty paragraphs)
                para_display_num = {}
                display_num = 0
                for i, para in enumerate(paragraphs):
                    if para.strip():
                        display_num += 1
                        para_display_num[i] = display_num

                # Group edits by paragraph
                edits_by_para = {}
                for info in all_edits_info:
                    para_idx = info["para_idx"]
                    if para_idx not in edits_by_para:
                        edits_by_para[para_idx] = []
                    edits_by_para[para_idx].append(info)

                # Display edits grouped by paragraph in collapsible sections
                for para_idx in sorted(edits_by_para.keys()):
                    para_edits = edits_by_para[para_idx]

                    # Filter by category
                    filtered_edits = [e for e in para_edits if e["edit"].rule_category in selected_categories]
                    if not filtered_edits:
                        continue

                    # Get display paragraph number
                    display_para_num = para_display_num.get(para_idx, para_idx + 1)

                    # Collapsible paragraph section
                    with st.expander(f"📄 Paragraph {display_para_num} — {len(filtered_edits)} edit(s)", expanded=True):
                        # Show original paragraph text with highlighted edits
                        if para_idx < len(paragraphs):
                            st.markdown("**Original text:**")
                            para_text = paragraphs[para_idx]
                            # Truncate if too long
                            if len(para_text) > 800:
                                para_text = para_text[:800] + "..."
                            highlighted_html = highlight_edits_in_text(para_text, filtered_edits, para_idx)
                            st.markdown(
                                f'<div style="font-family: \'Crimson Pro\', Georgia, serif; '
                                f'font-size: 1rem; line-height: 1.6; color: #444; '
                                f'padding: 0.8rem; background: #fafafa; border-radius: 8px; '
                                f'border-left: 3px solid #c9a227;">{highlighted_html}</div>',
                                unsafe_allow_html=True
                            )
                            st.markdown("---")

                        # Show each edit with numbering
                        for edit_num, info in enumerate(filtered_edits, 1):
                            edit = info["edit"]
                            edit_idx = info["edit_idx"]

                            st.markdown(f"**Edit {edit_num}**")
                            render_edit_card(edit, para_idx, edit_idx, paragraphs[para_idx])

                # Export section - only show if there are accepted edits
                if accepted_count > 0:
                    st.markdown("---")
                    st.markdown("### 📥 Export Revised Document")
                    st.info(f"📋 {accepted_count} edit(s) will be applied to the document.")

                    processor = st.session_state.get('processor')
                    if processor:
                        # Build list of accepted edits
                        accepted_edits = []
                        for info in all_edits_info:
                            key = get_edit_key(info["para_idx"], info["edit_idx"])
                            decision = st.session_state.edit_decisions.get(key, {})

                            if decision.get("status") == "accepted":
                                edit = info["edit"]
                                custom_text = decision.get("custom_text")
                                accepted_edits.append(AcceptedEdit(
                                    para_index=info["para_idx"],
                                    edit_index=info["edit_idx"],
                                    original_text=edit.original_text,
                                    final_text=custom_text if custom_text else edit.revised_text
                                ))

                        # Export with only accepted edits
                        doc_bytes = processor.export_with_accepted_edits(accepted_edits)

                        st.download_button(
                            label="⬇️ Download Revised Document",
                            data=doc_bytes,
                            file_name=f"edited_{uploaded_file.name}",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                elif total_edits > 0 and accepted_count == 0:
                    st.markdown("---")
                    st.info("💡 Accept at least one edit to enable document export.")
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
