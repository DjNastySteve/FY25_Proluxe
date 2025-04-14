
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

st.title("💼 FY25 Sales Manager Dashboard")

# Sidebar filter by territory
territory = st.sidebar.radio("Filter by Sales Manager", ["All", "Cole", "Jake"])
if territory != "All":
    df = df[df["Rep Name"] == territory]

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📦 Total Customers", f"{df['Customer Name'].nunique():,}")
with col2:
    total_sales = df["Current Sales"].sum()
    st.metric("💰 Total Current Sales", f"${total_sales:,.0f}")
with col3:
    st.metric("🧑‍💼 Sales Manager(s)", f"{df['Rep Name'].nunique()}")

# Bar Chart: Sales by Manager
st.subheader("💹 Total Sales by Manager")
sales_by_rep = df.groupby("Rep Name")["Current Sales"].sum().reset_index()
sales_by_rep["Current Sales"] = sales_by_rep["Current Sales"].astype(float)
sales_by_rep = sales_by_rep.sort_values("Current Sales", ascending=False)
st.bar_chart(sales_by_rep.set_index("Rep Name"))

# Top 10 Customers
st.subheader("🏆 Top 10 Customers by Sales")
top_customers = df.groupby("Customer Name")["Current Sales"].sum().sort_values(ascending=False).head(10).reset_index()
top_customers["Current Sales ($)"] = top_customers["Current Sales"].apply(lambda x: f"${x:,.0f}")
st.table(top_customers[["Customer Name", "Current Sales ($)"]])

# Sales Table View
st.subheader("📋 Customer-Level Sales Data")
filtered_df = df[["Customer Name", "Sales Rep", "Rep Name", "Current Sales"]].dropna()
filtered_df = filtered_df.sort_values("Current Sales", ascending=False)
filtered_df["Current Sales"] = filtered_df["Current Sales"].apply(lambda x: f"${x:,.0f}")
st.dataframe(filtered_df, use_container_width=True)

# Export option
csv = df.to_csv(index=False)
st.download_button("⬇️ Export Full Dataset as CSV", csv, "FY25_Sales_Data.csv", "text/csv")
