#!/usr/bin/env python3
"""
Testes unitários para o audit_engine.py (Fases 1 a 5 do runbook optimize_skills.md).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import audit_engine


class TestAuditEngine(unittest.TestCase):
    def test_precedence_order(self):
        # REMOVER > FUNDIR > PODAR > CORRIGIR > MANTER
        self.assertEqual(audit_engine.determine_destination(has_remove=True, has_merge=True, has_cut=True, has_fix=True), "REMOVER")
        self.assertEqual(audit_engine.determine_destination(has_remove=False, has_merge=True, has_cut=True, has_fix=True), "FUNDIR")
        self.assertEqual(audit_engine.determine_destination(has_remove=False, has_merge=False, has_cut=True, has_fix=True), "PODAR")
        self.assertEqual(audit_engine.determine_destination(has_remove=False, has_merge=False, has_cut=False, has_fix=True), "CORRIGIR")
        self.assertEqual(audit_engine.determine_destination(has_remove=False, has_merge=False, has_cut=False, has_fix=False), "MANTER")

    def test_state_classification(self):
        # Crítica: erros críticos arquiteturais
        # Ruim: múltiplos problemas
        # Regular: 1 ou 2 problemas pontuais
        # Boa: apenas ajustes de formato/description
        # Excelente: 0 problemas
        self.assertEqual(audit_engine.classify_state(has_critical=True, problem_count=3, has_format_only=False), "Crítica")
        self.assertEqual(audit_engine.classify_state(has_critical=False, problem_count=3, has_format_only=False), "Ruim")
        self.assertEqual(audit_engine.classify_state(has_critical=False, problem_count=1, has_format_only=False), "Regular")
        self.assertEqual(audit_engine.classify_state(has_critical=False, problem_count=0, has_format_only=True), "Boa")
        self.assertEqual(audit_engine.classify_state(has_critical=False, problem_count=0, has_format_only=False), "Excelente")


if __name__ == "__main__":
    unittest.main()
