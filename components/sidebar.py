import streamlit as st

WORKFLOW_STEPS = [
    ("upload", "Upload"),
    ("extraction", "Extraction"),
    ("characters", "Characters"),
    ("cultural_plan", "Cultural Plan"),
    ("adaptation", "Adaptation"),
    ("visual_studio", "Visual Studio"),
    ("continuity", "Continuity"),
    ("export", "Export"),
]


def render_sidebar(current_step: str) -> None:
    with st.sidebar:
        st.markdown("## CULTURA AI")
        st.caption("Cultural Screenplay & Visual Adaptation Studio")

        project = st.session_state.get("project_summary")
        st.markdown("**Project**")
        st.write(project["name"] if project else "No project loaded")

        st.markdown("---")
        st.markdown("**Workflow**")

        completed = st.session_state.get("completed_steps", set())
        step_keys = [s[0] for s in WORKFLOW_STEPS]
        current_index = step_keys.index(current_step) if current_step in step_keys else -1

        for i, (key, label) in enumerate(WORKFLOW_STEPS):
            if key in completed:
                marker = "✅"
            elif key == current_step:
                marker = "▶️"
            elif i < current_index:
                marker = "⚪"
            else:
                marker = "◻️"
            st.markdown(f"{marker} {label}")

        st.markdown("---")
        if project:
            st.caption(f"Status: `{project['extraction_status']}`")
