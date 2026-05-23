import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

st.set_page_config(
    page_title="Canadian Credit Card Optimizer",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 4px solid #1D9E75;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        margin-bottom: 10px;
    }
    .metric-card.gold { border-left-color: #BA7517; }
    .metric-card.red { border-left-color: #D85A30; }
    .metric-card.blue { border-left-color: #378ADD; }
    .metric-label { font-size: 12px; color: #888780; margin-bottom: 4px; }
    .metric-value { font-size: 26px; font-weight: 600; color: #111; }
    .metric-note { font-size: 11px; color: #888780; margin-top: 3px; }
    .section-header {
        font-size: 17px;
        font-weight: 600;
        color: #085041;
        border-bottom: 2px solid #1D9E75;
        padding-bottom: 6px;
        margin: 24px 0 14px 0;
    }
    .insight-box {
        background: #E1F5EE;
        border-left: 4px solid #1D9E75;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 10px 0;
        font-size: 13px;
        color: #085041;
        line-height: 1.6;
    }
    .warning-box {
        background: #FAECE7;
        border-left: 4px solid #D85A30;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 10px 0;
        font-size: 13px;
        color: #712B13;
        line-height: 1.6;
    }
    .card-result {
        background: white;
        border: 0.5px solid #E0E0E0;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .card-rank { font-size: 11px; color: #888; margin-bottom: 3px; }
    .card-name { font-size: 15px; font-weight: 600; color: #111; margin-bottom: 4px; }
    .card-value { font-size: 22px; font-weight: 700; color: #085041; }
    .card-details { font-size: 11px; color: #888; margin-top: 4px; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    base = Path(__file__).parent
    cards    = pd.read_csv(base / "card-database.csv")
    profiles = pd.read_csv(base / "spending-profiles.csv")
    results  = pd.read_csv(base / "scoring-results.csv")
    impact   = pd.read_csv(base / "category-impact.csv")
    findings = pd.read_csv(base / "summary-findings.csv")
    with open(base / "scoring-config.json") as f:
        config = json.load(f)
    return cards, profiles, results, impact, findings, config

cards_df, profiles_df, results_df, impact_df, findings_df, config = load_data()

def calculate_rewards(card_row, spending, config):
    annual_rewards = 0.0
    breakdown = {}
    for cat in config["categories"]:
        spend = spending.get(cat["key"], 0)
        rate = float(card_row[cat["rate_key"]]) / 100
        cap_key = cat.get("cap_key")
        if cap_key and cap_key in card_row and float(card_row[cap_key]) > 0:
            cap = float(card_row[cap_key])
            capped = min(spend, cap)
            excess = spend - capped
            monthly = (capped * rate) + (excess * float(card_row["Other Rate %"]) / 100)
        else:
            monthly = spend * rate
        annual = monthly * 12
        annual_rewards += annual
        breakdown[cat["key"]] = round(annual, 2)
    fee = float(card_row["Annual Fee CAD"])
    net = round(annual_rewards - fee, 2)
    return {"net": net, "gross": round(annual_rewards, 2), "fee": fee, "breakdown": breakdown}

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💳 Credit Card Optimizer")
    st.markdown("**Find the best Canadian credit card for how you actually spend.**")
    st.divider()
    st.markdown("### Your Monthly Spending")
    st.markdown("*Drag each slider to match your typical monthly spend.*")

    groceries = st.slider("Groceries", 0, 1500, 350, 25, format="$%d")
    gas = st.slider("Gas", 0, 600, 80, 10, format="$%d")
    dining = st.slider("Dining out", 0, 800, 150, 25, format="$%d")
    transit = st.slider("Transit", 0, 400, 120, 10, format="$%d")
    travel = st.slider("Travel", 0, 1000, 100, 25, format="$%d")
    online = st.slider("Online shopping", 0, 600, 100, 25, format="$%d")
    subscriptions = st.slider("Subscriptions", 0, 300, 70, 10, format="$%d")
    other = st.slider("Everything else", 0, 500, 150, 25, format="$%d")

    st.divider()
    annual_income = st.number_input("Annual income (CAD) — for eligibility check", 0, 500000, 55000, 5000, format="%d")
    include_welcome = st.checkbox("Include welcome bonus in year 1 value", value=False)
    st.divider()
    st.markdown("**Prepared by:** Simran Saran")
    st.markdown("**Data sources:** Ratehub.ca, Creditcardgenius.ca, card issuer websites — May 2026")

user_spending = {
    "Groceries": groceries,
    "Gas": gas,
    "Dining": dining,
    "Transit": transit,
    "Travel": travel,
    "Online Shopping": online,
    "Subscriptions": subscriptions,
    "Other": other,
}
total_monthly = sum(user_spending.values())
total_annual = total_monthly * 12

# ── SCORE ALL CARDS FOR USER ──────────────────────────────────────────────────
user_results = []
for _, card in cards_df.iterrows():
    if annual_income < float(card["Income Requirement Individual CAD"]):
        eligible = False
    else:
        eligible = True
    result = calculate_rewards(card, user_spending, config)
    welcome = float(card["Welcome Bonus Value CAD"]) if include_welcome else 0
    user_results.append({
        "Card Name": card["Card Name"],
        "Issuer": card["Issuer"],
        "Network": card["Network"],
        "Annual Fee": float(card["Annual Fee CAD"]),
        "Gross Rewards": result["gross"],
        "Net Value": result["net"],
        "Net with Welcome": round(result["net"] + welcome, 2),
        "Welcome Bonus": float(card["Welcome Bonus Value CAD"]),
        "FX Fee": float(card["Foreign Transaction Fee %"]),
        "Best For": card["Best For"],
        "Eligible": eligible,
        "Breakdown": result["breakdown"],
        "Travel Insurance": card["Travel Insurance"],
    })

user_results.sort(key=lambda x: (x["Eligible"], x["Net with Welcome"] if include_welcome else x["Net Value"]), reverse=True)
eligible_results = [r for r in user_results if r["Eligible"]]
ineligible_results = [r for r in user_results if not r["Eligible"]]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("# The Hidden Cost of a Canadian Credit Card")
st.markdown("**Which card is actually right for how you spend money?** Adjust your spending in the sidebar and see your personalised ranking update in real time.")
st.divider()

# ── SCORECARDS ────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class="metric-card gold">
        <div class="metric-label">Your annual spend</div>
        <div class="metric-value">${total_annual:,.0f}</div>
        <div class="metric-note">${total_monthly:,.0f} per month across all categories</div>
    </div>""", unsafe_allow_html=True)
with col2:
    best = eligible_results[0] if eligible_results else user_results[0]
    best_val = best["Net with Welcome"] if include_welcome else best["Net Value"]
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Best card for you</div>
        <div class="metric-value" style="font-size:18px">{best["Card Name"].split()[0]} {best["Card Name"].split()[1]}</div>
        <div class="metric-note">${best_val:,.0f} net annual value</div>
    </div>""", unsafe_allow_html=True)
with col3:
    worst = eligible_results[-1] if eligible_results else user_results[-1]
    worst_val = worst["Net with Welcome"] if include_welcome else worst["Net Value"]
    gap = round(best_val - worst_val, 0)
    st.markdown(f"""<div class="metric-card red">
        <div class="metric-label">Value gap (best vs worst)</div>
        <div class="metric-value" style="color:#D85A30">${gap:,.0f}</div>
        <div class="metric-note">Annual difference between best and worst card for your spend</div>
    </div>""", unsafe_allow_html=True)
with col4:
    no_fee = [r for r in eligible_results if r["Annual Fee"] == 0]
    best_no_fee = no_fee[0] if no_fee else None
    if best_no_fee:
        nf_val = best_no_fee["Net with Welcome"] if include_welcome else best_no_fee["Net Value"]
        st.markdown(f"""<div class="metric-card blue">
            <div class="metric-label">Best no-fee card</div>
            <div class="metric-value" style="font-size:16px;color:#378ADD">{best_no_fee["Card Name"].split()[0]} {best_no_fee["Card Name"].split()[1]}</div>
            <div class="metric-note">${nf_val:,.0f} net value with no annual fee</div>
        </div>""", unsafe_allow_html=True)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "💳 Your Card Ranking",
    "📊 Profile Comparison",
    "🔍 Card Deep Dive",
    "📈 Spending Breakdown",
])

# ── TAB 1: USER RANKING ───────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">Cards ranked for your spending profile</div>', unsafe_allow_html=True)

    if include_welcome:
        st.markdown('<div class="insight-box">Welcome bonus included in year 1 value. Toggle off in the sidebar to see steady-state annual value.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        display_results = eligible_results[:10]
        fig_rank = go.Figure()
        names = [r["Card Name"].replace(" Mastercard","").replace(" Visa Infinite","").replace(" Credit Card","") for r in display_results]
        values = [r["Net with Welcome"] if include_welcome else r["Net Value"] for r in display_results]
        fees = [r["Annual Fee"] for r in display_results]
        colors = ["#085041" if i == 0 else "#1D9E75" if i < 3 else "#9FE1CB" if i < 6 else "#D3D1C7" for i in range(len(display_results))]

        fig_rank.add_trace(go.Bar(
            y=names[::-1], x=values[::-1], orientation="h",
            marker_color=colors[::-1],
            text=[f"${v:,.0f}" for v in values[::-1]],
            textposition="outside",
        ))
        fig_rank.update_layout(
            height=420, plot_bgcolor="white",
            xaxis=dict(title="Net Annual Value (CAD)", gridcolor="#F1EFE8"),
            yaxis=dict(title=""),
            margin=dict(t=10, b=20, r=80),
            showlegend=False,
        )
        st.plotly_chart(fig_rank, use_container_width=True)

    with col2:
        st.markdown("**Top 5 cards for your profile**")
        for i, r in enumerate(eligible_results[:5]):
            val = r["Net with Welcome"] if include_welcome else r["Net Value"]
            medal = ["🥇","🥈","🥉","4️⃣","5️⃣"][i]
            st.markdown(f"""<div class="card-result">
                <div class="card-rank">{medal} Rank {i+1}</div>
                <div class="card-name">{r["Card Name"]}</div>
                <div class="card-value">${val:,.0f}/year</div>
                <div class="card-details">
                    Annual fee: ${r["Annual Fee"]:.0f} &nbsp;|&nbsp; 
                    FX fee: {r["FX Fee"]}% &nbsp;|&nbsp; 
                    Travel insurance: {r["Travel Insurance"]}
                </div>
                <div class="card-details" style="margin-top:4px;color:#085041">{r["Best For"]}</div>
            </div>""", unsafe_allow_html=True)

    if ineligible_results:
        with st.expander(f"Cards you do not qualify for yet ({len(ineligible_results)} cards)"):
            for r in ineligible_results:
                st.markdown(f"**{r['Card Name']}** — requires higher income threshold")

    st.markdown('<div class="section-header">Full ranking table</div>', unsafe_allow_html=True)
    table_data = []
    for i, r in enumerate(eligible_results, 1):
        val = r["Net with Welcome"] if include_welcome else r["Net Value"]
        table_data.append({
            "Rank": i,
            "Card": r["Card Name"],
            "Issuer": r["Issuer"],
            "Annual Fee": f"${r['Annual Fee']:.0f}",
            "Gross Rewards": f"${r['Gross Rewards']:,.0f}",
            "Net Value": f"${val:,.0f}",
            "FX Fee": f"{r['FX Fee']}%",
        })
    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

# ── TAB 2: PROFILE COMPARISON ─────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">How the three Canadian spending profiles compare</div>', unsafe_allow_html=True)
    st.markdown("The best card is not the same for everyone. Here is how the top cards perform across three realistic Canadian spending profiles — and how much money is left on the table by using the wrong card.")

    for _, f in findings_df.iterrows():
        gap = float(f["Value Gap Best vs Worst CAD"])
        st.markdown(f"""<div class="{'insight-box' if gap < 600 else 'warning-box'}">
            <strong>{f['Profile Name']}</strong> — Best card: {f['Best Card Overall']} at ${float(f['Best Card Net Annual Value CAD']):,.0f} net per year. 
            Best no-fee option: {f['Best No-Fee Card']} at ${float(f['Best No-Fee Card Net Value CAD']):,.0f} per year. 
            Gap between best and worst card: ${gap:,.0f} per year.
        </div>""", unsafe_allow_html=True)

    top3_per_profile = results_df[results_df["Rank"] <= 5]
    fig_compare = px.bar(
        top3_per_profile,
        x="Card Name", y="Net Annual Value CAD",
        color="Profile Name", barmode="group",
        color_discrete_sequence=["#085041","#1D9E75","#9FE1CB"],
    )
    fig_compare.update_layout(
        height=420, plot_bgcolor="white",
        xaxis=dict(title="", tickangle=45),
        yaxis=dict(title="Net Annual Value (CAD)", gridcolor="#F1EFE8"),
        margin=dict(t=10, b=120),
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    st.markdown('<div class="section-header">The no-fee vs premium card tradeoff</div>', unsafe_allow_html=True)
    st.markdown("A card with an annual fee is only worth paying if the extra rewards cover the fee with money to spare. Here is what the premium over the best no-fee option looks like for each profile.")

    tradeoff_rows = []
    for _, f in findings_df.iterrows():
        best_val = float(f["Best Card Net Annual Value CAD"])
        nofee_val = float(f["Best No-Fee Card Net Value CAD"])
        premium = round(best_val - nofee_val, 2)
        tradeoff_rows.append({
            "Profile": f["Profile Name"],
            "Best Paid Card": f["Best Card Overall"],
            "Net Value": f"${best_val:,.0f}",
            "Best No-Fee Card": f["Best No-Fee Card"],
            "No-Fee Net Value": f"${nofee_val:,.0f}",
            "Premium for Paid Card": f"${premium:,.0f}",
            "Worth Paying?": "Yes" if premium > 0 else "No",
        })
    st.dataframe(pd.DataFrame(tradeoff_rows), use_container_width=True, hide_index=True)

# ── TAB 3: CARD DEEP DIVE ─────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">Compare two cards head to head</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        card_a_name = st.selectbox("Card A", cards_df["Card Name"].tolist(), index=1)
    with col2:
        card_b_name = st.selectbox("Card B", cards_df["Card Name"].tolist(), index=3)

    card_a = cards_df[cards_df["Card Name"]==card_a_name].iloc[0]
    card_b = cards_df[cards_df["Card Name"]==card_b_name].iloc[0]
    result_a = calculate_rewards(card_a, user_spending, config)
    result_b = calculate_rewards(card_b, user_spending, config)

    col1, col2 = st.columns(2)
    with col1:
        winner = "A" if result_a["net"] >= result_b["net"] else ""
        st.markdown(f"""<div class="card-result" style="border-color:{'#085041' if winner=='A' else '#E0E0E0'};border-width:{'2px' if winner=='A' else '0.5px'}">
            <div class="card-name">{card_a_name} {'✓ Better for you' if winner=='A' else ''}</div>
            <div class="card-value">${result_a['net']:,.0f}/year net</div>
            <div class="card-details">Gross rewards: ${result_a['gross']:,.0f} &nbsp;|&nbsp; Annual fee: ${result_a['fee']:.0f}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        winner_b = "B" if result_b["net"] > result_a["net"] else ""
        st.markdown(f"""<div class="card-result" style="border-color:{'#085041' if winner_b=='B' else '#E0E0E0'};border-width:{'2px' if winner_b=='B' else '0.5px'}">
            <div class="card-name">{card_b_name} {'✓ Better for you' if winner_b=='B' else ''}</div>
            <div class="card-value">${result_b['net']:,.0f}/year net</div>
            <div class="card-details">Gross rewards: ${result_b['gross']:,.0f} &nbsp;|&nbsp; Annual fee: ${result_b['fee']:.0f}</div>
        </div>""", unsafe_allow_html=True)

    cats = list(result_a["breakdown"].keys())
    fig_head = go.Figure()
    fig_head.add_trace(go.Bar(name=card_a_name.split()[0]+" "+card_a_name.split()[1], x=cats, y=list(result_a["breakdown"].values()), marker_color="#085041"))
    fig_head.add_trace(go.Bar(name=card_b_name.split()[0]+" "+card_b_name.split()[1], x=cats, y=list(result_b["breakdown"].values()), marker_color="#1D9E75"))
    fig_head.update_layout(
        barmode="group", height=340, plot_bgcolor="white",
        yaxis=dict(title="Annual Rewards (CAD)", gridcolor="#F1EFE8"),
        xaxis=dict(title=""), margin=dict(t=10, b=20),
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig_head, use_container_width=True)

    st.markdown('<div class="section-header">All 15 cards — rate comparison by category</div>', unsafe_allow_html=True)
    rate_cols = ["Card Name","Groceries Rate %","Gas Rate %","Dining Rate %","Transit Rate %","Travel Rate %","Online Shopping Rate %","Subscriptions Rate %","Annual Fee CAD","Foreign Transaction Fee %"]
    st.dataframe(cards_df[rate_cols], use_container_width=True, hide_index=True)

# ── TAB 4: SPENDING BREAKDOWN ─────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">Where your rewards actually come from</div>', unsafe_allow_html=True)
    st.markdown("Not all spending categories are equal when it comes to rewards. Here is how your specific spending breaks down across all categories for your top card.")

    if eligible_results:
        best_card = eligible_results[0]
        breakdown = best_card["Breakdown"]

        fig_pie = px.pie(
            values=list(breakdown.values()),
            names=list(breakdown.keys()),
            color_discrete_sequence=["#085041","#1D9E75","#3BBDA0","#9FE1CB","#D3EDE8","#BA7517","#D85A30","#888780"],
            hole=0.4,
        )
        fig_pie.update_layout(height=360, margin=dict(t=10, b=20))

        col1, col2 = st.columns([1,1])
        with col1:
            st.markdown(f"**Rewards breakdown for {best_card['Card Name']}**")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.markdown("**Annual rewards by category**")
            for cat, val in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
                pct = round(val / sum(breakdown.values()) * 100, 1) if sum(breakdown.values()) > 0 else 0
                st.markdown(f"**{cat}:** ${val:,.0f} ({pct}%)")

    st.markdown('<div class="section-header">Your spending vs average Canadian household</div>', unsafe_allow_html=True)
    avg_canadian = {
        "Groceries": 800, "Gas": 150, "Dining": 250,
        "Transit": 80, "Travel": 200, "Online Shopping": 150,
        "Subscriptions": 120, "Other": 300,
    }
    fig_compare_spend = go.Figure()
    fig_compare_spend.add_trace(go.Bar(
        name="Your spending", x=list(user_spending.keys()),
        y=list(user_spending.values()), marker_color="#085041",
    ))
    fig_compare_spend.add_trace(go.Bar(
        name="Avg Canadian household", x=list(avg_canadian.keys()),
        y=list(avg_canadian.values()), marker_color="#D3D1C7",
    ))
    fig_compare_spend.update_layout(
        barmode="group", height=320, plot_bgcolor="white",
        yaxis=dict(title="Monthly spend (CAD)", gridcolor="#F1EFE8"),
        xaxis=dict(title=""), margin=dict(t=10, b=20),
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig_compare_spend, use_container_width=True)

st.divider()
st.markdown(
    "**Data note:** Card rates, fees, and features sourced from Ratehub.ca, Creditcardgenius.ca, and card issuer websites as of May 2026. "
    "Rewards values are estimates based on stated rates applied to spending inputs. Actual rewards may vary. "
    "This tool is for educational and comparison purposes and does not constitute financial advice. "
    "Prepared by Simran Saran as part of The Case Files portfolio series."
)
