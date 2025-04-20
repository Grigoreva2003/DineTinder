document.addEventListener('DOMContentLoaded', function () {
    const modifyBtn = document.querySelector('.modify-name');
    const nameInput = document.querySelector('.user-name');

    function performNameModification() {
        const modifiedName = nameInput.value.trim();

        if (modifiedName === '') {
            return;
        }

        const url = `/users/modify/?name=${modifiedName}`;
        console.log(url);

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                window.location.reload();
            })
            .catch(error => {
                console.error('Error modifying name:', error);

                nameInput.style.backgroundColor = 'rgba(255, 104, 105, 0.5)';
                // Reset the color after 3 seconds
                setTimeout(() => {
                    nameInput.style.backgroundColor = ''; // Reset to default
                }, 3000);
            });
    }

    modifyBtn.addEventListener("click", performNameModification);
});