# FASE 00 — Descoberta do Problema (Product Discovery)

## 1. Visão Geral
Este documento registra a análise do modelo de negócios da **Eureciclo** e justifica a escolha do projeto **EcoTrace Engine** para ser demonstrado como caso prático de arquitetura
e engenharia backend sênior.

## 2. O Modelo de Negócios da Eureciclo
A Eureciclo atua na logística reversa de embalagens pós-consumo conforme a Política Nacional de Resíduos Sólidos (PNRS - Lei nº 12.305/2010). 
- **Obrigatoriedade:** Empresas devem comprovar a reciclagem de ao menos 22% do equivalente em massa das embalagens enviadas ao mercado.
- **Funcionamento:** Em vez de recolher suas próprias embalagens, as marcas adquirem **Certificados de Reciclagem** lastreados nas 
Notas Fiscais Eletrônicas (NF-e) de venda de materiais recicláveis por cooperativas e operadores.

## 3. Principais Desafios Tecnológicos do Domínio
1. **Fraude por Dupla Contagem (Double Spending):** Reutilização da mesma NF-e em diferentes plataformas ou lotes.
2. **Parsing e Validação Fiscal em Lote:** Ingestão distribuída de XMLs com NCMs heterogêneos.
3. **Instabilidade e Latência da SEFAZ:** Necessidade de comunicação assíncrona tolerante a falhas.
4. **Cadeia de Custódia e Rastreabilidade:** Garantia de que a massa reciclada pertence ao material e estado corretos.

## 4. Comparativo de Soluções Candidatas

| Critério | Opção A: EcoTrace Engine (Ingestão & Antifraude) | Opção B: ClearBalance (Ledger & Matching) | Opção C: EcoStream (Analytics) |
| :--- | :--- | :--- | :--- |
| **Alinhamento com Stack (FastAPI/Async/Rabbit/Redis/Workers)** | **10/10** | 9/10 | 8/10 |
| **Relevância para Core Business Eureciclo** | **10/10** | 10/10 | 7/10 |
| **Sistemas Distribuídos e Resiliência** | **10/10** | 8/10 | 8/10 |
| **Invocação em Entrevista Técnica (Storytelling)** | **10/10** | 8/10 | 9/10 |
| **Pontuação Final** | **9.95 / 10 (VENCEDOR)** | **8.95 / 10** | **7.90 / 10** |

## 5. Projeto Selecionado: EcoTrace Engine
Um motor distribuído de alta performance para ingestão assíncrona de NF-es, validação de regras de NCM, consulta resiliente à SEFAZ, 
detecção de fraude por dupla contagem via SHA-256 e geração de Créditos de Reciclagem auditáveis.
