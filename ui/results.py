import streamlit as st

from core.document import AcceptedEdit
from ui.components import highlight_edits_in_text, render_edit_card
from ui.utils import get_edit_key


def render_results(paragraphs, uploaded_file):
    """Render the analysis results."""
    if "reviews" in st.session_state and st.session_state.reviews:
        reviews = st.session_state.reviews
        paragraphs = st.session_state.get("paragraphs", paragraphs)

        # Collect all edits with their indices
        all_edits_info = []
        for para_idx, review in enumerate(reviews):
            for edit_idx, edit in enumerate(review.get_actual_changes()):
                all_edits_info.append({"para_idx": para_idx, "edit_idx": edit_idx, "edit": edit})

        st.markdown("---")

        # Count stats
        total_edits = len(all_edits_info)
        accepted_count = sum(
            1
            for info in all_edits_info
            if st.session_state.edit_decisions.get(
                get_edit_key(info["para_idx"], info["edit_idx"]), {}
            ).get("status")
            == "accepted"
        )
        rejected_count = sum(
            1
            for info in all_edits_info
            if st.session_state.edit_decisions.get(
                get_edit_key(info["para_idx"], info["edit_idx"]), {}
            ).get("status")
            == "rejected"
        )
        pending_count = total_edits - accepted_count - rejected_count

        st.markdown(f"### 📝 Found **{total_edits}** Edit(s)")
        st.markdown(
            f"✅ Accepted: **{accepted_count}** | ❌ Rejected: **{rejected_count}** | ⏳ Pending: **{pending_count}**"
        )

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
                            "custom_text": current.get("custom_text"),
                        }
                    st.rerun()

            with col2:
                if st.button("❌ Reject All", use_container_width=True):
                    for info in all_edits_info:
                        key = get_edit_key(info["para_idx"], info["edit_idx"])
                        st.session_state.edit_decisions[key] = {
                            "status": "rejected",
                            "custom_text": None,
                        }
                    st.rerun()

            with col3:
                if st.button("🔄 Reset All", use_container_width=True):
                    for info in all_edits_info:
                        key = get_edit_key(info["para_idx"], info["edit_idx"])
                        st.session_state.edit_decisions[key] = {
                            "status": "pending",
                            "custom_text": None,
                        }
                    st.rerun()

            st.markdown("---")

            # Category filter
            categories = list({info["edit"].rule_category for info in all_edits_info})
            selected_categories = st.multiselect(
                "Filter by category:", options=categories, default=categories
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
                filtered_edits = [
                    e for e in para_edits if e["edit"].rule_category in selected_categories
                ]
                if not filtered_edits:
                    continue

                # Get display paragraph number
                display_para_num = para_display_num.get(para_idx, para_idx + 1)

                # Collapsible paragraph section
                with st.expander(
                    f"📄 Paragraph {display_para_num} — {len(filtered_edits)} edit(s)",
                    expanded=True,
                ):
                    # Show original paragraph text with highlighted edits
                    if para_idx < len(paragraphs):
                        st.markdown("**Original text:**")
                        para_text = paragraphs[para_idx]
                        # Truncate if too long
                        if len(para_text) > 800:
                            para_text = para_text[:800] + "..."
                        highlighted_html = highlight_edits_in_text(
                            para_text, filtered_edits, para_idx
                        )
                        st.markdown(
                            f"<div style=\"font-family: 'Crimson Pro', Georgia, serif; "
                            f"font-size: 1rem; line-height: 1.6; color: #444; "
                            f"padding: 0.8rem; background: #fafafa; border-radius: 8px; "
                            f'border-left: 3px solid #c9a227;">{highlighted_html}</div>',
                            unsafe_allow_html=True,
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

                processor = st.session_state.get("processor")
                if processor:
                    # Build list of accepted edits
                    accepted_edits = []
                    for info in all_edits_info:
                        key = get_edit_key(info["para_idx"], info["edit_idx"])
                        decision = st.session_state.edit_decisions.get(key, {})

                        if decision.get("status") == "accepted":
                            edit = info["edit"]
                            custom_text = decision.get("custom_text")
                            accepted_edits.append(
                                AcceptedEdit(
                                    para_index=info["para_idx"],
                                    edit_index=info["edit_idx"],
                                    original_text=edit.original_text,
                                    final_text=custom_text if custom_text else edit.revised_text,
                                )
                            )

                    # Export with only accepted edits
                    doc_bytes = processor.export_with_accepted_edits(accepted_edits)

                    st.download_button(
                        label="⬇️ Download Revised Document",
                        data=doc_bytes,
                        file_name=f"edited_{uploaded_file.name}",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
            elif total_edits > 0 and accepted_count == 0:
                st.markdown("---")
                st.info("💡 Accept at least one edit to enable document export.")
        else:
            st.success("✨ No edits needed! Your document looks perfect.")
