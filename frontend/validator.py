from typing import Any, Dict, List, Tuple
from frontend.config import (
    DEFAULT_DISTINCTION_PERCENTAGE,
    DEFAULT_MAX_MARKS,
    DEFAULT_PASSING_PERCENTAGE,
)


def validate_marksheet(data: Dict[str, Any]) -> List[str]:
    """
    Validates extracted marksheet data and returns a list of warnings or errors.
    Clearly distinguishes between verified warnings and confirmed anomalies.
    """
    warnings: List[str] = []

    is_broadsheet = data.get("is_broadsheet", False)
    if is_broadsheet and data.get("candidates"):
        # Broadsheet validation
        candidates = data["candidates"]
        if not candidates:
            warnings.append("Warning: Broadsheet document detected but no student records were extracted.")
        for idx, cand in enumerate(candidates, start=1):
            c_name = cand.get("name", {}).get("value", "") if isinstance(cand.get("name"), dict) else cand.get("name", "")
            c_roll = cand.get("roll_no", {}).get("value", "") if isinstance(cand.get("roll_no"), dict) else cand.get("roll_no", "")
            if not c_name.strip():
                warnings.append(f"Row {idx}: Missing student name.")
            if not c_roll.strip():
                warnings.append(f"Row {idx}: Missing roll / registration number.")
        return warnings

    # Single marksheet validation
    student = data
    name = student.get("name", {}).get("value", "") if isinstance(student.get("name"), dict) else student.get("name", "")
    roll = student.get("roll_no", {}).get("value", "") if isinstance(student.get("roll_no"), dict) else student.get("roll_no", "")

    if not str(name).strip() or str(name).strip() == "—":
        warnings.append("Notice: Student name was not explicitly identified in document.")

    if not str(roll).strip() or str(roll).strip() == "—":
        warnings.append("Notice: Roll number or registration number was not found.")

    subjects = student.get("subjects", [])
    if not subjects:
        warnings.append("Warning: No subject marks were detected in the document.")

    seen_subjects = set()
    total_obtained = 0.0
    total_max = 0.0
    has_numeric = False

    for s in subjects:
        s_name = str(s.get("subject", "")).strip()
        if not s_name:
            warnings.append("Warning: Found subject entry with empty subject name.")
        elif s_name in seen_subjects:
            warnings.append(f"Warning: Duplicate subject detected: '{s_name}'.")
        else:
            seen_subjects.add(s_name)

        obt_raw = s.get("obtained")
        max_raw = s.get("max", DEFAULT_MAX_MARKS)
        internal_raw = s.get("internal")
        external_raw = s.get("external")

        try:
            obt_val = float(obt_raw)
            max_val = float(max_raw) if max_raw else DEFAULT_MAX_MARKS
            total_obtained += obt_val
            total_max += max_val
            has_numeric = True

            if obt_val > max_val:
                warnings.append(f"Error: In '{s_name}', obtained marks ({obt_val}) exceed maximum possible marks ({max_val}).")

            if obt_val < 0:
                warnings.append(f"Error: In '{s_name}', negative marks ({obt_val}) recorded.")

            # Component verification (Internal + External = Total)
            if internal_raw is not None and external_raw is not None:
                try:
                    int_val = float(internal_raw)
                    ext_val = float(external_raw)
                    if round(int_val + ext_val, 2) != round(obt_val, 2):
                        warnings.append(f"Component Mismatch: In '{s_name}', Internal ({int_val}) + External ({ext_val}) != Total ({obt_val}).")
                except (ValueError, TypeError):
                    pass

        except (ValueError, TypeError):
            pass

    # Percentage / Aggregate check
    stated_pct_raw = student.get("percentage")
    if stated_pct_raw and has_numeric and total_max > 0:
        try:
            stated_pct = float(stated_pct_raw)
            calc_pct = round((total_obtained / total_max) * 100, 2)
            if abs(stated_pct - calc_pct) > 1.0:
                warnings.append(f"Calculation Discrepancy: Document states percentage as {stated_pct}%, but calculated is {calc_pct}%.")
        except (ValueError, TypeError):
            pass

    return warnings


def recalculate_totals(
    subjects: List[Dict[str, Any]],
    passing_pct: float = DEFAULT_PASSING_PERCENTAGE,
    distinction_pct: float = DEFAULT_DISTINCTION_PERCENTAGE
) -> Dict[str, Any]:
    """
    Recalculates total obtained marks, max marks, percentage,
    passed/failed subjects count, and suggests an overall result classification.
    """
    total_obtained = 0.0
    total_max = 0.0
    passed_count = 0
    failed_count = 0
    is_valid = True

    for s in subjects:
        try:
            obt = float(s.get("obtained", 0))
            mx = float(s.get("max", DEFAULT_MAX_MARKS))
            total_obtained += obt
            total_max += mx

            sub_pct = (obt / mx) * 100 if mx > 0 else 0
            if sub_pct >= passing_pct:
                passed_count += 1
            else:
                failed_count += 1
        except (ValueError, TypeError):
            is_valid = False

    percentage = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0.0

    # Determine classification
    if failed_count > 0:
        classification = f"FAIL ({failed_count} Subject{'s' if failed_count > 1 else ''} Backlog)"
    elif percentage >= distinction_pct:
        classification = "FIRST CLASS WITH DISTINCTION"
    elif percentage >= 60.0:
        classification = "FIRST CLASS"
    elif percentage >= 50.0:
        classification = "SECOND CLASS"
    elif percentage >= passing_pct:
        classification = "PASS"
    else:
        classification = "FAIL"

    return {
        "total_obtained": round(total_obtained, 2),
        "total_max": round(total_max, 2),
        "percentage": percentage,
        "subjects_passed": passed_count,
        "subjects_failed": failed_count,
        "suggested_classification": classification,
        "is_mathematically_valid": is_valid
    }
