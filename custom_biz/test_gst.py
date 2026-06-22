import frappe

def run():
    frappe.set_user("Guest")
    try:
        from india_compliance.gst_india.utils.gstin_info import _get_gstin_info
        gst_data = _get_gstin_info("29AAFCB1887N1Z0", throw_error=True)
        print("SUCCESS:", gst_data)
    except Exception as e:
        print("ERROR:", str(e))
        import traceback
        traceback.print_exc()
