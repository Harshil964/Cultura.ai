import streamlit as st

from components.sidebar import render_sidebar
from components.header import render_header
from database.repositories import project_repository as repo

st.set_page_config(page_title="Characters — Cultura AI", page_icon="🎬", layout="wide")

project_id = st.session_state.get("project_id")
if not project_id:
    st.warning("No project loaded. Start by uploading a screenplay.")
    st.stop()

summary = repo.get_project_summary(project_id)
st.session_state["project_summary"] = summary

render_sidebar(current_step="characters")
render_header("Character Bible")

if not summary["characters"]:
    st.info("No characters extracted yet. Run Extraction first.")
    st.stop()

approved_count = sum(1 for c in summary["characters"] if c["approved"])
st.caption(f"{approved_count} of {len(summary['characters'])} characters approved")

cols_per_row = 3
characters = summary["characters"]
for row_start in range(0, len(characters), cols_per_row):
    row = characters[row_start : row_start + cols_per_row]
    cols = st.columns(cols_per_row)
    for col, c in zip(cols, row):
        with col:
            with st.container(border=True):
                st.markdown(f"**{c['canonical_name']}**")
                st.caption(c["character_id"])
                st.write(f"Age: {c['age'] or '—'}")
                st.write(f"Role: {c['role'] or '—'}")
                if c["aliases"]:
                    st.write("Aliases: " + ", ".join(c["aliases"]))
                if c["relationships"]:
                    st.write("Relationships: " + ", ".join(c["relationships"]))

                btn_cols = st.columns(3)
                btn_cols[0].button("Edit", key=f"edit_{c['character_id']}", disabled=True)
                btn_cols[1].button("Merge", key=f"merge_{c['character_id']}", disabled=True)
                is_approved = c["approved"]
                label = "✓ Approved" if is_approved else "Approve"
                if btn_cols[2].button(label, key=f"approve_{c['character_id']}", type="secondary" if is_approved else "primary"):
                    repo.set_character_approved(c["character_id"], not is_approved)
                    st.rerun()

st.markdown("---")
if approved_count == len(characters) and characters:
    st.session_state["completed_steps"] = st.session_state.get("completed_steps", set()) | {"characters"}
    if st.button("Continue to Cultural Plan →", type="primary"):
        st.switch_page("pages/04_Cultural_Plan.py")
else:
    st.caption("Approve every character to continue to the Cultural Plan step.")
