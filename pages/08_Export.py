import streamlit as st

from components.sidebar import render_sidebar
from components.header import render_header
from database.repositories import project_repository as project_repo
from database.repositories import adaptation_repository as adaptation_repo
from database.repositories import continuity_repository as continuity_repo
from services.export_service import build_production_pack

st.set_page_config(page_title="Export — Cultura AI", page_icon="🎬", layout="wide")

project_id = st.session_state.get("project_id")
if not project_id:
    st.warning("No project loaded. Start by uploading a screenplay.")
    st.stop()

summary = project_repo.get_project_summary(project_id)
st.session_state["project_summary"] = summary

render_sidebar(current_step="export")
render_header("Production Pack")

adapted_scenes = adaptation_repo.get_adapted_scenes(project_id)
issues = continuity_repo.get_issues(project_id)
open_issues = [i for i in issues if i["status"] == "open"]

checklist = [
    ("Adapted Screenplay", bool(adapted_scenes)),
    ("Scene Breakdown", bool(summary["scenes"])),
    ("Continuity Report", bool(issues)),
    ("Character Bible", bool(summary["characters"])),
    ("Costume Bible", bool(summary["costumes"])),
    ("Structured Data (JSON)", True),
]

for label, ready in checklist:
    st.markdown(("✓ " if ready else "○ ") + label)

if open_issues:
    st.warning(f"{len(open_issues)} continuity issue(s) are still open. You can still export — they'll be listed in the report.")

st.markdown("---")

pack_bytes = build_production_pack(project_id)
st.download_button(
    "Download Complete Production Pack",
    data=pack_bytes,
    file_name=f"{summary['name'].replace(' ', '_')}_production_pack.zip",
    mime="application/zip",
    type="primary",
)

st.session_state["completed_steps"] = st.session_state.get("completed_steps", set()) | {"export"}
