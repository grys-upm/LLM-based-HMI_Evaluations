import psycopg2
import pandas as pd
import time
import csv
from statistics import mean, stdev
from psycopg2 import OperationalError, ProgrammingError, errors
from psycopg2.pool import SimpleConnectionPool

# Configuración mejorada
DB_CONFIG = {
    'dbname': 'AFarCloud',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': '5432'
}

TIMEOUT_MS = 30000  
COOLDOWN = 0.5  
POOL_SIZE = 3  


connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=POOL_SIZE,
    **DB_CONFIG
)

def classify_error(e):
    if isinstance(e, errors.QueryCanceled):
        return 'Timeout'
    if isinstance(e, ProgrammingError):
        return 'Error de sintaxis' if e.pgcode == '42601' else 'Error SQL'
    return 'Error en ejecución'

def execute_query(query, conn):
    result = None
    try:
        with conn.cursor() as cursor:
            
            cursor.execute(f"SET statement_timeout TO {TIMEOUT_MS};")
            cursor.execute("DISCARD ALL;")
            
            start_time = time.perf_counter()
            cursor.execute(query)
            elapsed = round(time.perf_counter() - start_time, 4)
            
            
            time.sleep(COOLDOWN)
            return elapsed
            
    except Exception as e:
        conn.rollback()
        return classify_error(e)

def benchmark_query(query, runs=10):
    results = []
    for _ in range(runs):
        conn = connection_pool.getconn()
        try:
            result = execute_query(query, conn)
            results.append(result)
        finally:
            connection_pool.putconn(conn)
            time.sleep(COOLDOWN/2)  
    return results


df = pd.read_excel('DeepSeek-Evaluation.xlsx', sheet_name='Sheet1', header=1)

with open('resultados.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    header = ['NLQ', 'Query', 'Ejecuciones', 'Promedio', 'Desviación'] + [f'Run_{i}' for i in range(1, 11)]
    writer.writerow(header)

    for idx, row in df.iterrows():
        nlq = row['NLQ']
        for q_num in range(1, 11):
            query = row[f'Q{q_num}']
            if pd.isna(query):
                continue

            print(f"Procesando: {nlq} | Q{q_num}")
            resultados = benchmark_query(query)
            
            
            tiempos = [r for r in resultados if isinstance(r, float)]
            stats = {
                'promedio': round(mean(tiempos), 4) if tiempos else 'N/A',
                'desviacion': round(stdev(tiempos), 4) if len(tiempos) > 1 else 'N/A'
            }

            writer.writerow([
                nlq,
                f'Q{q_num}',
                len(tiempos),
                stats['promedio'],
                stats['desviacion'],
                *resultados
            ])
            f.flush()

connection_pool.closeall()