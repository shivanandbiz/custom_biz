frappe.ready(function() {
    
    // ----------------------------------------------------
    // 1. GSTIN to PAN Auto-Extraction
    // ----------------------------------------------------
    $('input[name="gstin"]').on('input', function() {
        const gstin = $(this).val().trim().toUpperCase();
        $(this).val(gstin); // Force uppercase
        
        // If GSTIN is at least 15 characters, extract PAN (chars 3 to 12)
        if (gstin.length === 15) {
            const pan = gstin.substring(2, 12);
            $('input[name="pan"]').val(pan).css('background-color', '#f0fdf4');
            $('select[name="gst_category"]').val('Registered Regular').css('background-color', '#f0fdf4');
            setTimeout(() => { 
                $('input[name="pan"]').css('background-color', '#fcfcfc'); 
                $('select[name="gst_category"]').css('background-color', '#ffffff');
            }, 1500);
        }
    });

    // ----------------------------------------------------
    // 2. Form UI Logic (Supplier Group & Country toggle)
    // ----------------------------------------------------
    $('#supplier-group-select').on('change', function() {
        if ($(this).val() === 'IT/Non IT Staffing Service') {
            $('#skill-set-section').slideDown();
            // Add a default row if empty
            if ($('#skill-set-table tbody tr').length === 0) {
                $('#btn-add-skill-row').click();
            }
        } else {
            $('#skill-set-section').slideUp();
            // Clear rows
            $('#skill-set-table tbody').empty();
            skillRowCounter = 0;
        }
    });

    let skillRowCounter = 0;
    $('#btn-add-skill-row').on('click', function() {
        skillRowCounter++;
        const rowHtml = `
            <tr>
                <td class="text-center align-middle">${skillRowCounter}</td>
                <td><input type="text" class="form-control form-control-sm skill-tech" placeholder="e.g. Python, Java"></td>
                <td><input type="text" class="form-control form-control-sm skill-exp" placeholder="e.g. 2-5 Years"></td>
                <td><input type="text" class="form-control form-control-sm skill-sal" placeholder="e.g. 5L-10L"></td>
                <td><input type="text" class="form-control form-control-sm skill-loc" placeholder="e.g. Bangalore"></td>
                <td>
                    <select class="form-control form-control-sm skill-mode">
                        <option value="Onsite">Onsite</option>
                        <option value="Hybrid">Hybrid</option>
                        <option value="Remote">Remote</option>
                    </select>
                </td>
                <td class="text-center align-middle">
                    <button type="button" class="btn btn-sm btn-danger btn-remove-skill-row" title="Remove" style="padding: 2px 6px;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                    </button>
                </td>
            </tr>
        `;
        $('#skill-set-table tbody').append(rowHtml);
    });

    $('#skill-set-table').on('click', '.btn-remove-skill-row', function() {
        $(this).closest('tr').remove();
        // Re-number rows
        $('#skill-set-table tbody tr').each(function(index) {
            $(this).find('td:first').text(index + 1);
        });
        skillRowCounter = $('#skill-set-table tbody tr').length;
    });

    $('#country-select').on('change', function() {
        const country = $(this).val();
        
        // Show/hide 'Other' country text field
        if (country === 'Other') {
            $('#other-country-group').slideDown();
            $('#custom-country').prop('required', true);
        } else {
            $('#other-country-group').slideUp();
            $('#custom-country').prop('required', false);
        }

        // Show/hide India Statutory details
        if (country === 'India') {
            $('#india-statutory-details').slideDown();
        } else {
            $('#india-statutory-details').slideUp();
            // Clear India specific values if changed away from India
            $('input[name="pan"]').val('');
            $('select[name="gst_category"]').val('Unregistered');
        }
    });

    // ----------------------------------------------------
    // 3. Document Upload Handling
    // ----------------------------------------------------
    $('#vendor-document-upload').on('change', function(e) {
        let file = e.target.files[0];
        if (file) {
            // Update label
            $('#vendor-document-label').text(file.name);
            $('#vendor_document_name').val(file.name);
            
            // Validate size (5MB max)
            if (file.size > 5 * 1024 * 1024) {
                frappe.msgprint({title: 'File too large', indicator: 'red', message: 'Maximum allowed file size is 5MB.'});
                $(this).val('');
                $('#vendor-document-label').text('Choose file...');
                $('#vendor_document_name').val('');
                $('#vendor_document_base64').val('');
                return;
            }

            // Read file as Base64 Data URL
            let reader = new FileReader();
            reader.onload = function(event) {
                $('#vendor_document_base64').val(event.target.result);
            };
            reader.readAsDataURL(file);
        } else {
            $('#vendor-document-label').text('Choose file...');
            $('#vendor_document_name').val('');
            $('#vendor_document_base64').val('');
        }
    });

    // ----------------------------------------------------
    // 3. Form Submission Logic
    // ----------------------------------------------------
    $('#vendor-registration-form').on('submit', function(e) {
        e.preventDefault();
        
        // Gather all form data
        let formData = {};
        $(this).serializeArray().forEach(item => {
            formData[item.name] = item.value;
        });
        
        // Handle explicit checkboxes
        formData.preferred_billing_address = $('#preferred-billing').is(':checked') ? 1 : 0;
        formData.preferred_shipping_address = $('#preferred-shipping').is(':checked') ? 1 : 0;

        // Gather Skill Set rows if IT/Non IT Staffing Service
        if (formData.supplier_group === 'IT/Non IT Staffing Service') {
            let skillSet = [];
            $('#skill-set-table tbody tr').each(function() {
                let tech = $(this).find('.skill-tech').val();
                if (tech && tech.trim() !== '') {
                    skillSet.push({
                        technology: tech.trim(),
                        experience_range: $(this).find('.skill-exp').val().trim() || '',
                        salary_range: $(this).find('.skill-sal').val().trim() || '',
                        location: $(this).find('.skill-loc').val().trim() || '',
                        mode_of_support: $(this).find('.skill-mode').val()
                    });
                }
            });
            formData.custom_skill_set = skillSet;
        }

        // Use custom country if 'Other' is selected
        if (formData.country === 'Other') {
            formData.country = formData.custom_country;
        }
        delete formData.custom_country; // remove temp field
        
        // Basic frontend validation
        if (!formData.supplier_name || !formData.first_name || !formData.email_id) {
            frappe.msgprint({
                title: 'Missing Fields',
                indicator: 'orange',
                message: "Please fill in all mandatory fields."
            });
            return;
        }

        const submitBtn = $(this).find('button[type="submit"]');
        const originalText = submitBtn.text();
        submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span> Processing...');

        // Call the Frappe API endpoint
        frappe.call({
            method: 'custom_biz.api.vendor_registration_api.register_vendor',
            args: {
                data: formData
            },
            freeze: true,
            freeze_message: "Processing Registration...",
            callback: function(r) {
                submitBtn.prop('disabled', false).html(originalText);
                
                if(r.message && r.message.status === 'success') {
                    $('#vendor-registration-form')[0].reset();
                    $('#fetch-gstin-input').val('');
                    $('#gstin-feedback').html('');
                    
                    // reset toggles
                    $('#country-select').trigger('change');

                    $('#form-message').html(
                        `<div class="alert alert-success d-flex align-items-center shadow-sm" style="border-left: 5px solid #28a745; padding: 20px;">
                            <div style="margin-right: 15px;">
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#28a745" stroke-width="2" class="text-success"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                            </div>
                            <div>
                                <h5 class="alert-heading mb-1 text-success">Registration Successful!</h5>
                                <span class="text-muted">${r.message.message}</span> <br> 
                                <strong class="text-dark">Vendor Reference ID:</strong> ${r.message.supplier_id}
                            </div>
                        </div>`
                    );
                    
                    // Scroll down to the message
                    $('html, body').animate({
                        scrollTop: $("#form-message").offset().top - 150
                    }, 500);

                } else {
                    let errorMsg = (r.message && r.message.message) ? r.message.message : "An unknown error occurred.";
                    $('#form-message').html(
                        `<div class="alert alert-danger d-flex align-items-center shadow-sm" style="border-left: 5px solid #dc3545; padding: 20px;">
                            <div style="margin-right: 15px;">
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#dc3545" stroke-width="2" class="text-danger"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                            </div>
                            <div>
                                <h5 class="alert-heading mb-1 text-danger">Registration Failed</h5>
                                <span class="text-muted">${errorMsg}</span>
                            </div>
                        </div>`
                    );
                    
                    // Scroll down to the message
                    $('html, body').animate({
                        scrollTop: $("#form-message").offset().top - 150
                    }, 500);
                }
            }
        });
    });
});
