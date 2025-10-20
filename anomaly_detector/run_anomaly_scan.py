# backend/anomaly_detector/run_anomaly_scan.py
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from codebert_detector import analyze_codebase
from isolation_forest_detector import detect_anomalies


# ---------- Ciblage des fichiers à analyser (code) ----------
TARGET_BASENAMES = {
    "data_loader.py",
    "rag_service.py",          # garde celui-ci…
    "rag_vector_service.py",   # …et/ou celui-ci s’il existe
    "llm_service.py",
}


def _find_target_files(backend_dir: Path) -> list[str]:
    """Retourne la liste des chemins existants correspondant aux fichiers ciblés."""
    found: list[str] = []
    # Cherche aux emplacements directs
    for base in TARGET_BASENAMES:
        p = backend_dir / base
        if p.exists():
            found.append(str(p.resolve()))

    # Si certains n’ont pas été trouvés, balaye récursivement
    missing = {b for b in TARGET_BASENAMES if not (backend_dir / b).exists()}
    if missing:
        for p in backend_dir.rglob("*.py"):
            if p.name in missing:
                found.append(str(p.resolve()))
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan d’anomalies (CodeBERT + IsolationForest) restreint à data_loader / rag / llm."
    )
    parser.add_argument("--summary", action="store_true", help="Affiche un résumé console à la fin.")
    args = parser.parse_args(argv)

    here = Path(__file__).resolve().parent           # .../backend/anomaly_detector
    backend_dir = here.parent                        # .../backend
    results_dir = here / "results"
    results_dir.mkdir(exist_ok=True)

    # --------- Fichiers ciblés ---------
    only_paths = _find_target_files(backend_dir)
    if not only_paths:
        print("⚠️ Aucun des fichiers cibles n’a été trouvé. Vérifie les noms/chemins.")
        return 1

    print(f"🔍 {len(only_paths)} fichier(s) ciblé(s) pour l’analyse de code.")
    for p in only_paths:
        print("   •", p)

    # --------- 1) Analyse de code (CodeBERT + règles légères) ---------
    codebert_json = results_dir / "codebert_results.json"
    code_report = analyze_codebase(str(backend_dir), str(codebert_json), only_paths=only_paths)
    print(f"✅ Analyse code écrite dans : {codebert_json}")

    # --------- 2) Détection de perfs (IsolationForest) ---------
    metrics_csv = here / "metrics.csv"
    if not metrics_csv.exists():
        # Fichier d’exemple avec une anomalie volontaire
        metrics_csv.write_text(
            "timestamp,latency_ms,loss,perplexity,accuracy\n"
            "2025-10-19T18:00:00,180,0.42,12.3,0.82\n"
            "2025-10-19T18:05:00,190,0.41,12.1,0.83\n"
            "2025-10-19T18:10:00,175,0.39,11.9,0.84\n"
            "2025-10-19T18:15:00,950,0.90,40.0,0.50\n"
            "2025-10-19T18:25:00,2000,1.20,50.0,0.40\n",
            encoding="utf-8",
        )

    iso_json = results_dir / "isolation_results.json"
    perf_report = detect_anomalies(str(metrics_csv), str(iso_json), contamination=0.2)
    print(f"✅ Anomalies sauvegardées dans : {iso_json}")

    # --------- 3) Rapport consolidé (JSON) ---------
    consolidated = {
        "summary": {
            "files_scanned": len(only_paths),
            "code_issues": len(code_report.get("issues", [])),
            "perf_points": perf_report.get("total_points", 0),
            "perf_anomalies": perf_report.get("anomalies_detected", 0),
        },
        "code_issues": code_report.get("issues", []),
        "perf_anomalies": perf_report.get("anomalous_rows", []),
    }
    report_json = results_dir / "anomaly_report.json"
    report_json.write_text(json.dumps(consolidated, indent=4, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Rapport global écrit dans : {report_json}")

    # --------- 4) Export PDF ---------
    pdf_script = here / "export_pdf_report.py"
    pdf_path = results_dir / "anomaly_report.pdf"
    try:
        subprocess.run(
            [sys.executable, str(pdf_script)],
            check=True,
            cwd=str(here),
        )
        # Le script export écrit sur results/anomaly_report.pdf
        if pdf_path.exists():
            print(f"📄 PDF généré : {pdf_path}")
    except Exception as e:
        print(f"[⚠️] Export PDF non généré automatiquement : {e}")

    # --------- 5) Résumé console optionnel ---------
    if args.summary:
        s = consolidated["summary"]
        print("\n—— Résumé ——")
        print(f"Fichiers scannés       : {s['files_scanned']}")
        print(f"Issues détectées (code): {s['code_issues']}")
        print(f"Points de performance  : {s['perf_points']}")
        print(f"Anomalies de performance: {s['perf_anomalies']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
