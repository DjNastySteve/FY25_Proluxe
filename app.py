
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
st.title("📈 Proluxe Sales Dashboard")
view_option = st.sidebar.radio("📅 Select View", ["YTD", "MTD"])
territory = st.sidebar.radio("📌 Select Sales Manager", ["All", "Cole", "Jake", "Proluxe"])


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
