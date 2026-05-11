document.addEventListener("DOMContentLoaded", () => {
    // State
    const state = {
        lines: [],          // Array of line objects tracking each procurement line
        activeLineIndex: 0, // Currently visible line tab
    };

    // DOM References 

    const formAction = document.getElementById('ppmpForm').dataset.action;
    const lineContainer = document.getElementById("lineContainer");
    const lineTabs = document.getElementById("lineTabs");
    const addLineBtn = document.getElementById("addLineBtn");
    const prevLineBtn = document.getElementById("prevLineBtn");
    const nextLineBtn = document.getElementById("nextLineBtn");
    const pageIndicator = document.getElementById("pageIndicator");
    const totalAllLines = document.getElementById("totalAllLines");
    const ceilingWarning = document.getElementById("ceilingWarning");
    const ceilingInput = document.getElementById("id_ceiling");
    const classificationInput = document.getElementById("id_classification");
    const submitBtn = document.getElementById("submitBtn");

    const linePanelTemplate = document.getElementById("linePanelTemplate");
    const addedItemRowTemplate = document.getElementById("addedItemRowTemplate");

    const officeNameDisplay = document.getElementById("officeNameDisplay").textContent.trim();

    const baseUrl = "/inventory/api";
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    // Line Management

    function createLine() {
        const lineIndex = state.lines.length;

        const panel = linePanelTemplate.content.cloneNode(true).querySelector(".line-panel");
        panel.dataset.lineIndex = lineIndex;
        panel.querySelector(".line-number").textContent = lineIndex + 1;

        const choices = JSON.parse(document.getElementById('procurement-choices').textContent);
        const select = panel.querySelector('.mode-of-procurement');
        choices.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            select.appendChild(option);
        });

        // Wire up unique datalist id for this line's general description
        const gdInput = panel.querySelector(".general-description-input");
        const gdDatalist = panel.querySelector(".general-description-list");
        const gdListId = `general-description-list-${lineIndex}`;
        gdInput.setAttribute("list", gdListId);
        gdDatalist.setAttribute("id", gdListId);

        // Populate general description datalist
        fetchGeneralDescriptions(gdInput, gdDatalist, panel, lineIndex);

        // Remove line button
        panel.querySelector(".remove-line-btn").addEventListener("click", () => {
            removeLine(lineIndex);
        });

        lineContainer.appendChild(panel);

        state.lines.push({
            index: lineIndex,
            panel: panel,
            itemCodeId: null,
            entries: [],
        });

        renderTabs();
        navigateTo(lineIndex);
    }

    function removeLine(lineIndex) {
        if (state.lines.length === 1) {
            alert("At least one procurement line is required.");
            return;
        }

        state.lines.splice(lineIndex, 1);

        // Re-index remaining lines
        state.lines.forEach((line, i) => {
            line.index = i;
            line.panel.dataset.lineIndex = i;
            line.panel.querySelector(".line-number").textContent = i + 1;
        });

        lineContainer.removeChild(
            lineContainer.querySelector(`[data-line-index="${lineIndex}"]`)
        );

        const newActive = Math.min(state.activeLineIndex, state.lines.length - 1);
        renderTabs();
        navigateTo(newActive);
        recalculateGrandTotal();
    }

    function navigateTo(index) {
        state.activeLineIndex = index;

        state.lines.forEach((line, i) => {
            line.panel.classList.toggle("hidden", i !== index);
        });

        renderTabs();
        updatePagination();
    }

    function renderTabs() {
        lineTabs.innerHTML = "";

        state.lines.forEach((line, i) => {
            const tab = document.createElement("button");
            tab.type = "button";
            tab.textContent = `Line ${i + 1}`;
            tab.className = [
                "px-4 py-1.5 rounded-lg text-sm font-medium transition",
                i === state.activeLineIndex
                    ? "bg-red-600 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            ].join(" ");
            tab.addEventListener("click", () => navigateTo(i));
            lineTabs.appendChild(tab);
        });
    }

    function updatePagination() {
        const total = state.lines.length;
        const current = state.activeLineIndex;

        pageIndicator.textContent = `Line ${current + 1} of ${total}`;
        prevLineBtn.disabled = current === 0;
        nextLineBtn.disabled = current === total - 1;
    }

    function fetchGeneralDescriptions(input, datalist, panel, lineIndex) {
        fetch(`${baseUrl}/get-all-item-codes/`)
            .then(res => res.json())
            .then(data => {
                datalist.innerHTML = "";
                data.item_codes.forEach(itemCode => {
                    const option = document.createElement("option");
                    option.value = itemCode.general_description;
                    option.dataset.id = itemCode.id;
                    option.dataset.code = itemCode.code;
                    option.dataset.objectCode = itemCode.object_code_display;
                    datalist.appendChild(option);
                });

                input.addEventListener("input", () => {
                    const match = Array.from(datalist.options)
                        .find(o => o.value.toLowerCase() === input.value.toLowerCase());

                    if (match) {
                        onGeneralDescriptionSelected(match, panel, lineIndex);
                    }
                });
            });
    }

    function onGeneralDescriptionSelected(match, panel, lineIndex) {
        const itemCodeId = match.dataset.id;

        // Update hidden input and auto-fill displays
        panel.querySelector(".item-code-id-input").value = itemCodeId;
        panel.querySelector(".item-code-display").value = match.dataset.code;
        panel.querySelector(".object-code-display").value = match.dataset.objectCode;

        const generalDescription = panel.querySelector(".general-description-input").value;
        panel.querySelector(".procurement-program-input").value = `Procurement of various ${generalDescription} for ${officeNameDisplay}`;

        state.lines[lineIndex].itemCodeId = itemCodeId;

        fetchItemsByItemCode(itemCodeId, panel);
    }

    // ─── Items Fetch ──────────────────────────────────────────────────────────

    function fetchItemsByItemCode(itemCodeId, panel, callback = null) {
        fetch(`${baseUrl}/get-items-by-item-code/?item_code_id=${itemCodeId}`)
            .then(response => response.json())
            .then(data => {
                const section = panel.querySelector(".available-items-section");
                const list = panel.querySelector(".available-items-list");

                list.innerHTML = "";

                data.items.forEach(item => {
                    const wrapper = document.createElement("div");
                    wrapper.className = "flex items-center gap-3 py-1";
                    wrapper.innerHTML = `
                        <input type="checkbox" class="available-item-checkbox" 
                            data-item-id="${item.id}"
                            data-item-name="${item.name}"
                            data-unit="${item.unit}"
                            data-unit-cost="${item.unit_cost}">
                        <span class="text-sm text-gray-700">${item.name}</span>
                        <span class="text-xs text-gray-400">${item.unit} — ₱${parseFloat(item.unit_cost).toLocaleString()}</span>
                    `;
                    list.appendChild(wrapper);
                });

                section.classList.remove("hidden");

                panel.querySelector(".add-selected-items-btn")
                    .addEventListener("click", () => addSelectedItems(panel));

                if (callback) callback(); // Run after items are loaded
            });
    }

    // ─── Add Selected Items ───────────────────────────────────────────────────

    function addSelectedItems(panel) {
        const checkboxes = panel.querySelectorAll(".available-item-checkbox:checked");

        if (!checkboxes.length) {
            alert("Please select at least one item.");
            return;
        }

        const tbody = panel.querySelector(".added-items-tbody");
        const addedSection = panel.querySelector(".added-items-section");
        const lineIndex = parseInt(panel.dataset.lineIndex);

        checkboxes.forEach(checkbox => {
            const itemId = checkbox.dataset.itemId;

            // Prevent duplicate entries
            if (state.lines[lineIndex].entries.find(e => e.itemId === itemId)) {
                return;
            }

            const row = addedItemRowTemplate.content.cloneNode(true).querySelector(".added-item-row");
            row.dataset.itemId = itemId;
            row.dataset.unitCost = checkbox.dataset.unitCost;

            row.querySelector(".item-name-cell").textContent = checkbox.dataset.itemName;
            row.querySelector(".unit-cell").textContent = checkbox.dataset.unit;
            row.querySelector(".unit-cost-cell").textContent =
                `₱${parseFloat(checkbox.dataset.unitCost).toLocaleString()}`;

            // Initial total
            updateRowTotal(row);

            // Quantity change recalculates total
            row.querySelector(".quantity-input").addEventListener("input", () => {
                updateRowTotal(row);
                recalculateLineTotal(panel);
                recalculateGrandTotal();
                checkCeilingExceeded();
            });

            // Remove entry
            row.querySelector(".remove-entry-btn").addEventListener("click", () => {
                const entryIndex = state.lines[lineIndex].entries
                    .findIndex(e => e.itemId === itemId);

                if (entryIndex !== -1) {
                    state.lines[lineIndex].entries.splice(entryIndex, 1);
                }

                tbody.removeChild(row);
                recalculateLineTotal(panel);
                recalculateGrandTotal();
                checkCeilingExceeded();

                if (!tbody.children.length) {
                    addedSection.classList.add("hidden");
                }
            });

            tbody.appendChild(row);

            state.lines[lineIndex].entries.push({ itemId });

            checkbox.checked = false;
        });

        addedSection.classList.remove("hidden");
        recalculateLineTotal(panel);
        recalculateGrandTotal();
        checkCeilingExceeded();
    }

    // ─── Totals ───────────────────────────────────────────────────────────────

    function updateRowTotal(row) {
        const quantity = parseFloat(row.querySelector(".quantity-input").value) || 0;
        const unitCost = parseFloat(row.dataset.unitCost) || 0;
        const total = quantity * unitCost;
        row.querySelector(".total-cell").textContent = `₱${total.toLocaleString()}`;
        return total;
    }

    function recalculateLineTotal(panel) {
        const rows = panel.querySelectorAll(".added-item-row");
        const total = Array.from(rows).reduce((sum, row) => sum + updateRowTotal(row), 0);
        panel.querySelector(".line-total").textContent = `₱${total.toLocaleString()}`;
        return total;
    }

    function recalculateGrandTotal() {
        const total = state.lines.reduce((sum, line) => {
            return sum + recalculateLineTotal(line.panel);
        }, 0);

        totalAllLines.textContent = `₱${total.toLocaleString()}`;
        return total;
    }

    function checkCeilingExceeded() {
        const ceiling = parseFloat(ceilingInput.value) || 0;
        const total = recalculateGrandTotal();
        const exceeded = ceiling > 0 && total > ceiling;

        ceilingWarning.classList.toggle("hidden", !exceeded);
        submitBtn.disabled = exceeded;
    }

    // ─── Helpers ──────────────────────────────────────────────────────────────

    function getFiscalYear() {
        return document.getElementById("id_fiscal_year").value || new Date().getFullYear();
    }

    // ─── Submission ───────────────────────────────────────────────────────────

    function buildPayload() {
        return {
            fiscal_year: getFiscalYear(),
            classification: classificationInput.value,
            source_of_funds: document.getElementById("id_source_of_funds").value,
            ceiling: ceilingInput.value,
            procurement_lines: state.lines.map((line, i) => {
                const panel = line.panel;
                const rows = panel.querySelectorAll(".added-item-row");
                
                return {
                    item_code_id: line.itemCodeId,
                    mode_of_procurement: panel.querySelector(".mode-of-procurement").value,
                    procurement_program: panel.querySelector(".procurement-program-input").value,
                    order: i + 1,
                    entries: Array.from(rows)
                        .filter(row => row.querySelector(".entry-checkbox").checked)
                        .map(row => ({
                            item_id: row.dataset.itemId,
                            quantity: row.querySelector(".quantity-input").value,
                            unit_cost_snapshot: row.dataset.unitCost,
                            date_needed: row.querySelector(".date-needed-input").value,
                            remarks: row.querySelector(".remarks-input").value,
                        }))
                };
            })
        };
    }

    submitBtn.addEventListener("click", () => {
        if (submitBtn.disabled) return;

        const payload = buildPayload();

        fetch(formAction, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify(payload),
        })
            .then(res => res.json())
            .then(data => {
                if (data.ppmp_id) {
                    window.location.href = `/ppmp/ppmp/${data.ppmp_id}/`;
                } else {
                    alert(data.error || "Submission failed. Please check your inputs.");
                }
            })
            .catch(() => {
                alert("An unexpected error occurred. Please try again.");
            });
    });

    // ─── Pagination Controls ──────────────────────────────────────────────────

    prevLineBtn.addEventListener("click", () => navigateTo(state.activeLineIndex - 1));
    nextLineBtn.addEventListener("click", () => navigateTo(state.activeLineIndex + 1));
    addLineBtn.addEventListener("click", createLine);
    ceilingInput.addEventListener("input", checkCeilingExceeded);

    // Edit Mode Initialization

    function initializeFromExistingData() {
        const dataScript = document.getElementById("existing-lines-data");
        if (!dataScript) return; // Skip if not edit mode

        const existingLines = JSON.parse(dataScript.textContent);
        if (!existingLines.length) return;

        existingLines.forEach((lineData, index) => {
            createLine();

            const line = state.lines[index];
            const panel = line.panel;

            // Wait for datalist to populate then restore values
            // Poll until options are ready
            const restoreInterval = setInterval(() => {
                const datalist = panel.querySelector(".general-description-list");
                const options = Array.from(datalist.options);

                if (!options.length) return; // Mot loaded yet

                clearInterval(restoreInterval);

                // Match and select the general description
                const match = options.find(
                    option => option.dataset.id == lineData.item_code_id
                );

                if (match) {
                    const gdInput = panel.querySelector(".general-description-input");
                    gdInput.value = match.value;

                    panel.querySelector(".item-code-id-input").value = lineData.item_code_id;
                    panel.querySelector(".item-code-display").value = lineData.item_code_code;
                    panel.querySelector(".object-code-display").value = lineData.object_code;

                    line.itemCodeId = lineData.item_code_id;

                    panel.querySelector(".mode-of-procurement").value = lineData.mode_of_procurement;
                    panel.querySelector(".procurement-program-input").value = lineData.procurement_program;

                    // Fetch items then restore entries
                    fetchItemsByItemCode(lineData.item_code_id, panel, () => {
                        restoreEntries(panel, lineData.entries, index);
                    });
                }
            }, 100);
        });
    }

    function restoreEntries(panel, entries, lineIndex) {
        entries.forEach(entryData => {
            const row = addedItemRowTemplate.content.cloneNode(true).querySelector(".added-item-row");
            row.dataset.itemId = entryData.item_id;
            row.dataset.unitCost = entryData.unit_cost;

            row.querySelector(".item-name-cell").textContent = entryData.item_name;
            row.querySelector(".unit-cell").textContent = entryData.unit;
            row.querySelector(".unit-cost-cell").textContent =
                `₱${parseFloat(entryData.unit_cost).toLocaleString()}`;

            row.querySelector(".quantity-input").value = entryData.quantity;
            row.querySelector(".date-needed-input").value = entryData.date_needed;
            row.querySelector(".remarks-input").value = entryData.remarks;

            updateRowTotal(row);

            row.querySelector(".quantity-input").addEventListener("input", () => {
                updateRowTotal(row);
                recalculateLineTotal(panel);
                recalculateGrandTotal();
                checkCeilingExceeded();
            });

            row.querySelector(".remove-entry-btn").addEventListener("click", () => {
                const entryIndex = state.lines[lineIndex].entries
                    .findIndex(e => e.itemId == entryData.item_id);
                if (entryIndex !== -1) state.lines[lineIndex].entries.splice(entryIndex, 1);

                panel.querySelector(".added-items-tbody").removeChild(row);
                recalculateLineTotal(panel);
                recalculateGrandTotal();
                checkCeilingExceeded();
            });

            panel.querySelector(".added-items-tbody").appendChild(row);
            panel.querySelector(".added-items-section").classList.remove("hidden");

            state.lines[lineIndex].entries.push({ itemId: String(entryData.item_id) });
        });

        recalculateLineTotal(panel);
        recalculateGrandTotal();
        checkCeilingExceeded();
    }

    // Initialize

    const isEditMode = !!document.getElementById("existing-lines-data");

    if (isEditMode) {
        initializeFromExistingData();
    } else {
        createLine();
    }
});