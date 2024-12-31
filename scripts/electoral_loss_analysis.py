#%% Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#%% Set style and helper function
plt.style.use('classic')  # Use classic style instead of seaborn
# Add custom style configurations
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.grid': True,
    'grid.color': '#cccccc',
    'grid.alpha': 0.3,
    'axes.labelcolor': '#333333',
    'axes.titlecolor': '#333333',
    'font.family': 'sans-serif'
})

colors = ['#2c3e50', '#e74c3c', '#3498db', '#f1c40f', '#2ecc71']

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return f'{val}\n({pct:.1f}%)'
    return my_autopct

#%% Load and prepare the data
df = pd.read_csv('../data/Cleaned_ElectionSurvey.csv')
df['Voted_Last_Election'] = df['Voted_Last_Election'].fillna('No Response')
df['Party_Belong'] = df['Party_Belong'].fillna('No Response')

#%% Analyze voting patterns
voted_distribution = df['Voted_Last_Election'].value_counts()
print("\nVoting Distribution:")
print(voted_distribution)

#%% Visualize voting distribution
plt.figure(figsize=(10, 6))
plt.pie(voted_distribution, colors=colors,
        labels=voted_distribution.index,
        autopct=make_autopct(voted_distribution.values),
        startangle=90)
plt.title('Voting Distribution')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

#%% Analyze party affiliation
party_distribution = df['Party_Belong'].value_counts()
print("\nParty Affiliation Distribution:")
print(party_distribution)

#%% Visualize party affiliation
plt.figure(figsize=(10, 6))
plt.pie(party_distribution, colors=colors,
        labels=party_distribution.index,
        autopct=make_autopct(party_distribution.values),
        startangle=90)
plt.title('Party Affiliation Distribution')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

#%% Analyze reasons for NPP loss
reasons_npp_lost = df['Reason_NPP_Lost'].value_counts()
print("\nReasons for NPP Loss:")
print(reasons_npp_lost)

#%% Visualize NPP loss reasons
plt.figure(figsize=(12, 6))
top_reasons = reasons_npp_lost.head(5)
ax = sns.barplot(x=range(len(top_reasons)), y=top_reasons.values, palette=colors)
plt.title('Top 5 Reasons for NPP Loss')
plt.xticks([])

# Add value labels on bars
for i, v in enumerate(top_reasons.values):
    percentage = (v/len(df))*100
    ax.text(i, v, f'{int(v)}\n({percentage:.1f}%)', 
            ha='center', va='bottom')

# Create legend
plt.legend(title='Reasons',
          labels=[f'{i+1}: {reason[:30]}...' if len(reason) > 30 else f'{i+1}: {reason}'
                 for i, reason in enumerate(top_reasons.index)],
          bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

#%% Analyze project awareness
project_awareness = df['Know_Projects'].value_counts()
print("\nProject Awareness Distribution:")
print(project_awareness)

#%% Visualize project awareness
plt.figure(figsize=(10, 6))
plt.pie(project_awareness, colors=colors,
        labels=project_awareness.index,
        autopct=make_autopct(project_awareness.values),
        startangle=90)
plt.title('Project Awareness Distribution')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

#%% Analyze community problem solving
problem_solving = df['Solved_Community_Problems'].value_counts()
print("\nCommunity Problem Solving Assessment:")
print(problem_solving)

#%% Analyze NDC's perceived advantages
ndc_better = df['NDC_Better_Than_NPP'].value_counts()
print("\nWhy NDC Was Perceived Better:")
print(ndc_better)

#%% Visualize NDC advantages
plt.figure(figsize=(12, 6))
top_advantages = ndc_better.head(5)
ax = sns.barplot(x=range(len(top_advantages)), y=top_advantages.values, palette=colors)
plt.title('Top 5 Reasons Why NDC Was Perceived Better')
plt.xticks([])

# Add value labels on bars
for i, v in enumerate(top_advantages.values):
    percentage = (v/len(df))*100
    ax.text(i, v, f'{int(v)}\n({percentage:.1f}%)', 
            ha='center', va='bottom')

# Create legend
plt.legend(title='Advantages',
          labels=[f'{i+1}: {adv[:30]}...' if len(adv) > 30 else f'{i+1}: {adv}'
                 for i, adv in enumerate(top_advantages.index)],
          bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

#%% Create a summary of key findings
print("\nKEY FINDINGS:")
print("1. Voting Participation Rate:", 
      (voted_distribution['Yes'] / voted_distribution.sum() * 100).round(2), "%")

party_support = df[df['Party_Belong'].isin(['NPP', 'NDC'])]['Party_Belong'].value_counts()
print("2. Party Support Ratio (NDC:NPP):", 
      (party_support['NDC'] / party_support['NPP']).round(2))

top_reason = reasons_npp_lost.index[0]
print("3. Main Reason for NPP Loss:", top_reason)

project_awareness_rate = (
    df[df['Know_Projects'].str.contains('Yes', na=False)].shape[0] / 
    df['Know_Projects'].notna().sum() * 100
).round(2)
print("4. Project Awareness Rate:", project_awareness_rate, "%")
