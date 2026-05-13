from fastapi import FastAPI
from database import get_connection

app = FastAPI()

# ── Buscar CESTs pelo NCM ────────────────────────────────────────────────────
@app.get("/buscar-cest")
def buscar_cest(ncm: str):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT cn.cest, c.descricao
        FROM cest_ncm cn
        JOIN cest c ON c.cest = cn.cest
        WHERE cn.ncm = %s
    """, (ncm,))

    resultados = cursor.fetchall()
    cursor.close()
    connection.close()

    if not resultados:
        return []

    return [
        {"cest": row[0], "descricao": row[1]}
        for row in resultados
    ]

# ── Buscar alíquotas IBPT ────────────────────────────────────────────────────
@app.get("/buscar-ibpt")
def buscar_ibpt(ncm: str, uf: str):
    connection = get_connection()
    cursor = connection.cursor()

    ncm_limpo = ncm.replace('.', '')

    cursor.execute("""
        SELECT codigo, uf, nacionalfe, importados, estadual, municipal
        FROM ibpt
        WHERE codigo = %s
        AND uf = %s
    """, (ncm_limpo, uf))

    resultado = cursor.fetchone()
    cursor.close()
    connection.close()

    if not resultado:
        return {"mensagem": "Nenhuma alíquota encontrada para esse NCM e UF"}

    return {
        "ncm":       resultado[0],
        "uf":        resultado[1],
        "federal":   resultado[2],
        "importado": resultado[3],
        "estadual":  resultado[4],
        "municipal": resultado[5]
    }

# ── Cadastrar produto ────────────────────────────────────────────────────────
@app.post("/produto")
def cadastrar_produto(
    nome:  str,
    ncm:   str,
    cest:  str,
    preco: float,
    uf:    str
):
    connection = get_connection()
    cursor = connection.cursor()

    ncm_limpo = ncm.replace('.', '')

    cursor.execute("""
        SELECT nacionalfe, importados, estadual, municipal
        FROM ibpt
        WHERE codigo = %s
        AND uf = %s
    """, (ncm_limpo, uf))

    ibpt = cursor.fetchone()

    federal   = ibpt[0] if ibpt else 0
    importado = ibpt[1] if ibpt else 0
    estadual  = ibpt[2] if ibpt else 0
    municipal = ibpt[3] if ibpt else 0

    cursor.execute("""
        INSERT INTO produto
            (nome, ncm, cest, preco, uf, federal, importado, estadual, municipal)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (nome, ncm, cest, preco, uf, federal, importado, estadual, municipal))

    novo_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    connection.close()

    return {
        "mensagem": "Produto cadastrado com sucesso",
        "id":       novo_id,
        "nome":     nome,
        "ncm":      ncm,
        "cest":     cest,
        "preco":    preco,
        "uf":       uf,
        "aliquotas": {
            "federal":   federal,
            "importado": importado,
            "estadual":  estadual,
            "municipal": municipal
        }
    }

# ── Listar todos os produtos ─────────────────────────────────────────────────
@app.get("/produto")
def listar_produtos():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, nome, ncm, cest, preco, uf,
               federal, importado, estadual, municipal
        FROM produto
        ORDER BY id
    """)

    produtos = cursor.fetchall()
    cursor.close()
    connection.close()

    if not produtos:
        return []

    return [
        {
            "id":       row[0],
            "nome":     row[1],
            "ncm":      row[2],
            "cest":     row[3],
            "preco":    row[4],
            "uf":       row[5],
            "aliquotas": {
                "federal":   row[6],
                "importado": row[7],
                "estadual":  row[8],
                "municipal": row[9]
            }
        }
        for row in produtos
    ]

# ── Buscar produto por ID ────────────────────────────────────────────────────
@app.get("/produto/{id}")
def buscar_produto(id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, nome, ncm, cest, preco, uf,
               federal, importado, estadual, municipal
        FROM produto
        WHERE id = %s
    """, (id,))

    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if not row:
        return {"mensagem": "Produto não encontrado"}

    return {
        "id":       row[0],
        "nome":     row[1],
        "ncm":      row[2],
        "cest":     row[3],
        "preco":    row[4],
        "uf":       row[5],
        "aliquotas": {
            "federal":   row[6],
            "importado": row[7],
            "estadual":  row[8],
            "municipal": row[9]
        }
    }