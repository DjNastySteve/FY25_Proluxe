
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Proluxe Sales Dashboard", layout="wide")

@st.cache_data
def load_data():
    sales_df = pd.read_excel("FY25.PLX.xlsx", sheet_name="Sales Data YTD")
    mtd_df = pd.read_excel("FY25.PLX.xlsx", sheet_name="Monthly Goal Sales Data")
    
    cole_reps = ['609', '617', '621', '623', '625', '626']
    jake_reps = ['601', '614', '616', '619', '620', '622', '627']

    rep_map = pd.DataFrame({
        "REP": cole_reps + jake_reps + ['Home'],
        "Rep Name": ["Cole"] * len(cole_reps) + ["Jake"] * len(jake_reps) + ["Proluxe"]
    })

    for df in [sales_df, mtd_df]:
        df.columns = df.columns.str.strip()
        df["Sales Rep"] = df["Sales Rep"].astype(str)
        df["Current Sales"] = pd.to_numeric(df["Current Sales"], errors="coerce").fillna(0)
        df = df.merge(rep_map, left_on="Sales Rep", right_on="REP", how="left")

    return sales_df, mtd_df, rep_map

# Load data
sales_df, mtd_df, rep_map = load_data()

# Mapping for agency names
rep_agency_mapping = {
    "601": "New Era", "627": "Phoenix", "609": "Morris-Tait", "614": "Access", "616": "Synapse",
    "617": "NuTech", "619": "Connected Sales", "620": "Frontline", "621": "ProAct", "622": "PSG",
    "623": "LK", "625": "Sound-Tech", "626": "Audio Americas"
}

# Budget dictionary
budgets = {
    "Cole": 3769351.32,
    "Jake": 3027353.02,
    "Proluxe": 743998.29,
    "All": 7538702.63
}
agency_budget_mapping = {
    "New Era": 890397.95, "Phoenix": 712318.36, "Morris-Tait": 831038.09, "Access": 237439.45,
    "Synapse": 237439.45, "NuTech": 474878.91, "Connected Sales": 356159.18, "Frontline": 118719.73,
    "ProAct": 385839.11, "PSG": 474878.91, "LK": 1187197.26, "Sound-Tech": 890397.95, "Audio Americas": 0
}

# UI toggles

st.markdown(
    "<h1 style='font-size: 36px; color: #00c3ff; font-weight: 700;'>📊 Proluxe Sales Dashboard</h1>",
    unsafe_allow_html=True
)

# Display active view mode with a banner

st.markdown(f"<div style='background-color:#111; padding:0.8em 1em; border-radius:0.5em; color:#DDD;'>{banner}</div>", unsafe_allow_html=True)

view_option = st.sidebar.radio("📅 Select View", ["YTD", "MTD"])
territory = st.sidebar.radio("📌 Select Sales Manager", ["All", "Cole", "Jake", "Proluxe"])

# Display active view mode with a banner
banner = (
    "📅 <b>Now Viewing:</b> "
    + ("<span style='color:#00FFAA;'>Month-To-Date</span>" if view_option == "MTD" else "<span style='color:#FFD700;'>Year-To-Date</span>")
    + " Performance"
)
st.markdown(f"<div style='background-color:#111; padding:0.8em 1em; border-radius:0.5em; color:#DDD;'>{banner}</div>", unsafe_allow_html=True)



df = mtd_df.copy() if view_option == "MTD" else sales_df.copy()
df = df.merge(rep_map, left_on="Sales Rep", right_on="REP", how="left")

df["Agency"] = df["Sales Rep"].map(rep_agency_mapping)

agencies = sorted(df["Agency"].dropna().unique())
selected_agency = st.sidebar.selectbox("🏢 Filter by Agency", ["All"] + agencies)

df_filtered = df if territory == "All" else df[df["Rep Name"] == territory]
df_filtered = df_filtered if selected_agency == "All" else df_filtered[df_filtered["Agency"] == selected_agency]

