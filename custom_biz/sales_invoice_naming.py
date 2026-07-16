import frappe
from frappe.model.naming import make_autoname

def sales_invoice_autoname(doc, method):
    # Determine the financial year based on posting date or current date
    date = doc.posting_date or frappe.utils.today()
    date_obj = frappe.utils.getdate(date)
    
    year = date_obj.year
    month = date_obj.month
    
    if month >= 4:
        fy = f"{year}-{year+1}"
    else:
        fy = f"{year-1}-{year}"
        
    prefix = f"INV{fy}"
    
    # Generate the autoname, make_autoname handles series creation and incrementing
    doc.name = make_autoname(f"{prefix}.###")
