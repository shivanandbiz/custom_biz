frappe.ui.form.on("Interview", {
    refresh(frm) {
        if (frm.doc.job_applicant && !frm.doc.resume_attachment) {
            frappe.db.get_value(
                "Job Applicant",
                frm.doc.job_applicant,
                "resume_attachment"
            ).then(r => {
                if (r.message?.resume_attachment) {
                    frm.set_value(
                        "resume_attachment",
                        r.message.resume_attachment
                    );
                }
            });
        }
    }
});