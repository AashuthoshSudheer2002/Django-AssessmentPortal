    document.addEventListener('DOMContentLoaded', function () {
        const candidateSelect = document.getElementById('id_candidate');
        const sectionSelect = document.getElementById('id_section');

        candidateSelect.addEventListener('change', function () {
            const candidateId = this.value;

            fetch(`/ajax/get-sections/?candidate_id=${candidateId}`)
                .then(response => response.json())
                .then(data => {
                    sectionSelect.innerHTML = '';

                    const defaultOption = document.createElement('option');
                    defaultOption.value = '';
                    defaultOption.text = '---------';
                    sectionSelect.appendChild(defaultOption);

                    data.sections.forEach(section => {
                        const option = document.createElement('option');
                        option.value = section.id;
                        option.text = section.title;
                        sectionSelect.appendChild(option);
                    });
                });
        });
    });