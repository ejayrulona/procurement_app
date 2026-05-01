document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('reject-remark-modal');
    const declineForm = document.getElementById('decline-form');
    const modalCollegeName = document.getElementById('modal-college-name');
    const remarksTextarea = document.getElementById('id_remarks');

    document.querySelectorAll('.decline-btn').forEach(button => {
        button.addEventListener('click', () => {
            const userId = button.dataset.userId;
            const collegeName = button.dataset.collegeName;

            declineForm.action = `/users/admin/registration-requests/${userId}/decline/`;

            modalCollegeName.textContent = collegeName;
            remarksTextarea.value = '';

            modal.classList.remove('hidden');
        });
    });

    document.getElementById('close-modal-btn').addEventListener('click', closeModal);
    document.getElementById('cancel-modal-btn').addEventListener('click', closeModal);

    modal.addEventListener('click', event => {
        if (event.target === modal) closeModal();
    })

    function closeModal() {
        modal.classList.add('hidden');
        remarksTextarea.value = '';
    }
});