import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


plt.style.use('seaborn-whitegrid')
sns.set_context("paper", font_scale=1.3)
plt.rcParams['font.family'] = 'DejaVu Sans'
COLORS = sns.color_palette("husl", 4)


df = pd.read_csv('DeepSeek_resultados_ejecucion.csv', sep=';', decimal=',', encoding='latin-1',
                converters={'Execution '+str(i): lambda x: np.nan if x == 'Error en ejecución' else float(x.replace(',','.')) 
                          for i in range(1,11)})


df['NLQ_ID'] = df['NLQ'].str.extract('(\d+) -').astype(int)
df['Success Rate'] = df[[f'Execution {i}' for i in range(1,11)]].apply(lambda x: x.notna().mean(), axis=1)




plt.figure(figsize=(14, 8))
success_rates = df.groupby('NLQ_ID')['Success Rate'].mean().reset_index()

bar = sns.barplot(x='NLQ_ID', y='Success Rate', data=success_rates, palette='viridis')
plt.xlabel('Natural Language Query ID', labelpad=17, size=30)
plt.ylabel('Success Rate', labelpad=15, size=30)
plt.ylim(0, 1)

plt.xticks(fontsize=17)
plt.yticks(fontsize=17)


for p in bar.patches:
    bar.annotate(f'{p.get_height():.0%}', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', 
                xytext=(0, 9), 
                textcoords='offset points')

plt.savefig('success_rate_nlq_1.pdf', bbox_inches='tight', dpi=300)
plt.close()





"""Comparative Success Rate Analysis"""

try:
    df_validaciones = pd.read_excel('Resultados_Validacion.xlsx', sheet_name='Validaciones')
except Exception as e:
    print(f"Validation loading error: {str(e)}")


merged = pd.merge(df, df_validaciones, on='NLQ_ID', how='inner')


plot_data = merged.groupby('NLQ_ID')[['Success Rate', 'Tasa_Exito_Validado']].mean().reset_index()


plt.figure(figsize=(18, 12))
ax = plt.subplot()
colors = ['#2E86C1', '#27AE60']  # Modern blue-green palette


bar_width = 0.4
positions = np.arange(len(plot_data))


rects1 = ax.bar(positions - bar_width/2, plot_data['Success Rate'], 
               width=bar_width, color=colors[0], label='Execution Success')
rects2 = ax.bar(positions + bar_width/2, plot_data['Tasa_Exito_Validado'], 
               width=bar_width, color=colors[1], label='Validation Success')


ax.tick_params(axis='y', which='both', labelsize=25)
ax.set_xticks(positions)
ax.set_xticklabels([f'NLQ {int(x)}' for x in plot_data['NLQ_ID']], 
                      fontsize=25, rotation=45, ha='right')
ax.set_ylim(0, 1.15)
ax.grid(axis='y', linestyle='--', alpha=0.7)


def add_labels(rects, rotation):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.0%}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 5),  
                    textcoords="offset points",
                    ha='center', va='bottom',
                    rotation=rotation,
                    fontsize=20,
                    fontweight='bold')

add_labels(rects1, 45)
add_labels(rects2, 45)


ax.legend().set_visible(False)


ax.axhline(1.0, color='#E74C3C', linestyle='--', linewidth=1.5, alpha=0.7)

plt.tight_layout()
plt.savefig('success_rate_nlq.pdf', dpi=300, bbox_inches='tight')
plt.close()






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
cbar.set_label('Average Time (seconds)', fontsize=20, weight='bold')                
#plt.title('Average Performance per Natural Query and Version', pad=29, size=35)
plt.xlabel('Query Version (Q)', labelpad=17, size=30)
plt.ylabel('Natural Language Query (NLQ ID)', labelpad=15, size=30)
plt.savefig('heatmap_performance.pdf', bbox_inches='tight', dpi=300)
plt.close()


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


melted = df.melt(id_vars=['NLQ_ID', 'NLQ'], 
                value_vars=[f'Execution {i}' for i in range(1,11)],
                var_name='Ejecución',
                value_name='Tiempo')


melted = melted[melted['Tiempo'].apply(lambda x: isinstance(x, (int, float)))]


melted = melted.sort_values('NLQ_ID')


ax = sns.boxplot(x='NLQ_ID', y='Tiempo', data=melted, showfliers=False, width=0.6)
sns.stripplot(x='NLQ_ID', y='Tiempo', data=melted, color='.25', size=3, alpha=0.5)


plt.xlabel('Natural Language Query (NLQ ID)', labelpad=17, fontsize=30)
plt.ylabel('Execution Time (seconds)', labelpad=15, fontsize=30)
plt.xticks(rotation=45, fontsize=20)
plt.yticks(fontsize=17)


nlq_labels = [f"NLQ {row['NLQ_ID']}" 
             for _, row in df[['NLQ_ID', 'NLQ']].drop_duplicates().iterrows()]

ax.set_xticklabels(nlq_labels, rotation=45, ha='right', fontsize=17)

plt.tight_layout()
plt.savefig('Times_per_nlq.pdf', dpi=300)
plt.close()




"""Time Distribution per NLQ"""
plt.figure(figsize=(15, 10))


melted = df.melt(id_vars=['NLQ_ID', 'NLQ'], 
                value_vars=[f'Execution {i}' for i in range(1,11)],
                var_name='Ejecución',
                value_name='Tiempo')


melted = melted[(melted['Tiempo'] > 0.02) & (melted['Tiempo'] < melted['Tiempo'].quantile(0.95))]


ax = sns.boxplot(x='NLQ_ID', y='Tiempo', data=melted, 
                width=0.8,  
                linewidth=2.5,  
                fliersize=0)  


sns.stripplot(x='NLQ_ID', y='Tiempo', data=melted, 
             color='#2C3E50', size=6, alpha=0.4, 
             jitter=0.25)  


ax.set_yscale('log')
y_ticks = [0.1, 0.2, 0.5, 1, 2, 5]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f"{t} s" for t in y_ticks], fontsize=20, fontweight='semibold')


nlq_labels = [f"NLQ {int(x)}" 
             for x in sorted(melted['NLQ_ID'].unique())]

plt.xticks(ticks=range(len(nlq_labels)), 
          labels=nlq_labels,
          rotation=45, 
          ha='right', 
          fontsize=20,
          fontweight='semibold')


plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.axhline(1, color='#E74C3C', linestyle=':', linewidth=2, alpha=0.7)


plt.xlabel('', fontsize=16, labelpad=15)
plt.ylabel('', fontsize=16, labelpad=15)


plt.subplots_adjust(bottom=0.25, top=0.9)

plt.savefig('Times_nlq_improved.pdf', dpi=300, bbox_inches='tight')
plt.close()