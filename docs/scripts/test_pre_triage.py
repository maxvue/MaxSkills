#!/usr/bin/env python3
"""
Testes unitários para o script de pré-triagem determinística (pre_triage.py).
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Adiciona o diretório do script ao sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pre_triage


class TestPreTriage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_skill(self, rel_path: str, content: str) -> Path:
        p = self.base_path / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def test_valid_skill_within_range(self):
        # 250 chars description
        desc = "Este é um texto de descrição válido com tamanho perfeito para o frontmatter de uma skill no ecossistema, contendo detalhes técnicos claros sobre quando invocar e quais problemas resolve de forma determinística e precisa sem enrolação e sem redundâncias."
        self.assertTrue(200 <= len(desc) <= 400)

        content = f"""---
name: valid-skill
description: "{desc}"
---
# Conteúdo da Skill
Texto da skill.
"""
        file_path = self._create_skill("created-skills/backend_laravel/valid/SKILL.md", content)
        result = pre_triage.audit_skill(file_path, self.base_path)

        self.assertTrue(result["yaml_valid"])
        self.assertTrue(result["description_len_valid"])
        self.assertEqual(len(result["violations"]), 0)
        self.assertEqual(result["domain"], "created-skills")

    def test_description_too_short(self):
        content = """---
name: short-skill
description: "Descrição muito curta."
---
# Conteúdo
"""
        file_path = self._create_skill("Agentic Awesome Skills/skills/short/SKILL.md", content)
        result = pre_triage.audit_skill(file_path, self.base_path)

        self.assertTrue(result["yaml_valid"])
        self.assertFalse(result["description_len_valid"])
        self.assertEqual(result["domain"], "awesome-skills")
        self.assertTrue(any("curta" in v.lower() for v in result["violations"]))

    def test_description_too_long(self):
        desc = "A" * 450
        content = f"""---
name: long-skill
description: "{desc}"
---
# Conteúdo
"""
        file_path = self._create_skill("curated-youtube/long/SKILL.md", content)
        result = pre_triage.audit_skill(file_path, self.base_path)

        self.assertFalse(result["description_len_valid"])
        self.assertEqual(result["domain"], "curated-youtube")
        self.assertTrue(any("longa" in v.lower() for v in result["violations"]))

    def test_domain_specific_violation_in_created_skills(self):
        desc = "B" * 250
        # Inclui AdonisJS e rota crua no frontEnd de created-skills
        content = f"""---
name: adonis-leak
description: "{desc}"
---
# Frontend
Use fetch('/api/usuarios') e veja a arquitetura AdonisJS antiga.
"""
        file_path = self._create_skill("created-skills/frontEnd/adonis-leak/SKILL.md", content)
        result = pre_triage.audit_skill(file_path, self.base_path)

        self.assertEqual(result["domain"], "created-skills")
        violation_texts = " ".join(result["violations"])
        self.assertIn("Adonis", violation_texts)
        self.assertIn("/api/", violation_texts)

    def test_domain_adaptive_tolerates_adonis_in_awesome_skills(self):
        desc = "C" * 250
        # Em awesome skills, mencionar adonis não deve quebrar como violação do ecossistema Engeapp
        content = f"""---
name: adonis-official
description: "{desc}"
---
# Adonis Framework
Official documentation for AdonisJS framework.
"""
        file_path = self._create_skill("Agentic Awesome Skills/skills/adonis/SKILL.md", content)
        result = pre_triage.audit_skill(file_path, self.base_path)

        self.assertEqual(result["domain"], "awesome-skills")
        # Não deve conter violação de stack Engeapp
        for v in result["violations"]:
            self.assertNotIn("violação de convenção proprietária", v.lower())


if __name__ == "__main__":
    unittest.main()
