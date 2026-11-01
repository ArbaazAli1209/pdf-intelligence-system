# Deployment Guide (free options)

> No platform is permanently free. The limits below were checked in October 2026 and can change. Re-check each provider's pricing page before relying on them.

## Read this first: two real constraints
1. **Storage is not persistent on Render's free web service.** Render states that free web services have an ephemeral filesystem: local files (including SQLite databases and uploaded/vector files) are lost on redeploy, restart or spin-down, and persistent disks are not available on the free tier. In this app that means **all uploaded documents, vectors and chats disappear** after the service sleeps or restarts. This is fine for a short demo; it is not fine for real use.
2. **RAM.** Render free web services have 512 MB RAM and 0.1 CPU. `sentence-transformers` + PyTorch will very likely not fit in 512 MB. Options: (a) set `EMBEDDING_BACKEND=hash` on the free tier (works, but only lexical matching, lower quality); (b) run the full model locally for your viva and use the hosted version only as a lightweight demo; (c) pay for a larger instance. I could not test memory use on Render from the development sandbox.

Also expect **cold starts**: a free service spins down after 15 minutes of no traffic and takes roughly a minute to wake up.

## Practical workarounds for persistence
- **Best for the minor project:** demo locally (full quality, persistent), and deploy the hosted copy only as a portfolio link with a clear "demo data resets" notice.
- Re-upload the sample PDF after each wake-up (the app handles an empty database).
- A real fix needs persistent storage (paid disk, or moving metadata to an external free Postgres and vectors to object storage). That is **not implemented** in this version.

## Environments
| | Local | Production |
|---|---|---|
| Backend `.env` | `CORS_ORIGINS=http://localhost:5173` | `CORS_ORIGINS=https://<your-app>.vercel.app` |
| Frontend `.env` | `VITE_API_URL=http://localhost:8000` | `VITE_API_URL=https://<your-service>.onrender.com` |
| Embeddings | `sentence-transformers` | `hash` on Render free (see above) |

## 1. Push to GitHub
```powershell
cd pdf-intelligence-system
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```
Check that no `.env` file was committed.

## 2. Backend on Render (free web service)
1. Sign in at https://render.com with GitHub → **New → Web Service** → select your repo.
2. Settings: **Root Directory** `backend` · **Runtime** Python 3 · **Build Command** `pip install -r requirements.txt` · **Start Command** `uvicorn app.main:app --host 0.0.0.0 --port $PORT` · **Instance type** Free.
3. For the free tier, use a lighter requirements install to avoid PyTorch: set Build Command to
   `pip install fastapi "uvicorn[standard]" python-multipart pydantic pymupdf numpy faiss-cpu httpx python-dotenv`
   and set `EMBEDDING_BACKEND=hash`.
4. **Environment** tab → add variables: `CORS_ORIGINS`, `EMBEDDING_BACKEND`, `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, `MAX_UPLOAD_MB` (use the same names as `backend/.env.example`). Set `PYTHON_VERSION` to `3.11.9` if the build picks an incompatible version.
5. Deploy and copy the service URL.

## 3. Frontend on Vercel
1. https://vercel.com → **Add New → Project** → import the repo.
2. **Root Directory** `frontend`; framework preset Vite (build `npm run build`, output `dist`).
3. **Environment Variables:** `VITE_API_URL` = your Render URL (no trailing slash).
4. Deploy. `frontend/vercel.json` makes React Router paths work on refresh.
5. Go back to Render and set `CORS_ORIGINS` to your Vercel URL (add preview URLs comma-separated if needed), then redeploy.

## 4. Verify the deployment
1. Open `https://<service>.onrender.com/api/health` → JSON with `"status": "ok"` (allow ~1 minute after sleep).
2. Open `https://<service>.onrender.com/docs` and try the endpoints.
3. Open the Vercel URL: no red "Cannot reach the backend" banner; sidebar shows the answer mode.
4. Upload `backend/tests/sample_data/sample.pdf`, wait for "Ready", ask "What efficiency do silicon solar panels reach?" and confirm a page-1 source appears.
5. If the browser console shows a CORS error, fix `CORS_ORIGINS`.

## Privacy note
With a free LLM tier, document excerpts are sent to the provider and may be used to improve their products. Use extractive mode for sensitive documents.
