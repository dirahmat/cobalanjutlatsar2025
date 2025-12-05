import streamlit as st

def init_page_state(prefix, defaults: dict):
    """Initialize session_state with a prefix and default values."""
    for key, value in defaults.items():
        full_key = f"{prefix}{key}"
        if full_key not in st.session_state:
            st.session_state[full_key] = value

def get(prefix, key):
    return st.session_state.get(f"{prefix}{key}")

def set(prefix, key, value):
    st.session_state[f"{prefix}{key}"] = value

def clear_other_states(allowed_prefix):
    """Delete all session_state keys that are not from this page."""
    to_delete = [k for k in st.session_state if not k.startswith(allowed_prefix)]
    for k in to_delete:
        del st.session_state[k]
