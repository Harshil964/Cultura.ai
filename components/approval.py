import streamlit as st


def approval_gate(
    title: str,
    status: str,
    stats_line: str,
    on_approve,
    on_reject,
    edit_hint: str | None = None,
) -> None:
    """Renders the Approve/Reject/Edit card. status is one of
    'awaiting_approval' | 'approved' | 'rejected'.
    """
    with st.container(border=True):
        st.markdown(f"**{title}**")

        status_label = {
            "awaiting_approval": "● Awaiting Approval",
            "approved": "✓ Approved",
            "rejected": "✗ Rejected",
        }.get(status, status)
        st.write(f"Status: {status_label}")
        st.caption(stats_line)

        if status == "approved":
            st.success("Cultural plan approved.")
            return
        if status == "rejected":
            st.error("Plan rejected. Regenerate to try again.")
            return

        cols = st.columns(3)
        if edit_hint:
            cols[0].button("Edit", disabled=True, help=edit_hint)
        else:
            cols[0].button("Edit", disabled=True)
        if cols[1].button("Reject", key=f"reject_{title}"):
            on_reject()
            st.rerun()
        if cols[2].button("Approve", key=f"approve_{title}", type="primary"):
            on_approve()
            st.rerun()
