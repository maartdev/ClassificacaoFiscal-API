# API

from fastapi import FastAPI
from database import get_connection

app = FastAPI() # Objeto central

# Vincular NCM à CESTs relacionados
@app.get("/buscar-cest")
def buscar_cest(ncm: str):
    connection = get_connection()
    cursor = connection.cursor() # Cursor = Objeto que executa o SQL

    cursor.execute("""
        SELECT cn.cest, c.descricao
        FROM cest_ncm cn
        JOIN cest c ON c.cest = cn.cest
        WHERE cn.ncm = %s
    """, (ncm,))
    # %s = Placeholder para o ncm inserido | Espaço reservado

    resultados = cursor.fetchall()
    cursor.close()
    connection.close()

    if not resultados:
        return []

    return [
        {"cest": row[0], "descricao": row[1]}
        for row in resultados
    ]

# Calcular o IBPT
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