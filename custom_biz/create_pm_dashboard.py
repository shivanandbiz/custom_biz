import frappe

def run():
    module = "Custom Biz"
    
    # 1. Create Number Cards
    cards = [
        {
            "doctype": "Number Card",
            "name": "PM Total Open Projects",
            "label": "Total Open Projects",
            "document_type": "Project",
            "function": "Count",
            "filters_json": '[["Project","status","=","Open"]]',
            "is_standard": 1,
            "module": module,
            "show_percentage_stats": 1
        },
        {
            "doctype": "Number Card",
            "name": "PM Total Open Tasks",
            "label": "Total Open Tasks",
            "document_type": "Task",
            "function": "Count",
            "filters_json": '[["Task","status","not in",["Completed","Cancelled"]]]',
            "is_standard": 1,
            "module": module,
            "show_percentage_stats": 1
        },
        {
            "doctype": "Number Card",
            "name": "PM Pending Timesheets",
            "label": "Pending Timesheets",
            "document_type": "Timesheet",
            "function": "Count",
            "filters_json": '[["Timesheet","status","=","Draft"]]',
            "is_standard": 1,
            "module": module,
            "show_percentage_stats": 1
        },
        {
            "doctype": "Number Card",
            "name": "PM Total Utilized Hours",
            "label": "Total Utilized Hours",
            "type": "Report",
            "report_name": "Employee Project Task Utilization",
            "report_field": "utilized_hours",
            "report_function": "Sum",
            "is_standard": 1,
            "module": module,
            "show_percentage_stats": 0
        }
    ]

    for card_data in cards:
        if not frappe.db.exists("Number Card", card_data["name"]):
            doc = frappe.get_doc(card_data)
            doc.insert(ignore_permissions=True)
            card_data["actual_name"] = doc.name
            print(f"Created Number Card: {doc.name}")
        else:
            card_data["actual_name"] = card_data["name"]

    # 2. Create Dashboard Charts
    charts = [
        {
            "doctype": "Dashboard Chart",
            "chart_name": "PM Projects by Status",
            "chart_type": "Group By",
            "type": "Donut",
            "document_type": "Project",
            "group_by_type": "Count",
            "group_by_based_on": "status",
            "filters_json": "[]",
            "is_standard": 1,
            "module": module
        },
        {
            "doctype": "Dashboard Chart",
            "chart_name": "PM Tasks by Status",
            "chart_type": "Group By",
            "type": "Pie",
            "document_type": "Task",
            "group_by_type": "Count",
            "group_by_based_on": "status",
            "filters_json": "[]",
            "is_standard": 1,
            "module": module
        },
        {
            "doctype": "Dashboard Chart",
            "chart_name": "PM Employee Utilization",
            "chart_type": "Report",
            "type": "Bar",
            "report_name": "Employee Project Task Utilization",
            "use_report_chart": 1,
            "filters_json": "[]",
            "is_standard": 1,
            "module": module
        }
    ]

    for chart_data in charts:
        if not frappe.db.exists("Dashboard Chart", chart_data["chart_name"]):
            doc = frappe.get_doc(chart_data)
            doc.insert(ignore_permissions=True)
            chart_data["actual_name"] = doc.name
            print(f"Created Dashboard Chart: {doc.name}")
        else:
            chart_data["actual_name"] = chart_data["chart_name"]

    # 3. Create Dashboard
    dashboard_name = "Project Management Dashboard"
    if not frappe.db.exists("Dashboard", dashboard_name):
        dash_doc = frappe.get_doc({
            "doctype": "Dashboard",
            "dashboard_name": dashboard_name,
            "is_standard": 1,
            "module": module,
            "cards": [
                {"card": cards[0]["actual_name"]},
                {"card": cards[1]["actual_name"]},
                {"card": cards[2]["actual_name"]},
                {"card": cards[3]["actual_name"]}
            ],
            "charts": [
                {"chart": charts[0]["actual_name"]},
                {"chart": charts[1]["actual_name"]},
                {"chart": charts[2]["actual_name"]}
            ]
        })
        dash_doc.insert(ignore_permissions=True)
        print(f"Created Dashboard: {dashboard_name}")

    frappe.db.commit()
    print("Dashboard creation complete.")
