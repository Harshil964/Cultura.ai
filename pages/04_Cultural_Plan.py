import streamlit as st

from components.sidebar import render_sidebar
from components.header import render_header
from components.cards import info_card
from components.approval import approval_gate
from database.repositories import project_repository as project_repo
from database.repositories import cultural_repository as cultural_repo
from services.cultural_service import run_cultural_planning

st.set_page_config(page_title="Cultural Plan — Cultura AI", page_icon="🎬", layout="wide")

project_id = st.session_state.get("project_id")
if not project_id:
    st.warning("No project loaded. Start by uploading a screenplay.")
    st.stop()

summary = project_repo.get_project_summary(project_id)
st.session_state["project_summary"] = summary

render_sidebar(current_step="cultural_plan")
render_header("Cultural Adaptation Plan")
st.caption(
    f"{summary['selected_culture'] or '—'} • {summary['selected_region'] or '—'} • "
    f"{summary['selected_setting'] or '—'} • {summary['selected_script'] or '—'}"
)

plan = cultural_repo.get_plan(project_id)

col_generate, _ = st.columns([1, 3])
with col_generate:
    button_label = "Regenerate Plan" if plan else "Generate Cultural Plan"
    if st.button(button_label, type="primary" if not plan else "secondary"):
        with st.spinner("Analyzing cultural context…"):
            success, error = run_cultural_planning(project_id)
        if success:
            st.rerun()
        else:
            st.error(f"Cultural planning failed: {error}")

if not plan:
    st.info("No plan generated yet.")
    st.stop()

st.markdown("---")

c1, c2, c3 = st.columns(3)
with c1:
    info_card(
        "VERBAL ADAPTATION",
        "<br>".join(f"<b>{k}</b>: {v}" for k, v in plan["verbal_adaptation"].items()) or "—",
    )
with c2:
    info_card(
        "NON-VERBAL ADAPTATION",
        "<br>".join(f"<b>{k}</b>: {v}" for k, v in plan["non_verbal_adaptation"].items()) or "—",
    )
with c3:
    info_card(
        "VISUAL WORLD",
        "<br>".join(f"<b>{k}</b>: {v}" for k, v in plan["visual_world"].items()) or "—",
    )

conf = plan["confidence_summary"]
st.caption(f"Confidence: {conf.get('high', 0)} high-confidence decisions, {conf.get('needs_review', 0)} flagged for review")

if plan["uncertain_decisions"]:
    st.markdown("### ⚠ Uncertain Decisions")
    st.caption(f"{len(plan['uncertain_decisions'])} cultural decisions require review.")
    for d in plan["uncertain_decisions"]:
        with st.expander(d["topic"]):
            st.write(d["question"])
            if d["options"]:
                st.write("Options: " + ", ".join(d["options"]))
            st.caption(f"Confidence: {d['confidence']}")

st.markdown("---")

approval_gate(
    title="Cultural Plan Approval",
    status=plan["approval_status"],
    stats_line=(
        f"{conf.get('high', 0) + conf.get('needs_review', 0)} decisions • "
        f"{conf.get('high', 0)} high confidence • {conf.get('needs_review', 0)} require review"
    ),
    on_approve=lambda: cultural_repo.set_approval(project_id, True),
    on_reject=lambda: cultural_repo.set_approval(project_id, False),
    edit_hint="Inline editing of plan values is a fast follow — Reject and Regenerate for now.",
)

if plan["approval_status"] == "approved":
    st.session_state["completed_steps"] = st.session_state.get("completed_steps", set()) | {"cultural_plan"}
    if st.button("Generate Adaptation →", type="primary"):
        st.switch_page("pages/05_Adaptation.py")
