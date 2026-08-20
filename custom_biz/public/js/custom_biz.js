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

function apply_folder_filter_pill(folder_path) {
	if (window.cur_list && window.cur_list.doctype === "File" && window.cur_list.filter_area) {
		window.cur_list.filter_area.clear().then(() => {
			window.cur_list.filter_area.add([["File", "folder", "=", folder_path, true]]);
		}).catch(() => {
			frappe.set_route("List", "File", folder_path);
		});
	} else {
		frappe.set_route("List", "File", folder_path);
	}
}

// Handle folder click in Grid View to apply the Folder Equals filter pill and open folder
$(document).on("click", ".file-grid .file-wrapper, .file-list .list-row", function(e) {
	// Skip if clicking checkbox
	if ($(e.target).is(":checkbox") || $(e.target).hasClass("list-row-checkbox")) {
		return;
	}

	const $wrapper = $(this);
	const name = $wrapper.attr("data-name");
	
	if (name) {
		const doc_name = decodeURIComponent(name);

		// If clicking a folder (has folder icon or class)
		if ($wrapper.find(".icon-folder-normal-large, .icon-folder-normal, .folder-normal").length > 0 || $wrapper.hasClass("folder")) {
			e.preventDefault();
			e.stopPropagation();
			apply_folder_filter_pill(doc_name);
			return;
		}

		// Fallback check via DB
		frappe.db.get_value("File", doc_name, ["is_folder"]).then(r => {
			if (r && r.message && r.message.is_folder) {
				e.preventDefault();
				e.stopPropagation();
				apply_folder_filter_pill(doc_name);
			}
		});
	}
});

// Sync filter pill whenever route changes or File Manager page loads
frappe.router.on("change", function() {
	const route = frappe.get_route();
	if (route && route[0] === "List" && route[1] === "File") {
		if (frappe.views.FileView && (typeof frappe.views.FileView.grid_view === "undefined" || frappe.views.FileView.grid_view === false)) {
			frappe.views.FileView.grid_view = true;
		}

		// Sync current route folder to filter pill
		const current_folder = route.slice(2).join("/") || "Home";
		setTimeout(() => {
			if (window.cur_list && window.cur_list.doctype === "File" && window.cur_list.filter_area) {
				const current_filters = window.cur_list.filter_area.get();
				const has_folder_filter = current_filters.some(f => f[1] === "folder" && f[3] === current_folder);
				if (!has_folder_filter) {
					window.cur_list.filter_area.clear().then(() => {
						window.cur_list.filter_area.add([["File", "folder", "=", current_folder, true]]);
					});
				}
			}
		}, 300);
	}
});
