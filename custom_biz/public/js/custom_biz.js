frappe.provide("frappe.views");

// ── Default to Grid View ─────────────────────────────────────────────────────
function ensure_grid_view() {
	if (frappe.views.FileView) {
		frappe.views.FileView.grid_view = true;
	}
}
ensure_grid_view();
$(document).on("app_ready", ensure_grid_view);

// ── Core Fix: patch get_filters_for_args() on FileView ───────────────────────
//
// How Frappe builds the server query:
//   refresh() → get_call_args() → get_args() → get_filters_for_args()
//                                                 ↑ reads from filter_area.get()
//
// Problem: FileView is a SINGLETON. setup_defaults() runs ONCE. filter_area
// is initialized with folder = "Home" and NEVER updated on navigation.
//
// Fix: patch get_filters_for_args() to always replace the folder filter with
// the live URL route value. No filter_area manipulation needed — no
// "Field folder is not selectable." error.
//
function patch_file_view() {
	if (!frappe.views.FileView || frappe.views.FileView._custom_biz_patched) return;
	frappe.views.FileView._custom_biz_patched = true;

	const _original = frappe.views.FileView.prototype.get_filters_for_args;

	frappe.views.FileView.prototype.get_filters_for_args = function () {
		// Get current folder from the live URL route
		const route = frappe.get_route();
		const folder = route.slice(2).join("/") || "Home";

		// Keep current_folder in sync (for uploads, cut/paste, etc.)
		this.current_folder = folder;

		// Get whatever filters filter_area currently has
		const filters = _original.apply(this, arguments);

		// Remove stale folder filter, inject correct one from URL
		const without_folder = filters.filter(
			(f) => !(Array.isArray(f) && f[1] === "folder")
		);
		without_folder.push(["File", "folder", "=", folder]);

		return without_folder;
	};
}

$(document).on("app_ready", function () {
	ensure_grid_view();
	patch_file_view();
});

frappe.router.on("change", function () {
	const route = frappe.get_route();
	if (route && route[0] === "List" && route[1] === "File") {
		ensure_grid_view();
		// Re-attempt patch in case FileView was lazy-loaded after app_ready
		if (frappe.views.FileView && !frappe.views.FileView._custom_biz_patched) {
			patch_file_view();
		}
	}
});

// ── Folder click → let Frappe route naturally, patch handles the filter ───────
// We only block the click if ListView's own handler would incorrectly open
// the folder document in a form view instead of navigating into it.
// Using frappe.set_route keeps it a SPA navigation (no page reload).
$(document).on("click", ".file-grid a.file-wrapper", function (e) {
	if ($(e.target).is(":checkbox") || $(e.target).hasClass("list-row-checkbox")) {
		return;
	}

	const href = $(this).attr("href") || "";
	if (!href.includes("/app/List/File/")) return;

	e.preventDefault();
	e.stopImmediatePropagation();

	// Decode then split into path segments to avoid double-encoding of spaces
	const raw = href.replace("/app/List/File/", "");
	const folder_path = decodeURIComponent(raw);
	const segments = folder_path.split("/").filter(Boolean);

	// SPA navigation → triggers FileView.show() → refresh() →
	// get_filters_for_args() (our patched version) → correct server query
	frappe.set_route("List", "File", ...segments);
});
