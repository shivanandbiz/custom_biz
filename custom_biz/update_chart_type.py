import frappe

def run():
    frappe.db.set_value('Dashboard Chart', 'PM Tasks by Status', 'type', 'Pie')
    frappe.db.commit()
    print('Updated PM Tasks by Status to Pie')
