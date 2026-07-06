frappe.ready(function() {
	function redirectDashboard() {
		if (frappe.get_route && frappe.get_route()[0] === 'dashboard' && (!frappe.get_route()[1])) {
			// Small timeout to allow the workspace router to settle before redirecting
			setTimeout(() => {
				frappe.set_route('smarthr-admin-dashbo');
			}, 50);
		}
	}

	// Execute immediately in case the user loads /app/dashboard directly
	redirectDashboard();

	// Execute on subsequent client-side navigation
	frappe.router.on('change', redirectDashboard);

});
