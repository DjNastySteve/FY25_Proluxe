
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
        "REP": cole_reps + jake_reps + ['Home'],
        "Rep Name": ["Cole"] * len(cole_reps) + ["Jake"] * len(jake_reps) + ["Proluxe"]
    })

    sales_df["Sales Rep"] = sales_df["Sales Rep"].astype(str)
    rep_map["REP"] = rep_map["REP"].astype(str)
    merged_df = sales_df.merge(rep_map, left_on="Sales Rep", right_on="REP", how="left")

    merged_df["Current Sales"] = pd.to_numeric(merged_df["Current Sales"], errors="coerce").fillna(0)
    return merged_df

df = load_data()

rep_agency_mapping = {
    "601": "New Era", "627": "Phoenix", "609": "Morris-Tait", "614": "Access", "616": "Synapse",
    "617": "NuTech", "619": "Connected Sales", "620": "Frontline", "621": "ProAct", "622": "PSG",
    "623": "LK", "625": "Sound-Tech", "626": "Audio Americas"
}
df["Agency"] = df["Sales Rep"].map(rep_agency_mapping)


budgets = {
    "Cole": 3769351.32,
    "Jake": 3027353.02,
    "Proluxe": 743998.29,
    "All": 7538702.63
}

st.title("📈 FY25 Sales & Budget Performance Dashboard")

territory = st.sidebar.radio("📌 Select Sales Manager", ["All", "Cole", "Jake", "Proluxe"])

agencies = sorted(df["Agency"].dropna().unique())
selected_agency = st.sidebar.selectbox("🏢 Filter by Agency", ["All"] + agencies)
df_filtered = df if territory == "All" else df[df["Rep Name"] == territory]
df_filtered = df_filtered if selected_agency == "All" else df_filtered[df_filtered["Agency"] == selected_agency]


# KPI Cards
total_sales = df_filtered["Current Sales"].sum()
budget = budgets.get(territory, 0)
percent_to_goal = (total_sales / budget * 100) if budget > 0 else 0
total_customers = df_filtered["Customer Name"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Customers", "{:,}".format(total_customers))
col2.metric("💰 FY25 Sales", "${:,.0f}".format(total_sales))
col3.metric("🎯 FY25 Budget", "${:,.0f}".format(budget))
col4.metric("📊 % to Goal", "{:.1f}%".format(percent_to_goal))

# Agency Sales Chart
if "Agency" in df.columns:
    st.subheader("🏢 Sales by Agency")
    agency_sales = df_filtered.groupby("Agency")["Current Sales"].sum().sort_values(ascending=False)
    st.bar_chart(agency_sales)

# Top and Bottom Customers
st.subheader("🏆 Top 10 Customers by Sales")
top10 = df_filtered.groupby(["Customer Name", "Agency"])["Current Sales"].sum().sort_values(ascending=False).head(10).reset_index()
top10["Sales ($)"] = top10["Current Sales"].apply(lambda x: "${:,.0f}".format(x))
st.table(top10[["Customer Name", "Agency", "Sales ($)"]])

st.subheader("🚨 Bottom 10 Customers by Sales")
bottom10 = df_filtered.groupby(["Customer Name", "Agency"])["Current Sales"].sum().sort_values().head(10).reset_index()
bottom10["Sales ($)"] = bottom10["Current Sales"].apply(lambda x: "${:,.0f}".format(x))
st.table(bottom10[["Customer Name", "Agency", "Sales ($)"]])



# Top and Bottom 10 Agencies by Sales Difference
st.subheader("📊 Top & Bottom 10 Agencies by Sales Difference")

# Map REP to Agency
rep_agency_mapping = {
    "601": "New Era", "627": "Phoenix", "609": "Morris-Tait", "614": "Access", "616": "Synapse",
    "617": "NuTech", "619": "Connected Sales", "620": "Frontline", "621": "ProAct", "622": "PSG",
    "623": "LK", "625": "Sound-Tech", "626": "Audio Americas"
}
df_filtered["Agency"] = df_filtered["Sales Rep"].map(rep_agency_mapping)

agency_perf = df_filtered.groupby("Agency").agg({
    "Current Sales": "sum",
    "Prior Sales": "sum",
    "Sales Difference": "sum"
}).reset_index()

top10_agencies = agency_perf.sort_values(by="Sales Difference", ascending=False).head(10)
bottom10_agencies = agency_perf.sort_values(by="Sales Difference").head(10)

st.markdown("### 🏅 Top 10 Agencies")
st.table(top10_agencies[["Agency", "Current Sales", "Prior Sales", "Sales Difference"]])

st.markdown("### ⚠️ Bottom 10 Agencies")
st.table(bottom10_agencies[["Agency", "Current Sales", "Prior Sales", "Sales Difference"]])


# Detailed Table
st.subheader("📋 Customer-Level Sales Data")
table_df = df_filtered[["Customer Name", "Sales Rep", "Agency", "Rep Name", "Current Sales"]].dropna()
table_df = table_df.sort_values("Current Sales", ascending=False)
table_df["Current Sales"] = table_df["Current Sales"].apply(lambda x: "${:,.0f}".format(x))
st.dataframe(table_df, use_container_width=True)

# CSV Export
csv_export = df_filtered.to_csv(index=False)
st.download_button("⬇️ Download Filtered Data as CSV", csv_export, "Filtered_FY25_Sales.csv", "text/csv")
