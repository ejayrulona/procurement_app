document.addEventListener("DOMContentLoaded", () => {

    // ── Tabs ──────────────────────────────────────────────────────

    const tabs = document.querySelectorAll(".tab-btn");

    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            tabs.forEach((t) => t.classList.remove("active"));
            tab.classList.add("active");

            const selected   = tab.dataset.tab;
            const items      = document.querySelectorAll(".notification-item");
            const emptyState = document.getElementById("notification-empty");
            let visibleCount = 0;

            items.forEach((item) => {
                const isRead    = item.dataset.read === "true";
                const shouldShow =
                    selected === "all" ||
                    (selected === "unread" && !isRead) ||
                    (selected === "read"   && isRead);

                item.classList.toggle("hidden", !shouldShow);
                if (shouldShow) visibleCount++;
            });

            if (emptyState) emptyState.classList.toggle("hidden", visibleCount > 0);
        });
    });


    // ── Delete single notification ────────────────────────────────

    const deleteModal  = document.getElementById("delete-confirm");
    const deleteForm   = document.getElementById("delete-confirm-form");
    const cancelDelete = document.getElementById("btn-cancel-delete");

    if (deleteModal && deleteForm && cancelDelete) {
        document.getElementById("notification-list").addEventListener("click", (e) => {
            const deleteBtn = e.target.closest(".btn-delete");
            if (!deleteBtn) return;

            deleteForm.action = deleteBtn.dataset.deleteUrl;
            deleteModal.classList.remove("hidden");
            deleteModal.classList.add("flex");
            cancelDelete.focus();
        });

        cancelDelete.addEventListener("click", () => {
            deleteModal.classList.add("hidden");
            deleteModal.classList.remove("flex");
            deleteForm.action = "";
        });

        deleteModal.addEventListener("click", (e) => {
            if (e.target === deleteModal) {
                deleteModal.classList.add("hidden");
                deleteModal.classList.remove("flex");
                deleteForm.action = "";
            }
        });
    }


    // ── Clear all notifications ───────────────────────────────────

    const clearBtn     = document.getElementById("btn-clear-all");
    const clearModal   = document.getElementById("clear-all-confirm");
    const cancelClear  = document.getElementById("btn-cancel-clear");

    if (clearBtn && clearModal && cancelClear) {
        clearBtn.addEventListener("click", () => {
            clearModal.classList.remove("hidden");
            clearModal.classList.add("flex");
            cancelClear.focus();
        });

        cancelClear.addEventListener("click", () => {
            clearModal.classList.add("hidden");
            clearModal.classList.remove("flex");
        });

        clearModal.addEventListener("click", (e) => {
            if (e.target === clearModal) {
                clearModal.classList.add("hidden");
                clearModal.classList.remove("flex");
            }
        });
    }

});