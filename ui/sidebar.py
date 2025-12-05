import streamlit as st

from core.llm import get_rules_dir, load_rules
from ui.utils import get_default_api_key


def render_sidebar() -> tuple[str, int]:
    """Render the sidebar with API key, settings, and rules."""
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
                key="use_own_key_checkbox",
            )
            st.session_state.use_custom_key = use_own

            if use_own:
                custom_key = st.text_input(
                    "Your API Key",
                    type="password",
                    value=st.session_state.custom_api_key,
                    help="Enter your own Gemini API key",
                )
                st.session_state.custom_api_key = custom_key
        else:
            st.warning("No default API key configured")
            custom_key = st.text_input(
                "Gemini API Key",
                type="password",
                value=st.session_state.custom_api_key,
                help="Enter your Gemini API key",
            )
            st.session_state.custom_api_key = custom_key
            st.session_state.use_custom_key = True

        st.markdown("---")

        st.markdown("### ⚙️ Settings")

        # Language preference
        language = st.selectbox(
            "Document Language",
            options=["greek", "english"],
            format_func=lambda x: {"greek": "🇬🇷 Greek", "english": "🇬🇧 English"}[x],
        )

        st.markdown("---")

        # Rules file management
        st.markdown("### 📄 Rules")

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
            use_container_width=True,
        )

        # Upload custom rules
        uploaded_rules = st.file_uploader(
            "📤 Upload Custom Rules",
            type=["txt"],
            key=f"rules_upload_{language}",
            help="Upload a .txt file to replace the current rules",
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
                help="Number of paragraphs to analyze simultaneously. Higher = faster.",
            )

        return language, concurrency
