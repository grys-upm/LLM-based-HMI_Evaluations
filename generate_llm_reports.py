import os
import psycopg2
import time
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime


DB_CONFIG = {
    'dbname': 'AFarCloud',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': '5432'
}

LLM_DIRS = [
    'DeepSeek', 'GPT-3.0', 'GPT-3.5', 'GPT-3o_mini-high',
    'GPT-3o-mini', 'GPT-4o', 'GPT-4o_mini', 'GPT-o1',
    'Ollama_SQLCoder-7B', 'Ollama_SQLCoder-15B'
]

def print_progress(llm, nlq_id, q_num, start_time=None):
    """Show execution process"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    base_msg = f"[{timestamp}] LLM: {llm.ljust(20)} | NLQ: {str(nlq_id).zfill(2)} | Query: Q{q_num}"
    
    if start_time:
        elapsed = datetime.now() - start_time
        print(f"{base_msg} | Time: {elapsed.total_seconds():.2f}s")
    else:
        print(base_msg)

def execute_query(query, cursor, llm, nlq_id, q_num):
    """Execute query and return results with headers"""
    start_time = datetime.now()
    print_progress(llm, nlq_id, q_num)
    
    try:
        cursor.execute("DISCARD ALL;")
        cursor.execute(query)
        
        if cursor.description:
        
            columns = [desc[0] for desc in cursor.description]
            
            data = cursor.fetchall()
            result = "| ".join(columns) + "\n"  # Headers
            result += "\n".join(["| ".join(map(str, row)) for row in data])
        else:
            result = "Executed query (No results)"
            
    except Exception as e:
        result = f"Error: {str(e)}"
    
    print_progress(llm, nlq_id, q_num, start_time)
    
    time.sleep(1)
    
    return str(result)[:2000]  

def process_llm(llm_dir, writer):
    """Process all files of each LLM"""
    print(f"\n{'='*60}")
    print(f" Starting process for: {llm_dir.upper()} ")
    print(f"{'='*60}\n")
    
    file_path = os.path.join(llm_dir, f"{llm_dir}-Evaluation.xlsx")
    try:
        df = pd.read_excel(file_path, sheet_name='Sheet1', header=1)
    except Exception as e:
        print(f"!! ERROR in file reading: {e}")
        return
        
        
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()
    
    results = []
    total_queries = 0
    for idx, row in df.iterrows():
        nlq_full = row['NLQ']
        nlq_id = nlq_full.split(' - ')[0] if pd.notna(nlq_full) else 'UNknown'
        
        for q_num in range(1, 11):
            query = row.get(f'Q{q_num}')
            if pd.isna(query):
                continue
            
            total_queries += 1
            result = execute_query(query, cursor, llm_dir, nlq_id, q_num)
            results.append({
                'NLQ': nlq_id,
                'Query': f'Q{q_num}',
                'SQL': query,
                'Result': result,
                'Characters Returned': (len(result)) if ('result' in locals() and not result.startswith('Error')) else 0
            })
    
    
    df_results = pd.DataFrame(results)
    sheet_name = llm_dir[:31]
    df_results.to_excel(writer, sheet_name=sheet_name, index=False)
    
    
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    worksheet.cell(row=1, column=df_results.shape[1]+1, value="Execution Accuracy")
    
    print(f"\n{'='*60}")
    print(f" FINALIZADO: {llm_dir.upper()}")
    print(f" Consultas procesadas: {total_queries}")
    print(f" Errores detectados: {len(df_results[df_results['Result'].str.startswith('Error')])}")
    print(f"{'='*60}\n")
    
    cursor.close()
    conn.close()

def generate_report():
    """Generate report"""
    start_total = datetime.now()
    print(f"\n{'#'*60}")
    print(f" START OF GLOBAL PROCESS: {start_total.strftime('%Y-%m-%d %H:%M:%S')} ")
    print(f"{'#'*60}\n")
    
    with pd.ExcelWriter('LLM_Validation_Report.xlsx', engine='openpyxl') as writer:
        for llm_dir in LLM_DIRS:
            if os.path.exists(llm_dir):
                process_llm(llm_dir, writer)
            else:
                print(f"!! path not found: {llm_dir}")
    
    total_time = datetime.now() - start_total
    print(f"\n{'#'*60}")
    print(f" PROCESS COMPLETED")
    print(f" Total time: {total_time.total_seconds():.2f} seconds")
    print(f"{'#'*60}")

if __name__ == "__main__":
    generate_report()