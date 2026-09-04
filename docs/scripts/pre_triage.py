#!/usr/bin/env python3
"""
Fase 0.5 — Pré-Triagem Determinística (Zero-Token Fast-Path)
Varre todas as skills de all_skills/ em milissegundos sem gastar tokens de LLM.
Gera auditoria sintática, contagem de caracteres da description e detecção de convenções violadas.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def extract_frontmatter(content: str) -> Tuple[Optional[str], str]:
    """
    Separa o frontmatter YAML do corpo do documento markdown.
    Retorna (frontmatter_text, body_text).
    """
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, content

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            frontmatter_text = "\n".join(lines[1:i])
            body_text = "\n".join(lines[i + 1:])
            return frontmatter_text, body_text

    return None, content


def parse_frontmatter_dict(fm_text: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Converte o texto do frontmatter em dicionário via PyYAML com fallback via regex.
    """
    if not fm_text:
        return False, {}, "Frontmatter vazio ou ausente"

    if HAS_YAML:
        try:
            data = yaml.safe_load(fm_text)
            if isinstance(data, dict):
                return True, data, None
            else:
                return False, {}, "Frontmatter não é um mapeamento YAML (dicionário)"
        except Exception as e:
            err_msg = str(e)
    else:
        err_msg = "PyYAML não instalado"

    # Fallback via regex para extrair chaves básicas como description e name
    data = {}
    name_match = re.search(r"^name:\s*['\"]?(.*?)['\"]?\s*$", fm_text, re.MULTILINE)
    if name_match:
        data["name"] = name_match.group(1).strip()

    desc_match = re.search(r"^description:\s*(?:['\"](.*?)['\"]|([^\n]+))", fm_text, re.MULTILINE | re.DOTALL)
    if desc_match:
        val = desc_match.group(1) or desc_match.group(2)
        data["description"] = val.strip().strip("'\"")

    return False, data, f"Erro de sintaxe YAML: {err_msg}"


def identify_domain(rel_path: str) -> str:
    """
    Identifica o domínio da skill com base no caminho relativo.
    """
    rel_lower = rel_path.lower()
    if "created-skills" in rel_lower:
        return "created-skills"
    elif "agentic awesome skills" in rel_lower or "awesome_skills" in rel_lower:
        return "awesome-skills"
    elif "curated-youtube" in rel_lower:
        return "curated-youtube"
    return "other"


def audit_skill(file_path: Path, base_dir: Path) -> Dict[str, Any]:
    """
    Audita uma única skill determinística e estaticamente.
    """
    rel_path = str(file_path.relative_to(base_dir))
    domain = identify_domain(rel_path)

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {
            "skill_name": file_path.parent.name,
            "skill_path": rel_path,
            "domain": domain,
            "yaml_valid": False,
            "yaml_error": f"Erro de leitura de arquivo: {e}",
            "description_len": 0,
            "description_len_valid": False,
            "violations": [f"Erro ao abrir arquivo: {e}"],
            "needs_fast_fix": True,
        }

    fm_text, body_text = extract_frontmatter(content)
    yaml_valid, fm_data, yaml_error = parse_frontmatter_dict(fm_text) if fm_text is not None else (False, {}, "Frontmatter '---' não encontrado")

    skill_name = fm_data.get("name") or file_path.parent.name
    description = fm_data.get("description", "")
    desc_str = str(description).strip() if description is not None else ""
    desc_len = len(desc_str)

    violations: List[str] = []

    # Validação de YAML
    if not yaml_valid and yaml_error:
        violations.append(yaml_error)

    # Validação de Description
    if not desc_str:
        desc_valid = False
        violations.append("Campo 'description' ausente ou vazio no frontmatter")
    elif desc_len < 200:
        desc_valid = False
        violations.append(f"Description muito curta ({desc_len} caracteres; ideal entre 200 e 400)")
    elif desc_len > 400:
        desc_valid = False
        violations.append(f"Description muito longa ({desc_len} caracteres; ideal entre 200 e 400)")
    else:
        desc_valid = True

    # Regras adaptativas por domínio:
    if domain == "created-skills":
        # Checagem de menções a Adonis / AdonisJS
        if re.search(r"\badonis(js)?\b", content, re.IGNORECASE):
            violations.append("Menção à stack legada Adonis/AdonisJS encontrada em created-skills")

        # Regras de frontend em created-skills
        if "frontend" in rel_path.lower():
            # Checagem de rotas cruas /api/
            if re.search(r"['\"]/api/[a-zA-Z0-9_\-/]+['\"]", content):
                violations.append("Uso de rota crua '/api/' no frontend (deve adotar rotas Ziggy via MaxUse)")

            # Checagem de imports diretos proibidos
            if re.search(r"from\s+['\"](lodash|vueuse)['\"]", content):
                violations.append("Import direto de lodash ou vueuse no frontend (deve adotar @maxvue/max-use)")

    needs_fast_fix = len(violations) > 0

    return {
        "skill_name": skill_name,
        "skill_path": rel_path,
        "domain": domain,
        "yaml_valid": yaml_valid,
        "yaml_error": yaml_error,
        "description_len": desc_len,
        "description_len_valid": desc_valid,
        "violations": violations,
        "needs_fast_fix": needs_fast_fix,
    }


