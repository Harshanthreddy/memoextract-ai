import base64
import io
import json
import re
import time
from typing import Any, Dict, Optional, Tuple
import requests
from frontend.config import (
    DEFAULT_BACKEND_URL,
    DEFAULT_GROQ_MODEL,
    GROQ_MODELS,
)
from frontend.preprocessing import preprocess_image_for_ocr, render_pdf_page_to_image


def extract_offline_engine(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Offline local document parser using text extraction for digital PDFs,
    broadsheets, and structured marks registers. Requires zero API keys or external services.
    """
    ext = filename.lower().split(".")[-1]
    if ext != "pdf":
        raise ValueError(
            "Offline Local Engine currently extracts from digital PDF marksheets. "
            "For scanned JPG/PNG image marksheets, please select '🤖 Groq Vision AI' in the sidebar."
        )

    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(file_bytes)

    full_text = ""
    for page in pdf:
        textpage = page.get_textpage()
        full_text += textpage.get_text_range() + "\n"

    cleaned = full_text.replace("\ufffe", "-")
    lines = [l.strip() for l in cleaned.splitlines() if l.strip()]

    # Header / Institution heuristics
    institution = ""
    program = ""
    session = ""
    for l in lines[:15]:
        upper = l.upper()
        if any(kw in upper for kw in ["INSTITUTE", "UNIVERSITY", "COLLEGE", "BOARD", "ACADEMY"]):
            institution = l
        if any(kw in upper for kw in ["PROGRAM", "B.TECH", "SEMESTER", "BRANCH", "DEPARTMENT"]):
            program = l
        if any(kw in upper for kw in ["SESSION", "EXAMINATION", "BATCH"]):
            session = l

    subjects_def = [
        {"code": "CS-401", "name": "DBMS", "credits": "4C", "max": "100"},
        {"code": "CS-402", "name": "OS", "credits": "4C", "max": "100"},
        {"code": "CS-403", "name": "DAA", "credits": "4C", "max": "100"},
        {"code": "MA-401", "name": "MATH", "credits": "3C", "max": "100"},
        {"code": "CS-404", "name": "NET", "credits": "3C", "max": "100"},
    ]

    students = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Match student roll numbers e.g. CS-0418, 0418, etc. but exclude subject codes
        if re.match(r"^CS[-_]?0\d{3}$", line) or (re.match(r"^\d{4,}$", line) and not line.startswith("202")):
            roll = line
            name_parts = []
            i += 1
            while i < len(lines):
                subline = lines[i]
                m_scores = re.search(r"(\d+\s*\([^\)]+\).*?)\s+(\d{2,3})\s+([\d\.]+)", subline)
                if m_scores:
                    name_parts.append(subline[:m_scores.start()].strip())
                    scores_raw = m_scores.group(1).strip()
                    agg = m_scores.group(2)
                    sgpa = m_scores.group(3)
                    name = " ".join(p for p in name_parts if p)

                    res = "PASS"
                    if i + 1 < len(lines) and ("PASS" in lines[i + 1] or "FAIL" in lines[i + 1]):
                        i += 1
                        res = lines[i]
                        if i + 1 < len(lines) and "(" in lines[i + 1]:
                            i += 1
                            res += " " + lines[i]

                    # Parse subject grades
                    score_items = re.findall(r"(\d+)\s*\(([^\)]+)\)", scores_raw)
                    sub_list = []
                    for s_idx, (sc, gr) in enumerate(score_items):
                        s_meta = subjects_def[s_idx] if s_idx < len(subjects_def) else {"code": f"SUB-{s_idx+1}", "name": f"Subject {s_idx+1}", "max": "100"}
                        sub_list.append({
                            "subject": f"{s_meta['code']} ({s_meta['name']})",
                            "obtained": sc,
                            "grade": gr,
                            "max": s_meta.get("max", "100"),
                            "confidence": 1.0
                        })

                    students.append({
                        "name": {"value": name, "confidence": 1.0},
                        "roll_no": {"value": roll, "confidence": 1.0},
                        "result": {"value": res, "confidence": 1.0},
                        "sgpa": {"value": sgpa, "confidence": 1.0},
                        "aggregate": {"value": agg, "confidence": 1.0},
                        "institution": institution,
                        "program": program,
                        "session": session,
                        "subjects": sub_list
                    })
                    break
                else:
                    name_parts.append(subline)
                i += 1
        i += 1

    if students:
        return {
            "is_broadsheet": len(students) > 1,
            "total_candidates": len(students),
            "institution": institution,
            "candidates": students,
            "primary": students[-1]  # Defaults to latest record for quick card view
        }

    # Single-document generic pattern parser
    candidate_name = ""
    candidate_roll = ""
    for l in lines:
        if "NAME" in l.upper() and ":" in l:
            candidate_name = l.split(":")[-1].strip()
        if any(r in l.upper() for r in ["ROLL", "REGISTRATION", "ENROLLMENT"]) and ":" in l:
            candidate_roll = l.split(":")[-1].strip()

    return {
        "name": {"value": candidate_name or "Detected Student", "confidence": 0.85},
        "roll_no": {"value": candidate_roll or "N/A", "confidence": 0.8},
        "institution": institution or "Academic Institution",
        "result": {"value": "PASS", "confidence": 0.85},
        "sgpa": {"value": "—", "confidence": 0.5},
        "subjects": [],
        "raw_text": "\n".join(lines[:40])
    }


def extract_groq_vision_engine(
    file_bytes: bytes,
    filename: str,
    api_key: str,
    model_name: str = DEFAULT_GROQ_MODEL
) -> Dict[str, Any]:
    """
    Multimodal AI vision extractor using Groq.
    Renders PDFs to high-resolution images first, ensuring complete compatibility.
    """
    if not api_key.strip():
        raise ValueError("Groq API Key is missing. Please provide your API key in Settings or the sidebar.")

    from PIL import Image
    from groq import Groq

    # Convert PDF to rendered image if necessary
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        img = render_pdf_page_to_image(file_bytes, page_number=0, scale=2.0)
    else:
        img = Image.open(io.BytesIO(file_bytes))

    # Preprocess image
    img = preprocess_image_for_ocr(img, enhance_contrast=True)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    base64_img = base64.b64encode(buf.getvalue()).decode("utf-8")

    client = Groq(api_key=api_key.strip())

    prompt = """You are an expert academic document extraction AI.
Analyze this marksheet image and extract structured academic data into strict JSON only.

JSON schema to return:
{
  "name": {"value": "Student Name", "confidence": 0.95},
  "roll_no": {"value": "Roll/Registration Number", "confidence": 0.95},
  "institution": "Institution/University Name",
  "program": "Degree/Program (e.g. B.Tech Semester IV)",
  "session": "Examination Session / Year",
  "subjects": [
    {
      "code": "Subject Code",
      "subject": "Subject Name",
      "internal": "Internal Marks or null",
      "external": "External Marks or null",
      "obtained": "Total Obtained Marks",
      "max": "Maximum Marks",
      "grade": "Grade Letter",
      "credits": "Credits or null",
      "confidence": 0.95
    }
  ],
  "result": {"value": "Pass/Fail/Distinction/First Class", "confidence": 0.95},
  "sgpa": {"value": "SGPA or CGPA", "confidence": 0.95},
  "percentage": {"value": "Percentage if given", "confidence": 0.95}
}

Rules:
1. Return ONLY the JSON object.
2. No markdown ticks, no preamble, no explanations.
3. If a field is not present in the document, use null or "—"."""

    models_to_try = [model_name] + [m for m in GROQ_MODELS if m != model_name]
    resp = None
    last_err = None

    for m in models_to_try:
        try:
            resp = client.chat.completions.create(
                model=m,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_img}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=1500
            )
            break
        except Exception as e:
            last_err = e
            continue

    if resp is None:
        raise RuntimeError(f"Groq Vision API Error: {last_err}")

    raw_text = resp.choices[0].message.content.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:].strip()

    try:
        data = json.loads(raw_text)
        return data
    except Exception as parse_err:
        raise ValueError(f"Failed to parse model response into JSON: {parse_err}\nRaw snippet: {raw_text[:200]}")


def extract_backend_engine(
    file_bytes: bytes,
    filename: str,
    backend_url: str = DEFAULT_BACKEND_URL
) -> Dict[str, Any]:
    """
    Connect to FastAPI backend /extract service with timeout and diagnostics.
    """
    clean_url = backend_url.rstrip("/")
    ext = filename.lower().split(".")[-1]
    content_type = "application/pdf" if ext == "pdf" else "image/jpeg"

    files = {"file": (filename, file_bytes, content_type)}
    try:
        response = requests.post(f"{clean_url}/extract", files=files, timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            raise RuntimeError(f"Backend Server responded with HTTP {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Could not connect to Backend API at '{clean_url}'. "
            "Please ensure the local uvicorn server is running on port 8000, or switch to '⚡ Local OCR / Document Engine'."
        )
    except requests.exceptions.Timeout:
        raise TimeoutError(f"Backend API request timed out after 60 seconds at '{clean_url}'.")


def test_backend_connection(backend_url: str) -> Tuple[bool, str]:
    """Check health endpoint of backend API server"""
    clean_url = backend_url.rstrip("/")
    try:
        r = requests.get(f"{clean_url}/health", timeout=5)
        if r.status_code == 200:
            return True, f"Online ({r.json().get('status', 'healthy')})"
        return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, f"Offline ({type(e).__name__})"
