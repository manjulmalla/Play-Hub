# PlayHub 🎬

A complete, production-quality **video streaming service** built with **Django 5**, **SQLite**, **Bootstrap 5** and vanilla **HTML/CSS/JavaScript**. PlayHub is a portfolio-grade platform inspired by modern streaming sites, but entirely original.

> No React, Vue, Angular, Next.js, PostgreSQL or MongoDB. Just Django, Python, SQLite, HTML, CSS and JavaScript.

---

## ✨ Features

- **Authentication** — Register, login, logout, password reset, profile management, change password.
- **User Profiles / Channels** — Avatar, banner, bio, social links, uploaded videos, saved videos, subscriptions.
- **Video Upload** — Drag & drop upload with live progress bar, thumbnail upload, auto thumbnail generation, optional FFmpeg compression & HLS adaptive streaming, metadata extraction (duration/resolution/size).
- **Video Streaming** — HTML5 player with resume playback, playback speed, full screen, picture-in-picture, captions support, volume control and HLS quality selection when available.
- **Homepage** — Featured, Trending, Latest, Popular Categories, Continue Watching and Recommended sections.
- **Video Detail** — Player, metadata, like/dislike, share, save to playlist, report, related videos, threaded comments & replies.
- **Comments** — Add / edit / delete comments, threaded replies, like comments.
- **Categories** — Education, Technology, Gaming, Entertainment, Music, Sports, News, Movies, Tutorials, Other (seeded automatically).
- **Playlists** — Create public/private playlists, add/remove videos.
- **Watch History** — Recently watched, continue watching, clear history, resume progress.
- **Search** — By title/description/tags, filter by category, sort by newest/views/likes, with channel & category results.
- **Notifications** — New subscriber, comment, reply and like alerts.
- **Dashboard** — Creator stats (videos, views, subscribers, likes, comments, watch time, storage usage) + staff platform statistics.
- **Admin** — Manage users, videos, categories, moderate comments, feature videos, delete reported videos, view statistics.
- **Security** — Login required views, permission checks, CSRF, XSS-safe templates, SQL-injection-safe ORM, validated uploads.
- **Performance** — Pagination, optimized `select_related`/`prefetch_related`, DB indexes, LocMem caching.
- **Responsive UI** — Dark theme, red accent, animated cards, collapsible sidebar, mobile friendly.

---

## 🗂️ Project Structure

```
streamverse/
├── manage.py
├── requirements.txt
├── README.md
├── .env.example
├── streamverse/            # project config (settings, urls, wsgi, asgi)
│   └── context_processors.py
├── accounts/               # auth, profile, subscriptions, saved videos
├── categories/             # category model + views
├── videos/                 # video model, ffmpeg utils, upload, streaming
├── playlists/              # playlists + entries
├── comments/               # comments, replies, generic likes
├── history/                # watch history + progress
├── notifications/          # notifications + template tags
├── dashboard/              # creator + global stats
├── search/                 # search over videos/channels/categories
├── templates/              # Django templates (base + per-app)
├── static/                 # css/ js/ img
└── media/                  # uploaded videos / thumbnails / avatars / banners
```

---

## 🚀 Installation

### 1. Requirements
- Python 3.10+
- [FFmpeg](https://ffmpeg.org/) (optional — enables thumbnails, compression & HLS; the app runs without it)

### 2. Clone & enter the project
```bash
git clone <your-repo-url> streamverse
cd streamverse
```

### 3. Create a virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure environment (optional)
```bash
cp .env.example .env
```
Edit `.env` to set a strong `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` and optionally `FFMPEG_PATH`.
If `.env` is absent, sensible development defaults are used.

### 6. Apply migrations (this also seeds the default categories)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a superuser
```bash
python manage.py createsuperuser
```

### 8. Run the development server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** and log in with the superuser (or register a new account).

---

## 🎥 Using FFmpeg (recommended)

Install FFmpeg and make sure it is on your `PATH` (or set `FFMPEG_PATH` in `.env`).
When available, uploads automatically:
- extract video **duration / resolution / file size**,
- generate a **thumbnail** if none was uploaded,
- optionally **compress** the video to web-friendly H.264,
- build an **HLS** master playlist (`master.m3u8`) for adaptive streaming with a quality selector.

Without FFmpeg the video still uploads and plays; just provide a thumbnail manually.

---

## 🧭 URL Map

| Page                | URL                          |
|---------------------|------------------------------|
| Home                | `/`                          |
| Explore             | `/explore/`                  |
| Search              | `/search/`                  |
| Categories          | `/categories/`             |
| Video Detail        | `/watch/<slug>/`            |
| Upload              | `/upload/`                  |
| My Videos           | `/my/`                      |
| Edit Video          | `/edit/<slug>/`             |
| Report Video        | `/report/<slug>/`           |
| Playlists           | `/playlists/`               |
| Watch History       | `/history/`                 |
| Notifications       | `/notifications/`           |
| Profile / Channel   | `/accounts/profile/<user>/` |
| Settings            | `/accounts/settings/`       |
| Saved Videos        | `/accounts/saved/`          |
| Dashboard           | `/dashboard/`               |
| Platform Stats      | `/dashboard/stats/`         |
| Login / Register    | `/accounts/login/` `/accounts/register/` |
| Admin               | `/admin/`                   |

---

## 🛡️ Security Notes
- All media is served locally only when `DEBUG=True`. For production configure a real web server / object storage and set `DEBUG=False`.
- Uploads are validated by extension and size; `ALLOWED_HOSTS` is enforced.
- CSRF tokens protect every state-changing request; templates use Django's auto-escaping.

---

## 🧪 Running Tests
```bash
python manage.py check
```

---

## 📄 License
This project is provided as-is for learning and portfolio use.
