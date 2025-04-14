
import streamlit as st
import pandas as pd

st.set_page_config(page_title="FY25 Dashboard", layout="wide")

# Load Excel
@st.cache_data
def load_data(sheet_name):
    return pd.read_excel("FY25.PLX.xlsx", sheet_name=sheet_name)

# Sheet selector
sheet = st.sidebar.selectbox("Select Sheet", [
    "Cole Territory", "Jake Territory", "Budget.YTD", "YTD",
    "Sales Data YTD", "MTD ", "Monthly Goal Sales Data",
    "January", "February", "March", "April"
])

df = load_data(sheet)

st.title(f"📊 {sheet} Overview")

# Dynamic filters if common columns exist
filter_cols = [col for col in df.columns if df[col].dtype == "object" and df[col].nunique() < 50]
if filter_cols:
    with st.sidebar.expander("Filters", expanded=False):
        for col in filter_cols:
            options = df[col].dropna().unique()
            selected = st.multiselect(f"{col} filter", options, default=options)
            df = df[df[col].isin(selected)]

# Show KPIs
if "FY25 Current" in df.columns and "Proluxe FY25 Budget" in df.columns:
    total_current = df["FY25 Current"].sum()
    total_budget = df["Proluxe FY25 Budget"].sum()
    percent_to_goal = (total_current / total_budget * 100) if total_budget != 0 else 0

    st.metric("Total FY25 Sales", f"${total_current:,.0f}")
    st.metric("FY25 Budget", f"${total_budget:,.0f}")
    st.metric("% to Goal", f"{percent_to_goal:.1f}%")

# Charts
if "Agency" in df.columns and "FY25 Current" in df.columns:
    st.subheader("📈 Sales by Agency")
    chart_df = df.groupby("Agency")["FY25 Current"].sum().sort_values(ascending=False).reset_index()
    st.bar_chart(chart_df.set_index("Agency"))

# Show data
st.subheader("📄 Raw Data Table")
st.dataframe(df, use_container_width=True)
