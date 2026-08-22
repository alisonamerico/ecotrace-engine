3. Padrões Aplicados & Trade-offs
- Asynchronous Handoff: Retorno HTTP 202 imediato desacoplando o recebimento do processamento pesado.
- Distributed Lock (Redlock): Garante exclusão mútua global contra requisições concorrentes.
- Dead Letter Exchange (DLX): Tratamento de falhas e poison messages em filas isoladas.


# FASE 03 — Modelagem de Domínio (DDD)

## 1. Bounded Contexts
1. **Ingestion & Parsing Context:** Validação sintática e extração inicial de dados.
2. **Fraud & Fiscal Audit Context (Core Domain):** Verificação de integridade fiscal, validação SEFAZ e prevenção de dupla contagem.
3. **Credit Issuance Context (Core Domain):** Conversão de massa útil em créditos de reciclagem auditáveis.

## 2. Elementos Táticos do Domínio

### Value Objects
- **`AccessKey`:** Encapsula a chave de 44 dígitos da NF-e, calculando a Hash SHA-256 e validando dígitos verificadores.
- **`CNPJ`:** Documento fiscal formatado e validado.
- **`NCM`:** Nomenclatura Comum do Mercosul para validação de elegibilidade de materiais recicláveis.
- **`RecyclableMass`:** Representação imutável de massa (peso em kg/toneladas).

### Entidades e Agregados
- **`InvoiceItem` (Entidade):** Item individual da nota com descrição, NCM e peso.
- **`Invoice` (Raiz do Agregado):** Mantém a invariante do estado do ciclo de vida da nota (`PENDING`, `PROCESSING`, `APPROVED`, `REJECTED`, `FRAUD_SUSPECT`).

### Domain Services & Repositories (Contracts)
- **`FraudDetectionService`:** Serviço de domínio para identificar tentativa de duplo uso da mesma massa.
- **`InvoiceRepositoryInterface`:** Interface abstrata (ABC) para isolamento total entre o domínio e o ORM/Banco de dados.
