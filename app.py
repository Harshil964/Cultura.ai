import streamlit as st

from components.sidebar import render_sidebar
from components.header import render_header
from components.cards import metric_row
from database.connection import init_db
from database.repositories import project_repository as repo

st.set_page_config(page_title="Cultura AI", page_icon="🎬", layout="wide")
init_db()

st.session_state.setdefault("completed_steps", set())
st.session_state.setdefault("project_id", None)
st.session_state.setdefault("project_summary", None)

render_sidebar(current_step="upload")
render_header("Cultura AI — Cultural Screenplay & Visual Adaptation Studio")

st.write(
    "Transform a screenplay into a culturally authentic production package: "
    "structured scenes, a character bible, a reviewable cultural-adaptation plan, "
    "adapted dialogue, generated visuals, and a continuity report — exported as one pack."
)

summary = st.session_state.get("project_summary")

if summary:
    st.markdown("### Project status")
    metric_row(
        {
            "Scenes": len(summary["scenes"]),
            "Characters": len(summary["characters"]),
            "Costumes": len(summary["costumes"]),
            "Props": len(summary["props"]),
        }
    )
    st.markdown("---")
    if st.button("Continue Project →", type="primary"):
        st.switch_page("pages/02_Extraction.py")
else:
    st.info("No project loaded yet. Upload a screenplay to get started.")

st.markdown("---")
st.markdown("### Recent projects")
projects = repo.list_projects()
if projects:
    for p in projects[:5]:
        cols = st.columns([3, 2, 2, 1])
        cols[0].write(f"**{p['name']}**")
        cols[1].write(p["extraction_status"])
        cols[2].write(p["created_at"][:19].replace("T", " "))
        if cols[3].button("Open", key=f"open_{p['id']}"):
            st.session_state["project_id"] = p["id"]
            st.session_state["project_summary"] = repo.get_project_summary(p["id"])
            st.switch_page("pages/02_Extraction.py")
else:
    st.caption("Nothing here yet.")

st.markdown("")
if st.button("＋ New Adaptation"):
    st.switch_page("pages/01_Upload.py")
