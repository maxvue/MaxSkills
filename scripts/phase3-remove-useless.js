#!/usr/bin/env node

/**
 * Script de Execução da FASE 3: REMOÇÃO DE SKILLS INÚTEIS
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
const REMOVAL_PLAN_PATH = path.join(ROOT_DIR, 'scripts', 'phase2_removal_plan.json')

function runPhase3() {
  console.log('🚀 Executando Fase 3: Remoção de Skills Inúteis dos Catálogos e Disco...\n')

  const removalPlan = JSON.parse(fs.readFileSync(REMOVAL_PLAN_PATH, 'utf8'))
  const removalIds = new Set(removalPlan.map(s => s.id))

  const idxSkills = JSON.parse(fs.readFileSync(INDEX_JSON_PATH, 'utf8'))
  const otherSkills = JSON.parse(fs.readFileSync(OTHER_JSON_PATH, 'utf8'))
  const awesomeSkills = JSON.parse(fs.readFileSync(AWESOME_JSON_PATH, 'utf8'))

  const allCatalogs = [
    { name: 'index.json', path: INDEX_JSON_PATH, list: idxSkills },
    { name: 'other_skills.json', path: OTHER_JSON_PATH, list: otherSkills },
    { name: 'awesome_skills.json', path: AWESOME_JSON_PATH, list: awesomeSkills }
  ]

  let totalRemoved = 0
  let filesDeleted = 0
  const stats = {}

  for (const cat of allCatalogs) {
    const originalCount = cat.list.length
    const remaining = []

    for (const skill of cat.list) {
      if (removalIds.has(skill.id)) {
        totalRemoved++
        // Deletar pasta no disco
        if (skill.local_path) {
          const fullPath = path.join(ROOT_DIR, skill.local_path)
          const skillDir = path.dirname(fullPath)
          try {
            if (fs.existsSync(skillDir) && skillDir !== ROOT_DIR) {
              fs.rmSync(skillDir, { recursive: true, force: true })
              filesDeleted++
            }
          } catch (err) {
            console.error(`Erro ao deletar ${skillDir}:`, err.message)
          }
        }
      } else {
        remaining.push(skill)
      }
    }

    cat.list = remaining
    fs.writeFileSync(cat.path, JSON.stringify(cat.list, null, 4), 'utf8')
    stats[cat.name] = {
      before: originalCount,
      after: cat.list.length,
      removed: originalCount - cat.list.length
    }
  }

  console.log(`✅ Fase 3 Concluída com Sucesso!`)
  console.log(`   - Total de Skills Removidas dos JSONs: ${totalRemoved}`)
  console.log(`   - Pastas Físicas Deletadas do Disco: ${filesDeleted}`)
  console.log(`\nDetalhes por Catálogo:`)
  for (const [catName, data] of Object.entries(stats)) {
    console.log(`   - ${catName}: ${data.before} -> ${data.after} (Removidas: ${data.removed})`)
  }
}

runPhase3()
