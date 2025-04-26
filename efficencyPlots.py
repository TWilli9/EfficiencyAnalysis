import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.stdout.reconfigure(encoding='utf-8')

#Load the data
advancedStats = pd.read_csv(r"C:\Users\teddy\OneDrive\Desktop\EfficiencyAnalysis\nbaAdvancedStats.csv")
basicStats = pd.read_csv(r"C:\Users\teddy\OneDrive\Desktop\EfficiencyAnalysis\nbaStats.csv")

# Remove the combined team rows
basicStats = basicStats[basicStats["Team"].str.contains("TM") == False]
advancedStats = advancedStats[advancedStats["Team"].str.contains("TM") == False]

# Group by Player and combine stats
countingStats = ["G", "GS", "MP", "PTS", "AST", "TRB", "ORB", "DRB", "STL", "BLK", "TOV", "PF", "FGA", "FG", "3PA", "3P", "FTA", "FT"]
basicStatsSum = basicStats.groupby("Player")[countingStats].sum()

#Weighted averages for percentages
basicStats["FGA"].replace(0, np.nan, inplace=True)
basicStats["3PA"].replace(0, np.nan, inplace=True)
basicStats["FTA"].replace(0, np.nan, inplace=True)

weightedFgPct = (basicStats["FG"] / basicStats["FGA"] * basicStats["FGA"]).groupby(basicStats["Player"]).sum() / basicStats.groupby("Player")["FGA"].sum()
weighted3pPct = (basicStats["3P"] / basicStats["3PA"] * basicStats["3PA"]).groupby(basicStats["Player"]).sum() / basicStats.groupby("Player")["3PA"].sum()
weightedFtPct = (basicStats["FT"] / basicStats["FTA"] * basicStats["FTA"]).groupby(basicStats["Player"]).sum() / basicStats.groupby("Player")["FTA"].sum()

#Combine the basic stats
basicStatsFiltered = basicStatsSum.copy()
basicStatsFiltered["FG%"] = weightedFgPct
basicStatsFiltered["3P%"] = weighted3pPct
basicStatsFiltered["FT%"] = weightedFtPct
basicStatsFiltered = basicStatsFiltered.reset_index()

# Group and combine advanced stats
advancedStatsCounting = ["G", "MP"]
minutesPerPlayer = advancedStats.groupby("Player")["MP"].sum()

# Only use numeric columns for weighted averages
advancedStatsNumeric = advancedStats.select_dtypes(include=[np.number]).columns.tolist()
advancedStatsNumeric = [col for col in advancedStatsNumeric if col not in ["G", "MP"]]


# Weighted averages for advanced stats
def weightedAverage(df, valueCol, weightCol):
    return (df[valueCol] * df[weightCol]).groupby(df["Player"]).sum() / df.groupby("Player")[weightCol].sum()

advancedWeighted = pd.DataFrame(index=minutesPerPlayer.index)

for col in advancedStatsNumeric:
    advancedWeighted[col] = weightedAverage(advancedStats, col, "MP")

# Merge summed games and minutes with weighted stats
advancedStatsSum = advancedStats.groupby("Player")[advancedStatsCounting].sum()
advancedStatsFiltered = pd.concat([advancedStatsSum, advancedWeighted], axis=1).reset_index()




#Merge with advanced stats
combineddf = pd.merge(basicStatsFiltered, advancedStatsFiltered, on="Player", suffixes=("_basic", "_advanced"))



#Drop repeated columns
colsToDrop = [col for col in combineddf.columns if col.endswith("_advanced") and col[:-9] + "_basic" in combineddf.columns]
combineddf = combineddf.drop(columns=colsToDrop)


#Clean column names
renameCols = {col: col.replace("_basic", "") for col in combineddf.columns if "_basic" in col}
combineddf.rename(columns=renameCols, inplace=True)
#combineddf = combineddf.drop(index = 724)
combineddf = combineddf.drop(['Awards'], axis=1)
combineddf.fillna(0,inplace=True)




#PER Distribution Histogram
plt.figure(figsize=(10, 6))
plt.hist(combineddf["PER"], bins=30, color='gray', edgecolor='black')
plt.axvline(x=32.2, color='red', linestyle='--', label='Jokic') #replace 32.2 with Jokic's actual stat
plt.axvline(x=15, color='blue', linestyle='--', label='League Avg')
plt.title("Distribution of Player Efficiency Rating (PER)")
plt.xlabel("PER")
plt.ylabel("Number of Players")
plt.legend()
plt.show()


# Create Top 10 PER Table
top10_PER = combineddf[['Player', 'PER', 'TS%', 'WS', 'VORP']].sort_values('PER', ascending=False).head(10)

# Set up nice figure
fig, ax = plt.subplots(figsize=(10, 4))
ax.axis('off')  # Hide axes

# Create table
table = ax.table(
    cellText=top10_PER.values,
    colLabels=top10_PER.columns,
    cellLoc='center',
    loc='center'
)

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)  # Make table bigger
plt.title("Top 10 Players by PER", fontsize=14, pad=20)

plt.show()




#combineddf.to_csv('combinedStats.csv')


#print(combineddf["PER"].describe())
#print(combineddf.loc[combineddf["PER"].idxmax(), ["Player", "PER"]])
#print(combineddf.sort_values("PER", ascending=False).head(10))
#print(combineddf.tail(10))
#print(combineddf.info())
#print(combineddf.isna().sum())
#print(nbaStats.duplicated())
#print(numeric_df.corr())
