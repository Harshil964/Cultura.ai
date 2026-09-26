import streamlit as st

from components.sidebar import render_sidebar
from components.header import render_header
from database.repositories import project_repository as project_repo
from services.visual_service import generate_image, ImageGenerationNotConfigured

st.set_page_config(page_title="Visual Studio — Cultura AI", page_icon="🎬", layout="wide")

project_id = st.session_state.get("project_id")
if not project_id:
    st.warning("No project loaded. Start by uploading a screenplay.")
    st.stop()

summary = project_repo.get_project_summary(project_id)
st.session_state["project_summary"] = summary

render_sidebar(current_step="visual_studio")
render_header("Visual Studio", status_label="Image generation not configured", ok=False)

st.caption(
    "Character references, costume variants, and scene keyframes render here once an image "
    "provider is wired into services/visual_service.py (see IMAGE_PROVIDER / IMAGE_API_KEY in .env)."
)

tab_chars, tab_costumes, tab_scenes = st.tabs(["Characters", "Costumes", "Scenes"])


def _placeholder_grid(items: list[dict], id_key: str, label_key: str):
    if not items:
        st.info("Nothing to visualize yet.")
        return
    cols_per_row = 3
    for row_start in range(0, len(items), cols_per_row):
        row = items[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, item in zip(cols, row):
            with col:
                with st.container(border=True):
                    st.markdown(
                        "<div style='height:140px; background:#f3f4f6; border-radius:8px; "
                        "display:flex; align-items:center; justify-content:center; color:#9ca3af;'>"
                        "IMAGE</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**{item[label_key]}**")
                    st.caption(item[id_key])
                    if st.button("Generate", key=f"gen_{item[id_key]}"):
                        try:
                            generate_image(f"Reference image for {item[label_key]}")
                        except ImageGenerationNotConfigured as e:
                            st.warning(str(e))
                        except NotImplementedError as e:
                            st.warning(str(e))


with tab_chars:
    _placeholder_grid(summary["characters"], "character_id", "canonical_name")

with tab_costumes:
    _placeholder_grid(summary["costumes"], "costume_id", "description")

with tab_scenes:
    _placeholder_grid(summary["scenes"], "scene_id", "heading")

st.markdown("---")
if st.button("Continue to Continuity →", type="primary"):
    st.session_state["completed_steps"] = st.session_state.get("completed_steps", set()) | {"visual_studio"}
    st.switch_page("pages/07_Continuity.py")
