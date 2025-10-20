# backend/anomaly_detector/export_pdf_report.py
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.units import cm

HERE = Path(__file__).resolve().parent
RESULTS_DIR = HERE / "results"
JSON_REPORT = RESULTS_DIR / "anomaly_report.json"
PDF_REPORT = RESULTS_DIR / "anomaly_report.pdf"

def _truncate(text: str, max_len: int = 140) -> str:
    if text is None:
        return ""
    s = str(text)
    return s if len(s) <= max_len else s[: max_len - 1] + "…"

def _chunk_rows(rows: List[List[Any]], chunk_size: int) -> List[List[List[Any]]]:
    return [rows[i:i + chunk_size] for i in range(0, len(rows), chunk_size)]

def _build_top_files_table(issues: List[Dict[str, Any]], limit: int = 15):
    # Compte des issues par fichier
    counts: Dict[str, int] = {}
    for it in issues:
        f = it.get("file", "—")
        counts[f] = counts.get(f, 0) + 1
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    data = [["Fichier", "Nb d’issues"]]
    for f, c in top:
        data.append([_truncate(f, 100), c])

    table = Table(data, colWidths=[12*cm, 3*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table

def _build_perf_table(perf_anomalies: List[Dict[str, Any]]):
    data = [["Horodatage", "Latency (ms)", "Loss", "Perplexité", "Accuracy", "Score"]]
    for a in perf_anomalies:
        data.append([
            a.get("timestamp", "—"),
            a.get("latency_ms", "—"),
            a.get("loss", "—"),
            a.get("perplexity", "—"),
            a.get("accuracy", "—"),
            f'{a.get("score", "—"):.6f}' if isinstance(a.get("score", None), (int, float)) else "—",
        ])

    table = Table(data, colWidths=[4.5*cm, 2.5*cm, 2*cm, 2.5*cm, 2*cm, 2.5*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table

def _build_issues_table(issues: List[Dict[str, Any]], limit: int = 40):
    data = [["Type", "Fichier", "Ligne", "Détail"]]
    for it in issues[:limit]:
        data.append([
            _truncate(it.get("type", "—"), 40),
            _truncate(it.get("file", "—"), 60),
            str(it.get("line", "—")),
            _truncate(it.get("detail", "—"), 120),
        ])

    table = Table(data, colWidths=[3.5*cm, 7*cm, 1.5*cm, 6*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table

def main():
    if not JSON_REPORT.exists():
        raise FileNotFoundError(f"Introuvable : {JSON_REPORT}")

    data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))

    summary = data.get("summary", {})
    issues = data.get("code_issues", []) or []
    perf_anomalies = data.get("perf_anomalies", []) or []

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    normal = styles["BodyText"]
    small = ParagraphStyle("small", parent=normal, fontSize=9, leading=12)

    doc = SimpleDocTemplate(
        str(PDF_REPORT),
        pagesize=A4,
        leftMargin=1.7*cm, rightMargin=1.7*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        title="Rapport de détection d’anomalies",
        author="Nafass Anomaly Detector",
    )

    story = []
    story.append(Paragraph("Rapport de détection d’anomalies", title_style))
    story.append(Spacer(1, 0.4*cm))

    # Résumé
    story.append(Paragraph("Résumé", h1))
    summary_text = (
        f"<b>Fichiers scannés :</b> {summary.get('files_scanned', 0)}<br/>"
        f"<b>Issues détectées (code) :</b> {summary.get('code_issues', 0)}<br/>"
        f"<b>Points de performance :</b> {summary.get('perf_points', 0)}<br/>"
        f"<b>Anomalies de performance :</b> {summary.get('perf_anomalies', 0)}"
    )
    story.append(Paragraph(summary_text, normal))
    story.append(Spacer(1, 0.4*cm))

    # Top fichiers
    if issues:
        story.append(Paragraph("Top fichiers par nombre d’issues", h2))
        story.append(_build_top_files_table(issues, limit=15))
        story.append(Spacer(1, 0.4*cm))

    # Perf anomalies
    if perf_anomalies:
        story.append(Paragraph("Anomalies de performance (Isolation Forest)", h2))
        story.append(_build_perf_table(perf_anomalies))
        story.append(Spacer(1, 0.4*cm))

    # Détail des issues (paginer si beaucoup)
    if issues:
        story.append(PageBreak())
        story.append(Paragraph("Détails des issues (extrait)", h1))
        # On affiche par blocs de 40 lignes pour ne pas exploser la page
        chunks = _chunk_rows(
            [["Type", "Fichier", "Ligne", "Détail"]] + [
                [_truncate(it.get("type", "—"), 40),
                 _truncate(it.get("file", "—"), 60),
                 str(it.get("line", "—")),
                 _truncate(it.get("detail", "—"), 120)]
                for it in issues
            ],
            40
        )
        for i, block in enumerate(chunks):
            if i > 0:
                story.append(PageBreak())
            table = Table(block, colWidths=[3.5*cm, 7*cm, 1.5*cm, 6*cm])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.2*cm))

    doc.build(story)
    print(f"📄 PDF généré : {PDF_REPORT}")

if __name__ == "__main__":
    main()
