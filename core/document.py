"""
Document processing utilities for .docx files.
Handles reading, chunking, and writing with comments.
"""

import io
import re
from dataclasses import dataclass
from typing import BinaryIO, Optional

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from .models import EditAction, SegmentReview


@dataclass
class ProcessedParagraph:
    """Holds a paragraph's text and its index in the document."""
    index: int
    text: str
    original_paragraph: object  # docx Paragraph object


class DocumentProcessor:
    """
    Handles reading and writing .docx files with tracked changes.
    """
    
    def __init__(self):
        self.document: Optional[Document] = None
        self.paragraphs: list[ProcessedParagraph] = []
    
    def load_from_bytes(self, file_bytes: BinaryIO) -> list[str]:
        """
        Load a document from file bytes (e.g., from Streamlit uploader).
        
        Args:
            file_bytes: File-like object containing .docx data
            
        Returns:
            List of paragraph texts
        """
        self.document = Document(file_bytes)
        self.paragraphs = []
        
        for i, para in enumerate(self.document.paragraphs):
            self.paragraphs.append(ProcessedParagraph(
                index=i,
                text=para.text,
                original_paragraph=para
            ))
        
        return [p.text for p in self.paragraphs]
    
    def load_from_path(self, path: str) -> list[str]:
        """
        Load a document from a file path.
        
        Args:
            path: Path to the .docx file
            
        Returns:
            List of paragraph texts
        """
        self.document = Document(path)
        self.paragraphs = []
        
        for i, para in enumerate(self.document.paragraphs):
            self.paragraphs.append(ProcessedParagraph(
                index=i,
                text=para.text,
                original_paragraph=para
            ))
        
        return [p.text for p in self.paragraphs]
    
    def apply_edits_and_export(
        self, 
        reviews: list[SegmentReview],
        add_comments: bool = True,
        add_highlights: bool = True
    ) -> bytes:
        """
        Apply edits to the document and export as bytes.
        
        Args:
            reviews: List of SegmentReview objects, one per paragraph
            add_comments: Whether to add comments explaining edits
            add_highlights: Whether to highlight changed text
            
        Returns:
            Bytes of the modified .docx file
        """
        if not self.document:
            raise ValueError("No document loaded. Call load_from_bytes or load_from_path first.")
        
        # Create a new document with edits applied
        new_doc = Document()
        
        # Copy document styles if possible
        self._copy_styles(new_doc)
        
        for i, proc_para in enumerate(self.paragraphs):
            review = reviews[i] if i < len(reviews) else SegmentReview(edits=[])
            
            # Get the new paragraph text with all edits applied
            new_text = self._apply_edits_to_text(proc_para.text, review.edits)
            
            # Add paragraph to new document
            new_para = new_doc.add_paragraph()
            
            # Copy paragraph formatting from original
            self._copy_paragraph_format(proc_para.original_paragraph, new_para)
            
            if review.has_changes and add_highlights:
                # Add text with highlights and comments for changed portions
                self._add_highlighted_text(
                    new_para, 
                    proc_para.text, 
                    review.edits, 
                    add_comments
                )
            else:
                # Just add the text normally
                new_para.add_run(new_text)
        
        # Save to bytes
        buffer = io.BytesIO()
        new_doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _apply_edits_to_text(self, text: str, edits: list[EditAction]) -> str:
        """Apply all edits to a text string."""
        result = text
        # Sort edits by position (longest match first to avoid partial replacements)
        sorted_edits = sorted(edits, key=lambda e: len(e.original_text), reverse=True)
        
        for edit in sorted_edits:
            if edit.original_text != edit.revised_text:
                result = result.replace(edit.original_text, edit.revised_text, 1)
        
        return result
    
    def _add_highlighted_text(
        self, 
        paragraph, 
        original_text: str, 
        edits: list[EditAction],
        add_comments: bool
    ):
        """Add text with highlighted changes and optional comments."""
        # Build a map of edits
        text = original_text
        edit_positions = []
        
        for edit in edits:
            if edit.original_text == edit.revised_text:
                continue
                
            start = text.find(edit.original_text)
            if start != -1:
                edit_positions.append({
                    "start": start,
                    "end": start + len(edit.original_text),
                    "edit": edit
                })
        
        # Sort by position
        edit_positions.sort(key=lambda x: x["start"])
        
        # Build the paragraph with runs
        current_pos = 0
        comment_id = 0
        
        for ep in edit_positions:
            edit = ep["edit"]
            
            # Add text before this edit (unchanged)
            if ep["start"] > current_pos:
                paragraph.add_run(text[current_pos:ep["start"]])
            
            # Add the revised text with highlighting
            run = paragraph.add_run(edit.revised_text)
            
            # Yellow highlight for changes
            run.font.highlight_color = 7  # WD_COLOR_INDEX.YELLOW = 7
            
            # Add comment if requested
            if add_comments:
                self._add_comment_to_run(
                    run,
                    f"[{edit.rule_category}] {edit.reasoning}",
                    comment_id
                )
                comment_id += 1
            
            current_pos = ep["end"]
        
        # Add remaining text
        if current_pos < len(text):
            paragraph.add_run(text[current_pos:])
    
    def _add_comment_to_run(self, run, comment_text: str, comment_id: int):
        """
        Add a Word comment to a run.
        
        Note: python-docx doesn't natively support comments, so we use a workaround
        by adding the comment as a footnote-style annotation or by modifying the XML.
        For simplicity, we'll add a visible annotation.
        """
        # Since native Word comments require complex XML manipulation,
        # we'll add a superscript reference that links to the reasoning
        # This is a simpler but effective approach
        
        # Add superscript marker
        parent = run._r
        
        # Create comment reference
        comment_ref = OxmlElement('w:r')
        comment_ref_pr = OxmlElement('w:rPr')
        
        # Superscript
        vertAlign = OxmlElement('w:vertAlign')
        vertAlign.set(qn('w:val'), 'superscript')
        comment_ref_pr.append(vertAlign)
        
        # Color (blue for comment reference)
        color = OxmlElement('w:color')
        color.set(qn('w:val'), '0000FF')
        comment_ref_pr.append(color)
        
        # Font size (smaller)
        sz = OxmlElement('w:sz')
        sz.set(qn('w:val'), '16')  # 8pt
        comment_ref_pr.append(sz)
        
        comment_ref.append(comment_ref_pr)
        
        # Add the marker text
        text_elem = OxmlElement('w:t')
        text_elem.text = f'[{comment_id + 1}]'
        comment_ref.append(text_elem)
        
        parent.addnext(comment_ref)
    
    def _copy_styles(self, new_doc: Document):
        """Copy basic document styles."""
        # python-docx has limited style copying, so we just ensure basic styles exist
        pass
    
    def _copy_paragraph_format(self, source_para, target_para):
        """Copy paragraph formatting from source to target."""
        try:
            if source_para.style:
                target_para.style = source_para.style.name
        except Exception:
            pass  # Style may not exist in new document
    
    def export_with_track_changes_summary(
        self, 
        reviews: list[SegmentReview]
    ) -> bytes:
        """
        Export document with a summary of all changes at the end.
        
        Args:
            reviews: List of SegmentReview objects
            
        Returns:
            Bytes of the modified .docx file
        """
        if not self.document:
            raise ValueError("No document loaded.")
        
        new_doc = Document()
        
        # Add original content with applied edits
        all_edits = []
        
        for i, proc_para in enumerate(self.paragraphs):
            review = reviews[i] if i < len(reviews) else SegmentReview(edits=[])
            new_text = self._apply_edits_to_text(proc_para.text, review.edits)
            
            new_para = new_doc.add_paragraph(new_text)
            self._copy_paragraph_format(proc_para.original_paragraph, new_para)
            
            # Collect edits with paragraph reference
            for edit in review.get_actual_changes():
                all_edits.append((i + 1, edit))
        
        # Add separator
        new_doc.add_paragraph()
        separator = new_doc.add_paragraph("─" * 50)
        separator.alignment = 1  # Center
        
        # Add changes summary
        summary_title = new_doc.add_paragraph("📝 EDIT SUMMARY")
        summary_title.runs[0].bold = True
        summary_title.runs[0].font.size = Pt(14)
        
        new_doc.add_paragraph()
        
        for para_num, edit in all_edits:
            # Category badge
            category_para = new_doc.add_paragraph()
            cat_run = category_para.add_run(f"[{edit.rule_category}] ")
            cat_run.bold = True
            cat_run.font.color.rgb = RGBColor(0, 102, 204)
            
            # Original → Revised
            orig_run = category_para.add_run(f'"{edit.original_text}"')
            orig_run.font.color.rgb = RGBColor(204, 0, 0)  # Red
            
            category_para.add_run(" → ")
            
            rev_run = category_para.add_run(f'"{edit.revised_text}"')
            rev_run.font.color.rgb = RGBColor(0, 153, 0)  # Green
            
            # Reasoning
            reason_para = new_doc.add_paragraph()
            reason_para.add_run(f"   ↳ {edit.reasoning}")
            
            new_doc.add_paragraph()  # Spacing
        
        # Save to bytes
        buffer = io.BytesIO()
        new_doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()


def detect_language(text: str) -> str:
    """
    Simple language detection based on character ranges.
    
    Args:
        text: Text to analyze
        
    Returns:
        "greek", "english", or "mixed"
    """
    greek_chars = len(re.findall(r'[\u0370-\u03FF\u1F00-\u1FFF]', text))
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    
    total = greek_chars + latin_chars
    if total == 0:
        return "auto"
    
    greek_ratio = greek_chars / total
    
    if greek_ratio > 0.7:
        return "greek"
    elif greek_ratio < 0.3:
        return "english"
    else:
        return "mixed"

