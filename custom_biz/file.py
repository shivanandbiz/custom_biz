import frappe


def before_validate(doc, method):
    """
    Fix for: ValidationError: Attached To Name must be a string or an integer

    When an upload is triggered from the LMS lesson editor on a brand-new lesson
    that hasn't been saved yet, the frontend sends:
        doctype = "Course Lesson"
        docname = null / None

    Frappe's File.validate_attachment_references() then throws because
    attached_to_name is not a string or integer.

    This hook runs before File validation. If attached_to_doctype is set but
    attached_to_name is falsy (None / empty string), we clear attached_to_doctype
    as well so the validation guard is satisfied and the file is saved as a
    standalone (unattached) file. The file URL is still stored in the lesson
    content block by the frontend.
    """
    if doc.attached_to_doctype and not doc.attached_to_name:
        frappe.logger("custom_biz").debug(
            f"[custom_biz.file] Clearing attached_to_doctype='{doc.attached_to_doctype}' "
            f"because attached_to_name is empty. File will be saved as standalone."
        )
        doc.attached_to_doctype = None
        doc.attached_to_field = None
