document.addEventListener('DOMContentLoaded', () => {

    // ─── Item Form Datalist (Create/Edit page only) ───────────────────────────

    const objectExpenditureInput = document.getElementById('object-expenditure-dropdown');
    const objectCodeInput = document.getElementById('object-code-dropdown');
    const itemCodeInput = document.getElementById('item-code-dropdown');
    const objectExpenditureList = document.getElementById('object-expenditure-list');
    const objectCodeList = document.getElementById('object-code-list');
    const itemCodeList = document.getElementById('item-code-list');

    const baseUrl = '/inventory/api';

    let currentObjectExpenditureId = '';
    let currentObjectCodeId = '';

    if (objectExpenditureInput) {
        objectExpenditureInput.addEventListener("input", event => {
            const selectedOption = Array.from(objectExpenditureList.querySelectorAll('option'))
                .find(option => option.value === objectExpenditureInput.value);

            if (selectedOption) {
                currentObjectExpenditureId = selectedOption.dataset.id;
                if (objectCodeInput && event.isTrusted) objectCodeInput.value = "";
                fetchObjectCodes(currentObjectExpenditureId);
            }
        });

        const preselectedOption = Array.from(objectExpenditureList.querySelectorAll('option'))
            .find(option => option.value === objectExpenditureInput.value);

        if (preselectedOption) {
            currentObjectExpenditureId = preselectedOption.dataset.id;
            fetchObjectCodes(currentObjectExpenditureId);
        }
    }

    function fetchObjectCodes(objectExpenditureId) {
        if (!objectExpenditureId) return;

        fetch(`${baseUrl}/get-object-codes/?expenditure=${objectExpenditureId}`)
            .then(response => response.json())
            .then(data => {
                if (objectCodeList) {
                    objectCodeList.innerHTML = '';
                    data.object_codes.forEach(objectCode => {
                        const option = document.createElement('option');
                        option.value = objectCode.code;
                        option.setAttribute('data-id', objectCode.id);
                        objectCodeList.appendChild(option);
                    });

                    if (objectCodeInput && objectCodeInput.value) {
                        const event = new Event('input', { bubbles: true });
                        objectCodeInput.dispatchEvent(event);
                    }
                }
            });
    }

    if (objectCodeInput) {
        objectCodeInput.addEventListener("input", event => {
            const selectedOption = Array.from(objectCodeList.querySelectorAll('option'))
                .find(option => option.value === objectCodeInput.value);

            if (selectedOption) {
                currentObjectCodeId = selectedOption.dataset.id;
                if (itemCodeInput && event.isTrusted) itemCodeInput.value = "";
                fetchItemCodes(currentObjectCodeId);
            }
        });

        const preselectedOption = Array.from(objectCodeList.querySelectorAll('option'))
            .find(option => option.value === objectCodeInput.value);

        if (preselectedOption) {
            currentObjectCodeId = preselectedOption.dataset.id;
            fetchItemCodes(currentObjectCodeId);
        }
    }

    function fetchItemCodes(objectExpenditureId) {
        if (!objectExpenditureId) return;

        fetch(`${baseUrl}/get-item-codes/?object-code=${objectExpenditureId}`)
            .then(response => response.json())
            .then(data => {
                if (itemCodeList) {
                    itemCodeList.innerHTML = '';
                    data.item_codes.forEach(itemCode => {
                        const option = document.createElement('option');
                        option.value = itemCode.code;
                        option.setAttribute('data-id', itemCode.id);
                        option.setAttribute('data-general-description', itemCode.general_description);
                        itemCodeList.appendChild(option);
                    });

                    if (itemCodeInput && itemCodeInput.value) {
                        const event = new Event('input', { bubbles: true });
                        itemCodeInput.dispatchEvent(event);
                    }
                }
            });
    }

    function autoGenerateGeneralDescription(match) {
        if (match) {
            document.getElementById('general-description').value = match.dataset.generalDescription;
        } else {
            document.getElementById('general-description').value = '';
        }
    }

    function findMatch(value) {
        const options = itemCodeList.querySelectorAll('option');
        return Array.from(options).find(
            option => option.value.toLowerCase() === value.toLowerCase()
        );
    }

    if (itemCodeInput) {
        itemCodeInput.addEventListener('input', () => {
            autoGenerateGeneralDescription(findMatch(itemCodeInput.value));
        });

        if (itemCodeInput.value) {
            autoGenerateGeneralDescription(findMatch(itemCodeInput.value));
        }
    }

    // ─── Search & Pagination (Inventory list page only) ───────────────────────

    const tableBody = document.getElementById('inventoryTableBody');

    if (!tableBody) return;

    const searchInput = document.getElementById('searchInput');
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    const showingStart = document.getElementById('showingStart');
    const showingEnd = document.getElementById('showingEnd');
    const totalCount = document.getElementById('totalCount');

    const ROWS_PER_PAGE = 10;
    let currentPage = 1;
    let currentFiltered = [];

    const allRows = Array.from(tableBody.querySelectorAll('tr'));

    console.log('Total rows found:', allRows.length);

    function applyFilters() {
        const search = searchInput.value.toLowerCase().trim();

        currentFiltered = allRows.filter(row => {
            const itemCode = row.getAttribute('data-item-code') || "";
            const itemName = row.getAttribute('data-item-name') || "";
            const specification = row.getAttribute('data-specification') || "";

            return !search || [itemCode, itemName, specification]
                .some(val => val.includes(search));
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

        // Hide all rows first
        allRows.forEach(row => row.classList.add('hidden'));

        // Show only the current page rows
        pageRows.forEach(row => row.classList.remove('hidden'));

        // Empty state
        let emptyRow = tableBody.querySelector('.empty-state-row');
        if (pageRows.length === 0) {
            if (!emptyRow) {
                emptyRow = document.createElement('tr');
                emptyRow.className = 'empty-state-row';
                emptyRow.innerHTML = `
                    <td colspan="6" class="px-6 py-12 text-sm text-center text-gray-400">
                        No items found matching your search.
                    </td>
                `;
                tableBody.appendChild(emptyRow);
            }
        } else {
            emptyRow?.remove();
        }

        showingStart.textContent = total === 0 ? 0 : start + 1;
        showingEnd.textContent = end;
        totalCount.textContent = total;

        prevBtn.disabled = currentPage === 1;
        nextBtn.disabled = currentPage === totalPages;
    }

    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) { currentPage--; renderPage(); }
    });

    nextBtn.addEventListener('click', () => {
        const totalPages = Math.ceil(currentFiltered.length / ROWS_PER_PAGE);
        if (currentPage < totalPages) { currentPage++; renderPage(); }
    });

    searchInput.addEventListener('input', applyFilters);

    // Initial render
    applyFilters();
});