#!/usr/bin/env node

/**
 * Script de Execução da FASE 4: ANÁLISE CONJUNTA DE DUPLICIDADES E SOBREPOSIÇÕES
 * Analisa description_en em index.json, other_skills.json, awesome_skills.json
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

const STOPWORDS = new Set([
  'and', 'for', 'the', 'with', 'use', 'when', 'covers', 'best', 'practices', 'guidelines',
  'how', 'this', 'that', 'from', 'into', 'your', 'using', 'build', 'building', 'create',
  'creating', 'help', 'helps', 'guide', 'tools', 'tool', 'code', 'project', 'projects'
])

function normalizeTokens(str) {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(t => t.length > 2 && !STOPWORDS.has(t))
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

function runPhase4() {
  console.log('🚀 Executando Fase 4: Detecção de Duplicidades e Sobreposições por description_en...\n')

  const idxSkills = JSON.parse(fs.readFileSync(INDEX_JSON_PATH, 'utf8'))
  const otherSkills = JSON.parse(fs.readFileSync(OTHER_JSON_PATH, 'utf8'))
  const awesomeSkills = JSON.parse(fs.readFileSync(AWESOME_JSON_PATH, 'utf8'))

  const allCatalogs = [
    { name: 'index.json', path: INDEX_JSON_PATH, list: idxSkills },
    { name: 'other_skills.json', path: OTHER_JSON_PATH, list: otherSkills },
    { name: 'awesome_skills.json', path: AWESOME_JSON_PATH, list: awesomeSkills }
  ]

  const unifiedList = []
  for (const cat of allCatalogs) {
    for (const skill of cat.list) {
      unifiedList.push({
        catalog: cat.name,
        skill: skill,
        descTokens: new Set(normalizeTokens(skill.description_en || '')),
        nameTokens: new Set(normalizeTokens(skill.skill_name || ''))
      })
    }
  }

  console.log(`📦 Analisando ${unifiedList.length} skills transversalmente entre todos os catálogos...`)

  let countWithOverlaps = 0
  let countUnique = 0
  const sampleOverlaps = []

  for (let i = 0; i < unifiedList.length; i++) {
    const itemA = unifiedList[i]
    const overlaps = []

    for (let j = 0; j < unifiedList.length; j++) {
      if (i === j) continue
      const itemB = unifiedList[j]

      const descSim = calculateJaccardSimilarity(itemA.descTokens, itemB.descTokens)
      const nameSim = calculateJaccardSimilarity(itemA.nameTokens, itemB.nameTokens)

      // Critério de sobreposição semântica em description_en ou nome da skill
      if (descSim >= 0.40 || nameSim >= 0.70 || (descSim >= 0.30 && nameSim >= 0.40)) {
        overlaps.push(itemB.skill.id)
      }
    }

    itemA.skill.overlaps_ids = overlaps

    let fase4Msg = ''
    if (overlaps.length > 0) {
      countWithOverlaps++
      fase4Msg = `Fase 4 (Duplicidades): Sobreposição identificada com ${overlaps.length} skill(s) concorrente(s): [${overlaps.join(', ')}].`
      if (sampleOverlaps.length < 5) {
        sampleOverlaps.push({
          catalog: itemA.catalog,
          name: itemA.skill.skill_name,
          overlapsCount: overlaps.length
        })
      }
    } else {
      countUnique++
      fase4Msg = `Fase 4 (Duplicidades): Nenhuma sobreposição ou duplicidade detectada no escopo de description_en.`
    }

    const existingIdx = itemA.skill.details.findIndex(d => d.Fase4_Duplicidades)
    if (existingIdx >= 0) {
      itemA.skill.details[existingIdx] = { Fase4_Duplicidades: fase4Msg }
    } else {
      itemA.skill.details.push({ Fase4_Duplicidades: fase4Msg })
    }
  }

  for (const cat of allCatalogs) {
    fs.writeFileSync(cat.path, JSON.stringify(cat.list, null, 4), 'utf8')
  }

  console.log(`✅ Fase 4 Concluída:`)
  console.log(`   - Skills Únicas (overlaps_ids: []): ${countUnique}`)
  console.log(`   - Skills com Sobreposições (overlaps_ids preenchido): ${countWithOverlaps}`)
  console.log(`\nExemplos de sobreposição detectados:`)
  sampleOverlaps.forEach(s => console.log(`   - [${s.catalog}] ${s.name} -> Sobrepõe ${s.overlapsCount} skill(s)`))
}

runPhase4()
