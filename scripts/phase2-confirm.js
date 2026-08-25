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

function getDetailedReason(skill) {
  const text = [
    skill.skill_name || '',
    skill.description_en || '',
    (skill.languages || []).join(' '),
    (skill.frameworks || []).join(' '),
    (skill.libs || []).join(' ')
  ].join(' ').toLowerCase()

  const techMap = [
    { key: 'flutter', label: 'Flutter / Dart' },
    { key: 'swift', label: 'Swift / iOS / Xcode' },
    { key: 'kotlin', label: 'Kotlin / Android' },
    { key: 'unity', label: 'Unity 3D' },
    { key: 'unreal', label: 'Unreal Engine' },
    { key: 'godot', label: 'Godot Engine' },
    { key: 'roblox', label: 'Roblox / Lua' },
    { key: 'lua', label: 'Lua Scripting' },
    { key: 'rails', label: 'Ruby on Rails' },
    { key: 'django', label: 'Python / Django' },
    { key: 'flask', label: 'Python / Flask' },
    { key: 'spring', label: 'Java / Spring Boot' },
    { key: 'csharp', label: 'C# / .NET' },
    { key: 'dotnet', label: '.NET Core' },
    { key: 'angular', label: 'Angular Framework' },
    { key: 'svelte', label: 'Svelte / SvelteKit' },
    { key: 'solidjs', label: 'SolidJS' },
    { key: 'solidity', label: 'Solidity / Smart Contracts / Web3' },
    { key: 'drupal', label: 'Drupal CMS' },
    { key: 'wordpress', label: 'WordPress Themes / Plugins' },
    { key: 'rust', label: 'Rust Systems / Embedded' },
    { key: 'cuda', label: 'CUDA / GPU Low-level' },
    { key: 'assembly', label: 'Assembly / Low-level Hardware' },
    { key: 'c++', label: 'C++ Systems' }
  ]

  for (const { key, label } of techMap) {
    if (text.includes(key)) {
      return `Tecnologia exclusiva (${label}) sem qualquer aderência à stack dos projetos (PHP/Laravel, Vue 3, TS, Gemini).`
    }
  }

  return 'Sem qualquer correlação técnica, funcional ou de domínio com os projetos engeapp, SocialMedia e Agentedebolso.'
}

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
        const specificReason = getDetailedReason(skill)
        fase2Msg = `Fase 2 (Confirmação): Confirmada como INÚTIL para todos os 3 projetos (engeapp: 0, SocialMedia: 0, Agentedebolso: 0). ${specificReason}`
        uselessSkills.push({
          id: skill.id,
          catalog: cat.name,
          skill_name: skill.skill_name,
          local_path: skill.local_path,
          description: (skill.description_en || '').slice(0, 140),
          reason: specificReason
        })
      } else {
        confirmedUsefulCount++
        fase2Msg = `Fase 2 (Confirmação): Relevância confirmada com nota máxima ${maxScore}/10 (engeapp: ${engeappScore}, SocialMedia: ${socialScore}, Agentedebolso: ${agenteScore}). Mantida no catálogo.`
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

  // Salvar lista de remoção da fase 2 para auditoria e execução na Fase 3
  const removalPlanPath = path.join(ROOT_DIR, 'scripts', 'phase2_removal_plan.json')
  fs.writeFileSync(removalPlanPath, JSON.stringify(uselessSkills, null, 2), 'utf8')

  console.log(`✅ Fase 2 Concluída:`)
  console.log(`   - Skills Confirmadas como Úteis: ${confirmedUsefulCount}`)
  console.log(`   - Skills Confirmadas como Inúteis para Remoção: ${uselessSkills.length}`)
  console.log(`   - Plano de remoção salvo em: scripts/phase2_removal_plan.json\n`)
}

runPhase2()
