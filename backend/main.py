from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import tempfile
import os

from Ai.wigscore import analyze_clip


app = FastAPI(title="Wig Checker API")


# Allow React frontend to communicate with FastAPI
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_raw.split(",") if o.strip()]
if not allowed_origins:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False if "*" in allowed_origins else True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Wig Checker API is running 😂"
    }


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    # Check whether uploaded file is an image
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload an image."
        )

    suffix = Path(file.filename or "").suffix or ".jpg"

    temp_path = None

    try:
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp:

            temp.write(await file.read())
            temp_path = temp.name

        print(f"Analyzing image: {file.filename}")

        # Run CLIP Wig Checker
        result = analyze_clip(
            temp_path,
            show=False
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        print(f"Analysis error: {e}")

        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

    finally:

        # Delete temporary image
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)