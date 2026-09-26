import streamlit as st

from components.sidebar import render_sidebar
from components.header import render_header
from database.repositories import project_repository as project_repo
from database.repositories import cultural_repository as cultural_repo
from database.repositories import adaptation_repository as adaptation_repo
from services.adaptation_service import run_adaptation, AdaptationNotAllowed

st.set_page_config(page_title="Adaptation — Cultura AI", page_icon="🎬", layout="wide")

project_id = st.session_state.get("project_id")
if not project_id:
    st.warning("No project loaded. Start by uploading a screenplay.")
    st.stop()

summary = project_repo.get_project_summary(project_id)
st.session_state["project_summary"] = summary

render_sidebar(current_step="adaptation")
render_header("Adapted Screenplay")

plan = cultural_repo.get_plan(project_id)
if plan is None or plan["approval_status"] != "approved":
    st.warning("Adaptation requires an approved cultural plan.")
    if st.button("Go to Cultural Plan →"):
        st.switch_page("pages/04_Cultural_Plan.py")
    st.stop()

adapted_scenes = {s["scene_id"]: s for s in adaptation_repo.get_adapted_scenes(project_id)}

if st.button("Generate Adaptation" if not adapted_scenes else "Re-run Adaptation", type="primary"):
    with st.spinner("Adapting dialogue and action scene by scene…"):
        try:
            success, error = run_adaptation(project_id)
        except AdaptationNotAllowed as e:
            success, error = False, str(e)
    if success:
        st.rerun()
    else:
        st.error(f"Adaptation failed: {error}")

if not adapted_scenes:
    st.info("No adapted scenes yet.")
    st.stop()

st.markdown("---")

for scene in summary["scenes"]:
    adapted = adapted_scenes.get(scene["scene_id"])
    if not adapted:
        continue

    st.markdown(f"#### {scene['scene_id']} — {scene['heading']}")
    col_original, col_adapted = st.columns(2)
    with col_original:
        st.caption("ORIGINAL")
        st.text_area(
            "original", scene["raw_text"], height=180, disabled=True,
            key=f"orig_{scene['scene_id']}", label_visibility="collapsed",
        )
    with col_adapted:
        st.caption("ADAPTED")
        st.text_area(
            "adapted", adapted["adapted_text"], height=180, disabled=True,
            key=f"adapt_{scene['scene_id']}", label_visibility="collapsed",
        )

    if adapted["changes"]:
        with st.expander("Why was this changed?"):
            for c in adapted["changes"]:
                st.markdown(f"⚡ **{c['aspect']}** — {c['explanation']}")

    st.markdown("---")

st.session_state["completed_steps"] = st.session_state.get("completed_steps", set()) | {"adaptation"}
if st.button("Continue to Visual Studio →", type="primary"):
    st.switch_page("pages/06_Visual_Studio.py")
