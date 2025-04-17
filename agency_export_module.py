
from io import BytesIO
import xlsxwriter

def generate_agency_report(df, agency_name):
    output = BytesIO()
    workbook = None

    # Clean up blanks
    for col in ["Category 1", "Customer Name", "Sales Rep"]:
        df[col] = df[col].replace("(Blanks)", pd.NA)

    # Prep summary data
    total_sales = df["Current Sales"].sum()
    top_customers = df.groupby("Customer Name")["Current Sales"].sum().sort_values(ascending=False).head(10)
    bottom_customers = df.groupby("Customer Name")["Current Sales"].sum().sort_values(ascending=True).head(10)
    category_sales = df.groupby("Category 1")["Current Sales"].sum().sort_values(ascending=False)

    growth = df.groupby("Customer Name")[["Current Sales", "Prior Sales"]].sum()
    growth["$ Growth"] = growth["Current Sales"] - growth["Prior Sales"]
    growth["% Growth"] = growth["$ Growth"] / growth["Prior Sales"].replace(0, pd.NA) * 100
    top_growth_dollars = growth.sort_values("$ Growth", ascending=False).head(3)
    top_growth_percent = growth[growth["% Growth"] > 0].sort_values("% Growth", ascending=False).head(3)
    top_decline_dollars = growth.sort_values("$ Growth", ascending=True).head(3)

    # Recap summary text
    diff_total = df["Current Sales"].sum() - df["Prior Sales"].sum()
    summary_lines = []
    summary_lines.append(f"Hope everyone’s doing well! Here's your {agency_name} recap:\n")
    if diff_total < 0:
        summary_lines.append(f"We ended the period down ${abs(diff_total):,.0f} vs last year. Still some wins to celebrate.\n")
    else:
        summary_lines.append(f"We ended the period up ${abs(diff_total):,.0f} over last year — great momentum!\n")
    summary_lines.append("\nTop dealers:")
    for dealer, row in top_growth_dollars.iterrows():
        summary_lines.append(f"- {dealer}: +${row['$ Growth']:,.0f}")
    summary_lines.append("\nDealers who pulled back:")
    for dealer, row in top_decline_dollars.iterrows():
        summary_lines.append(f"- {dealer}: -${abs(row['$ Growth']):,.0f}")
    summary_lines.append("""\n🔥 Product to plug: Rhyme Downlights. Sleek, simple, and a showroom favorite.
    Let’s lean into wins, check in on our quiet ones, and light it up ⚡""")
    summary_text = "\n".join(summary_lines)

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book
        money_fmt = workbook.add_format({'num_format': '$#,##0'})
        bold = workbook.add_format({'bold': True})
        wrap_fmt = workbook.add_format({'text_wrap': True, 'valign': 'top'})

        # Summary
        df.to_excel(writer, index=False, sheet_name="Summary")
        ws_summary = writer.sheets["Summary"]
        for col_num, value in enumerate(df.columns):
            ws_summary.set_column(col_num, col_num, 18, money_fmt if "Sales" in value else None)

        # Auto Summary
        ws_auto = workbook.add_worksheet("Auto Summary")
        ws_auto.set_column("A:A", 100, wrap_fmt)
        ws_auto.write("A1", summary_text)

        # Deep Dive
        deep = workbook.add_worksheet("Deep Dive")
        deep.write("A1", "Best-Selling Product Categories", bold)
        for i, (cat, val) in enumerate(category_sales.items()):
            deep.write(i + 2, 0, cat)
            deep.write(i + 2, 1, val, money_fmt)

        deep.write("D1", "Top Dealers", bold)
        for i, (name, val) in enumerate(top_customers.items()):
            deep.write(i + 2, 3, name)
            deep.write(i + 2, 4, val, money_fmt)

        deep.write("G1", "Bottom Dealers", bold)
        for i, (name, val) in enumerate(bottom_customers.items()):
            deep.write(i + 2, 6, name)
            deep.write(i + 2, 7, val, money_fmt)

        deep.write("A20", "Client-Level Detail", bold)
        for col_idx, col in enumerate(df.columns):
            deep.write(21, col_idx, col, bold)
        for row_idx, row in df.iterrows():
            for col_idx, val in enumerate(row):
                deep.write(22 + row_idx, col_idx, val, money_fmt if "Sales" in df.columns[col_idx] else None)
        deep.autofilter(21, 0, 21 + len(df), len(df.columns) - 1)

    return output.getvalue()
