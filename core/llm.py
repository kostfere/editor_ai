"""
LLM Engine using Google GenAI SDK.
"""

import os
import json
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv

from core.models import SegmentReview

# Load environment variables
load_dotenv()

# Base system prompt
BASE_SYSTEM_PROMPT = """You are a strict, meticulous Publisher's Editor. Your role is to review text and identify ALL necessary corrections based on the rules provided.

## Your Editing Philosophy
- Be thorough: catch every error, no matter how small
- Be precise: explain exactly which rule applies
- Be consistent: apply the same standards throughout

## Output Requirements
For EACH edit you identify:
1. Quote the EXACT original text that needs to be changed
2. Provide the corrected text
3. Categorize the rule type
4. Explain WHY, citing the specific rule

If text is already correct, return an empty edits array.
"""


def get_rules_dir() -> Path:
    """Get the rules directory path."""
    # First check if there's a rules dir in current working directory
    cwd_rules = Path.cwd() / "rules"
    if cwd_rules.exists():
        return cwd_rules
    
    # Fall back to the package rules directory
    return Path(__file__).parent.parent / "rules"


def load_rules(language: str) -> str:
    """
    Load rules from the appropriate language file.
    
    Args:
        language: "greek" or "english"
        
    Returns:
        Rules text content
    """
    rules_dir = get_rules_dir()
    rules_file = rules_dir / f"{language}.txt"
    
    if not rules_file.exists():
        raise FileNotFoundError(
            f"Rules file not found: {rules_file}\n"
            f"Please create a rules file at: {rules_file}"
        )
    
    return rules_file.read_text(encoding="utf-8")


class EditorLLM:
    """
    Wrapper for Gemini with structured output for editing tasks.
    """
    
    MODEL_NAME = "gemini-2.5-flash"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Optional API key. If not provided, reads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in your environment "
                "or pass it to the constructor."
            )
        
        self.client = genai.Client(api_key=self.api_key)
    
    def review_segment(self, text: str, language: str) -> SegmentReview:
        """
        Review a text segment and return structured edit suggestions.
        
        Args:
            text: The text to review
            language: "greek" or "english"
            
        Returns:
            SegmentReview containing all identified edits
        """
        # Load rules for the specified language
        rules = load_rules(language)
        
        # Build the full prompt
        system_prompt = BASE_SYSTEM_PROMPT + "\n\n## Rules to Apply\n\n" + rules
        user_prompt = f"""## Text to Review

```
{text}
```

Analyze this text thoroughly. Identify ALL errors based on the rules provided and give corrections with detailed reasoning. If the text is perfect, return an empty edits array."""
        
        # Configure generation with thinking for thorough analysis
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=10000
            ),
            response_mime_type="application/json",
            response_schema=SegmentReview,
        )
        
        # Generate content with structured output
        response = self.client.models.generate_content(
            model=self.MODEL_NAME,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=system_prompt + "\n\n" + user_prompt)]
                )
            ],
            config=config,
        )
        
        # Parse the response into our Pydantic model
        if response.text:
            data = json.loads(response.text)
            return SegmentReview(**data)
        
        return SegmentReview(edits=[])
    
    def review_document(
        self, 
        paragraphs: list[str], 
        language: str,
        progress_callback: Optional[callable] = None
    ) -> list[SegmentReview]:
        """
        Review an entire document paragraph by paragraph.
        
        Args:
            paragraphs: List of paragraph texts
            language: "greek" or "english"
            progress_callback: Optional callback(current, total) for progress updates
            
        Returns:
            List of SegmentReview objects, one per paragraph
        """
        results = []
        total = len(paragraphs)
        
        for i, paragraph in enumerate(paragraphs):
            # Skip empty paragraphs
            if not paragraph.strip():
                results.append(SegmentReview(edits=[]))
                continue
            
            # Review this paragraph
            review = self.review_segment(paragraph, language)
            results.append(review)
            
            # Report progress
            if progress_callback:
                progress_callback(i + 1, total)
        
        return results
