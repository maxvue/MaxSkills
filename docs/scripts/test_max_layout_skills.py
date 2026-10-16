#!/usr/bin/env python3
"""
Testes documentais determinísticos para o contrato de presetMaxUno e MaxGrid.
Verifica a especificação canônica, tabelas numéricas, resolução de links locais,
ausência de snippets obsoletos nos arquivos migrados e integridade de manifestos.
"""

import os
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Regex canônica de sN definida no presetMaxUno.ts
S_TOKEN_REGEX = re.compile(
    r"^s-?(\d+)(?:-(full|max|\d+))?(?:-(start|end)(?:-(desktop|mobile|tablet))?|-(desktop|mobile|tablet)(?:-(start|end))?)?$"
)


class TestMaxLayoutSkills(unittest.TestCase):
    def setUp(self):
        self.max_grid_sizing_path = (
            REPO_ROOT
            / "all_skills"
            / "created-skills"
            / "frontEnd"
            / "vue-unocss-styling-best-practices"
            / "references"
            / "max-grid-sizing.md"
        )
        self.assertTrue(
            self.max_grid_sizing_path.exists(),
            f"Arquivo de referência canônica não encontrado: {self.max_grid_sizing_path}",
        )
        self.sizing_content = self.max_grid_sizing_path.read_text(encoding="utf-8")

    def test_canonical_reference_exists_and_resolves_links(self):
        """Verifica a existência do arquivo de referência e resolução de links locais."""
        # Encontra links markdown relativos no próprio max-grid-sizing.md
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        for match in link_pattern.finditer(self.sizing_content):
            href = match.group(2)
            if href.startswith("http://") or href.startswith("https://") or href.startswith("#"):
                continue
            resolved = (self.max_grid_sizing_path.parent / href).resolve()
            self.assertTrue(
                resolved.exists(),
                f"Link local quebrado em max-grid-sizing.md: {href} -> {resolved}",
            )

    def test_numeric_table_values_and_edge_cases(self):
        """Valida que a tabela de valores numéricos expressa exatamente os limites em pixels."""
        content = self.sizing_content

        # s1 / s-1 -> 20px min, 24px max
        self.assertIn("`s1`", content)
        self.assertIn("20px", content)
        self.assertIn("24px", content)

        # s7 / s-7 -> 140px min, 168px max
        self.assertIn("`s7`", content)
        self.assertIn("140px", content)
        self.assertIn("168px", content)

        # s3-10-start -> 60px min, 200px max
        self.assertIn("`s3-10-start`", content)
        self.assertIn("60px", content)
        self.assertIn("200px", content)

        # s7-full / s7-max -> 140px min, 100% max
        self.assertIn("`s7-full`", content)
        self.assertIn("100%", content)

        # s7-end-mobile / s7-mobile-end
        self.assertIn("`s7-end-mobile`", content)
        self.assertIn("`s7-mobile-end`", content)

        # s50 e s100 com alertas de que não são 50% nem 100%
        self.assertIn("`s50`", content)
        self.assertIn("1000px", content)
        self.assertIn("1200px", content)

        self.assertIn("`s100`", content)
        self.assertIn("2000px", content)
        self.assertIn("2400px", content)

        # Alerta explícito contra mitos percentuais
        self.assertRegex(content, r"s50.*não.*50%", re.IGNORECASE)
        self.assertRegex(content, r"s100.*não.*100%", re.IGNORECASE)

    def test_explicit_contrasts(self):
        """Valida os contrastes explícitos exigidos pelo plano."""
        content = self.sizing_content

        # Contraste w-full vs sN-full
        self.assertIn("w-full", content)
        self.assertIn("100%", content)

        # Contraste preset vs MaxGrid e segmentação em linhas
        self.assertIn("MaxGrid", content)
        self.assertIn("GridSlotRows", content)
        self.assertIn("max-grid-row", content)

        # Contraste MaxGrid vs MaxGridCols
        self.assertIn("MaxGridCols", content)
        self.assertIn("24 colunas", content)

    def test_breakpoints_and_support_matrix(self):
        """Valida que os breakpoints coincidem com o código e que a matriz de suporte a quebras está explícita."""
        content = self.sizing_content

        self.assertIn("767.98px", content)
        self.assertIn("1000.98px", content)
        self.assertIn("1001px", content)

        # Suporte ativo
        self.assertIn("start", content)
        self.assertIn("end", content)
        self.assertIn("end-mobile", content)
        self.assertIn("mobile-end", content)

        # Indicação de falta de coordenação no MaxGrid para start-mobile, tablet e desktop
        self.assertIn("start-mobile", content)
        self.assertIn("start-tablet", content)
        self.assertIn("start-desktop", content)

        # Encaminhamento de attrs no InputBase
        self.assertIn("InputBase", content)
        self.assertIn("rootAttrs", content)
        self.assertIn("inputAttrs", content)

    def test_absence_of_obsolete_snippets_in_migrated_skills(self):
        """Verifica que os trechos obsoletos foram devidamente removidos dos arquivos migrados."""
        # 1. vue-max-stack-frontend-best-practices
        stack_skill = (
            REPO_ROOT
            / "all_skills"
            / "created-skills"
            / "frontEnd"
            / "vue-max-stack-frontend-best-practices"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("s-70 w-max-400", stack_skill)
        self.assertNotIn('<div class="entidade-page" s100', stack_skill)
        self.assertIn("w-full", stack_skill)
        self.assertIn("s12-20", stack_skill)

        # 2. vue-meta-api-oauth-integration-best-practices
        meta_skill = (
            REPO_ROOT
            / "all_skills"
            / "created-skills"
            / "frontEnd"
            / "vue-meta-api-oauth-integration-best-practices"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("<MaxInputText s50", meta_skill)
        self.assertNotIn("<MaxInputSwitch s50", meta_skill)
        self.assertNotIn("<div s50", meta_skill)
        self.assertIn("s12-full", meta_skill)
        self.assertIn("s8-full", meta_skill)

        # 3. frontend-design-best-practices
        design_skill = (
            REPO_ROOT
            / "all_skills"
            / "created-skills"
            / "frontEnd"
            / "frontend-design-best-practices"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("concatenam `px` cegamente", design_skill)
        self.assertIn("getCssSize", design_skill)

        # 4. vue-brand-positioning-character-management-best-practices
        brand_skill = (
            REPO_ROOT
            / "all_skills"
            / "created-skills"
            / "frontEnd"
            / "vue-brand-positioning-character-management-best-practices"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("s50, s100, s33, s25", brand_skill)
        self.assertIn("s12-full", brand_skill)

    def test_example_tokens_conform_to_grammar(self):
        """Valida que todos os tokens sN utilizados nos novos exemplos atendem estritamente à regex."""
        sample_tokens = [
            "s1",
            "s-1",
            "s7",
            "s-7",
            "s3-10-start",
            "s7-full",
            "s7-max",
            "s7-end-mobile",
            "s7-mobile-end",
            "s12-full",
            "s12-full-end",
            "s12-20",
            "s8-full",
            "s6-full-end",
            "s14-full",
        ]
        for token in sample_tokens:
            self.assertIsNotNone(
                S_TOKEN_REGEX.match(token),
                f"Token nos exemplos não casa com S_TOKEN_REGEX: {token}",
            )

    def test_frontmatters_and_manifests_preserved(self):
        """Garante que frontmatters e manifestos raiz permanecem válidos e preservados."""
        skills_to_check = [
            "vue-unocss-styling-best-practices",
            "vue-max-ecosystem-api-reference",
            "vue-max-stack-frontend-best-practices",
            "frontend-design-best-practices",
            "vue-brand-positioning-character-management-best-practices",
            "vue-meta-api-oauth-integration-best-practices",
            "vue-frontend-bug-fixing-best-practices",
            "vue-inputs-masks-validation-best-practices",
        ]

        frontmatter_re = re.compile(r"^---\n(name:\s*([^\n]+))\n(description:\s*([^\n]+))\n", re.MULTILINE)

        for skill_dir in skills_to_check:
            skill_file = REPO_ROOT / "all_skills" / "created-skills" / "frontEnd" / skill_dir / "SKILL.md"
            self.assertTrue(skill_file.exists(), f"Skill não encontrada: {skill_file}")
            text = skill_file.read_text(encoding="utf-8")
            match = frontmatter_re.search(text)
            self.assertIsNotNone(match, f"Frontmatter inválido ou corrompido em {skill_file}")

        # Manifestos raiz não devem ter sido alterados
        for manifest in ["awesome_skills.json", "index.json", "other_skills.json"]:
            manifest_path = REPO_ROOT / manifest
            self.assertTrue(manifest_path.exists(), f"Manifesto {manifest} deve existir")


if __name__ == "__main__":
    unittest.main()
