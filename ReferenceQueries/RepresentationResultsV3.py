import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Configuración estética para paper científico
plt.style.use('seaborn-whitegrid')
sns.set_context("paper", font_scale=1.3)
plt.rcParams['font.family'] = 'DejaVu Sans'
COLORS = sns.color_palette("husl", 4)

# Leer CSV con formato específico
df = pd.read_csv('ReferenceQueries_resultados_ejecucion-1.csv', sep=';', decimal=',', encoding='latin-1',
                converters={'Execution '+str(i): lambda x: np.nan if (x == 'Error en ejecución' or x == 'Timeout' or x == 'Error de sintaxis') else float(x.replace(',','.')) 
                          for i in range(1,11)})

# Preparar datos
df['NLQ_ID'] = df['NLQ'].str.extract('(\d+) -').astype(int)
df['Success Rate'] = df[[f'Execution {i}' for i in range(1,11)]].apply(lambda x: x.notna().mean(), axis=1)

# 1. Gráfico de distribución de Times por consulta
#plt.figure(figsize=(14, 8))
#melted = df.melt(id_vars=['NLQ_ID', 'Query Number'], 
#                value_vars=[f'Execution {i}' for i in range(1,11)],
#                var_name='Execution',
#                value_name='Time')

#ax = sns.boxplot(x='Query Number', y='Time', data=melted, showfliers=False)
#sns.swarmplot(x='Query Number', y='Time', data=melted, color='.25', size=3)
#plt.title('Distribution of Execution Times by Query Version', pad=29, size=35)
#plt.xlabel('Query Version (Q)', labelpad=17, size=30)
#plt.ylabel('Time (seconds)', labelpad=15, size=30)
#plt.xticks(rotation=45)
#plt.savefig('Times_per_query.pdf', bbox_inches='tight', dpi=300)
#plt.close()

# 2. Gráfico de tasa de éxito por NLQ
plt.figure(figsize=(14, 8))
success_rates = df.groupby('NLQ_ID')['Success Rate'].mean().reset_index()

bar = sns.barplot(x='NLQ_ID', y='Success Rate', data=success_rates, palette='viridis')
#plt.title('Natural Query (NLQ) Success Rate', pad=29, size=35)
plt.xlabel('Natural Language Query ID', labelpad=17, size=30)
plt.ylabel('Success Rate', labelpad=15, size=30)
plt.ylim(0, 1)

plt.xticks(fontsize=17)
plt.yticks(fontsize=17)

# Añadir valores encima de las barras
for p in bar.patches:
    bar.annotate(f'{p.get_height():.0%}', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', 
                xytext=(0, 9), 
                textcoords='offset points')

plt.savefig('success_rate_nlq.pdf', bbox_inches='tight', dpi=300)
plt.close()

# 3. Heatmap de rendimiento relativo
heatmap_data = df.pivot_table(index='NLQ_ID', 
                             columns='Query Number', 
                             values='Promedio',
                             aggfunc='mean')

plt.figure(figsize=(16, 10))
ax = sns.heatmap(heatmap_data, 
           annot=True, 
           fmt=".2f",
           cmap="YlGnBu",
           cbar_kws={'label': 'Average Time (seconds)'},
           mask=heatmap_data.isnull())
cbar = ax.collections[0].colorbar
cbar.ax.tick_params(labelsize=15) 
cbar.set_label('Average Time (seconds)', fontsize=20, weight='bold')  # Tamaño y estilo                   
#plt.title('Average Performance per Natural Query and Version', pad=29, size=35)
plt.xlabel('Query Version (Q)', labelpad=17, size=30)
plt.ylabel('Natural Language Query (NLQ ID)', labelpad=15, size=30)
plt.savefig('heatmap_performance.pdf', bbox_inches='tight', dpi=300)
plt.close()

# 4. Gráfico comparativo de rendimiento vs estabilidad
plt.figure(figsize=(14, 8))
scatter = sns.scatterplot(x='Promedio', 
                         y='Desviación', 
                         hue='NLQ_ID',
                         size='Success Rate',
                         sizes=(50, 200),
                         data=df,
                         palette='tab20',
                         alpha=0.8)

#plt.title('Relationship between Performance and Consistency', pad=29, size=35)
plt.xlabel('Average Time (seconds)', labelpad=17, size=30)
plt.ylabel('Standard Deviation', labelpad=15, size=30)
plt.xscale('log')
plt.yscale('log')

# Añadir leyenda externa
handles, labels = scatter.get_legend_handles_labels()
plt.legend(handles[1:], labels[1:], 
          bbox_to_anchor=(1.05, 1), 
          loc='upper left', 
          borderaxespad=0.)

plt.savefig('performance_dispersion.pdf', bbox_inches='tight', dpi=300)
plt.close()




