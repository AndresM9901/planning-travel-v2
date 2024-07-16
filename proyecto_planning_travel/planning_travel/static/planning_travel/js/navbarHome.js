const btnDropdown = document.querySelector('.btn-profile');
const dropdown = document.querySelector('.dropdown-user');

btnDropdown.addEventListener('click', () => {
    dropdown.classList.toggle('active');
});

window.addEventListener('click', (event) => {
    if (!event.target.closest('.btn-dropdown')) {
        dropdown.classList.remove('active');
    }
});

document.querySelector('.burger').addEventListener('click', function() {
    this.classList.toggle('change');
    document.querySelector('.responsive-bar').classList.toggle('open');
});