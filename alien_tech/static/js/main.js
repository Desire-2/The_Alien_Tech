document.addEventListener('DOMContentLoaded', function() {
    const notificationBell = document.querySelector('#notification-bell');
    const notificationsDropdown = document.querySelector('#notifications-dropdown');

    notificationBell.addEventListener('click', function() {
        fetch('/notifications')
            .then(response => response.json())
            .then(data => {
                notificationsDropdown.innerHTML = '';
                data.notifications.forEach(notification => {
                    const li = document.createElement('li');
                    li.className = 'dropdown-item';
                    li.innerText = notification.message;
                    notificationsDropdown.appendChild(li);
                });
            });
    });
});

$(document).ready(function() {
    $.get('/notifications', function(data) {
        let notificationCount = data.notifications.length;
        $('#notificationCount').text(notificationCount);
        let notificationList = $('#notificationList');
        notificationList.empty();
        if (notificationCount > 0) {
            data.notifications.forEach(function(notification) {
                notificationList.append('<a class="dropdown-item" href="#">' + notification + '</a>');
            });
        } else {
            notificationList.append('<a class="dropdown-item" href="#">No new notifications</a>');
        }
    });
});