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
});