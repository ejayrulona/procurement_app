document.addEventListener('DOMContentLoaded', () => {
    // Might be used later if it's really decided to use data tables
    // let table = $('#aid-accounts-table').DataTable({
    //     responsive: true,
    //     ordering: false,
    //     language: {
    //         info: "Showing _START_ to _END_ of _TOTAL_ results",
    //         emptyTable: "No accounts found.",
    //     }
    // });

    // Create Admin Aid Modal
    const createAdminAidBtn = document.getElementById('create-admin-aid-btn');
    const createAdminAidModal = document.getElementById('create-admin-aid-modal');
    const createAdminAidModalContent = document.getElementById('create-admin-aid-modal-content');
    const cancelCreateBtn = document.getElementById('cancel-create-btn');
    // const confirmCreateBtn = document.getElementById('confirm-create-btn');

    function openCreateModal() {
        createAdminAidModal.classList.remove('hidden');
        // setTimeout(() => {
        //     createAdminAidModalContent.classList.remove('scale-95', 'opacity-0');
        //     createAdminAidModalContent.classList.add('scale-100', 'opacity-100');
        // }, 10);
    }
    
    function closeCreateModal() {
        createAdminAidModal.classList.add('hidden');
        // createAdminAidModalContent.classList.remove('scale-100', 'opacity-100');
        // createAdminAidModalContent.classList.add('scale-95', 'opacity-0');
        // setTimeout(() => {
        // }, 200);
    }
    
    createAdminAidBtn.addEventListener('click', openCreateModal);
    cancelCreateBtn.addEventListener('click', closeCreateModal);
    
    // confirmCreateBtn.addEventListener('click', () => {
    //     window.location.href = "{% url 'users:create_admin_aid' %}";
    // });
    
    createAdminAidModal.addEventListener('click', event => {
        if (event.target === createAdminAidModal) {
            closeCreateModal();
        }
    });
    
    // Status Toggle Variables
    // let pendingUserId = null;
    // let pendingUserName = null;
    // let pendingNewStatus = null;
    // let pendingCheckbox = null;
    
    const statusToggleForm = document.getElementById('status-toggle-form');
    const statusToggles = document.querySelectorAll('.status-toggle');
    const statusModal = document.getElementById('status-modal');
    const statusModalIcon = document.getElementById('status-modal-icon');
    const statusModalSvg = document.getElementById('status-modal-svg');
    const statusModalTitle = document.getElementById('status-modal-title');
    const actionText = document.getElementById('action-text');
    const userNameText = document.getElementById('user-name-text');
    const cancelStatusBtn = document.getElementById('cancel-status-btn');
    const confirmStatusBtn = document.getElementById('confirm-status-button');
    
    statusToggles.forEach(toggle => {
        toggle.addEventListener('change', () => {
            
            const userId = toggle.dataset.userId;
            const userName = toggle.dataset.name;
            const isActive = toggle.checked;
            const newStatus = isActive ? 'activate' : 'deactivate';
            
            toggle.checked = !isActive;
            
            if (newStatus === 'activate') {
                statusModalIcon.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 text-green-800 mb-4";
                statusModalSvg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>';
                statusModalTitle.textContent = 'Activate Account';
                statusModalTitle.getElementsByClassNameName = 'text-2xl font-bold text-green-800 mb-3';
                actionText.textContent = 'Activate';
                userNameText.textContent = userName;
                confirmStatusBtn.className = "flex-1 px-4 py-2 bg-gradient-to-r from-green-700 to-green-800 hover:from-green-800 hover:to-green-900 text-white font-semibold rounded-xl shadow-md transition";
            } else {
                statusModalIcon.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 text-red-800 mb-4";
                statusModalSvg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>';
                statusModalTitle.textContent = 'Deactivate Account';
                statusModalTitle.className = 'text-2xl font-bold text-red-800 mb-3';
                actionText.textContent = 'Deactivate';
                userNameText.textContent = userName;
                confirmStatusBtn.className = "flex-1 px-4 py-2 bg-gradient-to-r from-red-700 to-red-800 hover:from-red-800 hover:to-red-900 text-white font-semibold rounded-xl shadow-md transition";
            }

            statusToggleForm.action = `/users/admin-aid/${userId}/toggle-status/`;
            
            openStatusModal();
        });
    });

    function openStatusModal() {
        statusModal.classList.remove('hidden');
    }

    function closeStatusModal() {
        statusModal.classList.add('hidden');
    }
    
    cancelStatusBtn.addEventListener('click', closeStatusModal);

    statusModal.addEventListener('click', event => {
        if (event.target === statusModal) {
            closeStatusModal();
        }
    });
    
    
    // confirmStatusBtn.addEventListener('click', () => {
    //     if (pendingCheckbox) {
    //         pendingCheckbox.checked = (pendingNewStatus === 'activate');
            
    //         const row = pendingCheckbox.closest('tr');
    //         const statusBadge = row.querySelector('td:nth-child(4) span');
            
    //         if (pendingNewStatus === 'activate') {
    //             statusBadge.className = "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800";
    //             statusBadge.textContent = "Active";
    //             row.setAttribute('data-status', 'active');
    //         } else {
    //             statusBadge.className = "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800";
    //             statusBadge.textContent = "Inactive";
    //             row.setAttribute('data-status', 'inactive');
    //         }
            
    //         showCustomToast(`${pendingUserName} has been ${pendingNewStatus === 'activate' ? 'activated' : 'deactivated'} successfully!`);
    //         updateStats();
    //     }
        
    //     statusModal.classList.add('hidden');
    //     pendingUserId = null;
    //     pendingUserName = null;
    //     pendingNewStatus = null;
    //     pendingCheckbox = null;
    // });
    
    // function updateStats() {
    //     const rows = document.querySelectorAll('#accountsTableBody tr');
    //     let activeCount = 0;
    //     let inactiveCount = 0;
    //     let pendingCount = 0;
        
    //     rows.forEach(row => {
    //         const statusSpan = row.querySelector('td:nth-child(4) span');
    //         if (statusSpan) {
    //             const status = statusSpan.textContent.toLowerCase();
    //             if (status === 'active') activeCount++;
    //             else if (status === 'inactive') inactiveCount++;
    //             else if (status === 'pending') pendingCount++;
    //         }
    //     });
        
    //     const statNumbers = document.querySelectorAll('.stats-grid .text-3xl');
    //     if (statNumbers.length >= 4) {
    //         statNumbers[0].textContent = activeCount + inactiveCount + pendingCount;
    //         statNumbers[1].textContent = activeCount;
    //         statNumbers[2].textContent = inactiveCount;
    //         statNumbers[3].textContent = pendingCount;
    //     }
    // }
    
    // function showCustomToast(message) {
    //     const toast = document.getElementById('successToast');
    //     const toastMessage = document.getElementById('toastMessage');
    //     toastMessage.textContent = message;
    //     toast.classList.remove('hidden');
    //     setTimeout(() => {
    //         toast.classList.add('hidden');
    //     }, 3000);
    // }
    

    // Resend Email Modal
    const resendEmailForm = document.getElementById('resend-email-form');
    const resendModal = document.getElementById('resend-email-modal');
    const resendModalContent = document.getElementById('resend-modal-content');
    const resendEmailName = document.getElementById('resend-email-name');
    const cancelResendButton = document.getElementById('cancel-resend-btn');
    // const successToast = document.getElementById('successToast');
    
    document.querySelectorAll('.resend-email-btn').forEach(button => {
        button.addEventListener('click', () => {
            const userId = button.dataset.userId;
            const name = button.dataset.name;

            resendEmailForm.action = `/users/admin-aid/resend-email/${userId}/`;
            
            resendEmailName.textContent = name;

           openResendModal();
        });
    });
    
    function openResendModal() {
        resendModal.classList.remove('hidden');
        // setTimeout(() => {
        //     resendModalContent.classList.remove('scale-95', 'opacity-0');
        //     resendModalContent.classList.add('scale-100', 'opacity-100');
        // }, 10);
    }
    
    function closeResendModal() {
        resendModal.classList.add('hidden');

        // resendModalContent.classList.remove('scale-100', 'opacity-100');
        // resendModalContent.classList.add('scale-95', 'opacity-0');
        // setTimeout(() => {
        // }, 200);
    }
    
    // function showToast() {
    //     successToast.classList.remove('hidden');
    //     setTimeout(() => {
    //         successToast.classList.add('hidden');
    //     }, 3000);
    // }
    
    // Resend email function
    // window.resendEmail = function (name, email) {
    //     openResendModal(name, email);
    // };
    
    cancelResendButton.addEventListener('click', closeResendModal);
    
    // confirmResendBtn.addEventListener('click', () => {
        // Here you would make an AJAX call to resend the email
        // console.log(`Resending email to: ${currentResendName} (${currentResendEmail})`);
    
        // Close modal and show success message
        // closeResendModal();
        // showToast();
    
        // In production, you would send an AJAX request here
        // fetch('/api/resend-email/', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify({ email: currentResendEmail, name: currentResendName })
        // });
    // });
    
    // Close modal when clicking outside
    resendModal.addEventListener('click', event => {
        if (event.target === resendModal) {
            closeResendModal();
        }
    });
});