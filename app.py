
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Proluxe Sales Dashboard", layout="wide")
st.title("📊 Proluxe Sales Dashboard")

@st.cache_data
def load_data():
    sales_df = pd.read_excel("FY25.PLX.xlsx", sheet_name="Sales Data YTD")
    mtd_df = pd.read_excel("FY25.PLX.xlsx", sheet_name="Monthly Goal Sales Data")
    return sales_df, mtd_df

sales_df, mtd_df = load_data()

# Sidebar
st.sidebar.header("Filters")
view = st.sidebar.radio("View", ["YTD", "MTD"])
rep_filter = st.sidebar.selectbox("Select REP", ["All"] + sorted(sales_df["REP"].dropna().unique().tolist()))
agency_filter = st.sidebar.selectbox("Select Agency", ["All"] + sorted(sales_df["Agency"].dropna().unique().tolist()))

# Select data based on view
df = sales_df if view == "YTD" else mtd_df

# Apply filters
if rep_filter != "All":
    df = df[df["REP"] == rep_filter]
if agency_filter != "All":
    df = df[df["Agency"] == agency_filter]

# Display results
st.subheader(f"Filtered Sales Data ({view})")
st.dataframe(df)

# Placeholder: Charts & Metrics coming soon
st.info("📌 Charts and summary metrics will appear here.")
