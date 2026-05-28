document.addEventListener('DOMContentLoaded', () => {

    // ─── Modal ────────────────────────────────────────────────────────────────

    const modal = document.getElementById('reject-remark-modal');
    const declineForm = document.getElementById('decline-form');
    const modalOfficeName = document.getElementById('modal-office-name');
    const remarksTextarea = document.getElementById('id_remarks');

    document.querySelectorAll('.decline-btn').forEach(button => {
        button.addEventListener('click', () => {
            const userId = button.dataset.userId;
            const officeName = button.dataset.OfficeName;

            declineForm.action = `/users/admin/registration-requests/${userId}/decline/`;
            modalOfficeName.textContent = officeName;
            remarksTextarea.value = '';
            modal.classList.remove('hidden');
        });
    });

    document.getElementById('close-modal-btn').addEventListener('click', closeModal);
    document.getElementById('cancel-modal-btn').addEventListener('click', closeModal);
    modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });

    function closeModal() {
        modal.classList.add('hidden');
        remarksTextarea.value = '';
    }

    // ─── Search, Filter, Sort, Pagination ────────────────────────────────────

    const searchInput = document.getElementById('search-input');
    const filterType = document.getElementById('filter-type');
    const sortSelect = document.getElementById('sort-select');
    const tableBody = document.querySelector('tbody');
    const pageInfo = document.getElementById('page-info');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    const ROWS_PER_PAGE = 10;
    let currentPage = 1;

    // Snapshot all rows from the DOM on load
    const allRows = Array.from(tableBody.querySelectorAll('tr'));

    function getRowData(row) {
        return {
            officeName: row.dataset.officeName?.toLowerCase() || "",
            papCategory: row.dataset.papCategory?.toLowerCase() || "",
            headName: row.dataset.headName?.toLowerCase() || "",
            email: row.dataset.email?.toLowerCase() || "",
            dateRegistered: row.dataset.dateRegistered || "",
            status: row.dataset.status?.toLowerCase() || "",
        };
    }

    function filterAndSort() {
        const search = searchInput.value.toLowerCase().trim();
        const type = filterType.value.toLowerCase();
        const sort = sortSelect.value;

        let filtered = allRows.filter(row => {
            const d = getRowData(row);

            const matchesSearch = !search || [
                d.officeName, d.headName, d.email
            ].some(val => val.includes(search));

            const matchesType = !type || type === "all types" || d.papCategory.includes(type);

            return matchesSearch && matchesType;
        });

        // Sort
        filtered.sort((a, b) => {
            const da = getRowData(a);
            const db = getRowData(b);

            if (sort === "newest") {
                return db.dateRegistered.localeCompare(da.dateRegistered);
            } else if (sort === "oldest") {
                return da.dateRegistered.localeCompare(db.dateRegistered);
            } else if (sort === "name") {
                return da.officeName.localeCompare(db.officeName);
            }
            return 0;
        });

        currentPage = 1;
        renderPage(filtered);
    }

    function renderPage(rows) {
        const totalPages = Math.max(1, Math.ceil(rows.length / ROWS_PER_PAGE));
        const start = (currentPage - 1) * ROWS_PER_PAGE;
        const pageRows = rows.slice(start, start + ROWS_PER_PAGE);

        // Hide all rows then show only current page
        allRows.forEach(row => row.classList.add('hidden'));
        pageRows.forEach(row => {
            row.classList.remove('hidden');
            tableBody.appendChild(row); // maintain sort order in DOM
        });

        // Empty state
        let emptyRow = tableBody.querySelector('.empty-row');
        if (pageRows.length === 0) {
            if (!emptyRow) {
                emptyRow = document.createElement('tr');
                emptyRow.className = 'empty-row';
                emptyRow.innerHTML = `
                    <td colspan="7" class="px-6 py-12 text-sm text-center text-gray-400">
                        No registration requests found.
                    </td>
                `;
            }
            tableBody.appendChild(emptyRow);
        } else {
            emptyRow?.remove();
        }

        pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
        prevBtn.disabled = currentPage === 1;
        nextBtn.disabled = currentPage === totalPages;
    }

    // Store current filtered rows for pagination
    let currentFiltered = [...allRows];

    function applyFilters() {
        const search = searchInput.value.toLowerCase().trim();
        const type = filterType.value.toLowerCase();
        const sort = sortSelect.value;

        currentFiltered = allRows.filter(row => {
            const d = getRowData(row);

            const matchesSearch = !search || [
                d.officeName, d.headName, d.email
            ].some(val => val.includes(search));

            const matchesType = !type || type === "all types" || d.papCategory.includes(type);

            return matchesSearch && matchesType;
        });

        currentFiltered.sort((a, b) => {
            const da = getRowData(a);
            const db = getRowData(b);

            if (sort === "newest") return db.dateRegistered.localeCompare(da.dateRegistered);
            if (sort === "oldest") return da.dateRegistered.localeCompare(db.dateRegistered);
            if (sort === "name") return da.officeName.localeCompare(db.officeName);
            return 0;
        });

        currentPage = 1;
        renderPage(currentFiltered);
    }

    // Pagination buttons
    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderPage(currentFiltered);
        }
    });

    nextBtn.addEventListener('click', () => {
        const totalPages = Math.ceil(currentFiltered.length / ROWS_PER_PAGE);
        if (currentPage < totalPages) {
            currentPage++;
            renderPage(currentFiltered);
        }
    });

    // Event listeners
    searchInput.addEventListener('input', applyFilters);
    filterType.addEventListener('change', applyFilters);
    sortSelect.addEventListener('change', applyFilters);

    // Initial render
    applyFilters();
});