import csv
import io
import json
from datetime import datetime
from typing import Any, Dict, List
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def get_field_val(field: Any, default: str = "—") -> str:
    """Safely extracts field string regardless of whether it is a dict or string"""
    if isinstance(field, dict):
        return str(field.get("value", default))
    if field is None:
        return default
    return str(field)


# ==========================================
# 1. EXCEL EXPORTER (.xlsx)
# ==========================================
def export_excel(data: Dict[str, Any]) -> bytes:
    """Generate professional, multi-tab Excel workbook using openpyxl"""
    wb = openpyxl.Workbook()

    title_font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    subtitle_font = Font(name="Calibri", size=10, italic=True, color="FFFFFF")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    regular_font = Font(name="Calibri", size=11)
    bold_font = Font(name="Calibri", size=11, bold=True)

    primary_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    secondary_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    accent_fill = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid")
    light_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )

    is_broadsheet = data.get("is_broadsheet", False) and bool(data.get("candidates"))

    if is_broadsheet:
        candidates = data.get("candidates", [])
        ws1 = wb.active
        ws1.title = "Cohort Broadsheet"
        ws1.views.sheetView[0].showGridLines = True

        institution = data.get("institution") or "ACADEMIC MARKSHEET BROADSHEET"
        ws1.merge_cells("A1:K1")
        ws1["A1"] = institution
        ws1["A1"].font = title_font
        ws1["A1"].fill = primary_fill
        ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws1.row_dimensions[1].height = 30

        ws1.merge_cells("A2:K2")
        ws1["A2"] = f"Total Candidates: {len(candidates)} | Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ws1["A2"].font = subtitle_font
        ws1["A2"].fill = secondary_fill
        ws1["A2"].alignment = Alignment(horizontal="center", vertical="center")
        ws1.row_dimensions[2].height = 20

        # Unique subjects
        sub_names = []
        for c in candidates:
            for s in c.get("subjects", []):
                sname = s.get("subject", "Subject")
                if sname not in sub_names:
                    sub_names.append(sname)

        headers = ["#", "Roll No", "Student Name"] + sub_names + ["Aggregate", "SGPA", "Result"]
        ws1.append([])
        ws1.append(headers)

        header_row_idx = 4
        ws1.row_dimensions[header_row_idx].height = 25
        for col_idx in range(1, len(headers) + 1):
            cell = ws1.cell(row=header_row_idx, column=col_idx)
            cell.font = header_font
            cell.fill = accent_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for idx, cand in enumerate(candidates, start=1):
            roll = get_field_val(cand.get("roll_no"))
            name = get_field_val(cand.get("name"))
            agg = get_field_val(cand.get("aggregate"))
            sgpa = get_field_val(cand.get("sgpa"))
            res = get_field_val(cand.get("result"))

            sub_dict = {s.get("subject"): s for s in cand.get("subjects", [])}
            sub_vals = []
            for sn in sub_names:
                if sn in sub_dict:
                    sc = sub_dict[sn].get("obtained", "—")
                    gr = sub_dict[sn].get("grade")
                    sub_vals.append(f"{sc} ({gr})" if gr else str(sc))
                else:
                    sub_vals.append("—")

            row_data = [idx, roll, name] + sub_vals + [agg, sgpa, res]
            ws1.append(row_data)

            curr_row = header_row_idx + idx
            ws1.row_dimensions[curr_row].height = 22
            row_fill = zebra_fill if idx % 2 == 0 else PatternFill(fill_type=None)

            for col_idx in range(1, len(headers) + 1):
                cell = ws1.cell(row=curr_row, column=col_idx)
                cell.font = bold_font if col_idx == 3 else regular_font
                cell.border = thin_border
                if row_fill.fill_type:
                    cell.fill = row_fill
                cell.alignment = Alignment(horizontal="left" if col_idx == 3 else "center", vertical="center")

        for col in ws1.columns:
            max_len = max(len(str(c.value or "")) for c in col)
            ws1.column_dimensions[get_column_letter(col[0].column)].width = max(max_len + 4, 12)

    else:
        # Single Marksheet
        ws = wb.active
        ws.title = "Student Marksheet"
        ws.views.sheetView[0].showGridLines = True

        name = get_field_val(data.get("name"))
        roll = get_field_val(data.get("roll_no"))
        result = get_field_val(data.get("result"))
        sgpa = get_field_val(data.get("sgpa"))

        ws.merge_cells("A1:E1")
        ws["A1"] = "ACADEMIC MARKSHEET REPORT"
        ws["A1"].font = title_font
        ws["A1"].fill = primary_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 28

        ws["A3"] = "Student Name:"
        ws["A3"].font = bold_font
        ws["B3"] = name
        ws["D3"] = "Roll Number:"
        ws["D3"].font = bold_font
        ws["E3"] = roll

        ws["A4"] = "Overall Result:"
        ws["A4"].font = bold_font
        ws["B4"] = result
        ws["D4"] = "SGPA / GPA:"
        ws["D4"].font = bold_font
        ws["E4"] = sgpa

        for r in (3, 4):
            for c in ("A", "B", "D", "E"):
                ws[f"{c}{r}"].fill = light_fill
                ws[f"{c}{r}"].border = thin_border
            ws.row_dimensions[r].height = 22

        headers = ["Sl No", "Subject Name", "Marks Obtained", "Maximum Marks", "Grade"]
        ws.append([])
        ws.append(headers)

        header_row_idx = 6
        ws.row_dimensions[header_row_idx].height = 24
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=header_row_idx, column=col_idx)
            cell.font = header_font
            cell.fill = accent_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        subjects = data.get("subjects", [])
        for i, s in enumerate(subjects, start=1):
            s_name = s.get("subject", "—")
            s_obt = s.get("obtained", "—")
            s_max = s.get("max", "100")
            s_grd = s.get("grade", "—")

            ws.append([i, s_name, s_obt, s_max, s_grd])
            curr_row = header_row_idx + i
            ws.row_dimensions[curr_row].height = 20

            for col_idx in range(1, len(headers) + 1):
                cell = ws.cell(row=curr_row, column=col_idx)
                cell.font = regular_font
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="left" if col_idx == 2 else "center", vertical="center")

        for col in ws.columns:
            max_len = max(len(str(c.value or "")) for c in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = max(max_len + 4, 15)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ==========================================
# 2. CSV EXPORTER (.csv)
# ==========================================
def export_csv(data: Dict[str, Any]) -> str:
    """Generate clean CSV output for broadsheets or individual marksheets"""
    output = io.StringIO()
    writer = csv.writer(output)

    is_broadsheet = data.get("is_broadsheet", False) and bool(data.get("candidates"))

    if is_broadsheet:
        candidates = data.get("candidates", [])
        sub_names = []
        for c in candidates:
            for s in c.get("subjects", []):
                sn = s.get("subject", "Subject")
                if sn not in sub_names:
                    sub_names.append(sn)

        writer.writerow(["Sl_No", "Roll_Number", "Student_Name"] + sub_names + ["Aggregate", "SGPA", "Result"])
        for idx, cand in enumerate(candidates, start=1):
            roll = get_field_val(cand.get("roll_no"))
            name = get_field_val(cand.get("name"))
            agg = get_field_val(cand.get("aggregate"))
            sgpa = get_field_val(cand.get("sgpa"))
            res = get_field_val(cand.get("result"))

            sub_map = {s.get("subject"): s.get("obtained", "—") for s in cand.get("subjects", [])}
            row = [idx, roll, name] + [sub_map.get(sn, "—") for sn in sub_names] + [agg, sgpa, res]
            writer.writerow(row)
    else:
        name = get_field_val(data.get("name"))
        roll = get_field_val(data.get("roll_no"))
        result = get_field_val(data.get("result"))
        sgpa = get_field_val(data.get("sgpa"))

        writer.writerow(["Field", "Value"])
        writer.writerow(["Student_Name", name])
        writer.writerow(["Roll_Number", roll])
        writer.writerow(["Overall_Result", result])
        writer.writerow(["SGPA", sgpa])
        writer.writerow([])
        writer.writerow(["Sl_No", "Subject_Name", "Marks_Obtained", "Maximum_Marks", "Grade"])

        for i, s in enumerate(data.get("subjects", []), start=1):
            writer.writerow([i, s.get("subject", "—"), s.get("obtained", "—"), s.get("max", "100"), s.get("grade", "—")])

    return output.getvalue()


# ==========================================
# 3. JSON EXPORTER (.json)
# ==========================================
def export_json(data: Dict[str, Any]) -> str:
    """Export formatted JSON with metadata and timestamp"""
    export_payload = {
        "export_metadata": {
            "application": "Marksheet AI Enterprise",
            "version": "2.4.0",
            "timestamp": datetime.now().isoformat(),
            "status": "Verified"
        },
        "marksheet_data": data
    }
    return json.dumps(export_payload, indent=2, ensure_ascii=False)


# ==========================================
# 4. REPORTLAB PDF REPORT (.pdf)
# ==========================================
def export_pdf_report(data: Dict[str, Any], filename: str = "document.pdf") -> bytes:
    """Generate high-resolution printable PDF Summary Report using ReportLab"""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        alignment=1  # Centered
    )

    subtitle_style = ParagraphStyle(
        "DocSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1
    )

    card_label = ParagraphStyle(
        "CardLabel",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748B")
    )

    card_value = ParagraphStyle(
        "CardValue",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0F172A")
    )

    th_style = ParagraphStyle(
        "TH",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    td_style = ParagraphStyle(
        "TD",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
        alignment=1
    )

    story = []

    # Title Banner
    story.append(Paragraph("MARKSHEET AI — ACADEMIC EXTRACTION REPORT", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Source: {filename} | Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=15))

    is_broadsheet = data.get("is_broadsheet", False) and bool(data.get("candidates"))

    if is_broadsheet:
        candidates = data.get("candidates", [])
        story.append(Paragraph(f"<b>Cohort Summary:</b> {len(candidates)} Candidates Identified", card_value))
        story.append(Spacer(1, 10))

        # Broadsheet table
        sub_names = []
        for c in candidates:
            for s in c.get("subjects", []):
                sn = s.get("subject", "Sub")
                if sn not in sub_names:
                    sub_names.append(sn)

        sub_names = sub_names[:5]  # Limit to 5 subjects for letter width printable PDF

        th_row = [Paragraph("#", th_style), Paragraph("Roll No", th_style), Paragraph("Student Name", th_style)]
        for sn in sub_names:
            th_row.append(Paragraph(sn[:12], th_style))
        th_row.extend([Paragraph("SGPA", th_style), Paragraph("Result", th_style)])

        table_data = [th_row]

        for idx, cand in enumerate(candidates, start=1):
            roll = get_field_val(cand.get("roll_no"))
            name = get_field_val(cand.get("name"))
            sgpa = get_field_val(cand.get("sgpa"))
            res = get_field_val(cand.get("result"))

            sub_map = {s.get("subject"): s for s in cand.get("subjects", [])}
            row = [Paragraph(str(idx), td_style), Paragraph(roll, td_style), Paragraph(name[:20], td_style)]
            for sn in sub_names:
                sc = sub_map.get(sn, {}).get("obtained", "—")
                row.append(Paragraph(str(sc), td_style))
            row.extend([Paragraph(str(sgpa), td_style), Paragraph(str(res), td_style)])
            table_data.append(row)

        pdf_table = Table(table_data, repeatRows=1)
        pdf_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        story.append(pdf_table)

    else:
        # Single Student Card
        name = get_field_val(data.get("name"))
        roll = get_field_val(data.get("roll_no"))
        result = get_field_val(data.get("result"))
        sgpa = get_field_val(data.get("sgpa"))

        meta_table_data = [
            [Paragraph("Student Name", card_label), Paragraph("Roll / Reg No", card_label), Paragraph("SGPA / GPA", card_label), Paragraph("Result Status", card_label)],
            [Paragraph(name, card_value), Paragraph(roll, card_value), Paragraph(sgpa, card_value), Paragraph(result, card_value)]
        ]
        meta_table = Table(meta_table_data, colWidths=[1.8 * inch, 1.8 * inch, 1.8 * inch, 1.8 * inch])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 15))

        # Subjects Table
        th_row = [
            Paragraph("#", th_style),
            Paragraph("Subject Name", th_style),
            Paragraph("Marks Obtained", th_style),
            Paragraph("Max Marks", th_style),
            Paragraph("Grade", th_style)
        ]
        sub_rows = [th_row]

        subjects = data.get("subjects", [])
        for i, s in enumerate(subjects, start=1):
            sub_rows.append([
                Paragraph(str(i), td_style),
                Paragraph(str(s.get("subject", "—")), td_style),
                Paragraph(str(s.get("obtained", "—")), td_style),
                Paragraph(str(s.get("max", "100")), td_style),
                Paragraph(str(s.get("grade", "—")), td_style)
            ])

        sub_table = Table(sub_rows, colWidths=[0.5 * inch, 3.2 * inch, 1.2 * inch, 1.2 * inch, 1.1 * inch])
        sub_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(sub_table)

    story.append(Spacer(1, 20))
    story.append(Paragraph("<i>This extraction report was compiled automatically by Marksheet AI. Verification with original records is advised.</i>", subtitle_style))

    doc.build(story)
    return buf.getvalue()
