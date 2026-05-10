# Fornecendo conexão com o banco

import psycopg2

def get_connection():
    connection = psycopg2.connect(
        host = "localhost",  # Onde o banco está
        port = "5432",  # Porta padrão do PostgreSQL
        database = "deltaflow", # Nome do banco de dados
        user = "postgres",  # Usuário
        password = "2203092"    # Senha
    )
    return connection