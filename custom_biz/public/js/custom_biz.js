frappe.provide("frappe.views");

// ── Default to Grid View ─────────────────────────────────────────────────────
function ensure_grid_view() {
	if (frappe.views.FileView) {
		frappe.views.FileView.grid_view = true;
	}
}
ensure_grid_view();
$(document).on("app_ready", ensure_grid_view);

// ── Parse current folder (handles both dev and prod Frappe URL formats) ───────
function get_folder_from_route() {
	const route = frappe.get_route();
	// Production format: route segment "folder=Home/Kalpesh Vaza"
	for (const seg of route) {
		if (seg && typeof seg === "string" && seg.startsWith("folder=")) {
			return decodeURIComponent(seg.slice(7));
		}
	}
	// Dev/standard format: ["List", "File", "Home", "Kalpesh Vaza"]
	if (route[0] === "List" && route[1] === "File") {
		return route.slice(2).join("/") || "Home";
	}
	return (window.cur_list && window.cur_list.current_folder) || "Home";
}

// ── Patch FileView methods so filter always reflects current_folder ────────────
function patch_file_view() {
	if (!frappe.views.FileView || frappe.views.FileView._custom_biz_patched) return;
	frappe.views.FileView._custom_biz_patched = true;

	// show() → sync current_folder from route (handles browser back/forward)
	const _original_show = frappe.views.FileView.prototype.show;
	frappe.views.FileView.prototype.show = function () {
		const folder = get_folder_from_route();
		if (folder) this.current_folder = folder;
		return _original_show.apply(this, arguments);
	};

	// get_filters_for_args() → inject correct folder into every server query
	const _original_gffa = frappe.views.FileView.prototype.get_filters_for_args;
	frappe.views.FileView.prototype.get_filters_for_args = function () {
		const folder = this.current_folder || get_folder_from_route() || "Home";
		const filters = _original_gffa.apply(this, arguments);
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
		if (frappe.views.FileView && !frappe.views.FileView._custom_biz_patched) {
			patch_file_view();
		}
	}
});

// ── Folder click handler — CAPTURE PHASE (fires before all Frappe handlers) ───
//
// WHY CAPTURE PHASE?
//   jQuery $(document).on("click", ...) handlers run in BUBBLE phase.
//   Frappe's global anchor router was registered at boot → runs FIRST in bubble.
//   By the time our jQuery handler fires, Frappe has ALREADY navigated with the
//   old stale current_folder → wrong content shown.
//
//   Native addEventListener(capture=true) fires during CAPTURE phase,
//   BEFORE any bubble-phase jQuery handler. This guarantees WE go first:
//   1. We pre-set current_folder synchronously
//   2. We call frappe.set_route()
//   3. We stop propagation → Frappe's handler never fires
//   4. get_filters_for_args() runs with correct current_folder → correct content
//
document.addEventListener(
	"click",
	function (e) {
		// Find the closest folder anchor (handles clicks on child elements like icons/labels)
		const link = e.target.closest(".file-grid a.file-wrapper");
		if (!link) return;

		// Pass through checkbox interactions
		if (e.target.matches("input[type=checkbox]")) return;

		const href = link.getAttribute("href") || "";
		if (!href.includes("/app/List/File/")) return;

		// Stop ALL other handlers (including Frappe's router) from running
		e.preventDefault();
		e.stopPropagation();
		e.stopImmediatePropagation();

		const raw = href.replace("/app/List/File/", "");
		const folder_path = decodeURIComponent(raw);
		const segments = folder_path.split("/").filter(Boolean);

		// Pre-set current_folder SYNCHRONOUSLY before frappe.set_route fires.
		// get_filters_for_args() reads this.current_folder — must be correct BEFORE
		// the refresh() call that frappe.set_route triggers.
		if (window.cur_list && window.cur_list.doctype === "File") {
			window.cur_list.current_folder = folder_path;
		}

		frappe.set_route("List", "File", ...segments);
	},
	true // ← CAPTURE PHASE: runs before any bubble-phase handler
);
