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

// Handle folder click in Grid View to navigate directly into the folder
$(document).on("click", ".file-grid .file-wrapper", function(e) {
	// Skip if clicking checkbox
	if ($(e.target).is(":checkbox") || $(e.target).hasClass("list-row-checkbox")) {
		return;
	}

	const $wrapper = $(this);
	const name = $wrapper.attr("data-name");
	
	if (name) {
		const doc_name = decodeURIComponent(name);

		// If it has folder icon or class, navigate directly into folder
		if ($wrapper.find(".icon-folder-normal-large, .icon-folder-normal, .folder-normal").length > 0) {
			e.preventDefault();
			e.stopPropagation();
			frappe.set_route("List", "File", doc_name);
			return;
		}

		// Fallback check via DB
		frappe.db.get_value("File", doc_name, ["is_folder"]).then(r => {
			if (r && r.message && r.message.is_folder) {
				e.preventDefault();
				e.stopPropagation();
				frappe.set_route("List", "File", doc_name);
			}
		});
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
