import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Health Canada Recall Intelligence System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #FAFAFA; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 4px solid #1D9E75;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        margin-bottom: 10px;
    }
    .metric-card.red { border-left-color: #D85A30; }
    .metric-card.amber { border-left-color: #BA7517; }
    .metric-label { font-size: 12px; color: #888780; margin-bottom: 4px; }
    .metric-value { font-size: 28px; font-weight: 600; color: #111; }
    .metric-note { font-size: 11px; color: #888780; margin-top: 3px; }
    .section-header {
        font-size: 18px;
        font-weight: 600;
        color: #085041;
        border-bottom: 2px solid #1D9E75;
        padding-bottom: 6px;
        margin: 24px 0 14px 0;
    }
    .finding-box {
        background: #E1F5EE;
        border-left: 4px solid #1D9E75;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 10px 0;
        font-size: 13px;
        color: #085041;
    }
    .warning-box {
        background: #FAECE7;
        border-left: 4px solid #D85A30;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 10px 0;
        font-size: 13px;
        color: #712B13;
    }
    .stSelectbox label { font-size: 13px; color: #444441; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = Path(__file__).parent
    recalls       = pd.read_csv(base / "recall-dataset.csv")
    pareto        = pd.read_csv(base / "pareto-analysis.csv")
    category_risk = pd.read_csv(base / "category-risk-scores.csv")
    monthly       = pd.read_csv(base / "monthly-trend.csv")
    early_warning = pd.read_csv(base / "early-warning-framework.csv")
    business      = pd.read_csv(base / "business-impact.csv")
    with open(base / "chi-square-results.json") as f:
        chi2 = json.load(f)
    return recalls, pareto, category_risk, monthly, early_warning, business, chi2

recalls, pareto, category_risk, monthly, early_warning, business, chi2 = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Recall Intelligence System")
    st.markdown("**Health Canada Recall Analysis**")
    st.markdown("January 2023 to April 2026")
    st.divider()

    st.markdown("### Filter Data")
    selected_categories = st.multiselect(
        "Product Category",
        options=sorted(recalls["Product Category"].unique()),
        default=list(recalls["Product Category"].unique()),
    )
    selected_classes = st.multiselect(
        "Recall Class",
        options=["Class I", "Class II", "Class III"],
        default=["Class I", "Class II", "Class III"],
    )
    year_range = st.slider(
        "Year Range",
        min_value=2023, max_value=2026,
        value=(2023, 2026),
    )

    st.divider()
    st.markdown("**Prepared by:** Simran Saran")
    st.markdown("**Source:** Health Canada recall data modelled on publicly available notices")
    st.markdown("**Purpose:** Portfolio project — The Case Files")

# ── FILTER DATA ───────────────────────────────────────────────────────────────
filtered = recalls[
    (recalls["Product Category"].isin(selected_categories)) &
    (recalls["Recall Class"].isin(selected_classes)) &
    (recalls["Year"].between(year_range[0], year_range[1]))
]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("# The Recall Intelligence System")
st.markdown("**A pattern analysis of Health Canada recall data — January 2023 to April 2026**")
st.markdown("847 recalls. 12 product categories. 10 root causes. One question: what does the data tell us before the next recall happens?")
st.divider()

# ── SCORECARD ROW ─────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Total Recalls Analysed</div>
        <div class="metric-value">{len(filtered):,}</div>
        <div class="metric-note">Jan 2023 to Apr 2026</div>
    </div>""", unsafe_allow_html=True)
with col2:
    class1 = len(filtered[filtered["Recall Class"]=="Class I"])
    st.markdown(f"""<div class="metric-card red">
        <div class="metric-label">Class I (Serious Risk)</div>
        <div class="metric-value" style="color:#D85A30">{class1:,}</div>
        <div class="metric-note">{round(class1/len(filtered)*100,1) if len(filtered)>0 else 0}% of filtered recalls</div>
    </div>""", unsafe_allow_html=True)
with col3:
    top_rc = filtered["Root Cause"].value_counts().index[0] if len(filtered)>0 else "N/A"
    top_rc_count = filtered["Root Cause"].value_counts().iloc[0] if len(filtered)>0 else 0
    st.markdown(f"""<div class="metric-card amber">
        <div class="metric-label">Top Root Cause</div>
        <div class="metric-value" style="font-size:16px;color:#BA7517">{top_rc.split()[0]}</div>
        <div class="metric-note">{top_rc_count} recalls ({round(top_rc_count/len(filtered)*100,1) if len(filtered)>0 else 0}%)</div>
    </div>""", unsafe_allow_html=True)
with col4:
    avg_risk = round(filtered["Composite Risk Score"].mean(), 2) if len(filtered)>0 else 0
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Avg Composite Risk Score</div>
        <div class="metric-value">{avg_risk}</div>
        <div class="metric-note">Scale 0.5 to 3.0</div>
    </div>""", unsafe_allow_html=True)
with col5:
    chi2_p = chi2["p_value"]
    st.markdown(f"""<div class="metric-card red">
        <div class="metric-label">Chi-Square p-value</div>
        <div class="metric-value" style="color:#D85A30;font-size:20px">{chi2_p}</div>
        <div class="metric-note">Category and root cause are not independent</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── TAB LAYOUT ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview and Trends",
    "🔬 Root Cause Analysis",
    "⚠️ Category Risk Scores",
    "📈 Statistical Analysis",
    "🛡️ Early Warning Framework",
])

# ── TAB 1: OVERVIEW ───────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">Monthly Recall Volume — Control Chart</div>', unsafe_allow_html=True)

    monthly_filtered = monthly.copy()
    fig_control = go.Figure()

    fig_control.add_trace(go.Scatter(
        x=monthly_filtered["Month"],
        y=monthly_filtered["Total Recalls"],
        mode="lines+markers",
        name="Monthly Recalls",
        line=dict(color="#1D9E75", width=2),
        marker=dict(size=6),
    ))
    fig_control.add_trace(go.Scatter(
        x=monthly_filtered["Month"],
        y=monthly_filtered["UCL"],
        mode="lines",
        name="UCL",
        line=dict(color="#D85A30", width=1.5, dash="dash"),
    ))
    fig_control.add_trace(go.Scatter(
        x=monthly_filtered["Month"],
        y=monthly_filtered["Control Chart Mean"],
        mode="lines",
        name="Mean",
        line=dict(color="#BA7517", width=1, dash="dot"),
    ))
    fig_control.update_layout(
        height=320, plot_bgcolor="white",
        yaxis=dict(gridcolor="#F1EFE8", title="Recall Count"),
        xaxis=dict(gridcolor="#F1EFE8", title="Month"),
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=20, b=40),
    )
    st.plotly_chart(fig_control, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Recalls by Product Category</div>', unsafe_allow_html=True)
        cat_counts = filtered["Product Category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig_cat = px.bar(
            cat_counts, x="Count", y="Category", orientation="h",
            color="Count", color_continuous_scale=["#E1F5EE","#1D9E75","#085041"],
        )
        fig_cat.update_layout(
            height=380, plot_bgcolor="white", showlegend=False,
            yaxis=dict(title=""), xaxis=dict(title="Number of Recalls", gridcolor="#F1EFE8"),
            coloraxis_showscale=False, margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Recalls by Class</div>', unsafe_allow_html=True)
        class_counts = filtered["Recall Class"].value_counts().reset_index()
        class_counts.columns = ["Class", "Count"]
        colors = {"Class I": "#D85A30", "Class II": "#BA7517", "Class III": "#1D9E75"}
        fig_class = px.pie(
            class_counts, values="Count", names="Class",
            color="Class", color_discrete_map=colors, hole=0.45,
        )
        fig_class.update_layout(height=380, margin=dict(t=10, b=20))
        st.plotly_chart(fig_class, use_container_width=True)

    st.markdown('<div class="section-header">Province Distribution</div>', unsafe_allow_html=True)
    prov_counts = filtered["Province"].value_counts().reset_index()
    prov_counts.columns = ["Province", "Count"]
    fig_prov = px.bar(prov_counts, x="Province", y="Count",
        color="Count", color_continuous_scale=["#E1F5EE","#085041"])
    fig_prov.update_layout(height=280, plot_bgcolor="white",
        yaxis=dict(gridcolor="#F1EFE8"), coloraxis_showscale=False,
        margin=dict(t=10, b=20))
    st.plotly_chart(fig_prov, use_container_width=True)

# ── TAB 2: ROOT CAUSE ─────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">Pareto Analysis — Root Causes</div>', unsafe_allow_html=True)
    st.markdown('<div class="finding-box">The top 4 root causes account for over 60% of all recalls. Microbiological contamination, process deviation, and labelling errors together represent the primary prevention opportunity.</div>', unsafe_allow_html=True)

    rc_counts = filtered["Root Cause"].value_counts().reset_index()
    rc_counts.columns = ["Root Cause", "Count"]
    rc_counts["Cumulative %"] = (rc_counts["Count"].cumsum() / rc_counts["Count"].sum() * 100).round(1)

    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(
        x=rc_counts["Root Cause"], y=rc_counts["Count"],
        name="Count", marker_color="#D85A30",
    ))
    fig_pareto.add_trace(go.Scatter(
        x=rc_counts["Root Cause"], y=rc_counts["Cumulative %"],
        name="Cumulative %", yaxis="y2",
        line=dict(color="#085041", width=2), mode="lines+markers",
    ))
    fig_pareto.update_layout(
        height=400, plot_bgcolor="white",
        yaxis=dict(title="Count", gridcolor="#F1EFE8"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right",
                   range=[0,105], ticksuffix="%"),
        xaxis=dict(title=""),
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=20, b=80),
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    st.markdown('<div class="section-header">Root Cause by Product Category — Heatmap</div>', unsafe_allow_html=True)
    st.markdown("This heatmap shows where specific root causes are concentrated by product category. Darker cells indicate higher frequency — these are the highest-priority prevention targets.")

    cats = filtered["Product Category"].unique()
    rcs  = filtered["Root Cause"].unique()
    heat_data = []
    for cat in cats:
        row = []
        for rc in rcs:
            count = len(filtered[(filtered["Product Category"]==cat) & (filtered["Root Cause"]==rc)])
            row.append(count)
        heat_data.append(row)

    fig_heat = go.Figure(data=go.Heatmap(
        z=heat_data, x=list(rcs), y=list(cats),
        colorscale=[[0,"#E1F5EE"],[0.5,"#1D9E75"],[1,"#085041"]],
        text=heat_data, texttemplate="%{text}",
    ))
    fig_heat.update_layout(
        height=420, margin=dict(t=10, b=80),
        xaxis=dict(title=""), yaxis=dict(title=""),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ── TAB 3: CATEGORY RISK ──────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">Product Category Risk Scores</div>', unsafe_allow_html=True)
    st.markdown("Risk score is a composite of recall frequency, Class I rate, and average severity. Higher scores indicate categories that warrant more intensive monitoring.")

    cr = category_risk.copy()
    fig_risk = px.bar(
        cr.sort_values("Category Risk Score", ascending=True),
        x="Category Risk Score", y="Product Category", orientation="h",
        color="Risk Level",
        color_discrete_map={"High":"#D85A30","Medium":"#BA7517","Low":"#1D9E75"},
    )
    fig_risk.update_layout(
        height=400, plot_bgcolor="white",
        xaxis=dict(title="Composite Risk Score", gridcolor="#F1EFE8"),
        yaxis=dict(title=""), margin=dict(t=10, b=20),
    )
    st.plotly_chart(fig_risk, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Class I Rate by Category</div>', unsafe_allow_html=True)
        fig_c1 = px.bar(
            cr.sort_values("Class I Rate (%)", ascending=False),
            x="Product Category", y="Class I Rate (%)",
            color="Class I Rate (%)",
            color_continuous_scale=["#E1F5EE","#D85A30"],
        )
        fig_c1.update_layout(height=320, plot_bgcolor="white",
            yaxis=dict(gridcolor="#F1EFE8"), coloraxis_showscale=False,
            margin=dict(t=10, b=80))
        st.plotly_chart(fig_c1, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Business Impact by Class</div>', unsafe_allow_html=True)
        biz = business.copy()
        fig_biz = go.Figure()
        fig_biz.add_trace(go.Bar(
            name="Low Estimate", x=biz["Recall Class"],
            y=biz["Low Estimate (CAD)"], marker_color="#E1F5EE",
        ))
        fig_biz.add_trace(go.Bar(
            name="High Estimate", x=biz["Recall Class"],
            y=biz["High Estimate (CAD)"], marker_color="#D85A30",
        ))
        fig_biz.update_layout(
            height=320, barmode="group", plot_bgcolor="white",
            yaxis=dict(title="Cost per Recall (CAD)", gridcolor="#F1EFE8",
                      tickformat="$,.0f"),
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_biz, use_container_width=True)

    st.markdown('<div class="section-header">Full Risk Score Table</div>', unsafe_allow_html=True)
    st.dataframe(
        cr[["Product Category","Total Recalls","Class I Recalls","Class I Rate (%)","Category Risk Score","Risk Level"]],
        use_container_width=True, hide_index=True,
    )

# ── TAB 4: STATISTICAL ────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">Chi-Square Test of Independence</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown(f"""<div class="{'warning-box' if chi2['p_value'] < 0.05 else 'finding-box'}">
            <strong>Test result:</strong> {chi2['result']}<br>
            <strong>Chi-square statistic:</strong> {chi2['chi2_statistic']}<br>
            <strong>p-value:</strong> {chi2['p_value']}<br>
            <strong>Degrees of freedom:</strong> {chi2['degrees_of_freedom']}
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="finding-box">
            <strong>What this means:</strong> {chi2['interpretation']}
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="finding-box">
            <strong>Practical implication:</strong> {chi2['practical_implication']}
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("**Why this test matters for quality management**")
        st.markdown("""
A chi-square test of independence checks whether two categorical variables 
are related or independent. In this context it tests whether knowing the 
product category tells you something useful about the likely root cause 
of a recall.

If the result is statistically significant (p less than 0.05) it means the 
relationship is real and not due to random chance. Quality teams can use this 
to design category-specific prevention programs rather than applying generic 
controls equally across all product types.

This is the difference between reactive quality management (responding to 
recalls after they happen) and proactive quality management (designing 
targeted controls based on where failures actually concentrate).
        """)

    st.markdown('<div class="section-header">Root Cause Distribution Within Top Categories</div>', unsafe_allow_html=True)
    top5cats = category_risk.head(5)["Product Category"].tolist()
    filt_top5 = filtered[filtered["Product Category"].isin(top5cats)]
    cross = pd.crosstab(filt_top5["Product Category"], filt_top5["Root Cause"])

    fig_cross = px.imshow(
        cross,
        color_continuous_scale=["white","#E1F5EE","#1D9E75","#085041"],
        text_auto=True,
    )
    fig_cross.update_layout(height=380, margin=dict(t=10, b=80))
    st.plotly_chart(fig_cross, use_container_width=True)

    st.markdown('<div class="section-header">Recall Severity Distribution by Category</div>', unsafe_allow_html=True)
    fig_box = px.box(
        filtered, x="Product Category", y="Composite Risk Score",
        color="Recall Class",
        color_discrete_map={"Class I":"#D85A30","Class II":"#BA7517","Class III":"#1D9E75"},
    )
    fig_box.update_layout(
        height=380, plot_bgcolor="white",
        yaxis=dict(gridcolor="#F1EFE8"),
        xaxis=dict(tickangle=45),
        margin=dict(t=10, b=120),
    )
    st.plotly_chart(fig_box, use_container_width=True)

# ── TAB 5: EARLY WARNING ──────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-header">Early Warning Framework</div>', unsafe_allow_html=True)
    st.markdown("The following framework is designed for quality teams to identify elevated recall risk before a recall notice is issued. Indicators are drawn from the pattern analysis in this dataset.")

    st.markdown('<div class="finding-box">The chi-square analysis confirms that product category and root cause are not independent. This means targeted early warning indicators by category are more effective than generic controls applied uniformly.</div>', unsafe_allow_html=True)

    for _, row in early_warning.iterrows():
        risk_color = "warning-box" if row["Risk Level"]=="High" else "finding-box"
        st.markdown(f"""<div class="{risk_color}">
            <strong>{row['Category']}</strong> — Risk Level: {row['Risk Level']}<br>
            <strong>Primary risk:</strong> {row['Primary Risk']}
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Indicator 1:** {row['Early Warning Indicator 1']}")
            st.markdown(f"**Indicator 2:** {row['Early Warning Indicator 2']}")
            st.markdown(f"**Indicator 3:** {row['Early Warning Indicator 3']}")
        with col2:
            st.markdown(f"**Monitoring frequency:** {row['Recommended Monitoring Frequency']}")
            st.markdown(f"**Escalation threshold:** {row['Escalation Threshold']}")
        st.divider()

    st.markdown('<div class="section-header">Business Impact Reference</div>', unsafe_allow_html=True)
    st.markdown("Estimated cost ranges are based on publicly available CFIA recall cost benchmarks and industry reports. These represent the direct and indirect costs of a recall event, not including long-term brand impact.")
    st.dataframe(
        business[["Recall Class","Description","Estimated Cost Range (CAD)","Cost Drivers","Recalls in Dataset"]],
        use_container_width=True, hide_index=True,
    )

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "**Data note:** This analysis is based on a synthetic dataset modelled on Health Canada recall patterns. "
    "All recall descriptions, companies, and product names are fictional and created for portfolio purposes. "
    "The analytical methodology, statistical tests, and early warning framework reflect real quality management practice. "
    "Prepared by Simran Saran as part of The Case Files portfolio series."
)
