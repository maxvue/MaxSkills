#!/usr/bin/env node

/**
 * Script de Execução da FASE 6: ELEIÇÃO DA MELHOR SKILL (overlaps_best_id) E PLANO DE REMOÇÃO
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

function runPhase6() {
  console.log('🚀 Executando Fase 6: Eleição da Melhor Skill por Grupo de Duplicidade...\n')

  const idxSkills = JSON.parse(fs.readFileSync(INDEX_JSON_PATH, 'utf8'))
  const otherSkills = JSON.parse(fs.readFileSync(OTHER_JSON_PATH, 'utf8'))
  const awesomeSkills = JSON.parse(fs.readFileSync(AWESOME_JSON_PATH, 'utf8'))

  const allCatalogs = [
    { name: 'index.json', path: INDEX_JSON_PATH, list: idxSkills },
    { name: 'other_skills.json', path: OTHER_JSON_PATH, list: otherSkills },
    { name: 'awesome_skills.json', path: AWESOME_JSON_PATH, list: awesomeSkills }
  ]

  const allSkills = []
  for (const cat of allCatalogs) {
    for (const skill of cat.list) {
      allSkills.push({
        catalog: cat.name,
        skill: skill
      })
    }
  }

  const skillMap = new Map(allSkills.map(s => [s.skill.id, s]))

  // Formar clusters/grupos de sobreposição
  const visited = new Set()
  const duplicateGroups = []

  for (const item of allSkills) {
    if (visited.has(item.skill.id) || !item.skill.overlaps_ids || item.skill.overlaps_ids.length === 0) {
      continue
    }

    const groupIds = new Set([item.skill.id, ...item.skill.overlaps_ids])
    for (const id of groupIds) {
      const neighbor = skillMap.get(id)
      if (neighbor && Array.isArray(neighbor.skill.overlaps_ids)) {
        neighbor.skill.overlaps_ids.forEach(nId => groupIds.add(nId))
      }
    }

    groupIds.forEach(id => visited.add(id))
    duplicateGroups.push(Array.from(groupIds))
  }

  console.log(`🎯 Total de Grupos de Duplicidade Identificados: ${duplicateGroups.length}`)

  const deprecatedSkillsList = []
  const winnersList = []

  for (const group of duplicateGroups) {
    let bestSkillId = group[0]
    let bestScore = -1
    let bestCompleteness = -1

    for (const id of group) {
      const item = skillMap.get(id)
      if (!item) continue

      const totalImportance = (item.skill.importance_in || []).reduce((acc, cur) => acc + (cur.importance || 0), 0)
      const completeness = (item.skill.languages?.length || 0) + (item.skill.frameworks?.length || 0) + (item.skill.libs?.length || 0)

      // Bônus de especialização: se estiver em index.json (skills oficiais max), tem preferência
      const catalogBonus = item.catalog === 'index.json' ? 20 : (item.catalog === 'other_skills.json' ? 5 : 0)
      const compositeScore = totalImportance * 2 + catalogBonus

      if (compositeScore > bestScore || (compositeScore === bestScore && completeness > bestCompleteness)) {
        bestScore = compositeScore
        bestCompleteness = completeness
        bestSkillId = id
      }
    }

    const winnerItem = skillMap.get(bestSkillId)
    if (winnerItem) {
      winnersList.push({
        id: bestSkillId,
        name: winnerItem.skill.skill_name,
        catalog: winnerItem.catalog,
        groupSize: group.length
      })
    }

    for (const id of group) {
      const item = skillMap.get(id)
      if (!item) continue

      item.skill.overlaps_best_id = bestSkillId
      const isWinner = id === bestSkillId

      if (!isWinner) {
        deprecatedSkillsList.push({
          id: id,
          catalog: item.catalog,
          skill_name: item.skill.skill_name,
          local_path: item.skill.local_path,
          best_id: bestSkillId,
          best_name: winnerItem?.skill?.skill_name,
          reason: `Duplicata preterida em favor da skill eleita como melhor: [${winnerItem?.catalog}] ${winnerItem?.skill?.skill_name}.`
        })
      }

      const msgFase6 = isWinner
        ? `Fase 6 (Eleição): Eleita a MELHOR SKILL do grupo concorrente (ID: ${id}) por maior aderência técnica aos projetos.`
        : `Fase 6 (Eleição): Preterida em favor da skill eleita como melhor (ID: ${bestSkillId} - ${winnerItem?.skill?.skill_name}). Recomendada para remoção por redundância.`

      const existingIdx = item.skill.details.findIndex(d => d.Fase6_Eleicao)
      if (existingIdx >= 0) {
        item.skill.details[existingIdx] = { Fase6_Eleicao: msgFase6 }
      } else {
        item.skill.details.push({ Fase6_Eleicao: msgFase6 })
      }
    }
  }

  for (const cat of allCatalogs) {
    fs.writeFileSync(cat.path, JSON.stringify(cat.list, null, 4), 'utf8')
  }

  const removalPlanPath = path.join(ROOT_DIR, 'scripts', 'phase6_removal_plan.json')
  fs.writeFileSync(removalPlanPath, JSON.stringify(deprecatedSkillsList, null, 2), 'utf8')

  console.log(`✅ Fase 6 Concluída:`)
  console.log(`   - Total de Skills Vencedoras (Mantidas): ${winnersList.length}`)
  console.log(`   - Total de Skills Preteridas (Para Remoção na Fase 7): ${deprecatedSkillsList.length}`)
  console.log(`   - Plano de Remoção salvo em: scripts/phase6_removal_plan.json\n`)
}

runPhase6()
