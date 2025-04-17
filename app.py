
def generate_agency_report(df, agency_name):
    from io import BytesIO
    output = BytesIO()

    for col in ["Category 1", "Customer Name", "Sales Rep"]:
        df[col] = df[col].replace("(Blanks)", pd.NA)

    total_sales = df["Current Sales"].sum()
    top_customers = df.groupby("Customer Name")["Current Sales"].sum().sort_values(ascending=False).head(10)
    bottom_customers = df.groupby("Customer Name")["Current Sales"].sum().sort_values(ascending=True).head(10)
    category_sales = df.groupby("Category 1")["Current Sales"].sum().sort_values(ascending=False)

    growth = df.groupby("Customer Name")[["Current Sales", "Prior Sales"]].sum()
    growth["$ Growth"] = growth["Current Sales"] - growth["Prior Sales"]
    growth["% Growth"] = growth["$ Growth"] / growth["Prior Sales"].replace(0, pd.NA) * 100
    top_growth_dollars = growth.sort_values("$ Growth", ascending=False).head(3)
    top_decline_dollars = growth.sort_values("$ Growth", ascending=True).head(3)

    summary_lines = []
    summary_lines.append(f"Hope everyone's doing well! Here's your {agency_name} recap:\n")
    diff_total = total_sales - df["Prior Sales"].sum()
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
    summary_lines.append("🔥 Product to plug: Rhyme Downlights. Sleek, simple, and a showroom favorite. Let's lean into wins, check in on our quiet ones, and light it up ⚡")
    summary_text = "\n".join(summary_lines)

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Summary")
        workbook = writer.book
        money_fmt = workbook.add_format({'num_format': '$#,##0'})
        bold = workbook.add_format({'bold': True})
        wrap_fmt = workbook.add_format({'text_wrap': True, 'valign': 'top'})

        ws_summary = writer.sheets["Summary"]
        for col_num, value in enumerate(df.columns):
            ws_summary.set_column(col_num, col_num, 18, money_fmt if "Sales" in value else None)

        ws_auto = workbook.add_worksheet("Auto Summary")
        writer.sheets["Auto Summary"] = ws_auto
        ws_auto.set_column("A:A", 100, wrap_fmt)
        ws_auto.write("A1", summary_text)

        ws_dashboard = workbook.add_worksheet("Detailed Dashboard")
        writer.sheets["Detailed Dashboard"] = ws_dashboard
        ws_dashboard.set_column("A:A", 40)
        ws_dashboard.set_column("B:C", 18, money_fmt)
        ws_dashboard.write("A1", "FY25 Sales", bold)
        ws_dashboard.write("B1", total_sales, money_fmt)
        ws_dashboard.write("A2", "FY25 Budget", bold)
        ws_dashboard.write("B2", df["Budget"].sum(), money_fmt)
        pct_to_goal = (total_sales / df["Budget"].sum()) if df["Budget"].sum() != 0 else 0
        ws_dashboard.write("A3", "% to Goal", bold)
        ws_dashboard.write("B3", pct_to_goal, workbook.add_format({'num_format': '0.0%'}))

        ws_dashboard.write("D1", "Top Growth ($)", bold)
        for i, (name, row) in enumerate(top_growth_dollars.iterrows()):
            ws_dashboard.write(i + 2, 3, name)
            ws_dashboard.write(i + 2, 4, row["$ Growth"], money_fmt)

        ws_dashboard.write("F1", "Top Decline ($)", bold)
        for i, (name, row) in enumerate(top_decline_dollars.iterrows()):
            ws_dashboard.write(i + 2, 5, name)
            ws_dashboard.write(i + 2, 6, row["$ Growth"], money_fmt)

        pie_data_start = 10
        for i, (cat, amt) in enumerate(category_sales.items()):
            ws_dashboard.write(pie_data_start + i, 0, cat)
            ws_dashboard.write(pie_data_start + i, 1, amt)

        pie_chart = workbook.add_chart({'type': 'pie'})
        pie_chart.add_series({
            'categories': ['Detailed Dashboard', pie_data_start, 0, pie_data_start + len(category_sales) - 1, 0],
            'values':     ['Detailed Dashboard', pie_data_start, 1, pie_data_start + len(category_sales) - 1, 1],
        })
        pie_chart.set_title({'name': 'Sales by Product Category'})
        pie_chart.set_style(10)
        ws_dashboard.insert_chart('D10', pie_chart, {'x_offset': 25, 'y_offset': 10})

    output.seek(0)
    return output.getvalue()
