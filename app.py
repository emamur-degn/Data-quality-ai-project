import streamlit as st
import pandas as pd
import plotly.express as px
from data_quality import analyze_dataframe
from storage import init_db, save_run, recent_runs
from llm_analysis import explain_findings

st.set_page_config(page_title="DataQualityAI", page_icon="🛡️", layout="wide")
init_db()

st.markdown("""
<style>
.main {background: #f5f7fb;}
.block-container {padding-top: 1.5rem;}
div[data-testid="stMetric"] {background: white; padding: 18px; border-radius: 14px; border: 1px solid #e5eaf2;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🛡️ DataQualityAI")
    st.caption("LLM-Augmented Data Quality & Anomaly Detection")
    page = st.radio("Navigation", ["Dashboard", "Upload & Analyze", "Run History", "About"])
    st.divider()
    st.success("Local MVP is ready")

st.title("Data Quality & Anomaly Detection")
st.caption("Upload a CSV file to validate records, detect unusual values, and generate an AI explanation.")

if page == "Dashboard":
    history = recent_runs(limit=20)
    c1, c2, c3 = st.columns(3)
    c1.metric("Saved analyses", len(history))
    c2.metric("Latest dataset", history[0]["filename"] if history else "—")
    c3.metric("Latest issue count", history[0]["issues"] if history else "—")
    st.subheader("Recent analyses")
    if history:
        st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
    else:
        st.info("No analyses yet. Open **Upload & Analyze** to start.")
    st.subheader("How it works")
    st.write("CSV upload → data validation → anomaly detection → optional LLM explanation → saved report.")

elif page == "Upload & Analyze":
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    contamination = st.slider("Expected anomaly proportion (Isolation Forest)", 0.01, 0.25, 0.05, 0.01)
    use_llm = st.checkbox("Generate AI root-cause explanation (requires OPENAI_API_KEY)", value=False)
    if uploaded:
        try:
            df = pd.read_csv(uploaded)
            st.subheader("Data preview")
            st.write(f"Rows: **{len(df):,}** · Columns: **{len(df.columns)}**")
            st.dataframe(df.head(20), use_container_width=True)
            if st.button("Run quality checks", type="primary"):
                with st.spinner("Analyzing dataset..."):
                    result = analyze_dataframe(df, contamination=contamination)
                    ai_text = ""
                    if use_llm:
                        ai_text = explain_findings(result["summary"], result["issues"], result["anomalies"])
                    run_id = save_run(uploaded.name, result["summary"], result["issues"], result["anomalies"], ai_text)
                st.session_state["last_result"] = result
                st.session_state["last_ai"] = ai_text
                st.session_state["last_run_id"] = run_id
                st.success(f"Analysis complete. Run ID: {run_id}")

        except Exception as e:
            st.error(f"Could not read this CSV: {e}")

    result = st.session_state.get("last_result")
    if result:
        st.divider()
        st.subheader("Analysis results")
        s = result["summary"]
        a, b, c, d = st.columns(4)
        a.metric("Total records", f'{s["total_rows"]:,}')
        b.metric("Quality issues", f'{s["issue_count"]:,}')
        c.metric("Anomalies", f'{s["anomaly_count"]:,}')
        d.metric("Quality score", f'{s["quality_score"]:.1f}%')
        left, right = st.columns(2)
        with left:
            st.markdown("#### Missing values by column")
            missing = result["missing_by_column"]
            missing_df = pd.DataFrame({"Column": list(missing.keys()), "Missing": list(missing.values())})
            missing_df = missing_df[missing_df["Missing"] > 0]
            if not missing_df.empty:
                st.plotly_chart(px.bar(missing_df, x="Column", y="Missing"), use_container_width=True)
            else:
                st.success("No missing values found.")
        with right:
            st.markdown("#### Data quality issue summary")
            issue_df = pd.DataFrame(result["issues"])
            if not issue_df.empty:
                st.dataframe(issue_df, use_container_width=True, hide_index=True)
            else:
                st.success("No basic quality issues found.")
        st.markdown("#### Anomaly records")
        anomalies = result["anomaly_records"]
        if not anomalies.empty:
            st.dataframe(anomalies, use_container_width=True, hide_index=True)
            st.download_button("Download anomaly records CSV", anomalies.to_csv(index=False).encode("utf-8"), "anomalies.csv", "text/csv")
        else:
            st.info("No anomalies detected, or there were not enough numeric columns.")
        ai_text = st.session_state.get("last_ai", "")
        if ai_text:
            st.markdown("#### AI root-cause analysis")
            st.write(ai_text)
        st.download_button("Download full report JSON", result["report_json"].encode("utf-8"), "data_quality_report.json", "application/json")

elif page == "Run History":
    history = recent_runs(limit=100)
    if history:
        st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
    else:
        st.info("No saved runs yet.")

else:
    st.subheader("Project modules")
    st.markdown("""
    - **Validation:** missing values, duplicate rows, blank strings, and basic column profiling.
    - **Anomaly detection:** Isolation Forest on numeric columns when enough data is available.
    - **LLM analysis:** optional explanation based on aggregate findings, not the entire raw dataset.
    - **Storage:** SQLite run history.

    This is an educational MVP. Review results before making operational decisions. Do not upload confidential or personal data to an external LLM.
    """)
