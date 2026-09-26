import streamlit as st


def render_header(title: str, status_label: str = "AI Pipeline Ready", ok: bool = True) -> None:
    color = "#16a34a" if ok else "#dc2626"
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"## {title}")
    with col2:
        st.markdown(
            f"<div style='text-align:right; padding-top:14px;'>"
            f"<span style='color:{color}; font-weight:600;'>●</span> {status_label}"
            f"</div>",
            unsafe_allow_html=True,
        )
    st.markdown("<hr style='margin-top:0;'>", unsafe_allow_html=True)
