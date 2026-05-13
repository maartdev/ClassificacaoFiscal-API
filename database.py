# Fornecendo conexão com o banco

import psycopg2
import os
from dotenv import load_dotenv  

load_dotenv()

def get_connection():
    connection = psycopg2.connect(
        host = os.getenv('DB_HOST'),  # Onde o banco está
        port = os.getenv('DB_PORT'),  # Porta padrão do PostgreSQL
        database = os.getenv('DB_NAME'), # Nome do banco de dados
        user = os.getenv('DB_USER'),  # Usuário
        password = os.getenv('DB_PASSWORD')    # Senha
    )
    return connection