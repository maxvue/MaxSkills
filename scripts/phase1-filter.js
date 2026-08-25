#!/usr/bin/env node

/**
 * Script de Execução da FASE 1: FILTRO DE RELEVÂNCIA POR PROJETO
 * Projetos: engeapp, SocialMedia, Agentedebolso
 * Catálogos: index.json, other_skills.json, awesome_skills.json
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

const PROJECTS_CONFIG = {
  engeapp: {
    name: 'engeapp',
    highKeywords: [
      'laravel', 'vue', 'vue 3', 'vue3', 'unocss', 'max-components-ui', 'max-pinia', 'max-use',
      'livekit', 'webrtc', 'meilisearch', 'gemini', 'bigquery', 'whatsapp', 'asaas', 'efi', 'inter',
      'spatie', 'horizon', 'octane', 'pulse', 'reverb', 'sanctum', 'scout', 'telescope',
      'pdf', 'excel', 'phpspreadsheet', 'dompdf', 'mpdf', 'autentique', 'cpf', 'cnpj', 'boleto',
      'google maps', 'proj4', 'vuefinder', 'puppeteer', 'pest', 'typescript', 'tailwind'
    ],
    mediumKeywords: [
      'php', 'javascript', 'pinia', 'radix', 'reka', 'floating-vue', 'chart.js', 'dayjs',
      'clean architecture', 'systematic-debugging', 'tdd', 'test-driven', 'security', 'owasp',
      'docker', 'redis', 'api design', 'rest api', 'webhook', 'database', 'sql', 'mysql', 'postgresql',
      'ui', 'ux', 'frontend'
    ]
  },
  SocialMedia: {
    name: 'SocialMedia',
    highKeywords: [
      'social media', 'calendar', 'fullcalendar', 'mediapipe', 'vision', 'video', 'image processing',
      'vue', 'vue 3', 'vue3', 'pinia', 'max-components-ui', 'max-pinia', 'max-use', 'vueuse', 'vue router',
      'laravel', 'horizon', 'sanctum', 'socialite', 'spatie', 'pdf-to-text', 'ai content', 'copywriting',
      'instagram', 'tiktok', 'youtube', 'facebook', 'linkedin', 'marketing', 'seo', 'content strategy',
      'prompt engineering'
    ],
    mediumKeywords: [
      'php', 'javascript', 'typescript', 'axios', 'localforage', 'ziggy', 'tailwind', 'css',
      'systematic-debugging', 'frontend-design', 'ui', 'ux', 'analytics', 'clean architecture',
      'tdd', 'test-driven', 'docker', 'redis', 'api design', 'rest api', 'webhook'
    ]
  },
  Agentedebolso: {
    name: 'Agentedebolso',
    highKeywords: [
      'ai agents', 'agent', 'conversational ai', 'whatsapp', 'bot', 'gemini', 'llm', 'function calling',
      'voice recording', 'speech-to-text', 'transcription', 'ffmpeg', 'puppeteer', 'scraping',
      'laravel', 'vue', 'vue 3', 'vue3', 'radix', 'tailwind', 'sass', 'sweetalert2', 'emoji', 'quill',
      'brasilapi', 'webauthn', 'meilisearch', 'autentique', 'efi', 'inter', 'max-components-ui',
      'max-pinia', 'max-use', 'vuefinder', 'multitenant', 'agent-orchestrator', 'token-optimization'
    ],
    mediumKeywords: [
      'php', 'javascript', 'typescript', 'pinia', 'vite', 'octane', 'reverb', 'horizon', 'sanctum',
      'scout', 'systematic-debugging', 'security', 'owasp', 'api design', 'rest api', 'webhook',
      'database', 'sql', 'mysql', 'clean architecture', 'tdd', 'test-driven', 'ui', 'ux'
    ]
  }
}

const IRRELEVANT_PATTERNS = [
  /\b(flutter|dart)\b/i,
  /\b(swift|swiftui|xcode|objective-c|ios-only)\b/i,
  /\b(kotlin|android-studio|jetpack-compose)\b/i,
  /\b(unity|unreal-engine|godot|c-sharp-gamedev|roblox|lua-scripting)\b/i,
  /\b(ruby-on-rails|rails-only|django|flask|spring-boot|dotnet|csharp|\.net-core)\b/i,
  /\b(angular|svelte|solidjs|emberjs)\b/i,
  /\b(rust-embedded|c\+\+|verilog|vhdl|cuda|assembly)\b/i,
  /\b(solidity|smart-contracts|web3|ethereum|blockchain-defi)\b/i,
  /\b(drupal|joomla|magento|prestashop|wordpress-theme)\b/i
]

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function matchKeyword(kw, text) {
  const escaped = escapeRegExp(kw.toLowerCase())
  const regex = new RegExp(`(^|[^a-z0-9_-])${escaped}([^a-z0-9_-]|$)`, 'i')
  return regex.test(text)
}

function getLocalRelativePath(urlSkill) {
  if (!urlSkill) return null
  const decoded = decodeURIComponent(urlSkill)
  return decoded.replace('https://raw.githubusercontent.com/maxvue/MaxSkills/main/', '')
}

function calculateImportance(skill, projectConfig) {
  const textToAnalyze = [
    skill.skill_name || '',
    skill.description_en || '',
    skill.description_pt_br || '',
    skill.promo_en || '',
    (skill.languages || []).join(' '),
    (skill.frameworks || []).join(' '),
    (skill.libs || []).join(' ')
  ].join(' ').toLowerCase()

  for (const pattern of IRRELEVANT_PATTERNS) {
    if (pattern.test(textToAnalyze)) {
      if (!/\b(laravel|vue|vue3|php|typescript|javascript)\b/i.test(textToAnalyze)) {
        return { score: 0, reason: 'Stack tecnológica não utilizada no projeto (exclusiva de outro ecossistema).' }
      }
    }
  }

  let highMatches = 0
  let highHits = []
  for (const kw of projectConfig.highKeywords) {
    if (matchKeyword(kw, textToAnalyze)) {
      highMatches++
      highHits.push(kw)
    }
  }

  let mediumMatches = 0
  let mediumHits = []
  for (const kw of projectConfig.mediumKeywords) {
    if (matchKeyword(kw, textToAnalyze)) {
      mediumMatches++
      mediumHits.push(kw)
    }
  }

  let score = 0
  let reason = ''

  if (highMatches >= 4) {
    score = 10
    reason = `Altíssimo alinhamento direto com a arquitetura core (${highHits.slice(0, 3).join(', ')}).`
  } else if (highMatches === 3) {
    score = 9
    reason = `Excelente alinhamento com pacotes e serviços essenciais (${highHits.join(', ')}).`
  } else if (highMatches === 2) {
    score = 8
    reason = `Forte aderência funcional e técnica (${highHits.join(', ')}).`
  } else if (highMatches === 1) {
    score = mediumMatches >= 2 ? 7 : 6
    reason = `Aderência a módulo específico do projeto (${highHits[0]}).`
  } else if (mediumMatches >= 3) {
    score = 5
    reason = `Boa utilidade para padrões gerais de engenharia e stack (${mediumHits.slice(0, 3).join(', ')}).`
  } else if (mediumMatches === 2) {
    score = 4
    reason = `Utilidade moderada em práticas gerais (${mediumHits.join(', ')}).`
  } else if (mediumMatches === 1) {
    score = 3
    reason = `Baixa aderência, aplicável apenas como suporte secundário (${mediumHits[0]}).`
  } else {
    if (/\b(git|debug|test|refactor|architecture|api|security|auth|performance|sql|database|markdown|documentation)\b/i.test(textToAnalyze)) {
      score = 3
      reason = 'Prática genérica de engenharia de software aplicável genericamente.'
    } else {
      score = 0
      reason = 'Nenhuma aderência com a stack ou domínio do projeto.'
    }
  }

  return { score, reason }
}

function runPhase1() {
  console.log('🚀 Executando Fase 1: Filtro de Relevância nos 3 Catálogos...\n')

  const idxSkills = JSON.parse(fs.readFileSync(INDEX_JSON_PATH, 'utf8'))
  const otherSkills = JSON.parse(fs.readFileSync(OTHER_JSON_PATH, 'utf8'))
  const awesomeSkills = JSON.parse(fs.readFileSync(AWESOME_JSON_PATH, 'utf8'))

  const allCatalogs = [
    { name: 'index.json', path: INDEX_JSON_PATH, list: idxSkills },
    { name: 'other_skills.json', path: OTHER_JSON_PATH, list: otherSkills },
    { name: 'awesome_skills.json', path: AWESOME_JSON_PATH, list: awesomeSkills }
  ]

  let totalSkills = 0
  const stats = {
    engeapp: { 0: 0, low: 0, mid: 0, high: 0 },
    SocialMedia: { 0: 0, low: 0, mid: 0, high: 0 },
    Agentedebolso: { 0: 0, low: 0, mid: 0, high: 0 },
    allZero: 0
  }

  const sampleTopSkills = {
    engeapp: [],
    SocialMedia: [],
    Agentedebolso: []
  }

  for (const cat of allCatalogs) {
    totalSkills += cat.list.length
    for (const skill of cat.list) {
      const relPath = getLocalRelativePath(skill.url_skill)
      skill.local_path = relPath

      if (!Array.isArray(skill.details)) {
        skill.details = []
      }

      const resEngeapp = calculateImportance(skill, PROJECTS_CONFIG.engeapp)
      const resSocial = calculateImportance(skill, PROJECTS_CONFIG.SocialMedia)
      const resAgente = calculateImportance(skill, PROJECTS_CONFIG.Agentedebolso)

      skill.importance_in = [
        { project: 'engeapp', importance: resEngeapp.score },
        { project: 'SocialMedia', importance: resSocial.score },
        { project: 'Agentedebolso', importance: resAgente.score }
      ]

      const maxScore = Math.max(resEngeapp.score, resSocial.score, resAgente.score)
      const fase1Msg = `Fase 1 (Filtro): Notas atribuídas - engeapp: ${resEngeapp.score} (${resEngeapp.reason}), SocialMedia: ${resSocial.score} (${resSocial.reason}), Agentedebolso: ${resAgente.score} (${resAgente.reason}). Nota Máxima: ${maxScore}/10.`

      const existingIdx = skill.details.findIndex(d => d.Fase1)
      if (existingIdx >= 0) {
        skill.details[existingIdx] = { Fase1: fase1Msg }
      } else {
        skill.details.push({ Fase1: fase1Msg })
      }

      // Stats
      function updateStat(pName, score) {
        if (score === 0) stats[pName][0]++
        else if (score <= 3) stats[pName].low++
        else if (score <= 6) stats[pName].mid++
        else stats[pName].high++
      }

      updateStat('engeapp', resEngeapp.score)
      updateStat('SocialMedia', resSocial.score)
      updateStat('Agentedebolso', resAgente.score)

      if (maxScore === 0) {
        stats.allZero++
      }

      if (resEngeapp.score >= 8 && sampleTopSkills.engeapp.length < 5) {
        sampleTopSkills.engeapp.push({ name: skill.skill_name, score: resEngeapp.score, catalog: cat.name })
      }
      if (resSocial.score >= 8 && sampleTopSkills.SocialMedia.length < 5) {
        sampleTopSkills.SocialMedia.push({ name: skill.skill_name, score: resSocial.score, catalog: cat.name })
      }
      if (resAgente.score >= 8 && sampleTopSkills.Agentedebolso.length < 5) {
        sampleTopSkills.Agentedebolso.push({ name: skill.skill_name, score: resAgente.score, catalog: cat.name })
      }
    }

    fs.writeFileSync(cat.path, JSON.stringify(cat.list, null, 4), 'utf8')
  }

  console.log(`📊 Relatório da Fase 1:`)
  console.log(`- Total de Skills Processadas: ${totalSkills}`)
  console.log(`  • index.json: ${idxSkills.length}`)
  console.log(`  • other_skills.json: ${otherSkills.length}`)
  console.log(`  • awesome_skills.json: ${awesomeSkills.length}`)
  console.log(`\n- Distribuição de Relevância:`)
  console.log(`  • engeapp: [0: ${stats.engeapp[0]}, Baixa (1-3): ${stats.engeapp.low}, Média (4-6): ${stats.engeapp.mid}, Alta (7-10): ${stats.engeapp.high}]`)
  console.log(`  • SocialMedia: [0: ${stats.SocialMedia[0]}, Baixa (1-3): ${stats.SocialMedia.low}, Média (4-6): ${stats.SocialMedia.mid}, Alta (7-10): ${stats.SocialMedia.high}]`)
  console.log(`  • Agentedebolso: [0: ${stats.Agentedebolso[0]}, Baixa (1-3): ${stats.Agentedebolso.low}, Média (4-6): ${stats.Agentedebolso.mid}, Alta (7-10): ${stats.Agentedebolso.high}]`)
  console.log(`\n- Skills com Nota 0 em TODOS os 3 projetos (Candidatas à remoção na Fase 2): ${stats.allZero}`)
}

runPhase1()
