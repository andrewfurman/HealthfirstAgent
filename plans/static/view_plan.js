document.addEventListener('DOMContentLoaded', () => {
    const editButton = document.getElementById('editButton');
    const editForm = document.getElementById('editForm');
    const viewInfo = document.getElementById('viewInfo');
    const planTitle = document.getElementById('planTitle');
    const planShortName = document.getElementById('planShortName');
    const planTypeBadge = document.getElementById('planTypeBadge');
    const documentLink = document.getElementById('documentLink');
    
    // Form inputs
    const fullNameInput = document.getElementById('fullName');
    const shortNameInput = document.getElementById('shortName');
    const planTypeSelect = document.getElementById('planType');
    const documentUrlInput = document.getElementById('documentUrl');
    const planId = document.getElementById('planId').value;
    
    let isEditing = false;

    editButton.addEventListener('click', () => {
        isEditing = !isEditing;
        
        if (isEditing) {
            // Enter edit mode
            editButton.innerHTML = `
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path>
                </svg>
                Save Changes
            `;
            editButton.classList.remove('bg-green-600', 'hover:bg-green-700');
            editButton.classList.add('bg-blue-600', 'hover:bg-blue-700');
            
            // Show edit form, hide view info
            editForm.classList.remove('hidden');
            viewInfo.classList.add('hidden');
            
        } else {
            // Save changes
            const formData = {
                short_name: shortNameInput.value,
                full_name: fullNameInput.value,
                plan_type: planTypeSelect.value,
                summary_of_benefits_url: documentUrlInput.value,
                document_type: documentUrlInput.value.toLowerCase().endsWith('.pdf') ? 'pdf' : 'website'
            };

            // Send update request
            fetch(`/plans/${planId}/update`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Exit edit mode
                editButton.innerHTML = `
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                    Edit Plan
                `;
                editButton.classList.remove('bg-blue-600', 'hover:bg-blue-700');
                editButton.classList.add('bg-green-600', 'hover:bg-green-700');
                
                // Hide edit form, show view info
                editForm.classList.add('hidden');
                viewInfo.classList.remove('hidden');
                
                // Update the display with new values
                planTitle.textContent = fullNameInput.value;
                planShortName.textContent = shortNameInput.value;
                
                // Update plan type badge
                if (planTypeSelect.value) {
                    const typeColors = {
                        'Medicare': 'bg-blue-100 text-blue-800',
                        'Medicaid': 'bg-purple-100 text-purple-800',
                        'Dual Eligible': 'bg-amber-100 text-amber-800',
                        'Marketplace': 'bg-green-100 text-green-800'
                    };
                    
                    if (planTypeBadge) {
                        planTypeBadge.textContent = planTypeSelect.value;
                        planTypeBadge.className = `inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${typeColors[planTypeSelect.value] || ''}`;
                    } else {
                        // Create new badge if it didn't exist
                        const badgeContainer = viewInfo.querySelector('.bg-gray-50');
                        badgeContainer.innerHTML = `
                            <label class="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Plan Type</label>
                            <span id="planTypeBadge" class="inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${typeColors[planTypeSelect.value] || ''}">
                                ${planTypeSelect.value}
                            </span>
                        `;
                    }
                }
                
                // Update document link
                if (documentUrlInput.value) {
                    const isPdf = documentUrlInput.value.toLowerCase().endsWith('.pdf');
                    documentLink.innerHTML = `
                        <a href="${documentUrlInput.value}" target="_blank" 
                           class="inline-flex items-center text-sm font-medium text-green-600 hover:text-green-700">
                            ${isPdf ? `
                                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                                </svg>
                                View PDF
                            ` : `
                                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
                                </svg>
                                View Website
                            `}
                            <svg class="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                            </svg>
                        </a>
                    `;
                } else {
                    documentLink.innerHTML = '<p class="text-sm text-gray-500">No document available</p>';
                }
                
                // Show success message
                alert('Plan updated successfully!');
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to update plan. Please try again.');
                // Keep editing mode on if save failed
                isEditing = true;
            });
        }
    });
});