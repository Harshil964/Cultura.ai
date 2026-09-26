import streamlit as st

from components.sidebar import render_sidebar
from components.header import render_header
from database.repositories import project_repository as project_repo
from database.repositories import continuity_repository as continuity_repo
from services.continuity_service import run_continuity_check, CATEGORIES

st.set_page_config(page_title="Continuity — Cultura AI", page_icon="🎬", layout="wide")

project_id = st.session_state.get("project_id")
if not project_id:
    st.warning("No project loaded. Start by uploading a screenplay.")
    st.stop()

summary = project_repo.get_project_summary(project_id)
st.session_state["project_summary"] = summary

render_sidebar(current_step="continuity")
render_header("Continuity Control Center")

if st.button("Run Continuity Check", type="primary"):
    with st.spinner("Checking character, location, prop, and scene-order continuity…"):
        result = run_continuity_check(project_id)
    st.session_state["_continuity_result"] = result
    st.rerun()

issues = continuity_repo.get_issues(project_id)

if not issues and "_continuity_result" not in st.session_state:
    st.info("No continuity check has been run yet.")
    st.stop()

by_category = {cat: [i for i in issues if i["category"] == cat] for cat in CATEGORIES}
open_by_category = {cat: [i for i in items if i["status"] == "open"] for cat, items in by_category.items()}
total_open = sum(len(v) for v in open_by_category.values())
total_checked = len(issues)
consistency_pct = round(100 * (total_checked - total_open) / total_checked) if total_checked else 100

col_score, col_checklist = st.columns([1, 2])
with col_score:
    st.markdown(
        f"<div style='text-align:center; padding:24px; border:1px solid #e5e7eb; border-radius:12px;'>"
        f"<div style='font-size:2.5rem; font-weight:700;'>{consistency_pct}%</div>"
        f"<div style='color:#6b7280;'>CONSISTENT</div></div>",
        unsafe_allow_html=True,
    )

with col_checklist:
    for cat in CATEGORIES:
        label = cat.replace("_", " ").title()
        n_open = len(open_by_category[cat])
        marker = "✓" if n_open == 0 else "⚠"
        st.markdown(f"{marker} {label} consistency" + (f" — {n_open} open" if n_open else ""))

st.markdown("---")

for cat in CATEGORIES:
    items = open_by_category[cat]
    if not items:
        continue
    label = cat.replace("_", " ").upper()
    with st.expander(f"⚠ {label} CONTINUITY ({len(items)})", expanded=(cat == "prop")):
        for issue in items:
            st.write(issue["description"])
            st.caption("Affected: " + ", ".join(issue["affected_scene_ids"]))
            cols = st.columns(2)
            if cols[0].button("Fix Record", key=f"fix_{issue['id']}"):
                continuity_repo.resolve_issue(issue["id"])
                st.rerun()
            cols[1].button(
                f"Regenerate {issue['affected_scene_ids'][-1] if issue['affected_scene_ids'] else 'Scene'}",
                key=f"regen_{issue['id']}",
                disabled=True,
                help="Wire this to re-run agents/adaptation_agent.adapt_scene for the affected scene.",
            )
            st.markdown("---")

if total_open == 0 and total_checked:
    st.success("All continuity checks pass.")

st.session_state["completed_steps"] = st.session_state.get("completed_steps", set()) | {"continuity"}
if st.button("Continue to Export →", type="primary"):
    st.switch_page("pages/08_Export.py")
