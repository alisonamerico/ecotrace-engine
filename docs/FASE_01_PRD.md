# FASE 01 — Product Requirements Document (PRD)

## 1. Produto
- **Nome:** EcoTrace Engine
- **Elevator Pitch:** Motor distribuído assíncrono para ingestão, validação fiscal e auditoria antifraude de NF-es de reciclagem, garantindo unicidade de massa e emissão de certificados confiáveis.

## 2. Personas & Stakeholders
- **Operador de Cooperativa:** Realiza envio massivo de NF-es e precisa de respostas rápidas sobre o status do processamento.
- **Auditor de Compliance:** Monitora e analisa alertas de NF-es suspeitas de fraude.
- **SRE / Backend Engineer:** Acompanha a saúde das filas, retries, conexões com banco e disponibilidade do sistema.

## 3. Requisitos Funcionais (RF)
- **RF01 (MVP): Ingestão Assíncrona:** Endpoint HTTP aceitando chaves/XMLs de NF-e com resposta HTTP 202 (Accepted) e emissão de `tracking_id`.
- **RF02 (MVP): Distributed Lock & Idempotência:** Uso de lock distribuído no Redis para bloquear concorrência na mesma NF-e.
- **RF03 (MVP): Validação de NCM:** Parsing dos itens da nota filtrando apenas NCMs elegíveis e calculando massa reciclável (kg).
- **RF04 (MVP): Consulta SEFAZ Resiliente:** Integração simulada com SEFAZ contendo retries, exponential backoff e circuit breaker.
- **RF05 (MVP): Motor Antifraude de Dupla Contagem:** Bloqueio de reprocessamento por verificação de SHA-256 no banco e sinalização de `FRAUD_SUSPECT`.
- **RF06 (MVP): Emissão de Créditos:** Conversão de massa aprovada em registros de `RecyclingCredit`.
- **RF07 (MVP): Consulta de Status:** API de leitura para acompanhar o andamento do pipeline pelo `tracking_id`.

## 4. Requisitos Não Funcionais (RNF)
- **RNF01:** Latência p95 < 50ms na ingestão HTTP (`POST /api/v1/nfe/ingest`).
- **RNF02:** Processamento de até 500 NF-es/segundo via Celery Workers e RabbitMQ.
- **RNF03:** Garantia de Idempotência total (uma NF-e aprovada nunca é reprocessada).
- **RNF04:** Observabilidade total (Logs JSON estruturados, Tracing OpenTelemetry, Métricas Prometheus).
- **RNF05:** Cobertura de testes automatizados $\ge 90\%$.