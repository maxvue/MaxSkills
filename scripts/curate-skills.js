#!/usr/bin/env node

/**
 * Script de Curadoria, Deduplicação e Validação de Skills para MaxCode / MaxSkills.
 *
 * 1. Deduplica skills entre other_skills (YouTube) e awesome_skills (Awesome).
 * 2. Corrige caminhos aninhados em awesome_skills (ex: game-development, security, agent-squad).
 * 3. Valida a integridade referencial de todos os 3 catálogos (index.json, other_skills.json, awesome_skills.json).
 * 4. Remove diretórios duplicados em Agentic Awesome Skills.
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

const ENCODING = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
function generateUlid(timestamp = Date.now()) {
  let timeStr = ''
  for (let i = 9; i >= 0; i--) {
    timeStr = ENCODING[timestamp % 32] + timeStr
    timestamp = Math.floor(timestamp / 32)
  }
  let randStr = ''
  for (let i = 0; i < 16; i++) {
    randStr += ENCODING[Math.floor(Math.random() * 32)]
  }
  return timeStr + randStr
}

function findSkillFiles(dir) {
  let results = []
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  for (const e of entries) {
    const full = path.join(dir, e.name)
    if (e.isDirectory()) {
      const skillMd = path.join(full, 'SKILL.md')
      if (fs.existsSync(skillMd)) {
        results.push({
          dirName: e.name,
          fullDir: full,
          skillMdPath: skillMd,
          relPath: path.relative(ROOT_DIR, skillMd)
        })
      }
      results.push(...findSkillFiles(full).filter(sub => sub.skillMdPath !== skillMd))
    }
  }
  return results
}

function runCuration() {
  console.log('🚀 Iniciando curadoria e deduplicação dos catálogos de skills...')

  const idxJson = JSON.parse(fs.readFileSync(INDEX_JSON_PATH, 'utf8'))
  const otherJson = JSON.parse(fs.readFileSync(OTHER_JSON_PATH, 'utf8'))
  const awesomeOld = JSON.parse(fs.readFileSync(AWESOME_JSON_PATH, 'utf8'))

  const idxNames = new Set(idxJson.map(s => s.skill_name))
  const otherNames = new Set(otherJson.map(s => s.skill_name))
  const oldAwesomeMap = new Map(awesomeOld.map(s => [s.skill_name, s]))

  const awesomeSkillsDir = path.join(ROOT_DIR, 'other_skills/Agentic Awesome Skills/skills')
  const diskSkills = findSkillFiles(awesomeSkillsDir)

  console.log(`📦 Skills encontradas no disco em Agentic Awesome Skills: ${diskSkills.length}`)

  const curatedAwesome = []
  const duplicateDirsToRemove = []

  for (const diskItem of diskSkills) {
    const name = diskItem.dirName
    if (otherNames.has(name) || idxNames.has(name)) {
      duplicateDirsToRemove.push(diskItem.fullDir)
      continue
    }

    const existing = oldAwesomeMap.get(name)
    const relPath = diskItem.relPath
    const encodedRelPath = relPath.split('/').map(seg => encodeURIComponent(seg)).join('/')
    const directUrl = 'https://raw.githubusercontent.com/maxvue/MaxSkills/main/' + encodedRelPath

    if (existing) {
      curatedAwesome.push({
        id: existing.id || generateUlid(),
        skill_name: existing.skill_name || name,
        description_en: existing.description_en,
        description_pt_br: existing.description_pt_br,
        promo_en: existing.promo_en,
        promo_pt_br: existing.promo_pt_br,
        repo_name: 'Awesome',
        url_skill: directUrl,
        languages: existing.languages || [],
        frameworks: existing.frameworks || [],
        libs: existing.libs || []
      })
    } else {
      const content = fs.readFileSync(diskItem.skillMdPath, 'utf8')
      let desc = ''
      const match = content.match(/description:\s*([^\n\r]+)/i)
      if (match) {
        desc = match[1].trim().replace(/^["\x27]|["\x27]$/g, '')
      }
      curatedAwesome.push({
        id: generateUlid(),
        skill_name: name,
        description_en: desc || `Production-ready guidelines and agentic workflows for ${name}.`,
        description_pt_br: `Diretrizes e fluxos agênticos para ${name.replace(/-/g, ' ')}.`,
        promo_en: `Production-ready guidelines and agentic workflows for ${name}. Enforces best practices, maintainability, and error-free execution.`,
        promo_pt_br: `Diretrizes e fluxos agênticos para ${name.replace(/-/g, ' ')}. Assegura melhores práticas, manutenibilidade e execução padronizada em projetos.`,
        repo_name: 'Awesome',
        url_skill: directUrl,
        languages: [],
        frameworks: [],
        libs: []
      })
    }
  }

  curatedAwesome.sort((a, b) => a.skill_name.localeCompare(b.skill_name))

  console.log(`✨ Skills deduplicadas em awesome_skills.json: ${curatedAwesome.length}`)
  console.log(`🗑️  Diretórios duplicados identificados para remoção: ${duplicateDirsToRemove.length}`)

  // Gravar awesome_skills.json atualizado
  fs.writeFileSync(AWESOME_JSON_PATH, JSON.stringify(curatedAwesome, null, 4) + '\n', 'utf8')
  console.log(`✅ awesome_skills.json atualizado com sucesso.`)

  // Remover diretórios duplicados do disco em Agentic Awesome Skills
  for (const dir of duplicateDirsToRemove) {
    if (fs.existsSync(dir)) {
      fs.rmSync(dir, { recursive: true, force: true })
    }
  }
  console.log(`✅ Diretórios duplicados removidos com sucesso.`)

  // Validação final de integridade de todos os catálogos
  console.log('\n🔍 Executando validação cruzada de todos os catálogos...')

  function validateCatalog(catalog, name) {
    let broken = 0
    const ids = new Set()
    for (const item of catalog) {
      if (!item.id || ids.has(item.id)) {
        console.error(`❌ [${name}] ID duplicado ou inválido: ${item.skill_name} (${item.id})`)
        broken++
      }
      ids.add(item.id)

      const rawPrefix = 'https://raw.githubusercontent.com/maxvue/MaxSkills/main/'
      if (!item.url_skill || !item.url_skill.startsWith(rawPrefix)) {
        console.error(`❌ [${name}] URL com prefixo inválido: ${item.skill_name}`)
        broken++
        continue
      }

      const rel = decodeURIComponent(item.url_skill.slice(rawPrefix.length))
      const full = path.join(ROOT_DIR, rel)
      if (!fs.existsSync(full)) {
        console.error(`❌ [${name}] Arquivo não encontrado no disco: ${item.skill_name} (${rel})`)
        broken++
      }
    }
    if (broken === 0) {
      console.log(`✅ [${name}] 100% íntegro (${catalog.length} skills, 0 erros).`)
    } else {
      console.error(`❌ [${name}] Encontrados ${broken} problemas.`)
    }
    return broken === 0
  }

  const okIdx = validateCatalog(idxJson, 'index.json')
  const okOther = validateCatalog(otherJson, 'other_skills.json')
  const okAwesome = validateCatalog(curatedAwesome, 'awesome_skills.json')

  if (okIdx && okOther && okAwesome) {
    console.log('\n🎉 Todos os 3 catálogos de skills estão perfeitamente curados, deduplicados e validados!')
  } else {
    throw new Error('Falha na validação final dos catálogos de skills.')
  }
}

runCuration()
