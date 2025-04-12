import streamlit as st

def hide_default_sidebar():
    st.markdown("""
        <style>
            header {visibility: hidden;}
            footer {visibility: hidden;}
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

def hide_sidebar_when_not_logged_in():
    if not st.session_state.get("logged_in", False):
        hide_sidebar = """
            <style>
                [data-testid="stSidebar"] {display: none;}
                [data-testid="collapsedControl"] {display: none;}
            </style>
        """
        st.markdown(hide_sidebar, unsafe_allow_html=True)

def apply_custom_styles():
    st.markdown("""
        <style>
            .block-container {
                padding-top: 0rem !important;
            }
            h1 {
                margin-top: 50px !important;
                margin-bottom: 30px !important;
            }
        </style>
    """, unsafe_allow_html=True)
