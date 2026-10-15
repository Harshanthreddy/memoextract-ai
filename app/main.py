import os
import io
import time
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

# Ensure project root in sys.path
import sys
from pathlib import Path
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.utils import image_to_base64, get_llm_result
from app.models import Extraction
from frontend.db import (
    init_db,
    save_extracted_document,
    get_all_documents,
    get_dashboard_stats,
    delete_document,
    clear_all_documents,
)
from frontend.validator import validate_marksheet

load_dotenv()

app = FastAPI(title="Marksheet AI Backend API", version="2.0.0")

# Enable CORS for Next.js frontend (e.g. http://localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite database
init_db()


def get_groq_client(custom_key: Optional[str] = None):
    api_key = (custom_key or os.getenv("GROQ_API_KEY") or "").strip()
    if not api_key:
        return None
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except Exception:
        return None


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Marksheet AI Backend API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    groq_ready = bool(get_groq_client())
    return {
        "status": "healthy",
        "groq_configured": groq_ready,
        "database": "sqlite_connected"
    }


@app.get("/stats")
def get_stats():
    return get_dashboard_stats()


@app.get("/history")
def get_history(limit: int = 50):
    return get_all_documents(limit=limit)


@app.delete("/history/{doc_id}")
def remove_history(doc_id: int):
    success = delete_document(doc_id)
    return {"success": success, "deleted_id": doc_id}


@app.post("/extract")
async def extract(
    file: UploadFile = File(...),
    api_key: Optional[str] = Form(None),
    model: Optional[str] = Form("llama-3.2-11b-vision-preview")
):
    if file.size and file.size > 25 * 1024 * 1024:
        raise HTTPException(400, "File too large (Max 25MB)")

    bytes_data = await file.read()
    start_time = time.time()

    # 1. Convert input file (image or PDF) to PIL Image
    images = []
    try:
        if "image" in (file.content_type or "") or any(file.filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            img = Image.open(io.BytesIO(bytes_data))
            images = [img]
        elif "pdf" in (file.content_type or "") or (file.filename and file.filename.lower().endswith(".pdf")):
            try:
                import pypdfium2 as pdfium
                pdf = pdfium.PdfDocument(bytes_data)
                images = [page.render(scale=2).to_pil() for page in pdf]
            except Exception:
                from pdf2image import convert_from_bytes
                images = convert_from_bytes(bytes_data)
        else:
            # Fallback attempt as image
            img = Image.open(io.BytesIO(bytes_data))
            images = [img]
    except Exception as e:
        raise HTTPException(400, f"Cannot process file: {str(e)}")

    if not images:
        raise HTTPException(400, "No readable pages found in file")

    # 2. Extract with Groq Vision if client available, or fallback
    client = get_groq_client(api_key)
    result_dict = None
    engine_used = "Groq Vision AI"

    if client:
        try:
            base64_img = image_to_base64(images[0])
            result_dict = get_llm_result(client, base64_img, model=model)
        except Exception as e:
            print(f"Groq Vision failed: {e}, falling back to offline engine")
            result_dict = None

    if not result_dict:
        # Offline Extractor fallback
        from frontend.extractors import extract_offline_engine
        result_dict = extract_offline_engine(bytes_data, file.filename or "marksheet")
        engine_used = "Offline Engine"

    # Validate marksheet
    validations = validate_marksheet(result_dict)
    warnings = [f"{v['rule']}: {v['message']}" for v in validations if v.get("status") in ["WARNING", "ERROR"]]
    status = "NEEDS_REVIEW" if warnings else "SUCCESS"
    elapsed = round(time.time() - start_time, 2)

    # Save to SQLite Database
    doc_id = None
    try:
        doc_id = save_extracted_document(
            filename=file.filename or "marksheet.jpg",
            file_bytes=bytes_data,
            engine=engine_used,
            data=result_dict,
            validation_warnings=warnings,
            processing_time_sec=elapsed,
            status=status
        )
    except Exception as err:
        print(f"DB save warning: {err}")

    return {
        "success": True,
        "document_id": doc_id,
        "engine": engine_used,
        "processing_time_sec": elapsed,
        "status": status,
        "warnings": warnings,
        "data": result_dict
    }
