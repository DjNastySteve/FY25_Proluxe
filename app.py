
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

budgets = {{
    "Cole": 3769351.32,
    "Jake": 3027353.02,
    "All": 6796704.34
}}

st.title("📈 FY25 Sales & Budget Performance Dashboard")

territory = st.sidebar.radio("Filter by Sales Manager", ["All", "Cole", "Jake"])
df_filtered = df if territory == "All" else df[df["Rep Name"] == territory]

# KPIs
total_sales = df_filtered["Current Sales"].sum()
budget = budgets[territory]
percent_to_goal = (total_sales / budget * 100) if budget > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📦 Total Customers", f"{df_filtered['Customer Name'].nunique():,}")
with col2:
    st.metric("💰 FY25 Sales", f"${total_sales:,.0f}")
with col3:
    st.metric("🎯 FY25 Budget", f"${budget:,.0f}")
with col4:
    st.metric("📊 % to Goal", f"{percent_to_goal:.1f}%")

# Chart: Sales by Rep
st.subheader("💹 Total Sales by Manager")
sales_by_rep = df.groupby("Rep Name")["Current Sales"].sum().reset_index()
sales_by_rep["Current Sales"] = sales_by_rep["Current Sales"].astype(float)
st.bar_chart(sales_by_rep.set_index("Rep Name"))

# Top 10 Customers
st.subheader("🏆 Top 10 Customers by Sales")
top_customers = df_filtered.groupby("Customer Name")["Current Sales"].sum().sort_values(ascending=False).head(10).reset_index()
top_customers["Current Sales ($)"] = top_customers["Current Sales"].apply(lambda x: f"${x:,.0f}")
st.table(top_customers[["Customer Name", "Current Sales ($)"]])

# Full Customer Table
st.subheader("📋 Customer-Level Sales Data")
table_df = df_filtered[["Customer Name", "Sales Rep", "Rep Name", "Current Sales"]].dropna()
table_df = table_df.sort_values("Current Sales", ascending=False)
table_df["Current Sales"] = table_df["Current Sales"].apply(lambda x: f"${x:,.0f}")
st.dataframe(table_df, use_container_width=True)

# Export Option
csv = df_filtered.to_csv(index=False)
st.download_button("⬇️ Export Filtered Data as CSV", csv, "Filtered_FY25_Sales.csv", "text/csv")
