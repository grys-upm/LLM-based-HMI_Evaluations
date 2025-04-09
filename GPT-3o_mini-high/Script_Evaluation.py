import psycopg2
import pandas as pd
import time
import csv
from statistics import mean, stdev
from psycopg2 import OperationalError, ProgrammingError, errors


DB_CONFIG = {
    'dbname': 'AFarCloud',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': '5432'
}

TIMEOUT_MS = 30000  


df = pd.read_excel('GPT-3o_mini-high-Evaluation.xlsx', sheet_name='Sheet1', header=1)

def classify_error(e):
    """Clasifica el tipo de error de PostgreSQL"""
    if isinstance(e, errors.QueryCanceled):
        return 'Timeout'
    if isinstance(e, ProgrammingError):
        if e.pgcode == '42601':  # Syntax error
            return 'Error de sintaxis'
    return 'Error en ejecución'

def benchmark_query(query, conn, runs=10):
    results = []
    original_timeout = None
    
    for _ in range(runs):
        cursor = conn.cursor()
        try:
            
            cursor.execute("SHOW statement_timeout;")
            original_timeout = cursor.fetchone()[0]
            cursor.execute(f"SET statement_timeout TO {TIMEOUT_MS};")
            cursor.execute("SET lock_timeout TO '30s';")
            
            start = time.perf_counter()
            cursor.execute("DISCARD ALL;")
            cursor.execute(query)
            elapsed = round(time.perf_counter() - start, 4)
            results.append(elapsed)
            
        except Exception as e:
            conn.rollback()
            error_type = classify_error(e)
            results.append(error_type)
            print(f"Error ({error_type}) en consulta: {str(e)[:200]}...")
        finally:
            
            try:
                
                if original_timeout:
                    cursor.execute(f"SET statement_timeout TO {original_timeout};")
            except Exception as restore_error:
                print(f"Error restaurando timeout: {str(restore_error)}")
            cursor.close()
            if 'cursor' in locals(): cursor.close()
    
    return results


conn = psycopg2.connect(**DB_CONFIG)
conn.autocommit = True


with open('GPT-3o_mini-high_resultados_ejecucion.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    header = ['NLQ', 'Query Number', 'Execution 1', 'Execution 2', 'Execution 3',
              'Execution 4', 'Execution 5', 'Execution 6', 'Execution 7',
              'Execution 8', 'Execution 9', 'Execution 10', 'Promedio', 'Desviación']
    writer.writerow(header)

    
    for idx, row in df.iterrows():
        nlq = row['NLQ']
        for q_num in range(1, 11):
            print(f"Ejecutando NLQ: {nlq} | Query Q{q_num}")
            query = row[f'Q{q_num}']
            if pd.isna(query):
                continue

            
            resultados = benchmark_query(query, conn)
            
            
            tiempos_validos = [r for r in resultados if isinstance(r, float)]
            stats = {
                'promedio': round(mean(tiempos_validos), 4) if tiempos_validos else 'N/A',
                'desviacion': round(stdev(tiempos_validos), 4) if len(tiempos_validos) > 1 else 'N/A'
            }

            
            writer.writerow([
                nlq,
                f'Q{q_num}',
                *resultados,
                stats['promedio'],
                stats['desviacion']
            ])
            f.flush()

conn.close()