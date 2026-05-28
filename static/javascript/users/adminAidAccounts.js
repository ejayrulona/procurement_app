document.addEventListener('DOMContentLoaded', () => {

    // ─── Status Toggle Modal ──────────────────────────────────────────────────

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
            const action = isActive ? 'activate' : 'deactivate';

            // Revert toggle visually until confirmed
            toggle.checked = !isActive;

            if (action === 'activate') {
                statusModalIcon.className = "flex items-center justify-center w-16 h-16 mx-auto mb-4 text-green-800 bg-green-100 rounded-full";
                statusModalSvg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>';
                statusModalTitle.textContent = 'Activate Account';
                statusModalTitle.className = 'mb-3 text-2xl font-bold text-green-800';  // ✅ fixed
                actionText.textContent = 'activate';
                confirmStatusBtn.className = "w-full px-4 py-2 font-semibold text-white transition shadow-md bg-gradient-to-r from-green-700 to-green-800 hover:from-green-800 hover:to-green-900 rounded-xl";
            } else {
                statusModalIcon.className = "flex items-center justify-center w-16 h-16 mx-auto mb-4 text-red-800 bg-red-100 rounded-full";
                statusModalSvg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>';
                statusModalTitle.textContent = 'Deactivate Account';
                statusModalTitle.className = 'mb-3 text-2xl font-bold text-red-800';
                actionText.textContent = 'deactivate';
                confirmStatusBtn.className = "w-full px-4 py-2 font-semibold text-white transition shadow-md bg-gradient-to-r from-red-700 to-red-800 hover:from-red-800 hover:to-red-900 rounded-xl";
            }

            userNameText.textContent = userName;
            statusToggleForm.action = `/users/admin-aid/${userId}/toggle-status/`;
            statusModal.classList.remove('hidden');
        });
    });

    cancelStatusBtn.addEventListener('click', () => statusModal.classList.add('hidden'));
    statusModal.addEventListener('click', e => { if (e.target === statusModal) statusModal.classList.add('hidden'); });

    // ─── Resend Email Modal ───────────────────────────────────────────────────

    const resendEmailForm = document.getElementById('resend-email-form');
    const resendModal = document.getElementById('resend-email-modal');
    const resendEmailName = document.getElementById('resend-email-name');
    const cancelResendBtn = document.getElementById('cancel-resend-btn');

    document.querySelectorAll('.resend-email-btn').forEach(button => {
        button.addEventListener('click', () => {
            resendEmailForm.action = `/users/admin-aid/resend-email/${button.dataset.userId}/`;
            resendEmailName.textContent = button.dataset.name;
            resendModal.classList.remove('hidden');
        });
    });

    cancelResendBtn.addEventListener('click', () => resendModal.classList.add('hidden'));
    resendModal.addEventListener('click', e => { if (e.target === resendModal) resendModal.classList.add('hidden'); });

    // ─── Search, Filter, Pagination ──────────────────────────────────────────

    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const refreshBtn = document.getElementById('refreshBtn');
    const tableBody = document.getElementById('accountsTableBody');
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    const showingStart = document.getElementById('showingStart');
    const showingEnd = document.getElementById('showingEnd');
    const totalCount = document.getElementById('totalCount');

    const ROWS_PER_PAGE = 10;
    let currentPage = 1;
    let currentFiltered = [];

    // Snapshot all rows on load
    const allRows = Array.from(tableBody.querySelectorAll('tr'));

    function getRowStatus(row) {
        const badge = row.querySelector('span.inline-flex');
        if (!badge) return '';
        const text = badge.textContent.trim().toLowerCase();
        if (text.includes('pending')) return 'pending';
        if (text.includes('active')) return 'active';
        return 'inactive';
    }

    function getRowText(row) {
        return row.textContent.toLowerCase();
    }

    function applyFilters() {
        const search = searchInput.value.toLowerCase().trim();
        const status = statusFilter.value.toLowerCase();

        currentFiltered = allRows.filter(row => {
            const matchesSearch = !search || getRowText(row).includes(search);
            const rowStatus = getRowStatus(row);
            const matchesStatus = status === 'all' || rowStatus === status;
            return matchesSearch && matchesStatus;
        });

        currentPage = 1;
        renderPage();
    }

    function renderPage() {
        const total = currentFiltered.length;
        const totalPages = Math.max(1, Math.ceil(total / ROWS_PER_PAGE));
        const start = (currentPage - 1) * ROWS_PER_PAGE;
        const end = Math.min(start + ROWS_PER_PAGE, total);
        const pageRows = currentFiltered.slice(start, end);

        // Hide all rows then show current page
        allRows.forEach(row => row.classList.add('hidden'));
        pageRows.forEach(row => {
            row.classList.remove('hidden');
            tableBody.appendChild(row);
        });

        // Empty state row
        let emptyRow = tableBody.querySelector('.empty-state-row');
        if (pageRows.length === 0) {
            if (!emptyRow) {
                emptyRow = document.createElement('tr');
                emptyRow.className = 'empty-state-row';
                emptyRow.innerHTML = `
                    <td colspan="6" class="px-6 py-12 text-sm text-center text-gray-400">
                        No accounts found matching your search.
                    </td>
                `;
            }
            tableBody.appendChild(emptyRow);
        } else {
            emptyRow?.remove();
        }

        // Update pagination info
        showingStart.textContent = total === 0 ? 0 : start + 1;
        showingEnd.textContent = end;
        totalCount.textContent = total;

        // Update button states
        prevBtn.disabled = currentPage === 1;
        nextBtn.disabled = currentPage === totalPages;

        prevBtn.className = prevBtn.disabled
            ? "px-3 py-1 border border-gray-300 rounded-lg text-gray-400 bg-gray-100 cursor-not-allowed text-sm"
            : "px-3 py-1 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-100 text-sm";

        nextBtn.className = nextBtn.disabled
            ? "px-3 py-1 border border-gray-300 rounded-lg text-gray-400 bg-gray-100 cursor-not-allowed text-sm"
            : "px-3 py-1 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-100 text-sm";
    }

    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderPage();
        }
    });

    nextBtn.addEventListener('click', () => {
        const totalPages = Math.ceil(currentFiltered.length / ROWS_PER_PAGE);
        if (currentPage < totalPages) {
            currentPage++;
            renderPage();
        }
    });

    searchInput.addEventListener('input', applyFilters);
    statusFilter.addEventListener('change', applyFilters);

    refreshBtn.addEventListener('click', () => {
        searchInput.value = '';
        statusFilter.value = 'all';
        applyFilters();
    });

    // Initial render
    applyFilters();
});