# KPI Cards
total_sales = df_filtered["Current Sales"].sum()
budget = agency_budget_mapping.get(selected_agency, 0) if selected_agency != "All" else budgets.get(territory, 0)
percent_to_goal = (total_sales / budget * 100) if budget > 0 else 0
total_customers = df_filtered["Customer Name"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Customers", f"{total_customers:,}")
col2.metric("💰 FY25 Sales", f"${total_sales:,.2f}")
col3.metric("🎯 FY25 Budget", f"${budget:,.2f}")
col4.metric("📊 % to Goal", f"{percent_to_goal:.1f}%")


# Dynamic Budget Calculation
if selected_agency != "All":
    budget = agency_budget_mapping.get(selected_agency, 0)
else:
    budget = budgets.get(territory, 0)

percent_to_goal = (total_sales / budget * 100) if budget > 0 else 0
total_customers = df_filtered["Customer Name"].nunique()

# KPI Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Customers", f"{total_customers:,}")
col2.metric("💰 FY25 Sales", f"${total_sales:,.2f}")
col3.metric("🎯 FY25 Budget", f"${budget:,.2f}")
col4.metric("📊 % to Goal", f"{percent_to_goal:.1f}%")

# Agency Sales Chart
if "Agency" in df_filtered.columns:
    st.subheader("🏢 Sales by Agency")
    agency_sales = df_filtered.groupby("Agency")["Current Sales"].sum().sort_values(ascending=False)
    st.bar_chart(agency_sales)

# Top and Bottom Customers
st.subheader("🏆 Top 10 Customers by Sales")
top10 = df_filtered.groupby(["Customer Name", "Agency"])["Current Sales"].sum().sort_values(ascending=False).head(10).reset_index()
top10["Sales ($)"] = top10["Current Sales"].apply(lambda x: f"${x:,.2f}")
st.table(top10[["Customer Name", "Agency", "Sales ($)"]])

st.subheader("🚨 Bottom 10 Customers by Sales")
bottom10 = df_filtered.groupby(["Customer Name", "Agency"])["Current Sales"].sum().sort_values().head(10).reset_index()
bottom10["Sales ($)"] = bottom10["Current Sales"].apply(lambda x: f"${x:,.2f}")
st.table(bottom10[["Customer Name", "Agency", "Sales ($)"]])

# Top and Bottom 10 Agencies by Sales Difference
st.subheader("📊 Top & Bottom 10 Agencies by Sales Difference")
df_filtered["Agency"] = df_filtered["Sales Rep"].map(rep_agency_mapping)

agency_perf = df_filtered.groupby("Agency").agg({
    "Current Sales": "sum",
    "Prior Sales": "sum",
    "Sales Difference": "sum"
}).reset_index()

top10_agencies = agency_perf.sort_values(by="Sales Difference", ascending=False).head(10)
bottom10_agencies = agency_perf.sort_values(by="Sales Difference").head(10)

st.markdown("### 🏅 Top 10 Agencies")
for col in ["Current Sales", "Prior Sales", "Sales Difference"]:
    top10_agencies[col] = top10_agencies[col].apply(lambda x: f"${x:,.2f}")
st.table(top10_agencies)

st.markdown("### ⚠️ Bottom 10 Agencies")
for col in ["Current Sales", "Prior Sales", "Sales Difference"]:
    bottom10_agencies[col] = bottom10_agencies[col].apply(lambda x: f"${x:,.2f}")
st.table(bottom10_agencies)

# Detailed Table
st.subheader("📋 Customer-Level Sales Data")
table_df = df_filtered[["Customer Name", "Sales Rep", "Agency", "Rep Name", "Current Sales"]].dropna()
table_df = table_df.sort_values("Current Sales", ascending=False)
table_df["Current Sales"] = table_df["Current Sales"].apply(lambda x: f"${x:,.2f}")
st.dataframe(table_df, use_container_width=True)

# CSV Export
csv_export = df_filtered.to_csv(index=False)
st.download_button("⬇️ Download Filtered Data as CSV", csv_export, "Filtered_FY25_Sales.csv", "text/csv")


# Agency Chart - Enhanced
st.subheader("🏢 Agency Sales Comparison")
import matplotlib.pyplot as plt

agency_grouped = df_filtered.groupby("Agency")["Current Sales"].sum().sort_values()
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(agency_grouped.index, agency_grouped.values, color="#00c3ff")
ax.bar_label(bars, fmt="%.0f", label_type="edge")
ax.set_xlabel("Current Sales ($)")
st.pyplot(fig)

# Report Card
if selected_agency != "All":
    st.markdown(f"### 📝 {selected_agency} Performance Report")
    st.success(f"{selected_agency} is currently at **{percent_to_goal:.1f}%** of their FY25 goal with **${total_sales:,.0f}** in sales.")

# Export
with st.expander("📁 Export Options"):
    st.download_button("⬇ Download Filtered Data as CSV", df_filtered.to_csv(index=False), "Filtered_FY25_Sales.csv", "text/csv")
    st.info("📌 Pro PDF & Image exports available in advanced version.")

