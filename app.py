import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="India 1947 vs 2026 vs 2047",
    page_icon="🇮🇳",
    layout="wide"
)

st.title("🇮🇳 India - 1947 vs 2026 vs 2047")
st.caption("India's journey from independence to today and a clearly labelled 2047 scenario")

@st.cache_data
def load_data():
    return pd.read_csv("data/india_indicators_100_recheck_audit.csv")

df = load_data()

with st.sidebar:
    st.header("🔎 Explore")

    categories = ["All"] + sorted(df["domain"].dropna().unique())
    category = st.selectbox("Category", categories)

    search = st.text_input(
        "Search",
        placeholder="GDP, population, roads..."
    )

    verified = st.selectbox(
        "Verification",
        ["All", "🟢 3x Checked", "🟡 Verified but not 3x"]
    )

    sources = st.checkbox("Show sources & methodology")

view = df.copy()

if category != "All":
    view = view[view["domain"] == category]

if search:
    view = view[
        view["indicator"].str.contains(search, case=False, na=False)
    ]

if verified == "🟢 3x Checked":
    view = view[view["verification_status"] == "3x checked"]

elif verified == "🟡 Verified but not 3x":
    view = view[view["verification_status"] != "3x checked"]

st.subheader(f"📊 {len(view)} indicators")

table = view[
    [
        "domain",
        "indicator",
        "unit",
        "1947_value",
        "2026_value",
        "2047_value",
        "2047_type",
        "verification_status"
    ]
].copy()

table.columns = [
    "Category",
    "Indicator",
    "Unit",
    "1947",
    "2026",
    "2047",
    "2047 Status",
    "Verification"
]

table["Verification"] = table["Verification"].replace({
    "3x checked": "🟢 3x Checked",
    "Not yet 3x verified": "🟡 Verified but not 3x"
})

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True
)

st.divider()
st.subheader("🔬 Compare an indicator")

if not view.empty:

    options = [
        f"{r.domain} - {r.indicator}"
        for _, r in view.iterrows()
    ]

    choice = st.selectbox("Indicator", options)

    index = options.index(choice)
    row = view.iloc[index]

    if row["verification_status"] == "3x checked":
        st.success("🟢 3x Checked")
    else:
        st.warning("🟡 This indicator has not completed 3x verification")

    c1, c2, c3 = st.columns(3)

    def val(x):
        return "N/A" if pd.isna(x) else f"{x:,.2f}"

    c1.metric("🇮🇳 1947", val(row["1947_value"]), row["unit"])
    c2.metric("🇮🇳 2026,", val(row["2026_value"]), row["unit"])
    c3.metric("🇮🇳 2047,", val(row["2047_value"]), row["unit"])

    chart = pd.DataFrame({
        "Year": ["1947", "2026", "2047"],
        "Value": [
            row["1947_value"],
            row["2026_value"],
            row["2047_value"]
    ]
}).dropna()

    if len(chart) >= 2:
        fig = px.bar(
            chart,
            x="Year",
            y="Value",
            text_auto=".2f",
            title=row["indicator"]
        )
        st.plotly_chart(fig, use_container_width=True)

    if sources:
        st.markdown("### 📚 Sources & methodology")
        st.write("**1947:**", row["source_1947"])
        st.write("**2026:**", row["source_2026"])
        st.write("**2047:**", row["methodology_2047"])

st.divider()

st.info(
    "2047 values are projections, scenarios or targets - not observed facts."
)