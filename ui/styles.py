"""
Custom CSS styles for the application.
"""

CUSTOM_CSS = """
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
"""
