import * as XLSX from "xlsx";

export function exportMarksheetToExcel(data, customFilename = "marksheet_extracted.xlsx") {
  if (!data) return;

  const aoa = [
    ["MARKSHEET REPORT - EXTRACTED VIA MARKSHEET AI"],
    ["Generated on:", new Date().toLocaleString()],
    [],
    ["STUDENT INFORMATION"],
    ["Student Name:", data.student_name || "N/A"],
    ["Roll Number:", data.roll_no || "N/A"],
    ["Institution / College:", data.institution || "N/A"],
    ["Examination / Session:", data.examination || data.semester || "N/A"],
    ["Overall Result:", data.result || "N/A"],
    ["SGPA / CGPA:", data.sgpa || "N/A"],
    ["Percentage (%):", data.percentage ? `${data.percentage}%` : "N/A"],
    [],
    ["SUBJECT PERFORMANCE BREAKDOWN"],
    ["Subject Code", "Subject Name", "Max Marks", "Marks Obtained", "Grade", "Status"]
  ];

  const subjects = data.subjects || [];
  subjects.forEach((sub) => {
    aoa.push([
      sub.code || sub.subject_code || "-",
      sub.name || sub.subject_name || "Unknown",
      sub.max_marks !== undefined ? sub.max_marks : 100,
      sub.obtained_marks !== undefined ? sub.obtained_marks : (sub.marks || 0),
      sub.grade || "-",
      sub.status || (sub.obtained_marks >= 40 ? "PASS" : "FAIL")
    ]);
  });

  aoa.push([]);
  aoa.push(["TOTALS", "", data.total_max || 0, data.total_obtained || 0, "", data.result || "PASS"]);

  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.aoa_to_sheet(aoa);

  // Set column widths for readability
  ws["!cols"] = [
    { wch: 18 },
    { wch: 38 },
    { wch: 14 },
    { wch: 16 },
    { wch: 12 },
    { wch: 12 }
  ];

  XLSX.utils.book_append_sheet(wb, ws, "Marksheet");
  XLSX.writeFile(wb, customFilename.endsWith(".xlsx") ? customFilename : `${customFilename}.xlsx`);
}