#def plot_nlq_time_distribution(df):
"""Distribución de tiempos por NLQ"""
plt.figure(figsize=(16, 10))

# Preparar datos
melted = df.melt(id_vars=['NLQ_ID', 'NLQ'], 
                value_vars=[f'Execution {i}' for i in range(1,11)],
                var_name='Ejecución',
                value_name='Tiempo')

# Filtrar solo valores numéricos y convertir tiempos a segundos
melted = melted[melted['Tiempo'].apply(lambda x: isinstance(x, (int, float)))]

# Ordenar por NLQ_ID
melted = melted.sort_values('NLQ_ID')

# Crear gráfico
ax = sns.boxplot(x='NLQ_ID', y='Tiempo', data=melted, color='.93', showfliers=False, width=0.6)
sns.stripplot(x='NLQ_ID', y='Tiempo', data=melted, color='.25', size=3, alpha=0.5)

# Personalización
#plt.title('Distribución de Tiempos por Consulta Natural (NLQ)', pad=20, fontsize=18)
plt.xlabel('Natural Language Query (NLQ ID)', labelpad=17, fontsize=30)
plt.ylabel('Execution Time (seconds)', labelpad=15, fontsize=30)
plt.xticks(rotation=45, fontsize=20)
plt.yticks(fontsize=17)

# Añadir etiquetas descriptivas
nlq_labels = [f"NLQ {row['NLQ_ID']}" 
             for _, row in df[['NLQ_ID', 'NLQ']].drop_duplicates().iterrows()]

ax.set_xticklabels(nlq_labels, rotation=45, ha='right', fontsize=17)

plt.tight_layout()
plt.savefig('Times_per_nlq.pdf', dpi=300)
plt.close()



print('------------------------------------------\n--------------------------')



#"""Distribución por NLQ con facetas"""
#g = sns.FacetGrid(df.melt(id_vars=['NLQ_ID', 'NLQ'], 
#                        value_vars=[f'Execution {i}' for i in range(1,11)]),
#                col='NLQ_ID', 
#                col_wrap=3,
#                height=4,
#                aspect=1.5,
#                sharey=False)

#g.map(sns.boxplot, 'variable', 'value', showfliers=False)
#g.set_titles("NLQ {col_name}")
#g.set_axis_labels("Versión de Consulta", "Tiempo (segundos)")
#g.set_xticklabels(rotation=45)

#plt.savefig('distribucion_facetas_nlq.pdf', bbox_inches='tight', dpi=300)




"""Distribución de tiempos por NLQ (versión mejorada)"""
plt.figure(figsize=(15, 10))

# Preparar datos
melted = df.melt(id_vars=['NLQ_ID', 'NLQ'], 
                value_vars=[f'Execution {i}' for i in range(1,11)],
                var_name='Ejecución',
                value_name='Tiempo')

# Filtrar y limpiar datos
melted = melted[(melted['Tiempo'] > 0.02) & (melted['Tiempo'] < melted['Tiempo'].quantile(0.99))]

# Crear gráfico con parámetros ajustados
ax = sns.boxplot(x='NLQ_ID', y='Tiempo', data=melted, 
                width=0.8,  # Ancho aumentado de cajas
                linewidth=2.5,  # Grosor de bordes
                fliersize=0,
                color='orange')  # Ocultar outliers

# Añadir puntos individuales con transparencia
sns.stripplot(x='NLQ_ID', y='Tiempo', data=melted, 
             color='#2C3E50', size=6, alpha=0.4, 
             jitter=0.25)  # Mayor dispersión horizontal

# Personalización avanzada
ax.set_yscale('log')
y_ticks = [0.1, 0.2, 0.5, 1, 2, 5, 10]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f"{t} s" for t in y_ticks], fontsize=20, fontweight='semibold')

# Formato de eje X mejorado
nlq_labels = [f"NLQ {int(x)}" 
             for x in sorted(melted['NLQ_ID'].unique())]

plt.xticks(ticks=range(len(nlq_labels)), 
          labels=nlq_labels,
          rotation=45, 
          ha='right', 
          fontsize=20,
          fontweight='semibold')

# Añadir elementos de referencia
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.axhline(1, color='#E74C3C', linestyle=':', linewidth=2, alpha=0.7)

# Títulos y etiquetas
#plt.title('Distribución de Tiempos de Ejecución por NLQ (Escala Logarítmica)\n', 
#         fontsize=18, pad=20, fontweight='bold')
plt.xlabel('', fontsize=16, labelpad=15)
plt.ylabel('', fontsize=16, labelpad=15)

# Ajustar márgenes
plt.subplots_adjust(bottom=0.25, top=0.9)

plt.savefig('Times_per_nlq.pdf', dpi=300, bbox_inches='tight')
plt.close()