#!/usr/bin/env node

/**
 * Script de Execução da FASE 5: CONFIRMAÇÃO E REFUTAÇÃO PROFUNDA DE DUPLICIDADES
 * Analisa conteúdo interno de SKILL.md e refuta falsos positivos.
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

function normalizeTokens(str) {
  return (str || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(t => t.length > 2)
}

function calculateJaccardSimilarity(setA, setB) {
  if (setA.size === 0 || setB.size === 0) return 0
  let intersection = 0
  for (const item of setA) {
    if (setB.has(item)) intersection++
  }
  const union = new Set([...setA, ...setB]).size
  return intersection / union
}

function readSkillMdSample(localPath) {
  if (!localPath) return ''
  const fullPath = path.isAbsolute(localPath) ? localPath : path.join(ROOT_DIR, localPath)
  if (!fs.existsSync(fullPath)) return ''
  try {
    const content = fs.readFileSync(fullPath, 'utf8')
    return content.slice(0, 5000)
  } catch {
    return ''
  }
}

function runPhase5() {
  console.log('🚀 Executando Fase 5: Refutação e Confirmação de Duplicidades por Conteúdo...\n')

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
        skill: skill,
        nameTokens: new Set(normalizeTokens(skill.skill_name || '')),
        descTokens: new Set(normalizeTokens(skill.description_en || ''))
      })
    }
  }

  const skillMap = new Map(allSkills.map(s => [s.skill.id, s]))

  let totalConfirmedOverlaps = 0
  let refutedCount = 0

  for (const item of allSkills) {
    const originalOverlaps = item.skill.overlaps_ids || []
    if (originalOverlaps.length === 0) {
      const existingIdx = item.skill.details.findIndex(d => d.Fase5_Refutacao)
      const msg = 'Fase 5 (Refutação): Skill única validada. Nenhuma duplicidade concorrente.'
      if (existingIdx >= 0) item.skill.details[existingIdx] = { Fase5_Refutacao: msg }
      else item.skill.details.push({ Fase5_Refutacao: msg })
      continue
    }

    const verifiedOverlaps = []
    const contentA = readSkillMdSample(item.skill.local_path)
    const tokensContentA = new Set(normalizeTokens(contentA))

    for (const oId of originalOverlaps) {
      const otherItem = skillMap.get(oId)
      if (!otherItem) continue

      const nameSim = calculateJaccardSimilarity(item.nameTokens, otherItem.nameTokens)
      const descSim = calculateJaccardSimilarity(item.descTokens, otherItem.descTokens)

      const contentB = readSkillMdSample(otherItem.skill.local_path)
      const tokensContentB = new Set(normalizeTokens(contentB))
      const contentSim = calculateJaccardSimilarity(tokensContentA, tokensContentB)

      // Regra de Refutação de Falso Positivo:
      const fwA = (item.skill.frameworks || []).join(' ').toLowerCase()
      const fwB = (otherItem.skill.frameworks || []).join(' ').toLowerCase()
      const isConflictingFramework = (fwA && fwB && fwA !== fwB && !fwA.includes(fwB) && !fwB.includes(fwA) && nameSim < 0.6)

      if (isConflictingFramework) {
        refutedCount++
        continue // Falso positivo refutado
      }

      // Duplicidade confirmada se o conteúdo interno se sobrepõe
      if (contentSim >= 0.20 || (contentSim >= 0.15 && descSim >= 0.35) || nameSim >= 0.50) {
        verifiedOverlaps.push(oId)
      } else {
        refutedCount++
      }
    }

    item.skill.overlaps_ids = verifiedOverlaps

    let fase5Msg = ''
    if (verifiedOverlaps.length > 0) {
      totalConfirmedOverlaps++
      fase5Msg = `Fase 5 (Refutação): Duplicidade real confirmada por análise de conteúdo interno com ${verifiedOverlaps.length} skill(s) concorrente(s). Não devem ser utilizadas juntas.`
    } else {
      fase5Msg = `Fase 5 (Refutação): Falsos positivos refutados por análise de conteúdo interno. Tratam de escopos complementares e independentes.`
    }

    const existingIdx = item.skill.details.findIndex(d => d.Fase5_Refutacao)
    if (existingIdx >= 0) {
      item.skill.details[existingIdx] = { Fase5_Refutacao: fase5Msg }
    } else {
      item.skill.details.push({ Fase5_Refutacao: fase5Msg })
    }
  }

  for (const cat of allCatalogs) {
    fs.writeFileSync(cat.path, JSON.stringify(cat.list, null, 4), 'utf8')
  }

  console.log(`✅ Fase 5 Concluída:`)
  console.log(`   - Falsos Positivos Refutados: ${refutedCount}`)
  console.log(`   - Skills com Duplicidade Real Confirmada: ${totalConfirmedOverlaps}`)
  console.log(`   - Atualização persistida em index.json, other_skills.json e awesome_skills.json.\n`)
}

runPhase5()
