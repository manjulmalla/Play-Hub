/* PlayHub - global client-side behaviour. */

// --- Sidebar toggle (mobile) -------------------------------------
(function () {
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (!toggle || !sidebar) return;

    // Create a backdrop element for mobile navigation.
    const backdrop = document.createElement('div');
    backdrop.className = 'sv-sidebar-backdrop';
    document.body.appendChild(backdrop);

    function openSidebar() {
        sidebar.classList.add('open');
        backdrop.classList.add('show');
    }
    function closeSidebar() {
        sidebar.classList.remove('open');
        backdrop.classList.remove('show');
    }

    toggle.addEventListener('click', () => {
        if (sidebar.classList.contains('open')) closeSidebar();
        else openSidebar();
    });
    backdrop.addEventListener('click', closeSidebar);
})();

// --- CSRF helper -------------------------------------------------
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const parts = document.cookie.split(';');
        for (let i = 0; i < parts.length; i++) {
            const part = parts[i].trim();
            if (part.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(part.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- Generic AJAX post ------------------------------------------
function svPost(url, body) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body || {}),
    }).then((r) => r.json());
}

// --- Like a video -----------------------------------------------
document.addEventListener('click', function (e) {
    const likeBtn = e.target.closest('[data-like-video]');
    if (likeBtn) {
        e.preventDefault();
        const slug = likeBtn.getAttribute('data-like-video');
        svPost('/like/' + slug + '/').then((data) => {
            const icon = likeBtn.querySelector('i');
            const label = likeBtn.querySelector('.sv-like-count');
            if (data.liked) {
                likeBtn.classList.add('active');
                if (icon) icon.className = 'bi bi-heart-fill';
            } else {
                likeBtn.classList.remove('active');
                if (icon) icon.className = 'bi bi-heart';
            }
            if (label) label.textContent = data.like_count;
        });
    }

    // --- Save / bookmark a video ---
    const saveBtn = e.target.closest('[data-save-video]');
    if (saveBtn) {
        e.preventDefault();
        const slug = saveBtn.getAttribute('data-save-video');
        svPost('/save/' + slug + '/').then((data) => {
            const icon = saveBtn.querySelector('i');
            if (data.saved) {
                saveBtn.classList.add('active');
                if (icon) icon.className = 'bi bi-bookmark-fill';
            } else {
                saveBtn.classList.remove('active');
                if (icon) icon.className = 'bi bi-bookmark';
            }
        });
    }

    // --- Like a comment ---
    const likeComment = e.target.closest('[data-like-comment]');
    if (likeComment) {
        e.preventDefault();
        const id = likeComment.getAttribute('data-like-comment');
        svPost('/comments/like/' + id + '/').then((data) => {
            const label = likeComment.querySelector('.sv-like-count');
            if (label) label.textContent = data.like_count;
            likeComment.classList.toggle('active', data.liked);
        });
    }
});
