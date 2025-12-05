import concurrent.futures

import streamlit as st

from core.llm import EditorLLM
from core.models import Language, SegmentReview


def analyze_document(
    paragraphs: list[str],
    language: Language,
    concurrency: int,
    active_api_key: str,
    temperature: float,
) -> None:
    """
    Analyze the document paragraphs using the LLM.

    Args:
        paragraphs: List of paragraph strings
        language: Language enum value
        concurrency: Number of parallel requests
        active_api_key: API key to use
        temperature: LLM temperature setting
    """
    # Reset edit decisions for new analysis
    st.session_state.edit_decisions = {}

    # Initialize LLM with the active API key
    try:
        llm = EditorLLM(api_key=active_api_key, temperature=temperature)
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

    def analyze_paragraph(task: tuple[int, str]) -> tuple[int, SegmentReview]:
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
