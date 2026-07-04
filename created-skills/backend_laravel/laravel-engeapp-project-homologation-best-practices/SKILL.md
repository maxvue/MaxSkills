---
name: laravel-engeapp-project-homologation-best-practices
description: Use when managing solar project homologation flows, tracking concessionaire submittals, managing concessionaire rules/requirements, or tracking protocol statuses for solar integration projects in the Engeapp ecosystem.
---

# Laravel Engeapp Project Homologation Best Practices

## Objetivo
Estabelecer diretrizes padrão para gerenciar os fluxos de homologação de projetos fotovoltaicos solares junto às concessionárias de energia dentro do ecossistema Engeapp, garantindo conformidade com as regulamentações técnicas das subsidiárias locais, o rastreamento correto de protocolos e a validação da documentação obrigatória.

## Instruções

### 1. Validação das Regulamentações Técnicas da Concessionária
Ao lidar com validações de projeto elétrico e aprovações de projetos:
- Sempre referencie o model `ConcessionaireSubsidiaryRegulation` para obter as capacidades permitidas de disjuntores e condutores com base nas fases de instalação (monofásica, bifásica, trifásica) e nas tensões de linha (127V, 220V).
- Valide os cálculos antes de despachar os envios (submittals) para prevenir a rejeição pela concessionária. Os parâmetros são armazenados nas tabelas `concessionaires_subsidiaries_regulations` e nas tabelas `data` relacionadas.
- Use verificações explícitas utilizando os atributos dinâmicos do model, como `$regulation->mono_127`, `$regulation->mono_220`, `$regulation->bi_127`, etc.

### 2. Ciclo de Vida & Auditoria do Protocolo de Homologação
- Todos os envios e interações com a concessionária devem gerar um registro `Protocol`.
- Implemente a trait `HasProtocol` nos models que precisam de associação direta com protocolos da concessionária (ex.: `Project`, `PlannerCard`).
- Toda transição de status (ex.: "Enviado", "Em Análise", "Pendente de Correções", "Aprovado") deve ser rastreada. Atualizações em um protocolo devem sincronizar automaticamente entre o projeto e o planner card via `HasProtocol::setProtocol()`.
- Use queue workers ou tarefas do scheduler para monitorar as datas de expiração dos protocolos (`expires_at`) e gerar alertas para prazos iminentes da concessionária.

### 3. Desacoplamento da Lógica de Negócio de Homologação
- Não coloque lógica de validação ou de persistência no banco de dados dentro dos controllers.
- Implemente todas as ações específicas de homologação dentro de um `HomologationService` dedicado.
- O service deve orquestrar:
  1. Validar os inputs técnicos contra a `ConcessionaireSubsidiaryRegulation` selecionada.
  2. Verificar a presença dos documentos exigidos (ex.: Procuração via `ProjectPowerOfAttorneyDocument`, Diagramas Unifilares, Memoriais Descritivos).
  3. Gerar e atribuir um novo `Protocol` ao projeto e ao planner card.
  4. Disparar notificações para o cliente, projetista ou empresa solar com base nos checkboxes (`notify_client`, `notify_designer`, `notify_solar_company`).

### 4. Validação e UI no Frontend Vue 3
- Utilize componentes da biblioteca `MaxComponentsUi` para campos de formulário, zonas de upload e indicadores de status.
- Aproveite composables e funções helper do `MaxUse` para lidar com validações reativas, formatação de datas e gerenciamento de estado.
- Garanta que os estados de upload de documentos sejam atualizados dinamicamente e reflitam os requisitos da concessionária.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill está escrito.
- **Não burle as regulamentações técnicas:** Nunca permita que um projeto siga para envio se ele violar os limites especificados na `ConcessionaireSubsidiaryRegulation` ativa.
- **Não escreva queries diretas ao banco em controllers:** Todas as modificações ou atualizações de query nos processos de homologação devem passar pela camada de service (`HomologationService`).
- **Não burle a lógica de notificações:** Garanta que as mudanças de status de protocolo respeitem as flags de notificação (`notify_client`, `notify_designer`, `notify_solar_company`) e delegue a entrega das notificações a Jobs assíncronos para prevenir o bloqueio das requisições do usuário.
