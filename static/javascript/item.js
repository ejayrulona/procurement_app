document.addEventListener('DOMContentLoaded', () => {
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
        // Used later when form validation is included
        // objectExpenditureInput.addEventListener('change', () => {
        //     if (objectExpenditureInput.value) {
        //         document.querySelector('.object-code-error')?.remove();
        //     }

        //     if (!objectExpenditureInput.value) {
        //         if (objectCodeInput) objectCodeInput.value = '';
        //     }
        // });

        objectExpenditureInput.addEventListener("input", event => {
            const selectedOption = Array.from(objectExpenditureList.querySelectorAll('option'))
                .find(option => option.value === objectExpenditureInput.value);
                
            if (selectedOption) {
                currentObjectExpenditureId = selectedOption.dataset.id;
                
                if (objectCodeInput && event.isTrusted ) objectCodeInput.value = "";
                
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

    // Used later when form validation is included
    // objectCodeInput?.addEventListener('focus', () => {
    //     document.querySelector('.object-code-error')?.remove();

    //     if (!objectExpenditureInput.value) {
    //         let errorElement = document.createElement('p');
    //         errorElement.classList.add('object-code-error', 'text-red-500', 'text-xs', 'mt-1');
    //         errorElement.innerText = 'Please select a object of expenditure first.';
    //         objectCodeInput.insertAdjacentElement('afterend', errorElement);
    //     }
    // });

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

                    if (objectCodeInput && objectCodeInput.value ) {
                        const event = new Event('input', {bubbles: true});
                        objectCodeInput.dispatchEvent(event);
                    }
                }
            });
    }

    if (objectCodeInput) {
        // Used later when form validation is included
        // objectCodeInput.addEventListener('change', () => {
        //     if (objectCodeInput.value) {
        //         document.querySelector('.item-code-error')?.remove();
        //     }

        //     if (!objectCodeInput.value) {
        //         if (objectCodeInput) objectCodeInput.value = '';
        //     }
        // });

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

                    if (itemCodeInput && itemCodeInput.value ) {
                        const event = new Event('input', {bubbles: true});
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

    if(itemCodeInput){
        itemCodeInput.addEventListener('input', () => {
            autoGenerateGeneralDescription(findMatch(itemCodeInput.value));        
        });
    }

    if(itemCodeInput.value){
        autoGenerateGeneralDescription(findMatch(itemCodeInput.value));
    }
});