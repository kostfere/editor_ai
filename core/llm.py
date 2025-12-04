"""
LLM Engine using Google GenAI SDK with Gemini 3 Pro.
"""

import os
from typing import Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv

from .models import SegmentReview

# Load environment variables
load_dotenv()


# System prompt for the editor
EDITOR_SYSTEM_PROMPT = """You are a strict, meticulous Publisher's Editor with expertise in both Greek and English language rules. Your role is to review text and identify ALL necessary corrections.

## Your Editing Philosophy
- Be thorough: catch every error, no matter how small
- Be precise: explain exactly which rule applies
- Be consistent: apply the same standards throughout

## Greek Language Rules (CRITICAL)

### 1. Τελικό Ν (Final Nu) Rule - ENFORCE STRICTLY
The words: τον, την, έναν, αυτόν, αυτήν, δεν, μην KEEP the final ν (n) ONLY before:
- Vowels (α, ε, η, ι, ο, υ, ω)
- Consonants: κ, π, τ, γκ, μπ, ντ, ξ, ψ

REMOVE the final ν before all other consonants (β, γ, δ, ζ, θ, λ, μ, ν, ρ, σ, φ, χ).

Examples:
- "τον πατέρα" ✓ (keep ν before π)
- "το βιβλίο" ✓ (remove ν before β → "το" not "τον")
- "την καρδιά" ✓ (keep ν before κ)
- "τη μητέρα" ✓ (remove ν before μ → "τη" not "την")
- "δεν ξέρω" ✓ (keep ν before ξ)
- "δε θέλω" ✓ (remove ν before θ → "δε" not "δεν")

### 2. Monotonic System
- Only one accent mark (τόνος) per word
- Accent on the stressed syllable
- No breathing marks (πνεύματα) in modern Greek

## English Language Rules

### 1. Oxford Comma (Serial Comma)
ALWAYS use a comma before "and" or "or" in a list of three or more items.
- "red, white, and blue" ✓
- "red, white and blue" ✗

### 2. Active Voice
Prefer active voice over passive voice when the agent is known.
- "The team completed the project" ✓
- "The project was completed by the team" ✗ (unless passive is intentional for emphasis)

### 3. Subject-Verb Agreement
Ensure subjects and verbs agree in number.

### 4. Punctuation
- Periods and commas inside quotation marks (American English)
- Proper use of semicolons and colons
- No double spaces after periods

## Output Requirements
For EACH edit you identify:
1. Quote the EXACT original text
2. Provide the corrected text
3. Categorize the rule type
4. Explain WHY, citing the specific rule

If text is already correct, return an empty edits array.
"""


class EditorLLM:
    """
    Wrapper for Gemini 3 Pro with structured output for editing tasks.
    """
    
    MODEL_NAME = "gemini-3-pro-preview"
    
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
    
    def review_segment(self, text: str, language_hint: str = "auto") -> SegmentReview:
        """
        Review a text segment and return structured edit suggestions.
        
        Args:
            text: The text to review
            language_hint: "greek", "english", or "auto" for automatic detection
            
        Returns:
            SegmentReview containing all identified edits
        """
        # Build the user prompt
        user_prompt = self._build_prompt(text, language_hint)
        
        # Configure generation with thinking_level for deep reasoning
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=10000  # High thinking budget for thorough analysis
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
                    parts=[types.Part(text=EDITOR_SYSTEM_PROMPT + "\n\n" + user_prompt)]
                )
            ],
            config=config,
        )
        
        # Parse the response into our Pydantic model
        if response.text:
            import json
            data = json.loads(response.text)
            return SegmentReview(**data)
        
        return SegmentReview(edits=[])
    
    def _build_prompt(self, text: str, language_hint: str) -> str:
        """Build the user prompt for text review."""
        hint_text = ""
        if language_hint == "greek":
            hint_text = "This text is in Greek. Pay special attention to Final Nu (Τελικό Ν) rules."
        elif language_hint == "english":
            hint_text = "This text is in English. Enforce Oxford comma and active voice."
        else:
            hint_text = "Detect the language and apply appropriate rules."
        
        return f"""## Text to Review

{hint_text}

```
{text}
```

Analyze this text thoroughly. Identify ALL errors and provide corrections with detailed reasoning. If the text is perfect, return an empty edits array."""
    
    def review_document(
        self, 
        paragraphs: list[str], 
        language_hint: str = "auto",
        progress_callback: Optional[callable] = None
    ) -> list[SegmentReview]:
        """
        Review an entire document paragraph by paragraph.
        
        Args:
            paragraphs: List of paragraph texts
            language_hint: Language hint for all paragraphs
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
            review = self.review_segment(paragraph, language_hint)
            results.append(review)
            
            # Report progress
            if progress_callback:
                progress_callback(i + 1, total)
        
        return results

