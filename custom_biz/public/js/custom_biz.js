frappe.provide("frappe.views");

// Set default grid view on FileView class
if (frappe.views.FileView) {
	frappe.views.FileView.grid_view = true;
}

$(document).on("app_ready", function() {
	if (frappe.views.FileView) {
		frappe.views.FileView.grid_view = true;
	}
});

// Enforce grid_view = true whenever File Manager page loads
frappe.router.on("change", function() {
	const route = frappe.get_route();
	if (route && route[0] === "List" && route[1] === "File") {
		if (frappe.views.FileView && (typeof frappe.views.FileView.grid_view === "undefined" || frappe.views.FileView.grid_view === false)) {
			frappe.views.FileView.grid_view = true;
		}
	}
});
