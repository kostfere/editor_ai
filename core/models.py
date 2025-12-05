"""
Pydantic models for structured LLM output.
These models define the schema for Gemini's response_schema parameter.
"""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class GeminiModel(str, Enum):
    """Available Gemini models."""

    GEMINI_2_5_FLASH = "gemini-2.5-flash"


class Language(str, Enum):
    """Supported languages for document analysis."""

    GREEK = "greek"
    ENGLISH = "english"


class EditAction(BaseModel):
    """
    Represents a single edit action with justification.

    Attributes:
        original_text: The original text segment that needs revision
        revised_text: The corrected/improved text
        rule_category: Classification of the edit type
        reasoning: Detailed explanation of why this edit was made
    """

    original_text: str = Field(description="The exact original text that needs to be edited")
    revised_text: str = Field(description="The corrected or improved version of the text")
    rule_category: Literal[
        "Grammar", "Style", "Formatting", "Punctuation", "Spelling", "Syntax" "Other"
    ] = Field(description="The category of rule that triggered this edit")
    reasoning: str = Field(
        description=(
            "Detailed explanation of why this edit was made, "
            "citing the specific rule applied. For Greek Final Nu: "
            "explain the phonetic context. For English: cite style guide rule."
        )
    )


class SegmentReview(BaseModel):
    """
    Contains all edits for a text segment/paragraph.

    This is the top-level response schema passed to Gemini.
    """

    edits: list[EditAction] = Field(
        default_factory=list, description="List of all edits identified in the text segment"
    )

    @property
    def has_changes(self) -> bool:
        """Check if any actual changes were made."""
        return any(edit.original_text != edit.revised_text for edit in self.edits)

    def get_actual_changes(self) -> list[EditAction]:
        """Return only edits where text was actually modified."""
        return [edit for edit in self.edits if edit.original_text != edit.revised_text]
