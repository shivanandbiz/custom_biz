import frappe
from frappe.model.naming import set_name_by_naming_series

def employee_autoname(doc, method):
    # Only act if it's using one of our custom prefixes
    custom_series = ['BIZ.####', 'CRM.####', 'ERP.####', 'CMS.####', 'INF.####']
    if doc.naming_series and doc.naming_series in custom_series:
        prefix = doc.naming_series.replace('.####', '')
        
        # Check current max in Employee table for this prefix
        # E.g. prefix is BIZ, we look for BIZ%
        names = frappe.db.sql(f"SELECT name FROM `tabEmployee` WHERE name LIKE '{prefix}%'", as_dict=True)
        
        max_num = 0
        for row in names:
            try:
                num = int(row.name.replace(prefix, ''))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
        
        if max_num > 0:
            num = max_num
            
            # Ensure the Series table is up to date
            series_name = doc.naming_series.split('.')[0] + '.'
            current_series = frappe.db.sql("SELECT current FROM `tabSeries` WHERE name = %s", series_name)
            current_series = current_series[0][0] if current_series else 0
            
            if current_series < num:
                # Update series table to the highest existing number
                if current_series == 0:
                    frappe.db.sql("INSERT INTO `tabSeries` (name, current) VALUES (%s, %s)", (series_name, num))
                else:
                    frappe.db.sql("UPDATE `tabSeries` SET current = %s WHERE name = %s", (num, series_name))
                
                frappe.db.commit() # Important: Commit the sequence update to prevent race conditions during set_name
        
        # Now let standard set_name_by_naming_series run
        set_name_by_naming_series(doc)
        
        # Important: set employee field as well because standard Employee autoname does this
        doc.employee = doc.name
