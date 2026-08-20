frappe.provide("frappe.views");

// ── Default to Grid View ─────────────────────────────────────────────────────
function ensure_grid_view() {
	if (frappe.views.FileView) {
		frappe.views.FileView.grid_view = true;
	}
}
ensure_grid_view();
$(document).on("app_ready", ensure_grid_view);

// ── Patch FileView.prototype.show to re-read route on EVERY navigation ────────
// FileView is a singleton — setup_defaults() only runs once at construction.
// On subsequent navigations (back/forward, folder click), only show() is called.
// This patch makes show() always sync current_folder + filters from the URL.
function patch_file_view_show() {
	if (!frappe.views.FileView || frappe.views.FileView._custom_biz_patched) return;
	frappe.views.FileView._custom_biz_patched = true;

	const _original_show = frappe.views.FileView.prototype.show;
	frappe.views.FileView.prototype.show = function () {
		const route = frappe.get_route();
		const new_folder = route.slice(2).join("/") || "Home";

		// Always update current_folder and filters from the live route
		this.current_folder = new_folder;
		this.filters = [["File", "folder", "=", new_folder, true]];

		return _original_show.apply(this, arguments);
	};
}

$(document).on("app_ready", function () {
	ensure_grid_view();
	patch_file_view_show();
});

frappe.router.on("change", function () {
	const route = frappe.get_route();
	if (route && route[0] === "List" && route[1] === "File") {
		ensure_grid_view();
		patch_file_view_show(); // ensure patch applied even if app_ready fired before FileView loaded
	}
});

// ── Folder Click → navigate using properly split route segments ───────────────
// Split "Home/Yashil Raj" into ["Home", "Yashil Raj"] so frappe.set_route
// encodes each segment independently → no %2520 double-encoding of spaces.
$(document).on("click", ".file-grid a.file-wrapper", function (e) {
	if ($(e.target).is(":checkbox") || $(e.target).hasClass("list-row-checkbox")) {
		return;
	}

	const href = $(this).attr("href") || "";
	if (!href.includes("/app/List/File/")) return;

	e.preventDefault();
	e.stopImmediatePropagation();

	const raw = href.replace("/app/List/File/", "");
	const folder_path = decodeURIComponent(raw);
	const segments = folder_path.split("/").filter(Boolean);

	// frappe.set_route triggers FileView.show() which (after our patch) will
	// re-read the route and set filters = [["File","folder","=",folder_path,true]]
	frappe.set_route("List", "File", ...segments);
});
