document.addEventListener('DOMContentLoaded', function() {
    const alertList = document.querySelectorAll('.alert');
    alertList.forEach(function(alert) {
        setTimeout(function() {
            alert.classList.add('fade');
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 3000);
    });

    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            const url = event.target.dataset.url;
            const deleteForm = document.getElementById('deleteForm');
            deleteForm.action = url;
            const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
            deleteModal.show();
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const completeLessonButtons = document.querySelectorAll('.complete-lesson');
    completeLessonButtons.forEach(button => {
        button.addEventListener('click', function() {
            const lessonId = this.dataset.lessonId;
            fetch(`/lesson/${lessonId}/complete`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.innerText = 'Completed';
                        this.classList.remove('btn-primary');
                        this.classList.add('btn-success');
                    }
                });
        });
    });
});

window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'YOUR_GA_ID');

