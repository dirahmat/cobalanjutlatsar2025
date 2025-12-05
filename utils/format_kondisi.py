# state_utils.py
import streamlit as st

def init_page_state(prefix, defaults: dict):
    """
    Initialize page-specific session state.
    Example: prefix="upah_" → keys "upah_num_rows", "upah_page" etc.
    """
    for key, value in defaults.items():
        full = f"{prefix}{key}"
        if full not in st.session_state:
            st.session_state[full] = value


def get(prefix, key):
    """Safe helper to read session state."""
    return st.session_state.get(f"{prefix}{key}")


def set(prefix, key, value):
    """Safe helper to write session state."""
    st.session_state[f"{prefix}{key}"] = value


def clear_other_states(allowed_prefix):
    """
    Clear all session_state entries EXCEPT those with this prefix.
    Prevents data leakage between Streamlit pages.
    """
    to_delete = [
        k for k in st.session_state.keys()
        if not k.startswith(allowed_prefix)
    ]
    for k in to_delete:
        del st.session_state[k]
