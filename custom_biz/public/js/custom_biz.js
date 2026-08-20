frappe.provide("frappe.views");

// ── Default to Grid View ─────────────────────────────────────────────────────
function ensure_grid_view() {
	if (frappe.views.FileView) {
		frappe.views.FileView.grid_view = true;
	}
}

ensure_grid_view();

$(document).on("app_ready", ensure_grid_view);

// ── Keep grid view ON whenever File Manager page is active ───────────────────
frappe.router.on("change", function () {
	const route = frappe.get_route();
	if (route && route[0] === "List" && route[1] === "File") {
		ensure_grid_view();
	}
});

// ── Folder Click → apply route so "Folder Equals" filter pill appears ────────
// The FileView reads route in setup_defaults() and sets the folder filter.
// So the correct approach is: intercept the click, stop the native anchor,
// then call frappe.set_route which triggers a full view reload with the
// correct filter pill already applied.
$(document).on("click", ".file-grid a.file-wrapper", function (e) {
	// Allow checkbox clicks to pass through
	if ($(e.target).is(":checkbox") || $(e.target).hasClass("list-row-checkbox")) {
		return;
	}

	const $link = $(this);
	const href = $link.attr("href") || "";

	// Only intercept folder links (e.g. /app/List/File/Home%2FYashil%20Raj)
	if (href.includes("/app/List/File/")) {
		e.preventDefault();
		e.stopImmediatePropagation();

		// Extract folder path from the href
		const folder_path = decodeURIComponent(href.replace("/app/List/File/", ""));

		// Navigate — this triggers FileView.setup_defaults() which sets
		// this.filters = [["File", "folder", "=", folder_path, true]]
		// producing the "Folder Equals <folder_path>" filter pill.
		frappe.set_route("List", "File", folder_path);
	}
});
