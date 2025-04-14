
import streamlit as st
import pandas as pd

st.set_page_config(page_title="FY25 Sales Dashboard", layout="wide")

@st.cache_data
def load_data():
    sales_df = pd.read_excel("FY25.PLX.xlsx", sheet_name="Sales Data YTD")
    sales_df.columns = sales_df.columns.str.strip()
    sales_df = sales_df.dropna(how="all")

    cole_reps = ['609', '617', '621', '623', '625', '626']
    jake_reps = ['601', '614', '616', '619', '620', '622', '627']
    rep_map = pd.DataFrame({
        "REP": cole_reps + jake_reps,
        "Rep Name": ["Cole"] * len(cole_reps) + ["Jake"] * len(jake_reps)
    })

    sales_df["Sales Rep"] = sales_df["Sales Rep"].astype(str)
    rep_map["REP"] = rep_map["REP"].astype(str)
    merged_df = sales_df.merge(rep_map, left_on="Sales Rep", right_on="REP", how="left")

    merged_df["Current Sales"] = pd.to_numeric(merged_df["Current Sales"], errors="coerce").fillna(0)
    return merged_df

df = load_data()

# Set known budgets
budgets = {
    "Cole": 3769351.32,
    "Jake": 3027353.02,
    "All": 6796704.34
}

# Sidebar manager filter
territory = st.sidebar.radio("📌 Select Sales Manager", ["All", "Cole", "Jake"])
df_filtered = df if territory == "All" else df[df["Rep Name"] == territory]

# KPI Metrics
total_sales = df_filtered["Current Sales"].sum()
budget = budgets[territory]
percent_to_goal = (total_sales / budget * 100) if budget > 0 else 0
total_customers = df_filtered["Customer Name"].nunique()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📦 Customers", f"{total_customers:,}")
with col2:
    st.metric("💰 FY25 Sales", f"${total_sales:,.0f}")
with col3:
    st.metric("🎯 FY25 Budget", f"${budget:,.0f}")
with col4:
    st.metric("📊 % to Goal", f"{percent_to_goal:.1f}%")

# Section: Agency-Level Sales Chart
if "Agency" in df.columns:
    st.subheader("🏢 Sales by Agency")
    agency_sales = df_filtered.groupby("Agency")["Current Sales"].sum().sort_values(ascending=False)
    st.bar_chart(agency_sales)

# Section: Top/Bottom Customers
st.subheader("🏆 Top 10 Customers by Sales")
top10 = df_filtered.groupby("Customer Name")["Current Sales"].sum().sort_values(ascending=False).head(10).reset_index()
top10["Sales ($)"] = top10["Current Sales"].apply(lambda x: f"${x:,.0f}")
st.table(top10[["Customer Name", "Sales ($)"]])

st.subheader("🚨 Bottom 10 Customers by Sales")
bottom10 = df_filtered.groupby("Customer Name")["Current Sales"].sum().sort_values().head(10).reset_index()
bottom10["Sales ($)"] = bottom10["Current Sales"].apply(lambda x: f"${x:,.0f}")
st.table(bottom10[["Customer Name", "Sales ($)"]])

# Section: Full Sales Table
st.subheader("📋 Customer-Level Sales Data")
table_df = df_filtered[["Customer Name", "Sales Rep", "Rep Name", "Current Sales"]].dropna()
table_df = table_df.sort_values("Current Sales", ascending=False)
table_df["Current Sales"] = table_df["Current Sales"].apply(lambda x: f"${x:,.0f}")
st.dataframe(table_df, use_container_width=True)

# Export CSV Button
csv_export = df_filtered.to_csv(index=False)
st.download_button("⬇️ Download Filtered Data as CSV", csv_export, "Filtered_FY25_Sales.csv", "text/csv")
