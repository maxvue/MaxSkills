#!/usr/bin/env node

/**
 * Script de Execução da FASE 4: ANÁLISE CONJUNTA DE DUPLICIDADES E SOBREPOSIÇÕES
 * Analisa exclusivamente o campo description_en em index.json, other_skills.json, awesome_skills.json
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
  'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
  'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were',
  'will', 'with', 'use', 'when', 'covers', 'best', 'practices', 'guidelines',
  'how', 'this', 'into', 'your', 'using', 'build', 'building', 'create',
  'creating', 'help', 'helps', 'guide', 'tools', 'tool', 'code', 'project',
  'projects', 'expert', 'provides', 'providing', 'comprehensive', 'rules',
  'triggers', 'trigger', 'agent', 'assistant'
])

function normalizeTokens(str) {
  return (str || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s_-]/g, ' ')
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

function calculateCosineTFIDF(tokensA, tokensB) {
  const tfA = {}
  const tfB = {}
  for (const t of tokensA) tfA[t] = (tfA[t] || 0) + 1
  for (const t of tokensB) tfB[t] = (tfB[t] || 0) + 1

  let dotProduct = 0
  for (const [k, v] of Object.entries(tfA)) {
    if (tfB[k]) {
      dotProduct += v * tfB[k]
    }
  }

  let magA = 0
  for (const v of Object.values(tfA)) magA += v * v
  let magB = 0
  for (const v of Object.values(tfB)) magB += v * v

  if (magA === 0 || magB === 0) return 0
  return dotProduct / (Math.sqrt(magA) * Math.sqrt(magB))
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
      const rawTokens = normalizeTokens(skill.description_en || '')
      unifiedList.push({
        catalog: cat.name,
        skill: skill,
        rawTokens: rawTokens,
        tokenSet: new Set(rawTokens)
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

      const jaccard = calculateJaccardSimilarity(itemA.tokenSet, itemB.tokenSet)
      const cosine = calculateCosineTFIDF(itemA.rawTokens, itemB.rawTokens)

      // Sobreposição identificada em description_en quando similaridade semântica / tokens é alta
      if (jaccard >= 0.35 || cosine >= 0.45) {
        overlaps.push(itemB.skill.id)
      }
    }

    itemA.skill.overlaps_ids = overlaps

    let fase4Msg = ''
    if (overlaps.length > 0) {
      countWithOverlaps++
      fase4Msg = `Fase 4 (Duplicidades): Sobreposição de escopo em description_en identificada com ${overlaps.length} skill(s) concorrente(s): [${overlaps.join(', ')}].`
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
  console.log(`\nExemplos de sobreposição detectados em description_en:`)
  sampleOverlaps.forEach(s => console.log(`   - [${s.catalog}] ${s.name} -> Sobrepõe ${s.overlapsCount} skill(s)`))
}

runPhase4()
