/* PlayHub - HTML5 video player enhancements:
   - resume playback from saved progress
   - persist progress for the "continue watching" feature
   - playback speed control and picture-in-picture
   - adaptive HLS streaming when available */

(function () {
    const video = document.getElementById('svVideo');
    if (!video) return;

    const videoId = video.getAttribute('data-video-id');
    const savedProgress = parseInt(video.getAttribute('data-progress') || '0', 10);
    const durationAttr = parseInt(video.getAttribute('data-duration') || '0', 10);
    const hlsSrc = video.getAttribute('data-hls');

    // --- Adaptive HLS setup (when a master playlist is present) ---
    if (hlsSrc) {
        if (video.canPlayType('application/vnd.apple.mpegurl')) {
            // Native HLS (Safari / iOS).
            video.src = hlsSrc;
        } else if (window.Hls && window.Hls.isSupported()) {
            const hls = new window.Hls();
            hls.loadSource(hlsSrc);
            hls.attachMedia(video);
            window.__svHls = hls;
        }
    }

    // --- Resume playback ---
    video.addEventListener('loadedmetadata', function () {
        if (savedProgress > 5 && savedProgress < (video.duration || durationAttr) - 5) {
            video.currentTime = savedProgress;
        }
    });

    // --- Persist progress periodically ---
    let lastSave = 0;
    setInterval(function () {
        if (!videoId || video.paused) return;
        const current = Math.floor(video.currentTime);
        if (current !== lastSave) {
            lastSave = current;
            fetch('/history/progress/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: new URLSearchParams({ video_id: videoId, progress: current }),
            }).catch(() => {});
        }
    }, 5000);

    // --- Playback speed control ---
    const speedSelect = document.getElementById('svSpeed');
    if (speedSelect) {
        speedSelect.addEventListener('change', function () {
            video.playbackRate = parseFloat(this.value);
        });
    }

    // --- Picture-in-picture ---
    const pipBtn = document.getElementById('svPip');
    if (pipBtn && document.pictureInPictureEnabled) {
        pipBtn.addEventListener('click', function () {
            if (document.pictureInPictureElement) {
                document.exitPictureInPicture();
            } else {
                video.requestPictureInPicture().catch(() => {});
            }
        });
    } else if (pipBtn) {
        pipBtn.style.display = 'none';
    }

    // --- Quality selection (HLS levels) ---
    const qualityMenu = document.getElementById('svQualityMenu');
    if (qualityMenu && window.__svHls) {
        const hls = window.__svHls;
        hls.on(hls.Events.MANIFEST_PARSED, function () {
            const levels = hls.levels;
            qualityMenu.innerHTML = '';
            const auto = document.createElement('button');
            auto.className = 'dropdown-item';
            auto.textContent = 'Auto';
            auto.addEventListener('click', () => { hls.currentLevel = -1; });
            qualityMenu.appendChild(auto);
            levels.forEach((lvl, idx) => {
                const btn = document.createElement('button');
                btn.className = 'dropdown-item';
                btn.textContent = (lvl.height || '?') + 'p';
                btn.addEventListener('click', () => { hls.currentLevel = idx; });
                qualityMenu.appendChild(btn);
            });
        });
    } else if (qualityMenu) {
        qualityMenu.innerHTML = '<span class="dropdown-item-text sv-muted">Auto</span>';
    }

    function getCookie(name) {
        let value = null;
        if (document.cookie && document.cookie !== '') {
            document.cookie.split(';').forEach((c) => {
                const part = c.trim();
                if (part.startsWith(name + '=')) {
                    value = decodeURIComponent(part.substring(name.length + 1));
                }
            });
        }
        return value;
    }
})();
