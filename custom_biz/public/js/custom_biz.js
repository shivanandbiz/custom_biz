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

// ── Folder Click → update cur_list filter + navigate correctly ───────────────
// The FileView is a singleton — setup_defaults() runs only once. On subsequent
// navigations, Frappe reuses the same instance, so we must update cur_list
// directly. Also, we split folder_path by "/" so frappe.set_route encodes
// each segment separately, preventing double-encoding of spaces (e.g. %2520).
$(document).on("click", ".file-grid a.file-wrapper", function (e) {
	if ($(e.target).is(":checkbox") || $(e.target).hasClass("list-row-checkbox")) {
		return;
	}

	const $link = $(this);
	const href = $link.attr("href") || "";

	// Only intercept folder links (e.g. /app/List/File/Home/Yashil Raj)
	if (!href.includes("/app/List/File/")) return;

	e.preventDefault();
	e.stopImmediatePropagation();

	// Decode once to get clean folder path (e.g. "Home/Yashil Raj")
	const raw_path = href.replace("/app/List/File/", "");
	const folder_path = decodeURIComponent(raw_path);

	// Split into route segments so frappe.set_route handles encoding correctly.
	// frappe.set_route("List", "File", "Home", "Yashil Raj")
	//   → /app/List/File/Home/Yashil%20Raj  ✓  (no double-encoding)
	const path_segments = folder_path.split("/").filter(Boolean);
	const route_args = ["List", "File", ...path_segments];

	if (window.cur_list && window.cur_list.doctype === "File") {
		const list = window.cur_list;

		// Update tracked folder
		list.current_folder = folder_path;

		// Navigate first (updates breadcrumb + URL)
		frappe.set_route(...route_args);

		// Then apply the Folder Equals filter pill
		list.filter_area.clear().then(() => {
			list.filter_area.add([["File", "folder", "=", folder_path, true]]);
		}).catch(() => {
			list.filters = [["File", "folder", "=", folder_path, true]];
			list.refresh();
		});
	} else {
		frappe.set_route(...route_args);
	}
});
