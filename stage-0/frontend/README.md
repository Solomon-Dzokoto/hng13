# Profile Card — Frontend Stage 0

Small semantic, accessible, responsive profile card built with plain HTML/CSS/vanilla JS.

Files:
- `index.html` — markup with required data-testids
- `styles.css` — responsive styles, primary color yellow (no gradients)
- `script.js` — avatar URL/upload handling and time display

How to run locally:
1. Open `frontend/index.html` in your browser (double-click or serve with a static server).

Optional (serve with Python):
```bash
cd frontend
python3 -m http.server 8000
# then open http://localhost:8000
```

Notes:
- All required data-testid attributes are present exactly as specified in the task.
- Primary color is yellow and no gradients are used.

Deploying to Netlify
--------------------

This is a static site. You can deploy it to Netlify in two ways:

1) Quick (connect GitHub repo):
	- Push your repository to GitHub.
	- In Netlify, click "New site from Git" and connect your GitHub repo.
	- For the "Publish directory" set: `frontend` (this tells Netlify to serve files from the `frontend` folder).
	- Leave the build command blank (it's a static site) and deploy.

2) Manual (drag & drop):
	- Build a ZIP of the `frontend` folder (or open it) and drag the contents into the Netlify Sites drag-and-drop area.

Local testing
-------------
To emulate a simple static server locally:

```bash
cd frontend
python3 -m http.server 8000
# open http://localhost:8000
```

Notes about `netlify.toml`
------------------------
- A minimal `netlify.toml` is included. Because this project is a plain static site there are no build steps.

