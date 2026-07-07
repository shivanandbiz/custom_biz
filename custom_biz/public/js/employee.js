frappe.ui.form.on('Employee', {
    company: function(frm) {
        set_naming_series(frm);
    },
    onload: function(frm) {
        if(frm.is_new()) {
            set_naming_series(frm);
        }
    }
});

function set_naming_series(frm) {
    if (frm.doc.company === 'Biztechnosys Infotech Pvt Ltd' || frm.doc.company === 'Biztechnosys Infotech Pvt Ltd (Demo)' || frm.doc.company === 'BIZTECHNOSYS INFOTECH PRIVATE LIMITED') {
        frm.set_value('naming_series', 'BIZ.####');
    } else if (frm.doc.company === 'CRM DATA ANALYTIC LLP') {
        frm.set_value('naming_series', 'CRM.####');
    } else if (frm.doc.company === 'BIZTECHNOSYS ERP PRIVATE LIMITED') {
        frm.set_value('naming_series', 'ERP.####');
    } else if (frm.doc.company === 'BIZTECHNOSYS CMS PRIVATE LIMITED') {
        frm.set_value('naming_series', 'CMS.####');
    } else if (frm.doc.company === 'BIZTECHNOSYS INFRATECH PVT LTD' || frm.doc.company === 'Biztechnosys Infratech Pvt Ltd') {
        frm.set_value('naming_series', 'INF.####');
    }
}
