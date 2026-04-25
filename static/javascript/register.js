import { initializeTogglePassword } from "./utils/togglePassword.js";

document.addEventListener('DOMContentLoaded', () => {
    initializeTogglePassword();

    const collegeOfficeInputElement = document.getElementById('college-office-dropdown');
    const datalist = document.getElementById('college-office-list');
    const previewImage = document.getElementById('college-photo-preview');
    const placeholder = document.getElementById('photo-placeholder');
    const noPhotoHint = document.getElementById('no-photo-hint');
    const photoHint = document.getElementById('photo-hint');

    function populateCollegeFields(match) {
        if (match) {
            document.getElementById('college-code').value = match.dataset.code;
            document.getElementById('college-type').value = match.dataset.type;
            document.getElementById('college-campus').value = match.dataset.campus;
            document.getElementById('college-address').value = match.dataset.address;

            const photoUrl = match.dataset.photo;

            if (photoUrl) {
                previewImage.src = photoUrl;
                previewImage.classList.remove('hidden');
                placeholder.classList.add('hidden');
                noPhotoHint.classList.add('hidden');
                photoHint.classList.remove('hidden');
            } else {
                previewImage.src = '#';
                previewImage.classList.add('hidden');
                placeholder.classList.remove('hidden');
                noPhotoHint.classList.remove('hidden');
                photoHint.classList.add('hidden');
            }
        } else {
            document.getElementById('college-code').value = '';
            document.getElementById('college-type').value = '';
            document.getElementById('college-campus').value = '';
            document.getElementById('college-address').value = '';

            previewImage.src = '#';
            previewImage.classList.add('hidden');
            placeholder.classList.remove('hidden');
            noPhotoHint.classList.add('hidden');
            photoHint.classList.remove('hidden');
        }
    }

    function findMatch(value) {
        const options = datalist.querySelectorAll('option');
        return Array.from(options).find(
            option => option.value.toLowerCase() === value.toLowerCase()
        ) || null;
    }

    collegeOfficeInputElement.addEventListener('input', () => {
        populateCollegeFields(findMatch(collegeOfficeInputElement.value));        
    });

    if(collegeOfficeInputElement.value){
        populateCollegeFields(findMatch(collegeOfficeInputElement.value));
    }
});