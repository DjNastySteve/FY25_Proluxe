
import streamlit as st
import pandas as pd

st.set_page_config(page_title="FY25 Dashboard", layout="wide")

@st.cache_data
def load_data():
    sales_df = pd.read_excel("FY25.PLX.xlsx", sheet_name="Sales Data YTD")
    sales_df.columns = sales_df.columns.str.strip()
    sales_df = sales_df.dropna(how="all")

    # REP to Rep Name mapping
    cole_reps = ['609', '617', '621', '623', '625', '626']
    jake_reps = ['601', '614', '616', '619', '620', '622', '627']
    rep_map = pd.DataFrame({
        "REP": cole_reps + jake_reps,
        "Rep Name": ["Cole"] * len(cole_reps) + ["Jake"] * len(jake_reps)
    })

    sales_df["Sales Rep"] = sales_df["Sales Rep"].astype(str)
    rep_map["REP"] = rep_map["REP"].astype(str)
    merged_df = sales_df.merge(rep_map, left_on="Sales Rep", right_on="REP", how="left")

    return merged_df

df = load_data()

st.title("📊 FY25 Sales Data Dashboard")

# Sidebar: Territory Filter
territory = st.sidebar.radio("Filter by Territory", ["All", "Cole", "Jake"])
if territory != "All":
    df = df[df["Rep Name"] == territory]

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📦 Total Customers", f"{df['Customer Name'].nunique():,}")
with col2:
    if "Current Sales" in df.columns:
        total_sales = pd.to_numeric(df["Current Sales"], errors="coerce").sum()
        st.metric("💰 Total Current Sales", f"${total_sales:,.0f}")
with col3:
    st.metric("🧍 Sales Reps Included", f"{df['Rep Name'].nunique()}")

# Bar Chart: Sales by Rep
if "Current Sales" in df.columns and "Rep Name" in df.columns:
    st.subheader("💹 Total Sales by Territory")
    sales_by_rep = df.groupby("Rep Name")["Current Sales"].sum().reset_index()
    sales_by_rep["Current Sales"] = pd.to_numeric(sales_by_rep["Current Sales"], errors="coerce")
    st.bar_chart(sales_by_rep.set_index("Rep Name"))

# Table: Customer List
st.subheader("📋 Customer Sales Records")
st.dataframe(df[["Customer Name", "Sales Rep", "Rep Name", "Current Sales"]].dropna(), use_container_width=True)
