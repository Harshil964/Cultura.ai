import streamlit as st


def metric_row(metrics: dict[str, int]) -> None:
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics.items()):
        with col:
            st.metric(label, value)


def status_badge(status: str) -> str:
    mapping = {
        "ok": "🟢 OK",
        "needs_review": "🟠 Needs review",
        "warning": "🟠 Warning",
        "extracted": "🟢 Extracted",
        "extracting": "🔵 Extracting…",
        "pending": "⚪ Pending",
        "failed": "🔴 Failed",
    }
    return mapping.get(status, status)


def info_card(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div style="border:1px solid #e5e7eb; border-radius:10px; padding:16px; margin-bottom:12px;">
            <div style="font-weight:600; margin-bottom:6px;">{title}</div>
            <div style="color:#374151; font-size:0.92rem;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
