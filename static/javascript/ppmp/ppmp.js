document.addEventListener("DOMContentLoaded", () => {

    // ─── Shared Utilities ─────────────────────────────────────────────────────

    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
        return "";
    }

    const ppmpDataEl = document.getElementById("ppmp-data");
    const ppmpId = ppmpDataEl?.dataset.ppmpId;

    // ─── Remarks Modal (Decline / Revise) ─────────────────────────────────────

    const remarksModal = document.getElementById("remarks-modal");
    const remarksHeader = document.getElementById("remarks-modal-header");
    const remarksIconWrap = document.getElementById("remarks-modal-icon");
    const remarksTitleEl = document.getElementById("remarks-modal-title");
    const remarksBanner = document.getElementById("remarks-modal-banner");
    const remarksBannerIcon = document.getElementById("remarks-banner-icon");
    const remarksDescEl = document.getElementById("remarks-modal-description");
    const remarksInput = document.getElementById("remarks-input");
    const remarksErrorEl = document.getElementById("remarks-error");
    const remarksConfirmBtn = document.getElementById("confirm-remarks-btn");
    const remarksCancelBtn = document.getElementById("cancel-remarks-btn");
    const remarksCloseBtn = document.getElementById("close-remarks-modal-btn");

    let currentRemarksAction = null;

    const REMARKS_ICONS = {
        revise: `<svg class="w-5 h-5 text-yellow-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
        </svg>`,
        decline: `<svg class="w-5 h-5 text-red-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/>
        </svg>`,
    };

    const REMARKS_THEMES = {
        revise: {
            headerGradient: "linear-gradient(to right, #92400e, #b45309)",
            bannerBg: "#fffbeb",
            bannerBorder: "#fde68a",
            bannerText: "#78350f",
            bannerIconColor: "#d97706",
            confirmBg: "#b45309",
            confirmHover: "#92400e",
            label: "Send for Revision",
            title: "Request Revision",
            description: "Please provide a clear reason so the end-user unit can correct the PPMP accordingly.",
        },
        decline: {
            headerGradient: "linear-gradient(to right, #991b1b, #b91c1c)",
            bannerBg: "#fef2f2",
            bannerBorder: "#fca5a5",
            bannerText: "#7f1d1d",
            bannerIconColor: "#dc2626",
            confirmBg: "#b91c1c",
            confirmHover: "#991b1b",
            label: "Decline PPMP",
            title: "Decline PPMP",
            description: "This PPMP will be declined and the end-user unit will be notified. This action cannot be undone.",
        },
    };

    function openRemarksModal(action) {
        if (!remarksModal) return;

        const theme = REMARKS_THEMES[action];
        currentRemarksAction = action;

        remarksHeader.style.background = theme.headerGradient;
        remarksIconWrap.innerHTML = REMARKS_ICONS[action];
        remarksTitleEl.textContent = theme.title;
        remarksBanner.style.cssText = `background:${theme.bannerBg}; border-color:${theme.bannerBorder}; color:${theme.bannerText};`;
        remarksBannerIcon.style.color = theme.bannerIconColor;
        remarksDescEl.textContent = theme.description;
        remarksConfirmBtn.textContent = theme.label;
        remarksConfirmBtn.style.background = theme.confirmBg;
        remarksInput.value = "";
        remarksErrorEl?.classList.add("hidden");

        remarksConfirmBtn.onmouseover = () => remarksConfirmBtn.style.background = theme.confirmHover;
        remarksConfirmBtn.onmouseout = () => remarksConfirmBtn.style.background = theme.confirmBg;

        remarksModal.style.display = "flex";
        document.body.style.overflow = "hidden";
        setTimeout(() => remarksInput.focus(), 80);
    }

    function closeRemarksModal() {
        if (!remarksModal) return;
        remarksModal.style.display = "none";
        document.body.style.overflow = "";
        currentRemarksAction = null;
    }

    function submitRemarksModal() {
        const remarks = remarksInput?.value.trim();

        if (!remarks) {
            remarksErrorEl?.classList.remove("hidden");
            remarksInput?.focus();
            return;
        }

        remarksErrorEl?.classList.add("hidden");
        remarksConfirmBtn.disabled = true;
        remarksConfirmBtn.textContent = "Submitting…";

        fetch(`/ppmp/${ppmpId}/${currentRemarksAction}/`, {
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
                    alert("Error: " + (data.error || "Unknown error"));
                }
            })
            .catch(() => {
                alert("Request failed. Please try again.");
            })
            .finally(() => {
                remarksConfirmBtn.disabled = false;
                remarksConfirmBtn.textContent = REMARKS_THEMES[currentRemarksAction]?.label || "Confirm";
            });
    }

    document.getElementById("revision-btn")?.addEventListener("click", () => openRemarksModal("revise"));
    document.getElementById("decline-btn")?.addEventListener("click", () => openRemarksModal("decline"));
    remarksCancelBtn?.addEventListener("click", closeRemarksModal);
    remarksCloseBtn?.addEventListener("click", closeRemarksModal);
    remarksConfirmBtn?.addEventListener("click", submitRemarksModal);
    remarksModal?.addEventListener("click", e => { if (e.target === remarksModal) closeRemarksModal(); });

    const approveModal = document.getElementById("approve-modal");
    const approveBtn = document.getElementById("approve-btn");
    const approveConfirmBtn = document.getElementById("confirm-approve-btn");
    const approveCancelBtn = document.getElementById("cancel-approve-btn");
    const approveCloseBtn = document.getElementById("close-approve-modal-btn");

    function openApproveModal() {
        if (!approveModal) return;
        approveModal.style.display = "flex";
        document.body.style.overflow = "hidden";
    }

    function closeApproveModal() {
        if (!approveModal) return;
        approveModal.style.display = "none";
        document.body.style.overflow = "";
    }

    function submitApproval() {
        if (!approveConfirmBtn) return;

        approveConfirmBtn.disabled = true;
        approveConfirmBtn.innerHTML = `
            <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
            </svg> Approving…
        `;

        fetch(`/ppmp/${ppmpId}/approve/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({}),
        })
            .then(res => res.json())
            .then(data => {
                if (data.ppmp_id) {
                    closeApproveModal();
                    window.location.reload();
                } else {
                    alert("Error: " + (data.error || "Unknown error"));
                    approveConfirmBtn.disabled = false;
                    approveConfirmBtn.textContent = "Approve";
                }
            })
            .catch(() => {
                alert("Request failed. Please try again.");
                approveConfirmBtn.disabled = false;
                approveConfirmBtn.textContent = "Approve";
            });
    }

    approveBtn?.addEventListener("click", openApproveModal);
    approveCancelBtn?.addEventListener("click", closeApproveModal);
    approveCloseBtn?.addEventListener("click", closeApproveModal);
    approveConfirmBtn?.addEventListener("click", submitApproval);
    approveModal?.addEventListener("click", e => { if (e.target === approveModal) closeApproveModal(); });

    // ─── Edit Request Modal ───────────────────────────────────────────────────

    const editRequestModal = document.getElementById("editRequestModal");

    function openEditRequestModal(id, title) {
        if (!editRequestModal) return;
        document.getElementById("modal_ppmp_id").value = id;
        document.getElementById("modal_ppmp_title").innerText = title;
        document.getElementById("edit_reason").value = "";
        editRequestModal.classList.remove("hidden");
        document.body.style.overflow = "hidden";
    }

    function closeEditRequestModal() {
        if (!editRequestModal) return;
        editRequestModal.classList.add("hidden");
        document.body.style.overflow = "";
    }

    // Expose to inline onclick handlers in template if needed
    window.openEditRequestModal = openEditRequestModal;
    window.closeEditRequestModal = closeEditRequestModal;

    // ─── Export Excel ─────────────────────────────────────────────────────────

    const exportExcelBtn = document.getElementById("export-excel-btn");

    if (exportExcelBtn) {
        exportExcelBtn.addEventListener("click", async () => {
            const fiscalYear = exportExcelBtn.dataset.fiscalYear;
            const id = exportExcelBtn.dataset.ppmpId;

            exportExcelBtn.disabled = true;
            exportExcelBtn.textContent = "Exporting…";

            try {
                const response = await fetch(`/ppmp/${id}/export/`, {
                    method: "GET",
                    headers: { "X-CSRFToken": getCookie("csrftoken") },
                });

                if (!response.ok) {
                    throw new Error(`Export failed: ${response.statusText}`);
                }

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const disposition = response.headers.get("Content-Disposition");

                let filename = `PPMP_FY${fiscalYear}.xlsx`;
                if (disposition?.includes("filename=")) {
                    filename = disposition.split("filename=")[1].replace(/"/g, "");
                }

                const anchor = document.createElement("a");
                anchor.href = url;
                anchor.download = filename;
                document.body.appendChild(anchor);
                anchor.click();
                anchor.remove();
                URL.revokeObjectURL(url);

            } catch (err) {
                console.error("Export error:", err);
                alert("Export failed. Please try again or contact support.");
            } finally {
                exportExcelBtn.disabled = false;
                exportExcelBtn.textContent = "Export to Excel";
            }
        });
    }

    // ─── Global Escape Key Handler ────────────────────────────────────────────

    document.addEventListener("keydown", e => {
        if (e.key !== "Escape") return;
        if (remarksModal?.style.display === "flex") closeRemarksModal();
        if (approveModal?.style.display === "flex") closeApproveModal();
        if (!editRequestModal?.classList.contains("hidden")) closeEditRequestModal();
    });
});