import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-whitegrid')
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12
})

df = pd.read_excel('VES.xlsx', sheet_name='Sheet1', skiprows=1, index_col=0) # Provide VES CSV for its processing and representation
df.columns = [col.strip() for col in df.columns]

fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
plt.subplots_adjust(bottom=0.35)  

palette = sns.color_palette("tab20", n_colors=len(df.columns))

for i, model in enumerate(df.columns):
    ax.plot(df.index, df[model],
            marker='o' if i%2==0 else 's',  
            markersize=8,
            linewidth=2,
            alpha=0.95,
            color=palette[i],
            markeredgecolor='w',
            markeredgewidth=0.8,
            label=model.replace('_', ' ').title())

ax.set_xlabel('NLQ Identifier', fontweight='semibold', labelpad=10)
ax.set_ylabel('VES Score', fontweight='semibold', labelpad=10)
ax.set_xticks(df.index)
ax.set_xticklabels([f'NLQ {int(x)}' for x in df.index], rotation=0)
ax.set_ylim(0, 1.05)
ax.yaxis.set_major_locator(plt.MaxNLocator(6))

leg = ax.legend(bbox_to_anchor=(0.5, -0.45),
              loc='upper center',
              ncol=3,  
              frameon=True,
              framealpha=1,
              edgecolor='#CCCCCC',
              fontsize=10,
              handlelength=1.5,
              handletextpad=0.4,
              columnspacing=1.5)


ax.grid(True, linestyle='--', alpha=0.4, which='both')
sns.despine(left=True, bottom=True)


plt.text(0.5, -0.55, 'VES: Valid Efficiency Score | LLM: Large Language Model',
        transform=ax.transAxes,
        ha='center',
        fontsize=9,
        color='#666666')

plt.savefig('VES_Compact_Visualization.pdf', bbox_inches='tight')
plt.close()