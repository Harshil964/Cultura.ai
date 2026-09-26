import streamlit as st

from components.sidebar import render_sidebar
from components.header import render_header
from services.document_service import extract_text, UnsupportedFileType
from services.extraction_service import run_extraction
from database.repositories import project_repository as repo

st.set_page_config(page_title="Upload — Cultura AI", page_icon="🎬", layout="wide")

render_sidebar(current_step="upload")
render_header("Create New Adaptation")

st.markdown("#### Upload Screenplay")

tab_upload, tab_paste = st.tabs(["Drag & Drop", "Paste Text"])

screenplay_text = None
source_filename = None

with tab_upload:
    uploaded = st.file_uploader("PDF / DOCX / TXT", type=["pdf", "docx", "txt"])
    if uploaded is not None:
        try:
            screenplay_text = extract_text(uploaded.read(), uploaded.name)
            source_filename = uploaded.name
            st.success(f"Loaded {len(screenplay_text.split())} words from {uploaded.name}")
            with st.expander("Preview extracted text"):
                st.text(screenplay_text[:3000] + ("…" if len(screenplay_text) > 3000 else ""))
        except UnsupportedFileType as e:
            st.error(str(e))

with tab_paste:
    pasted = st.text_area("Paste screenplay text", height=240)
    if pasted.strip():
        screenplay_text = pasted
        source_filename = "pasted_text.txt"

st.markdown("---")
st.markdown("#### Cultural Target")

col1, col2 = st.columns(2)
with col1:
    culture = st.selectbox("Culture", ["Marwari", "Bengali", "Tamil", "Punjabi", "Awadhi", "Other"])
    setting = st.radio("Setting", ["Rural", "Urban"], horizontal=True)
with col2:
    region = st.text_input("Region", value="Rajasthan" if culture == "Marwari" else "")
    script = st.selectbox("Script", ["Devanagari", "Latin", "Bengali", "Tamil", "Gurmukhi", "Other"])

st.markdown("---")

disabled = screenplay_text is None
if st.button("Analyze Screenplay →", type="primary", disabled=disabled):
    project_name = (source_filename or "Untitled Project").rsplit(".", 1)[0]
    project_id = repo.create_project(project_name, source_filename, screenplay_text)
    repo.set_cultural_target(project_id, culture, region, setting, script)

    st.session_state["project_id"] = project_id
    st.session_state["completed_steps"] = {"upload"}

    with st.spinner("Extracting scenes, characters, locations, costumes, and props…"):
        success, error = run_extraction(project_id, screenplay_text)

    if success:
        st.session_state["completed_steps"] = {"upload", "extraction"}
        st.session_state["project_summary"] = repo.get_project_summary(project_id)
        st.switch_page("pages/02_Extraction.py")
    else:
        st.error(f"Extraction failed: {error}")
        st.caption(
            "Check that LLM_PROVIDER and the matching API key are set in your .env file "
            "(see .env.example)."
        )
