# Classificação Fiscal API

API back-end para consulta de NCM, CEST e alíquotas IBPT.
Desenvolvida com FastAPI e PostgreSQL.

---

## Tecnologias

- Python 3.14
- FastAPI
- PostgreSQL 18
- psycopg2
- python-dotenv

---

## Como rodar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/maartdev/ClassificacaoFiscal-API.git
cd ClassificacaoFiscal-API
```

### 2. Instale as dependências

```bash
pip install fastapi uvicorn psycopg2-binary python-dotenv requests
```

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=deltaflow
DB_USER=postgres
DB_PASSWORD=sua_senha

### 4. Configure o banco de dados

Execute os seguintes comandos SQL no PostgreSQL:

```sql
CREATE TABLE cest (
    cest      VARCHAR(9)  NOT NULL,
    descricao TEXT        NOT NULL,
    CONSTRAINT pk_cest PRIMARY KEY (cest)
);

CREATE TABLE cest_ncm (
    id   SERIAL      NOT NULL,
    cest VARCHAR(9)  NOT NULL,
    ncm  VARCHAR(15) NOT NULL,
    CONSTRAINT pk_cest_ncm PRIMARY KEY (id),
    CONSTRAINT fk_cest FOREIGN KEY (cest) REFERENCES cest (cest)
);

CREATE INDEX idx_cest_ncm_ncm ON cest_ncm (ncm);

CREATE TABLE ibpt (
    id         SERIAL        NOT NULL,
    codigo     VARCHAR(10)   NOT NULL,
    uf         VARCHAR(2)    NOT NULL,
    ex         VARCHAR(5),
    nacionalfe NUMERIC(10,2) NOT NULL,
    importados NUMERIC(10,2) NOT NULL,
    estadual   NUMERIC(10,2) NOT NULL,
    municipal  NUMERIC(10,2) NOT NULL,
    CONSTRAINT pk_ibpt PRIMARY KEY (id)
);

CREATE INDEX idx_ibpt_consulta ON ibpt (codigo, uf, ex);

CREATE TABLE produto (
    id        SERIAL        NOT NULL,
    nome      VARCHAR(255)  NOT NULL,
    ncm       VARCHAR(10)   NOT NULL,
    cest      VARCHAR(9),
    preco     NUMERIC(10,2) NOT NULL,
    uf        VARCHAR(2)    NOT NULL,
    federal   NUMERIC(10,2),
    importado NUMERIC(10,2),
    estadual  NUMERIC(10,2),
    municipal NUMERIC(10,2),
    CONSTRAINT pk_produto PRIMARY KEY (id)
);
```

### 5. Importe os dados

Os arquivos CSV para importação estão disponíveis no repositório:

- `tabela_cest.csv` → importar na tabela `cest`
- `tabela_cest_ncm.csv` → importar na tabela `cest_ncm`
- `ibpt_SP.csv` → importar na tabela `ibpt`

Para importar via pgAdmin:
- Clique com botão direito na tabela → Import/Export
- Formato: CSV | Separador: `;` | Header: ativado
- Encoding: UTF8

### 6. Rode a API

```bash
uvicorn main:app --reload
```

A API estará disponível em: http://localhost:8000
Documentação interativa: http://localhost:8000/docs

---

## Rotas disponíveis

### GET /buscar-cest
Retorna os CESTs vinculados a um NCM.

**Parâmetros:**
| Nome | Tipo | Obrigatório | Exemplo |
|------|------|-------------|---------|
| ncm | string | ✅ | 22030000 |

**Retorno:**
```json
[
  {
    "cest": "03.021.00",
    "descricao": "Cerveja"
  }
]
```

---

### GET /buscar-ibpt
Retorna as alíquotas IBPT de um NCM por estado.

**Parâmetros:**
| Nome | Tipo | Obrigatório | Exemplo |
|------|------|-------------|---------|
| ncm | string | ✅ | 2203.00.00 |
| uf | string | ✅ | SP |

**Retorno:**
```json
{
  "ncm": "22030000",
  "uf": "SP",
  "federal": 16.21,
  "importado": 24.35,
  "estadual": 18.00,
  "municipal": 0.00
}
```

---

### POST /produto
Cadastra um produto. As alíquotas IBPT são preenchidas automaticamente.

**Parâmetros:**
| Nome | Tipo | Obrigatório | Exemplo |
|------|------|-------------|---------|
| nome | string | ✅ | Cerveja Heineken |
| ncm | string | ✅ | 2203.00.00 |
| cest | string | ✅ | 03.021.00 |
| preco | float | ✅ | 5.99 |
| uf | string | ✅ | SP |

**Retorno:**
```json
{
  "mensagem": "Produto cadastrado com sucesso",
  "id": 1,
  "nome": "Cerveja Heineken",
  "ncm": "2203.00.00",
  "cest": "03.021.00",
  "preco": 5.99,
  "uf": "SP",
  "aliquotas": {
    "federal": 16.21,
    "importado": 24.35,
    "estadual": 18.00,
    "municipal": 0.00
  }
}
```

---

### GET /produto
Lista todos os produtos cadastrados.

**Retorno:**
```json
[
  {
    "id": 1,
    "nome": "Cerveja Heineken",
    "ncm": "2203.00.00",
    "cest": "03.021.00",
    "preco": 5.99,
    "uf": "SP",
    "aliquotas": {
      "federal": 16.21,
      "importado": 24.35,
      "estadual": 18.00,
      "municipal": 0.00
    }
  }
]
```

---

### GET /produto/{id}
Busca um produto específico pelo ID.

**Parâmetros:**
| Nome | Tipo | Obrigatório | Exemplo |
|------|------|-------------|---------|
| id | integer | ✅ | 1 |

**Retorno:**
```json
{
  "id": 1,
  "nome": "Cerveja Heineken",
  "ncm": "2203.00.00",
  "cest": "03.021.00",
  "preco": 5.99,
  "uf": "SP",
  "aliquotas": {
    "federal": 16.21,
    "importado": 24.35,
    "estadual": 18.00,
    "municipal": 0.00
  }
}
```

---

## Fluxo de cadastro de produto
1. Usuário digita o NCM
2. Front chama GET /buscar-cest → exibe sugestões de CEST
3. Usuário seleciona o CEST
4. Usuário preenche nome, preço e UF
5. Front chama POST /produto
6. API busca alíquotas no IBPT automaticamente
7. Produto salvo com alíquotas embutidas
8. Front exibe confirmação com os dados completos

---

## Atualização semestral do IBPT

A tabela IBPT é atualizada pelo governo a cada semestre (janeiro e julho).
Quando uma nova tabela for lançada:

1. Baixar o novo arquivo em: `https://github.com/devrafalima/tabela-ibpt`
2. Processar o CSV para o formato correto
3. Executar no banco: `TRUNCATE TABLE ibpt;`
4. Reimportar o novo CSV via pgAdmin

---

## Observações

- A API está configurada para rodar em ambiente local
- Antes de ir para produção, substituir as credenciais do `.env` pelas de produção
- O arquivo `.env` nunca deve ser commitado no repositório
