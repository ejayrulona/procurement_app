document.addEventListener("DOMContentLoaded", () => {
    // Create Final PPMP Button Modal
    const createFinalAPPBtn = document.getElementById('create-final-app-btn');
    const createFinalAPPModal = document.getElementById('create-final-app-modal');
    const cancelCreateFinalAPPBtn = document.getElementById('cancel-create-final-app-btn');

    function openCreatePpmpModal() {
        createFinalAPPModal.classList.remove('hidden');
    }
    
    function closeCreatePpmpModal() {
        createFinalAPPModal.classList.add('hidden');
    }
    
    if (createFinalAPPBtn) {
        createFinalAPPBtn.addEventListener('click', openCreatePpmpModal);
    }
    
    if (cancelCreateFinalAPPBtn) {
        cancelCreateFinalAPPBtn.addEventListener('click', closeCreatePpmpModal);
    }
    
    if (createFinalAPPModal) {
        createFinalAPPModal.addEventListener('click', event => {
            if (event.target === createFinalAPPModal) {
                closeCreatePpmpModal();
            }
        });
    }

    const modal = document.getElementById("scheduleModal");
    const openBtn = document.getElementById("add-schedule-btn");
    const closeBtn = document.getElementById("closeScheduleModal");
    const cancelBtn = document.getElementById("cancelScheduleBtn");
    const saveBtn = document.getElementById("saveScheduleBtn");
    const scheduleError = document.getElementById("scheduleError");
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    const appId = document.getElementById("appData").dataset.appId;

    const adInput = document.getElementById("scheduleAdvertisementDate");
    const subInput = document.getElementById("scheduleSubmissionDate");
    const noaInput = document.getElementById("scheduleNoticeOfAwardDate");
    const csInput = document.getElementById("scheduleContractSigningDate");

    function openModal() {
        scheduleError.classList.add("hidden");
        scheduleError.textContent = "";
        modal.classList.remove("hidden");
        modal.classList.add("flex");
    }

    function closeModal() {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
    }

    openBtn.addEventListener("click", openModal);
    closeBtn.addEventListener("click", closeModal);
    cancelBtn.addEventListener("click", closeModal);

    // Close on backdrop click
    modal.addEventListener("click", (e) => {
        if (e.target === modal) closeModal();
    });

    function validateDates() {
        const dates = [
            { value: adInput.value, label: "Advertisement" },
            { value: subInput.value, label: "Submission" },
            { value: noaInput.value, label: "Notice of Award" },
            { value: csInput.value, label: "Contract Signing" },
        ];

        // Only validate order among filled dates
        const filled = dates.filter(date => date.value);

        for (let i = 1; i < filled.length; i++) {
            if (filled[i].value <= filled[i - 1].value) {
                return `${filled[i].label} date must be after ${filled[i - 1].label} date.`;
            }
        }

        return null;
    }

    saveBtn.addEventListener("click", () => {
        scheduleError.classList.add("hidden");
        scheduleError.textContent = "";

        const validationError = validateDates();
        if (validationError) {
            scheduleError.textContent = validationError;
            scheduleError.classList.remove("hidden");
            return;
        }

        const payload = {
            advertisement_date: adInput.value || null,
            submission_date: subInput.value || null,
            notice_of_award_date: noaInput.value || null,
            contract_signing_date: csInput.value || null,
        };

        fetch(`/ppmp/app/${appId}/add-schedule/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify(payload),
        })
            .then(res => res.json())
            .then(data => {
                if (data.app_id) {
                    closeModal();
                    window.location.reload();
                } else {
                    scheduleError.textContent = data.error || "Failed to save. Please try again.";
                    scheduleError.classList.remove("hidden");
                }
            })
            .catch(() => {
                scheduleError.textContent = "An unexpected error occurred. Please try again.";
                scheduleError.classList.remove("hidden");
            });
    });
});