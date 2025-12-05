import html
from typing import Any

import streamlit as st

from core.models import EditAction
from ui.utils import get_edit_key, get_rule_badge_class


def highlight_edits_in_text(text: str, edits: list[dict[str, Any]], para_idx: int) -> str:
    """
    Create HTML with highlighted portions where edits were identified.

    Args:
        text: Original paragraph text
        edits: List of edit info dicts with 'edit' containing the EditAction
        para_idx: Paragraph index for generating anchor IDs

    Returns:
        HTML string with highlighted edit portions
    """

    if not edits:
        return html.escape(text)

    # Find all edit positions
    highlights = []
    for edit_num, info in enumerate(edits, 1):
        edit = info["edit"]
        original = edit.original_text
        start = text.find(original)
        if start != -1:
            highlights.append(
                {
                    "start": start,
                    "end": start + len(original),
                    "text": original,
                    "edit_num": edit_num,
                }
            )

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
            result.append(html.escape(text[pos : h["start"]]))

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


def render_edit_card(
    edit: EditAction, para_idx: int, edit_idx: int, original_paragraph: str
) -> None:
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
    st.markdown(
        f"""
    <div class="{card_class}">
        <span class="rule-badge {badge_class}">{edit.rule_category}</span>
        <div class="original-text">{edit.original_text}</div>
        <div class="arrow-divider">↓</div>
        <div class="revised-text">{custom_text if custom_text else edit.revised_text}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Reasoning expander
    with st.expander("📖 View Reasoning", expanded=False):
        st.markdown(
            f"""
        <div class="reasoning-text">
            {edit.reasoning}
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Action buttons
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])

    with col1:
        if st.button("✅ Accept", key=f"accept_{key}", disabled=(status == "accepted")):
            st.session_state.edit_decisions[key] = {
                "status": "accepted",
                "custom_text": custom_text,
            }
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
            label_visibility="collapsed",
        )

        with col4:
            if st.button("💾 Use Custom", key=f"save_custom_{key}"):
                if new_custom.strip():
                    st.session_state.edit_decisions[key] = {
                        "status": "accepted",
                        "custom_text": new_custom.strip(),
                    }
                    st.rerun()

    # Status indicator
    status_class = f"status-{status}"
    status_text = {"pending": "⏳ Pending", "accepted": "✅ Accepted", "rejected": "❌ Rejected"}
    st.markdown(
        f'<small class="{status_class}">{status_text[status]}</small>', unsafe_allow_html=True
    )

    st.markdown("---")
