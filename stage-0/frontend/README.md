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

Deploying to GitHub Pages
-------------------------

This repository includes a GitHub Actions workflow that will publish the contents of the `stage-0/frontend/` folder to the `gh-pages` branch whenever you push to `main`.

Steps to enable:

1. Push your code to the `main` branch on GitHub.
2. Make sure the workflow file exists at `.github/workflows/gh-pages.yml` (it is included here).
3. On GitHub the action will run automatically on push to `main` and publish the `stage-0/frontend/` folder to the `gh-pages` branch.
4. In your repository Settings → Pages, set the source to the `gh-pages` branch and the root directory `/`.
5. Wait a minute and your site will be available at `https://<your-username>.github.io/<your-repo>/`.

Notes:
- The workflow uses the built-in `GITHUB_TOKEN` so no extra secret is required.
- If you want the site to publish from a different branch or path, edit `.github/workflows/gh-pages.yml` and change `publish_dir`.

Note: The repository root contains a `stage-0/` folder (this project). The workflow publishes that subfolder's `frontend/` to GitHub Pages so you can keep other projects or code at repo root.


