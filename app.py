
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Proluxe Sales Dashboard", layout="wide")

# Declare view/territory filters early
view_option = st.sidebar.radio("📅 Select View", ["YTD", "MTD"])
territory = st.sidebar.radio("📌 Select Sales Manager", ["All", "Cole", "Jake", "Proluxe"])

@st.cache_data
def load_data(file):
    sales_df = pd.read_excel(file, sheet_name="Sales Data YTD")
    mtd_df = pd.read_excel(file, sheet_name="Monthly Goal Sales Data")

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

    return sales_df, mtd_df, rep_map

uploaded_file = st.sidebar.file_uploader("📁 Upload FY25 Sales Excel File", type=["xlsx"])
if not uploaded_file:
    st.warning("Please upload the FY25.PLX.xlsx file to proceed.")
    st.stop()

sales_df, mtd_df, rep_map = load_data(uploaded_file)

df = mtd_df.copy() if view_option == "MTD" else sales_df.copy()
df["Sales Rep"] = df["Sales Rep"].astype(str)
df = df.merge(rep_map, left_on="Sales Rep", right_on="REP", how="left")

rep_agency_mapping = {
"601": "New Era", "627": "Phoenix", "609": "Morris-Tait", "614": "Access", "616": "Synapse",
"617": "NuTech", "619": "Connected Sales", "620": "Frontline", "621": "ProAct", "622": "PSG",
"623": "LK", "625": "Sound-Tech", "626": "Audio Americas"
}

budgets = {
"Cole": 3769351.32, "Jake": 3027353.02, "Proluxe": 743998.29, "All": 7538702.63
}
agency_budget_mapping = {
"New Era": 890397.95, "Phoenix": 712318.36, "Morris-Tait": 831038.09, "Access": 237439.45,
"Synapse": 237439.45, "NuTech": 474878.91, "Connected Sales": 356159.18, "Frontline": 118719.73,
"ProAct": 385839.11, "PSG": 474878.91, "LK": 1187197.26, "Sound-Tech": 890397.95, "Audio Americas": 0
}

df["Agency"] = df["Sales Rep"].map(rep_agency_mapping)


agencies = sorted(df["Agency"].dropna().unique())
selected_agency = st.sidebar.selectbox("🏢 Filter by Agency", ["All"] + agencies)

df_filtered = df if territory == "All" else df[df["Rep Name"] == territory]
df_filtered = df_filtered if selected_agency == "All" else df_filtered[df_filtered["Agency"] == selected_agency]


if view_option == "MTD":
    banner_html = "<div style='background-color:#111; padding:0.8em 1em; border-radius:0.5em; color:#DDD;'>📅 <b>Now Viewing:</b> <span style='color:#00FFAA;'>Month-To-Date</span> Performance</div>"
else:
    banner_html = "<div style='background-color:#111; padding:0.8em 1em; border-radius:0.5em; color:#DDD;'>📅 <b>Now Viewing:</b> <span style='color:#FFD700;'>Year-To-Date</span> Performance</div>"
st.markdown(banner_html, unsafe_allow_html=True)


total_sales = df_filtered["Current Sales"].sum()
budget = agency_budget_mapping.get(selected_agency, 0) if selected_agency != "All" else budgets.get(territory, 0)
percent_to_goal = (total_sales / budget * 100) if budget > 0 else 0
total_customers = df_filtered["Customer Name"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Customers", f"{total_customers:,}")
col2.metric("💰 FY25 Sales", f"${total_sales:,.2f}")
col3.metric("🎯 FY25 Budget", f"${budget:,.2f}")
col4.metric("📊 % to Goal", f"{percent_to_goal:.1f}%")

# Top & Bottom Customers
st.subheader("🏆 Top 10 Customers by Sales")
top10 = df_filtered.groupby(["Customer Name", "Agency"])["Current Sales"].sum().sort_values(ascending=False).head(10).reset_index()
top10["Sales ($)"] = top10["Current Sales"].apply(lambda x: f"${x:,.2f}")
st.table(top10[["Customer Name", "Agency", "Sales ($)"]])

st.subheader("🚨 Bottom 10 Customers by Sales")
bottom10 = df_filtered.groupby(["Customer Name", "Agency"])["Current Sales"].sum().sort_values().head(10).reset_index()
bottom10["Sales ($)"] = bottom10["Current Sales"].apply(lambda x: f"${x:,.2f}")
st.table(bottom10[["Customer Name", "Agency", "Sales ($)"]])

# Agency Bar Chart
st.subheader("🏢 Agency Sales Comparison")
agency_grouped = df_filtered.groupby("Agency")["Current Sales"].sum().sort_values()
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(agency_grouped.index, agency_grouped.values, color="#00c3ff")
ax.bar_label(bars, fmt="%.0f", label_type="edge")
ax.set_xlabel("Current Sales ($)")
st.pyplot(fig)

# Download filtered data
st.subheader("📁 Export")
csv_export = df_filtered.to_csv(index=False)
st.download_button("⬇ Download Filtered Data as CSV", csv_export, "Filtered_FY25_Sales.csv", "text/csv")

# st.dataframe(df[["Sales Rep", "Rep Name", "Agency"]].drop_duplicates().head(10))