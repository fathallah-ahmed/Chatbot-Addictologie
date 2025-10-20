# backend/anomaly_detector/codebert_detector.py
from __future__ import annotations
import ast
import json
import re
from pathlib import Path
from typing import Iterable, List, Dict, Any, Optional

# -----------------------------
# Options facultatives
# -----------------------------
USE_CODEBERT = True  # si indisponible, on tombera en mode "gracieux"
CODEBERT_MODEL_ID = "microsoft/codebert-base"

# -----------------------------
# Helpers: sélection des fichiers
# -----------------------------
FILE_EXTS = {".py"}
EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    "data/vector_store", "backend/anomaly_detector/results",
    ".pytest_cache", ".mypy_cache", ".idea", ".vscode"
}

def _should_exclude(path: Path) -> bool:
    posix = path.as_posix()
    if any(ex in posix for ex in EXCLUDE_DIRS):
        return True
    return False

def _collect_files(root_dir: Path, only_paths: Optional[Iterable[Path]] = None) -> List[Path]:
    root_dir = root_dir.resolve()

    if only_paths:
        targets = []
        only_set = {Path(p).resolve() for p in only_paths}
        for p in only_set:
            if p.is_dir():
                targets.extend([f for f in p.rglob("*") if f.suffix in FILE_EXTS and not _should_exclude(f)])
            elif p.is_file() and p.suffix in FILE_EXTS and not _should_exclude(p):
                targets.append(p)
        # dédoublonnage + tri
        return sorted({t.resolve() for t in targets})
    else:
        files = []
        for p in root_dir.rglob("*"):
            if p.is_file() and p.suffix in FILE_EXTS and not _should_exclude(p):
                files.append(p.resolve())
        return sorted(files)

# -----------------------------
# Règles "lint" simples
# -----------------------------
TODO_RE = re.compile(r"\b(TODO|FIXME)\b", re.IGNORECASE)

def _find_missing_docstrings(tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            # node.lineno existe pour fonctions/classes; pour module, docstring est au top-level
            doc = ast.get_docstring(node, clean=False)
            if doc is None:
                # ligne de déclaration si possible
                line = getattr(node, "lineno", 1)
                issues.append({
                    "type": "missing_docstring",
                    "file": str(file_path),
                    "line": int(line),
                    "detail": f"Fonction/Classe/Module '{getattr(node, 'name', '<module>')}' sans docstring"
                })
    return issues

def _find_debug_prints(tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # print(...) simple (non logging)
            is_print = (
                isinstance(node.func, ast.Name) and node.func.id == "print"
            )
            if is_print:
                issues.append({
                    "type": "debug_print",
                    "file": str(file_path),
                    "line": int(getattr(node, "lineno", 1)),
                    "detail": "print() présent (utiliser des logs structurés plutôt)"
                })
    return issues

def _find_todos(source: str, file_path: Path) -> List[Dict[str, Any]]:
    issues = []
    for i, line in enumerate(source.splitlines(), start=1):
        if TODO_RE.search(line):
            issues.append({
                "type": "todo_fixme_present",
                "file": str(file_path),
                "line": i,
                "detail": "Commentaire TODO/FIXME"
            })
    return issues

def _find_pass_only_functions(tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body or []
            # fonction dont le corps est uniquement "pass"
            if len(body) == 1 and isinstance(body[0], ast.Pass):
                issues.append({
                    "type": "pass_only_function",
                    "file": str(file_path),
                    "line": int(getattr(node, "lineno", 1)),
                    "detail": f"Fonction '{node.name}' vide (pass)"
                })
    return issues

# -----------------------------
# Empreinte CodeBERT (optionnelle)
# -----------------------------
def _codebert_fingerprint(text: str) -> Optional[float]:
    """
    Renvoie une "norme" d'embedding (valeur flottante) pour donner une empreinte
    simple et stable. Si CodeBERT/torch ne sont pas dispos, renvoie None.
    """
    if not USE_CODEBERT:
        return None
    try:
        from transformers import AutoTokenizer, AutoModel
        import torch
    except Exception:
        return None

    try:
        tokenizer = AutoTokenizer.from_pretrained(CODEBERT_MODEL_ID)
        model = AutoModel.from_pretrained(CODEBERT_MODEL_ID)
        with torch.no_grad():
            tokens = tokenizer(text[:5000], return_tensors="pt", truncation=True, padding=True)
            out = model(**tokens).last_hidden_state.mean(dim=1)  # [1, hidden]
            norm = float(torch.linalg.norm(out).item())
        return norm
    except Exception:
        return None

# -----------------------------
# API principale
# -----------------------------
def analyze_codebase(root_dir: str, out_json_path: str, only_paths: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """
    Analyse le code sous root_dir. Si only_paths est fourni (liste de chemins absolus/relatifs),
    on restreint l'analyse à ces fichiers/dossiers.
    Écrit un JSON de résultats dans out_json_path et renvoie le dict en mémoire.
    """
    root = Path(root_dir).resolve()
    only_list: Optional[List[Path]] = None
    if only_paths:
        only_list = [Path(p).resolve() for p in only_paths]

    files = _collect_files(root, only_list)

    issues: List[Dict[str, Any]] = []
    for fp in files:
        try:
            src = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # parse AST
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "file": str(fp),
                "line": int(getattr(e, "lineno", 1) or 1),
                "detail": f"SyntaxError: {e.msg}"
            })
            continue

        # règles statiques
        issues.extend(_find_missing_docstrings(tree, fp))
        issues.extend(_find_debug_prints(tree, fp))
        issues.extend(_find_todos(src, fp))
        issues.extend(_find_pass_only_functions(tree, fp))

        # empreinte codebert (facultative)
        fp_val = _codebert_fingerprint(src)
        if fp_val is not None:
            issues.append({
                "type": "codebert_fingerprint",
                "file": str(fp),
                "detail": f"Empreinte vectorielle CodeBERT={fp_val:.3f}"
            })

    report = {
        "scanned_root": str(root),
        "scanned_files": len(files),
        "issues": issues,
    }

    out_path = Path(out_json_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    return report
