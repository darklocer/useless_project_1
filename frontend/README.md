# WigCheck Frontend v2

A completely new React/Vite frontend for the current Wig Checker backend.

## Backend expected

The frontend calls:

`POST http://127.0.0.1:8000/analyze`

and expects JSON containing:

- `wig_probability`
- `natural_probability`
- `result`
- `strongest_signal`
- `signal_confidence`

## Install and run

From this folder:

```bash
npm install
npm run dev
```

Then open the Vite URL, normally:

`http://localhost:5173`

Keep FastAPI running separately:

```bash
conda activate wigchecker
uvicorn backend.main:app --reload
```

No `Content-Type` header is manually set for the upload request; the browser handles the multipart boundary.