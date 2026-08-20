frappe.provide("frappe.views");

// ── Default to Grid View ─────────────────────────────────────────────────────
function ensure_grid_view() {
	if (frappe.views.FileView) {
		frappe.views.FileView.grid_view = true;
	}
}
ensure_grid_view();
$(document).on("app_ready", ensure_grid_view);

// ── Core fix: patch FileView so folder filter always tracks the live URL ──────
// 
// Problem: FileView is a singleton. setup_defaults() runs only once (first load).
// filter_area.add() fails for "folder" field with "Field folder is not selectable"
// because `folder` is not in FieldSelect's public meta fields.
//
// Solution: patch get_args() (which builds the server query) and show() (which
// updates current_folder + breadcrumb). The server always gets the right folder.
// For the filter pill UI, we use window.location navigation which triggers a
// fresh FileView init, so setup_defaults() re-reads the route correctly.
//
function patch_file_view() {
	if (!frappe.views.FileView || frappe.views.FileView._custom_biz_patched) return;
	frappe.views.FileView._custom_biz_patched = true;

	// Patch get_args() → always injects the correct folder filter into the query
	const _original_get_args = frappe.views.FileView.prototype.get_args;
	frappe.views.FileView.prototype.get_args = function () {
		const route = frappe.get_route();
		const folder = route.slice(2).join("/") || "Home";

		// Keep current_folder in sync for breadcrumb + other features
		this.current_folder = folder;

		const args = _original_get_args.apply(this, arguments);

		// Replace any folder filter with the route-based one
		if (!args.filters) args.filters = [];
		args.filters = args.filters.filter(
			(f) => !(Array.isArray(f) && f[1] === "folder")
		);
		args.filters.push(["File", "folder", "=", folder]);

		return args;
	};

	// Patch show() → sync current_folder from route on every navigation
	const _original_show = frappe.views.FileView.prototype.show;
	frappe.views.FileView.prototype.show = function () {
		const route = frappe.get_route();
		this.current_folder = route.slice(2).join("/") || "Home";
		return _original_show.apply(this, arguments);
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
		patch_file_view();
	}
});

// ── Folder click → navigate using window.location for clean re-init ───────────
// window.location triggers a full Frappe desk load which runs setup_defaults()
// fresh → correct folder filter, correct filter pill, correct content.
// Also prevents ListView's default open_doc() from opening the folder as a form.
$(document).on("click", ".file-grid a.file-wrapper", function (e) {
	if ($(e.target).is(":checkbox") || $(e.target).hasClass("list-row-checkbox")) {
		return;
	}

	const href = $(this).attr("href") || "";
	if (!href.includes("/app/List/File/")) return;

	e.preventDefault();
	e.stopImmediatePropagation();

	// Decode then re-encode each segment cleanly (prevents %2520 double-encoding)
	const raw = href.replace("/app/List/File/", "");
	const folder_path = decodeURIComponent(raw);
	const segments = folder_path.split("/").filter(Boolean);
	const clean_url = "/app/List/File/" + segments.map((s) => encodeURIComponent(s)).join("/");

	// Use window.location for a guaranteed-clean navigation that runs
	// setup_defaults() fresh → filter pill and content are always correct
	window.location.href = clean_url;
});
