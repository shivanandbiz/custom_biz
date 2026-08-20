frappe.provide("frappe.views");

// ── Default to Grid View ─────────────────────────────────────────────────────
function ensure_grid_view() {
	if (frappe.views.FileView) {
		frappe.views.FileView.grid_view = true;
	}
}
ensure_grid_view();
$(document).on("app_ready", ensure_grid_view);
frappe.router.on("change", function () {
	const route = frappe.get_route();
	if (route && route[0] === "List" && route[1] === "File") {
		ensure_grid_view();
	}
});

// ── Folder Click → directly update cur_list filter and reload ────────────────
// setup_defaults() is only called once. On subsequent navigations Frappe reuses
// the existing FileView instance, so we must update cur_list directly.
$(document).on("click", ".file-grid a.file-wrapper", function (e) {
	if ($(e.target).is(":checkbox") || $(e.target).hasClass("list-row-checkbox")) {
		return;
	}

	const $link = $(this);
	const href = $link.attr("href") || "";

	// Only intercept folder links
	if (!href.includes("/app/List/File/")) return;

	e.preventDefault();
	e.stopImmediatePropagation();

	const folder_path = decodeURIComponent(href.replace("/app/List/File/", ""));

	// If cur_list is already a FileView for File doctype, update it directly
	if (window.cur_list && window.cur_list.doctype === "File") {
		const list = window.cur_list;

		// Update the folder tracking property
		list.current_folder = folder_path;

		// Update the URL without reloading the whole page
		frappe.set_route("List", "File", folder_path);

		// Directly update the filter to "Folder Equals folder_path"
		list.filter_area.clear().then(() => {
			list.filter_area.add([["File", "folder", "=", folder_path, true]]);
		}).catch(() => {
			list.filters = [["File", "folder", "=", folder_path, true]];
			list.refresh();
		});
	} else {
		// Fallback: full route navigation
		frappe.set_route("List", "File", folder_path);
	}
});
