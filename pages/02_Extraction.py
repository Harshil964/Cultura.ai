import pandas as pd
import streamlit as st

from components.sidebar import render_sidebar
from components.header import render_header
from components.cards import metric_row, status_badge
from database.repositories import project_repository as repo

st.set_page_config(page_title="Extraction — Cultura AI", page_icon="🎬", layout="wide")

project_id = st.session_state.get("project_id")
if not project_id:
    st.warning("No project loaded. Start by uploading a screenplay.")
    st.stop()

summary = repo.get_project_summary(project_id)
st.session_state["project_summary"] = summary

render_sidebar(current_step="extraction")
render_header("Screenplay Analysis", status_label=status_badge(summary["extraction_status"]))

metric_row(
    {
        "Scenes": len(summary["scenes"]),
        "Characters": len(summary["characters"]),
        "Locations": len(summary["locations"]),
        "Costumes": len(summary["costumes"]),
        "Props": len(summary["props"]),
    }
)

tab_scenes, tab_chars, tab_locs, tab_costumes, tab_props = st.tabs(
    ["Scenes", "Characters", "Locations", "Costumes", "Props"]
)

with tab_scenes:
    st.caption("Review the extracted scene breakdown. ⚠ flags scenes worth a manual check.")
    if summary["scenes"]:
        df = pd.DataFrame(
            [
                {
                    "Scene": s["scene_id"],
                    "Heading": s["heading"],
                    "Location": s["location_name"],
                    "Time": s["time_of_day"],
                    "Characters": ", ".join(s["character_names"]),
                    "Status": "⚠" if s["review_status"] == "needs_review" else "✓",
                }
                for s in summary["scenes"]
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

        selected = st.selectbox(
            "Inspect a scene", options=[s["scene_id"] for s in summary["scenes"]]
        )
        scene = next(s for s in summary["scenes"] if s["scene_id"] == selected)
        with st.expander(f"{scene['scene_id']} — {scene['heading']}", expanded=True):
            st.write(scene["summary"])
            st.markdown("**Props:** " + (", ".join(scene["prop_names"]) or "—"))
            st.markdown("**Costume notes:** " + (", ".join(scene["costume_notes"]) or "—"))
            st.text_area("Raw text", scene["raw_text"], height=150, disabled=True, key=f"raw_{selected}")
    else:
        st.info("No scenes extracted yet.")

with tab_chars:
    if summary["characters"]:
        for c in summary["characters"]:
            with st.container(border=True):
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"**{c['canonical_name']}**")
                    st.caption(c["character_id"])
                    st.write(f"Age: {c['age'] or '—'} • Role: {c['role'] or '—'}")
                    if c["aliases"]:
                        st.write("Aliases: " + ", ".join(c["aliases"]))
                    if c["relationships"]:
                        st.write("Relationships: " + ", ".join(c["relationships"]))
                with cols[1]:
                    st.button("Edit", key=f"edit_{c['character_id']}", disabled=True)
                    st.button("Merge", key=f"merge_{c['character_id']}", disabled=True)
    else:
        st.info("No characters extracted yet.")

with tab_locs:
    if summary["locations"]:
        st.dataframe(
            pd.DataFrame(
                [{"Location": l["name"], "Scenes": ", ".join(l["scene_ids"])} for l in summary["locations"]]
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No locations extracted yet.")

with tab_costumes:
    if summary["costumes"]:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Costume": co["costume_id"],
                        "Description": co["description"],
                        "Character": co["character_id"] or "—",
                        "Scenes": ", ".join(co["scene_ids"]),
                    }
                    for co in summary["costumes"]
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No costumes extracted yet.")

with tab_props:
    if summary["props"]:
        st.dataframe(
            pd.DataFrame(
                [{"Prop": p["name"], "Scenes": ", ".join(p["scene_ids"])} for p in summary["props"]]
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No props extracted yet.")

st.markdown("---")
st.caption(
    "Next milestone: Cultural Plan (dialect, kinship, wardrobe, etc.) with a human "
    "approval gate before adaptation runs."
)
