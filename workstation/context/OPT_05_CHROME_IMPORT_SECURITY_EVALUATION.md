# OPT-05: Avaliação de Segurança e Privacidade — Importação de Sessões do Chrome

**Status:** HOLD / BLOQUEADO  
**Data:** 2026-10-11  
**Autoridade:** Hermes Workstation Security & Privacy Policy (`SECURITY.md`, `UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md`)

---

## 1. Contexto e Motivação do HOLD

Durante a auditoria de ecossistemas Browser (ex.: browser-use/desktop, Chrome import utilities), identificou-se a capacidade de importação local de sessões ativas do Google Chrome (cookies via DPAPI no Windows, Keychain no macOS, libsecret no Linux).

No contexto do **Hermes Workstation**, esta funcionalidade foi **deliberadamente colocada em HOLD** e **NÃO deve ser implementada como rotina automática ou silenciosa**.

### Motivos Centrais:
1. **Violação de Fronteira de Confiança (§2 do SECURITY.md):**  
   O agente não possui autorização implícita para inspecionar credenciais mestras ou cookies autenticados do usuário fora de seu perfil isolado (`workstationBrowserProfilePath()`).
2. **Risco de Vazamento de Segredos e Sessões Bancárias/Corporativas:**  
   A extração indiscriminada de cookies de terceiros pode transferir sessões sensíveis (bancos, provedores de identidade corporativos, SSO) para o contexto de navegação automatizada do LLM.
3. **Ausência de Mecanismo Nativo de Consentimento Granular:**  
   Qualquer importação que não solicite confirmação visual explícita com listagem dos domínios autorizados viola o contrato de transparência do Hermes Work.

---

## 2. Requisitos Mandatórios para Futura Implementação

Antes de qualquer consideração de desbloqueio do OPT-05 em ciclos futuros, os seguintes critérios devem ser atendidos e validados:

### A. Consentimento Ativo e Granular
- **Nunca silencioso:** Nenhuma leitura de arquivo do sistema (`Login Data`, `Cookies`) pode ocorrer sem uma solicitação explícita de consentimento na interface do Hermes Desktop.
- **Lista Branca por Origem:** O usuário deve selecionar individualmente quais origens (ex.: `github.com`, `linear.app`) terão suas sessões importadas. Todas as demais devem ser descartadas antes da persistência.
- **Bloqueio de Domínios de Alto Risco:** Domínios bancários, de pagamentos, de infraestrutura em nuvem (AWS, GCP, Azure consoles) e provedores de e-mail primários devem ter importação terminantemente proibida.

### B. Isolamento e Criptografia
- **Armazenamento Isolado:** As sessões importadas devem residir exclusivamente no perfil de sandbox do Hermes (`~/.hermes/profiles/.../workstation/browser`), sem retroalimentar o navegador de origem.
- **Proteção em Repouso:** Os cookies importados devem ser protegidos com chaves derivadas do perfil local do usuário.

### C. Ciclo de Vida e Retenção
- **TTL Bounded / Efêmero:** Sessões importadas devem expirar automaticamente após período determinado (ex.: 24 horas) ou na conclusão da `BrowserTask` proprietária.
- **Revogação Imediata:** Um botão "Limpar todas as sessões importadas" deve estar visível no painel do navegador.

### D. Redação Estrita em Logs e Telemetria
- Cookies, tokens `Bearer`, tokens de sessão (`sessionid`, `SSID`, etc.) e cabeçalhos de autorização **jamais** podem aparecer em `WorkstationEvent`, `ExecutionJournal`, traces de depuração ou saídas de terminal.

---

## 3. Decisão de Engenharia

O item **OPT-05 permanece bloqueado (HOLD)**. O ecossistema Hermes Work continuará utilizando o perfil dedicado Chromium persistente gerido pelo Electron, exigindo login manual ou autorização via `BrowserHumanControlLease` quando necessário.
