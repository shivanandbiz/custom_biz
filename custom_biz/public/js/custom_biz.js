frappe.provide("frappe.views");

// ── Default to Grid View ─────────────────────────────────────────────────────
function ensure_grid_view() {
	if (frappe.views.FileView) {
		frappe.views.FileView.grid_view = true;
	}
}
ensure_grid_view();
$(document).on("app_ready", ensure_grid_view);

// ── Parse current folder from Frappe route (handles both URL formats) ─────────
// Dev format:  ["List", "File", "Home", "Yashil Raj"]
// Prod format: ["file", "view", "home", "Sumathi M N", "folder=Home/Sumathi M N"]
function get_folder_from_route() {
	const route = frappe.get_route();

	// Look for "folder=VALUE" segment (production Frappe format)
	for (const seg of route) {
		if (seg && typeof seg === "string" && seg.startsWith("folder=")) {
			return decodeURIComponent(seg.slice(7));
		}
	}

	// Standard: ["List", "File", "Home", ...]
	if (route[0] === "List" && route[1] === "File") {
		return route.slice(2).join("/") || "Home";
	}

	// Fallback
	return (window.cur_list && window.cur_list.current_folder) || "Home";
}

// ── Core Fix: patch FileView methods to always use live current_folder ─────────
//
// Problem: FileView is a SINGLETON — filter_area is frozen at first load.
// get_filters_for_args() reads filter_area.get() → always returns stale folder.
//
// Fix:
//  • show()                 → sync current_folder from route on every navigation
//  • get_filters_for_args() → inject "folder = this.current_folder" into query
//
function patch_file_view() {
	if (!frappe.views.FileView || frappe.views.FileView._custom_biz_patched) return;
	frappe.views.FileView._custom_biz_patched = true;

	// --- patch show() ---
	const _original_show = frappe.views.FileView.prototype.show;
	frappe.views.FileView.prototype.show = function () {
		// Sync current_folder from live route (covers browser back/forward)
		const folder = get_folder_from_route();
		if (folder) this.current_folder = folder;
		return _original_show.apply(this, arguments);
	};

	// --- patch get_filters_for_args() ---
	const _original_gffa = frappe.views.FileView.prototype.get_filters_for_args;
	frappe.views.FileView.prototype.get_filters_for_args = function () {
		// Use current_folder (always kept in sync) as the source of truth
		const folder = this.current_folder || get_folder_from_route() || "Home";

		const filters = _original_gffa.apply(this, arguments);

		// Remove stale folder filter from filter_area, inject the correct one
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
	if (route && (route[0] === "List" || route[0] === "file")) {
		ensure_grid_view();
		// Re-apply patch if FileView was lazy-loaded after app_ready
		if (frappe.views.FileView && !frappe.views.FileView._custom_biz_patched) {
			patch_file_view();
		}
	}
});

// ── Folder click → pre-set current_folder then navigate ──────────────────────
// PRE-SETTING current_folder BEFORE frappe.set_route() eliminates the race
// condition where get_filters_for_args() fires before the route has updated.
$(document).on("click", ".file-grid a.file-wrapper", function (e) {
	if ($(e.target).is(":checkbox") || $(e.target).hasClass("list-row-checkbox")) {
		return;
	}

	const href = $(this).attr("href") || "";
	if (!href.includes("/app/List/File/")) return;

	e.preventDefault();
	e.stopImmediatePropagation();

	// Extract and clean the folder path
	const raw = href.replace("/app/List/File/", "");
	const folder_path = decodeURIComponent(raw);
	const segments = folder_path.split("/").filter(Boolean);

	// ★ Pre-set current_folder synchronously so get_filters_for_args() uses
	//   the new folder immediately when frappe.set_route triggers refresh().
	if (window.cur_list && window.cur_list.doctype === "File") {
		window.cur_list.current_folder = folder_path;
	}

	// Navigate (triggers show() → refresh() → get_filters_for_args())
	frappe.set_route("List", "File", ...segments);
});
