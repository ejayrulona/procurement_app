document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("remarks-modal");
    const ppmpId = document.getElementById("ppmp-data").dataset.ppmpId;
    const modalTitle = document.getElementById("remarks-modal-title");
    const modalDescription = document.getElementById("remarks-modal-description");
    const remarksInput = document.getElementById("remarks-input");
    const confirmBtn = document.getElementById("confirm-remarks-btn");
    const cancelBtn = document.getElementById("cancel-remarks-btn");
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    let currentAction = null;

    function openRemarksModal(action, title, description) {
        currentAction = action;
        modalTitle.textContent = title;
        modalDescription.textContent = description;
        remarksInput.value = "";
        modal.classList.remove("hidden");
        modal.classList.add("flex");
    }

    function closeRemarksModal() {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
        currentAction = null;
    }

    // Decline button
    document.getElementById("decline-btn")?.addEventListener("click", () => {
        openRemarksModal(
            `/ppmp/${ppmpId}/decline/`,
            "Decline PPMP",
            "Please provide a reason for declining this PPMP."
        );
    });

    // Revise button
    document.getElementById("revision-btn")?.addEventListener("click", () => {
        openRemarksModal(
            `/ppmp/${ppmpId}/revise/`,
            "Return for Revision",
            "Please provide instructions on what needs to be corrected."
        );
    });

    cancelBtn.addEventListener("click", closeRemarksModal);

    // Confirm — builds and sends the payload
    confirmBtn.addEventListener("click", () => {
        const remarks = remarksInput.value.trim();

        fetch(currentAction, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ remarks }),
        })
            .then(res => res.json())
            .then(data => {
                if (data.ppmp_id) {
                    closeRemarksModal();
                    window.location.reload();
                } else {
                    alert(data.error || "An error occurred.");
                }
            })
            .catch(() => {
                alert("An unexpected error occurred. Please try again.");
            });
    });

    const exportExcelBtn = document.getElementById("export-excel-btn");

    exportExcelBtn.addEventListener('click', async () => {
        const fiscal_year = exportExcelBtn.dataset.fiscalYear;

        try {
            if (exportExcelBtn) {
                exportExcelBtn.disabled = true;
                exportExcelBtn.textContent = "Exporting…";
            }

            const response = await fetch(`/ppmp/${appId}/export/`, {
                method: "GET",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            });

            if (!response.ok) {
                throw new Error(`Export failed: ${response.statusText}`);
            }

            // Convert the response to a downloadable Blob
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);

            // Trigger browser download
            const disposition = response.headers.get("Content-Disposition");

            let filename = `PPMP_FY${fiscal_year}.xlsx`;

            if (disposition && disposition.includes("filename=")) {
                filename = disposition
                    .split("filename=")[1]
                    .replace(/"/g, "");
            }

            const anchor = document.createElement("a");
            anchor.href = url;
            anchor.download = filename;

            document.body.appendChild(anchor);
            anchor.click();

            // Clean up
            anchor.remove();
            URL.revokeObjectURL(url);

        } catch (err) {
            console.error("Export error:", err);
            alert("Export failed. Please try again or contact support.");
        } finally {
            if (exportExcelBtn) {
                exportExcelBtn.disabled = false;
                exportExcelBtn.textContent = "Export to Excel";
            }
        }
    })


    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
        return "";
    }
});