def run_pre_triage(
    target_dir: Path,
    output_path: Optional[Path] = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Executa a pré-triagem determinística em todas as skills do diretório alvo.
    """
    skills_files = sorted(target_dir.rglob("SKILL.md"))
    total_scanned = len(skills_files)

    results: List[Dict[str, Any]] = []
    domain_counts = {"created-skills": 0, "awesome-skills": 0, "curated-youtube": 0, "other": 0}
    yaml_errors_count = 0
    desc_short_count = 0
    desc_long_count = 0
    desc_ok_count = 0
    desc_missing_count = 0
    domain_violations_count = 0
    clean_count = 0

    for sf in skills_files:
        audit = audit_skill(sf, target_dir)
        results.append(audit)

        dom = audit["domain"]
        domain_counts[dom] = domain_counts.get(dom, 0) + 1

        if not audit["yaml_valid"]:
            yaml_errors_count += 1

        if audit["description_len"] == 0:
            desc_missing_count += 1
        elif audit["description_len"] < 200:
            desc_short_count += 1
        elif audit["description_len"] > 400:
            desc_long_count += 1
        else:
            desc_ok_count += 1

        # Verifica se teve violações de convenção além do tamanho de descrição/yaml
        other_viols = [v for v in audit["violations"] if "description" not in v.lower() and "yaml" not in v.lower()]
        if other_viols:
            domain_violations_count += 1

        if not audit["needs_fast_fix"]:
            clean_count += 1

    summary = {
        "total_scanned": total_scanned,
        "clean_skills": clean_count,
        "skills_with_issues": total_scanned - clean_count,
        "domains": domain_counts,
        "yaml_syntax_issues": yaml_errors_count,
        "descriptions": {
            "conformes_200_400": desc_ok_count,
            "muito_curtas": desc_short_count,
            "muito_longas": desc_long_count,
            "ausentes": desc_missing_count,
        },
        "domain_convention_violations": domain_violations_count,
    }

    report = {
        "summary": summary,
        "skills": results,
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    return report


def main():
    parser = argparse.ArgumentParser(description="Fase 0.5 — Pré-Triagem Determinística de Skills")
    parser.add_argument("--target", default="all_skills", help="Diretório contendo as skills (padrão: all_skills)")
    parser.add_argument("--output", default="docs/reports/pre_triage.json", help="Caminho do relatório JSON de saída")
    parser.add_argument("--verbose", action="store_true", help="Imprime detalhes de cada skill com pendência")
    args = parser.parse_args()

    repo_root = Path.cwd()
    target_path = (repo_root / args.target).resolve()
    output_path = (repo_root / args.output).resolve() if args.output else None

    if not target_path.exists():
        print(f"❌ Erro: Diretório alvo não encontrado: {target_path}", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 Iniciando Pré-Triagem Determinística (Zero-Token)...")
    print(f"📂 Diretório alvo: {target_path}")

    report = run_pre_triage(target_path, output_path, verbose=args.verbose)
    s = report["summary"]

    print("\n" + "=" * 50)
    print("📊 RESUMO DA PRÉ-TRIAGEM DETERMINÍSTICA")
    print("=" * 50)
    print(f"Total de SKILL.md auditados:       {s['total_scanned']}")
    print(f"  - created-skills (proprietárias): {s['domains'].get('created-skills', 0)}")
    print(f"  - Agentic Awesome Skills:         {s['domains'].get('awesome-skills', 0)}")
    print(f"  - curated-youtube:                {s['domains'].get('curated-youtube', 0)}")
    print(f"  - Outros:                         {s['domains'].get('other', 0)}")
    print("-" * 50)
    print(f"Skills 100% Limpas Sintaticamente: {s['clean_skills']}")
    print(f"Skills com Pendências Identificadas:{s['skills_with_issues']}")
    print(f"  - Erros de Sintaxe YAML:          {s['yaml_syntax_issues']}")
    print(f"  - Descriptions Conformes (200-400): {s['descriptions']['conformes_200_400']}")
    print(f"  - Descriptions Muito Curtas (<200): {s['descriptions']['muito_curtas']}")
    print(f"  - Descriptions Muito Longas (>400): {s['descriptions']['muito_longas']}")
    print(f"  - Descriptions Ausentes/Vazias:   {s['descriptions']['ausentes']}")
    print(f"  - Violações de Convenção Stack:   {s['domain_convention_violations']}")
    print("=" * 50)

    if output_path:
        print(f"💾 Relatório estruturado salvo em: {output_path}")

    if args.verbose:
        print("\n🔍 DETALHE DAS SKILLS COM PENDÊNCIAS:")
        for sk in report["skills"]:
            if sk["needs_fast_fix"]:
                print(f"\n• [{sk['domain']}] {sk['skill_name']} ({sk['skill_path']}):")
                for v in sk["violations"]:
                    print(f"   - {v}")


if __name__ == "__main__":
    main()
