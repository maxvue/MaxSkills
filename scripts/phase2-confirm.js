#!/usr/bin/env node

/**
 * Script de Execução da FASE 2: CONFIRMAÇÃO DO FILTRO E PLANO DE REMOÇÃO DE INÚTEIS
 */

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const ROOT_DIR = path.resolve(__dirname, '..')
const INDEX_JSON_PATH = path.join(ROOT_DIR, 'index.json')
const OTHER_JSON_PATH = path.join(ROOT_DIR, 'other_skills.json')
const AWESOME_JSON_PATH = path.join(ROOT_DIR, 'awesome_skills.json')

function runPhase2() {
  console.log('🚀 Executando Fase 2: Confirmação do Filtro e Preparação do Plano de Remoção...\n')

  const idxSkills = JSON.parse(fs.readFileSync(INDEX_JSON_PATH, 'utf8'))
  const otherSkills = JSON.parse(fs.readFileSync(OTHER_JSON_PATH, 'utf8'))
  const awesomeSkills = JSON.parse(fs.readFileSync(AWESOME_JSON_PATH, 'utf8'))

  const allCatalogs = [
    { name: 'index.json', path: INDEX_JSON_PATH, list: idxSkills },
    { name: 'other_skills.json', path: OTHER_JSON_PATH, list: otherSkills },
    { name: 'awesome_skills.json', path: AWESOME_JSON_PATH, list: awesomeSkills }
  ]

  const uselessSkills = []
  let confirmedUsefulCount = 0

  for (const cat of allCatalogs) {
    for (const skill of cat.list) {
      const engeappScore = skill.importance_in.find(p => p.project === 'engeapp')?.importance || 0
      const socialScore = skill.importance_in.find(p => p.project === 'SocialMedia')?.importance || 0
      const agenteScore = skill.importance_in.find(p => p.project === 'Agentedebolso')?.importance || 0

      const maxScore = Math.max(engeappScore, socialScore, agenteScore)

      let fase2Msg = ''
      if (maxScore === 0) {
        fase2Msg = `Fase 2 (Confirmação): Confirmada como INÚTIL para todos os 3 projetos (engeapp: 0, SocialMedia: 0, Agentedebolso: 0). Recomendada para remoção definitiva.`
        uselessSkills.push({
          id: skill.id,
          catalog: cat.name,
          skill_name: skill.skill_name,
          local_path: skill.local_path,
          description: (skill.description_en || '').slice(0, 120),
          reason: 'Tecnologia/domínio incompatível com a stack PHP/Laravel + Vue 3 + TS do ecossistema.'
        })
      } else {
        confirmedUsefulCount++
        fase2Msg = `Fase 2 (Confirmação): Relevância confirmada com nota máxima ${maxScore}/10. Mantida no catálogo.`
      }

      const existingIdx = skill.details.findIndex(d => d.Fase2)
      if (existingIdx >= 0) {
        skill.details[existingIdx] = { Fase2: fase2Msg }
      } else {
        skill.details.push({ Fase2: fase2Msg })
      }
    }

    fs.writeFileSync(cat.path, JSON.stringify(cat.list, null, 4), 'utf8')
  }

  // Salvar lista de remoção da fase 2 para auditoria e execução rápida na Fase 3
  const removalPlanPath = path.join(ROOT_DIR, 'scripts', 'phase2_removal_plan.json')
  fs.writeFileSync(removalPlanPath, JSON.stringify(uselessSkills, null, 2), 'utf8')

  console.log(`✅ Fase 2 Concluída:`)
  console.log(`   - Skills Confirmadas como Úteis: ${confirmedUsefulCount}`)
  console.log(`   - Skills Confirmadas como Inúteis para Remoção: ${uselessSkills.length}`)
  console.log(`   - Plano de remoção salvo em: scripts/phase2_removal_plan.json\n`)
}

runPhase2()
