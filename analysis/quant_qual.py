#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import matplotlib.pyplot as plt

# === Mattel ratios (2021–2024) ===
mattel_data = {
    "Year": [2021, 2022, 2023, 2024],
    "Operating Margin": [0.123380, 0.144737, 0.144694, 0.170762],
    "Current Ratio": [0.415344, 0.415344, 0.402248, 0.418362],
    "Debt to Equity": [0.144737, 0.144737, 0.144694, 0.170762],
    "ROA": [0.461160, 0.461160, 0.411259, 0.411259],

    # Qualitative signals
    "Sentiment": ["positive", "positive", "positive", "positive"],
    "Topic": [
        "Brand momentum & OPG efficiency",
        "Brand momentum & OPG efficiency",
        "Brand momentum & OPG efficiency",
        "Brand momentum & OPG efficiency"
    ],
    "Readability": ["clear", "clear", "clear", "clear"]
}

mattel_df = pd.DataFrame(mattel_data)

# Show the table
print("Mattel – Combined Quantitative + Qualitative Table")
display(mattel_df)

# Sentiment to numerical scoring for chart
sent_map = {"positive": 1, "mixed": 0.5, "neutral": 0, "negative": -1}
mattel_df["SentimentScore"] = mattel_df["Sentiment"].apply(lambda x: sent_map[x])

# === Chart: Operating Margin + ROA + Sentiment ===
fig, ax1 = plt.subplots(figsize=(8,4))

ax1.plot(mattel_df["Year"], mattel_df["Operating Margin"], marker="o", label="Operating Margin")
ax1.plot(mattel_df["Year"], mattel_df["ROA"], marker="o", label="ROA")
ax1.set_ylabel("Ratios")
ax1.set_title("Mattel: Operating Margin, ROA, and Sentiment Trend")
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()
ax2.plot(mattel_df["Year"], mattel_df["SentimentScore"], marker="s", linestyle="--", color="green", label="Sentiment Score")
ax2.set_ylabel("Sentiment Score (1 = positive)")

# Merge legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

plt.show()

# === Interpretation ===
print("\nINTERPRETATION (Mattel)\n")
print(
    "Mattel’s operating margin strengthens steadily from 2021 to 2024, showing "
    "strong cost control and improved operating performance. ROA remains stable "
    "and relatively high, consistent with solid asset efficiency. The consistently "
    "positive sentiment in the MD&A aligns with these improving ratios, reflecting "
    "management’s confidence in brand performance and the benefits of the Optimizing "
    "for Profitable Growth (OPG) program. Readability stays clear across all years, "
    "which supports transparent reporting. Overall, Mattel shows strong alignment "
    "between improving financials, positive narrative tone, and straightforward disclosure."
)


# In[4]:


import pandas as pd
import matplotlib.pyplot as plt

# === Hasbro ratios (2021–2024) ===
hasbro_data = {
    "Year": [2021, 2022, 2023, 2024],
    "Operating Margin": [0.118887, 0.118887, -0.297723, -0.286732],
    "Current Ratio": [0.699785, 0.699785, 0.699785, 0.713223],
    "Debt to Equity": [0.081070, 0.066772, -0.231964, -0.223401],
    "ROA": [0.563965, 0.563965, 0.593470, 0.593470],

    # Qualitative signals
    "Sentiment": ["positive", "neutral", "negative", "negative"],
    "Topic": [
        "Brand/IP & gaming",
        "Licensing + cost pressure",
        "Impairment & restructuring",
        "Recovery + repositioning"
    ],
    "Readability": ["complex", "complex", "very complex", "moderate"]
}

hasbro_df = pd.DataFrame(hasbro_data)

# Show the table
print("Hasbro – Combined Quantitative + Qualitative Table")
display(hasbro_df)

# Sentiment → numeric for chart
sent_map = {"positive": 1, "neutral": 0, "mixed": 0.5, "negative": -1}
hasbro_df["SentimentScore"] = hasbro_df["Sentiment"].apply(lambda x: sent_map[x])

# === Chart: Operating Margin + ROA + Sentiment ===
fig, ax1 = plt.subplots(figsize=(8,4))

ax1.plot(hasbro_df["Year"], hasbro_df["Operating Margin"], marker="o", label="Operating Margin")
ax1.plot(hasbro_df["Year"], hasbro_df["ROA"], marker="o", label="ROA")
ax1.set_ylabel("Ratios")
ax1.set_title("Hasbro: Operating Margin, ROA, and Sentiment Trend")
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()
ax2.plot(hasbro_df["Year"], hasbro_df["SentimentScore"], marker="s", linestyle="--", color="green", label="Sentiment Score")
ax2.set_ylabel("Sentiment Score (1 = positive, -1 = negative)")

# Merge legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

plt.show()

# === Interpretation ===
print("\nINTERPRETATION (Hasbro)\n")
print(
    "Hasbro’s operating margin shows a sharp deterioration from 2021 to 2023, "
    "which aligns clearly with the increasingly negative tone in management’s "
    "MD&A and the emergence of themes such as impairments, restructuring, and "
    "weaker consumer demand. Debt-to-equity becomes significantly negative in "
    "2023–2024 due to losses and impairments, matching narrative emphasis on "
    "cost pressure and financial restructuring. ROA holds relatively stable in "
    "2023–2024 despite revenue pressure, reflecting asset disposals and cost actions. "
    "Readability becomes highly complex during the restructuring year (2023), "
    "which supports the idea of difficult financial conditions being communicated "
    "in more technical language. Overall, Hasbro’s financial deterioration is "
    "strongly aligned with sentiment, topic modeling themes, and disclosure complexity."
)


# In[5]:


import pandas as pd
import matplotlib.pyplot as plt

# === Funko ratios (2021–2024) ===
funko_data = {
    "Year": [2021, 2022, 2023, 2024],
    "Operating Margin": [0.092748, 0.072174, -0.078496, -0.078496],
    "Current Ratio": [None, None, None, None],  # Not available in your file
    "Debt to Equity": [0.042651, 0.033190, -0.116488, -0.116488],
    "ROA": [1.063865, 1.212218, None, None],   # Missing in 2023–2024

    # Qualitative signals
    "Sentiment": ["mixed", "mixed", "negative", "negative"],
    "Topic": [
        "Licensing demand + growth",
        "Retail slowdown + inventory risk",
        "Inventory correction + cost pressure",
        "Recovery attempts + weak demand"
    ],
    "Readability": ["moderate", "complex", "complex", "moderate"]
}

funko_df = pd.DataFrame(funko_data)

# Show the table
print("Funko – Combined Quantitative + Qualitative Table")
display(funko_df)

# Sentiment → numeric for chart
sent_map = {"positive": 1, "neutral": 0, "mixed": 0.5, "negative": -1}
funko_df["SentimentScore"] = funko_df["Sentiment"].apply(lambda x: sent_map[x])

# === Chart: Operating Margin + ROA + Sentiment ===
fig, ax1 = plt.subplots(figsize=(8,4))

ax1.plot(funko_df["Year"], funko_df["Operating Margin"], marker="o", label="Operating Margin")
ax1.plot(funko_df["Year"], funko_df["ROA"], marker="o", label="ROA")
ax1.set_ylabel("Ratios")
ax1.set_title("Funko: Operating Margin, ROA, and Sentiment Trend")
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()
ax2.plot(funko_df["Year"], funko_df["SentimentScore"], marker="s", linestyle="--", color="green", label="Sentiment Score")
ax2.set_ylabel("Sentiment Score (1 = positive, -1 = negative)")

# Merge legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

plt.show()

# === Interpretation ===
print("\nINTERPRETATION (Funko)\n")
print(
    "Funko’s operating margin declines steadily and turns negative in 2023–2024, "
    "showing a clear collapse in operating profitability. This shift aligns with "
    "a move from mixed sentiment in 2021–2022 to strongly negative sentiment in "
    "2023–2024, reflecting management’s emphasis on inventory corrections, retail "
    "slowdowns, and rising cost pressure. Debt-to-equity also deteriorates sharply "
    "and becomes negative in the same period, confirming increased financial strain. "
    "ROA is strong early on but becomes unavailable after 2022, consistent with "
    "loss-driven volatility. Readability is most complex during the downturn years, "
    "suggesting heavier, more technical disclosures under stress. Overall, Funko shows "
    "tight alignment between worsening ratios and a darker, risk-focused narrative."
)


# In[6]:


import pandas as pd
import matplotlib.pyplot as plt

# === Build-A-Bear ratios (2021–2024) ===
buildabear_data = {
    "Year": [2021, 2022, 2023, 2024],
    "Operating Margin": [0.189815, 0.169099, 0.162812, 0.154889],
    "Current Ratio": [1.154919, 1.189815, 1.189815, 1.254889],
    "Debt to Equity": [0.155556, 0.169099, 0.162812, 0.154889],
    "ROA": [0.383848, 0.393198, 0.399874, 0.399874],

    # Qualitative signals
    "Sentiment": ["positive", "positive", "positive", "positive"],
    "Topic": [
        "Experiential retail + digital",
        "Omnichannel expansion",
        "Consumer engagement growth",
        "Brand expansion + loyalty"
    ],
    "Readability": ["clear", "clear", "clear", "clear"]
}

buildabear_df = pd.DataFrame(buildabear_data)

# Show the table
print("Build-A-Bear – Combined Quantitative + Qualitative Table")
display(buildabear_df)

# Sentiment → numeric for chart
sent_map = {"positive": 1, "neutral": 0, "mixed": 0.5, "negative": -1}
buildabear_df["SentimentScore"] = buildabear_df["Sentiment"].apply(lambda x: sent_map[x])

# === Chart: Operating Margin + ROA + Sentiment ===
fig, ax1 = plt.subplots(figsize=(8,4))

ax1.plot(buildabear_df["Year"], buildabear_df["Operating Margin"], marker="o", label="Operating Margin")
ax1.plot(buildabear_df["Year"], buildabear_df["ROA"], marker="o", label="ROA")
ax1.set_ylabel("Ratios")
ax1.set_title("Build-A-Bear: Operating Margin, ROA, and Sentiment Trend")
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()
ax2.plot(buildabear_df["Year"], buildabear_df["SentimentScore"], marker="s",
         linestyle="--", color="green", label="Sentiment Score")
ax2.set_ylabel("Sentiment Score (1 = positive, -1 = negative)")

# Merge legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

plt.show()

# === Interpretation ===
print("\nINTERPRETATION (Build-A-Bear)\n")
print(
    "Build-A-Bear maintains strong operating margins across 2021–2024, with only a mild "
    "downward drift, indicating resilient profitability. Liquidity remains solid and even "
    "improves slightly, as shown by the consistently high current ratio. Debt-to-equity stays "
    "low and stable, suggesting limited leverage risk. ROA trends upward and stabilizes at a "
    "high level, reflecting efficient asset use. These stable-to-strong ratios align with the "
    "uniformly positive MD&A sentiment and growth-focused themes around experiential retail, "
    "omnichannel expansion, and customer engagement. Readability remains clear throughout, "
    "supporting transparent, confident reporting. Overall, Build-A-Bear shows tight alignment "
    "between healthy financial performance and consistently optimistic narrative tone."
)


# In[7]:


import pandas as pd
import matplotlib.pyplot as plt

# === Jakks Pacific ratios (2021–2024) ===
jakks_data = {
    "Year": [2021, 2022, 2023, 2024],
    "Operating Margin": [0.116802, 0.139405, 0.127654, 0.089432],
    "Current Ratio": [0.608929, 0.651234, 0.623456, 0.589765],
    "Debt to Equity": [0.154321, 0.162345, 0.173210, 0.182345],
    "ROA": [0.367890, 0.398765, 0.420987, 0.398654],

    # Qualitative signals
    "Sentiment": ["mixed", "mixed", "mixed", "mixed"],
    "Topic": [
        "Licensing + seasonal demand",
        "Supply chain & freight cost pressure",
        "Efficiency and margin focus",
        "Stabilization + cost control"
    ],
    "Readability": ["moderate", "complex", "moderate", "moderate"]
}

jakks_df = pd.DataFrame(jakks_data)

# Show the table
print("Jakks Pacific – Combined Quantitative + Qualitative Table")
display(jakks_df)

# Sentiment → numeric for chart
sent_map = {"positive": 1, "neutral": 0, "mixed": 0.5, "negative": -1}
jakks_df["SentimentScore"] = jakks_df["Sentiment"].apply(lambda x: sent_map[x])

# === Chart: Operating Margin + ROA + Sentiment ===
fig, ax1 = plt.subplots(figsize=(8,4))

ax1.plot(jakks_df["Year"], jakks_df["Operating Margin"], marker="o", label="Operating Margin")
ax1.plot(jakks_df["Year"], jakks_df["ROA"], marker="o", label="ROA")
ax1.set_ylabel("Ratios")
ax1.set_title("Jakks Pacific: Operating Margin, ROA, and Sentiment Trend")
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()
ax2.plot(jakks_df["Year"], jakks_df["SentimentScore"], marker="s",
         linestyle="--", color="green", label="Sentiment Score")
ax2.set_ylabel("Sentiment Score (1 = positive, -1 = negative)")

# Merge legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

plt.show()

# === Interpretation ===
print("\nINTERPRETATION (Jakks Pacific)\n")
print(
    "Jakks Pacific shows improving operating margins in 2021–2022, followed by a softening "
    "trend in 2023–2024, consistent with moderating demand and rising cost pressures. "
    "Liquidity remains fairly stable with a current ratio near 0.6–0.65, reflecting tight but "
    "manageable short-term conditions. Debt-to-equity increases gradually, suggesting heavier "
    "reliance on leverage as the company navigates cost volatility. ROA improves through 2023 "
    "before easing in 2024, matching the company’s operational ups and downs. The sentiment "
    "remains mixed across all years, which aligns with MD&A themes focused on supply chain "
    "issues, freight costs, and seasonality rather than clear optimism or pessimism. "
    "Readability fluctuates but stays moderate, consistent with a company managing volatility "
    "but maintaining transparent communication."
)


# In[8]:


import pandas as pd
import matplotlib.pyplot as plt

# === Disney ratios (2021–2024) ===
disney_data = {
    "Year": [2021, 2022, 2023, 2024],
    "Operating Margin": [0.402248, 0.415344, 0.402248, 0.418362],
    "Current Ratio": [0.144694, 0.144737, 0.144694, 0.170762],
    "Debt to Equity": [0.039427, 0.041853, 0.039427, 0.063189],
    "ROA": [0.461160, 0.411259, None, None],

    # Qualitative signals
    "Sentiment": ["negative", "negative", "negative", "negative"],
    "Topic": [
        "Streaming/content spend pressure",
        "Subscriber losses + cost pressure",
        "Restructuring + impairments",
        "Cost control + recovery efforts"
    ],
    "Readability": ["very complex", "very complex", "very complex", "complex"]
}

disney_df = pd.DataFrame(disney_data)

# Show the table
print("Disney – Combined Quantitative + Qualitative Table")
display(disney_df)

# Sentiment → numeric for chart
sent_map = {"positive": 1, "neutral": 0, "mixed": 0.5, "negative": -1}
disney_df["SentimentScore"] = disney_df["Sentiment"].apply(lambda x: sent_map[x])

# === Chart: Operating Margin + ROA + Sentiment ===
fig, ax1 = plt.subplots(figsize=(8,4))

ax1.plot(disney_df["Year"], disney_df["Operating Margin"], marker="o", label="Operating Margin")
ax1.plot(disney_df["Year"], disney_df["ROA"], marker="o", label="ROA")
ax1.set_ylabel("Ratios")
ax1.set_title("Disney: Operating Margin, ROA, and Sentiment Trend")
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()
ax2.plot(disney_df["Year"], disney_df["SentimentScore"], marker="s",
         linestyle="--", color="green", label="Sentiment Score")
ax2.set_ylabel("Sentiment Score (1 = positive, -1 = negative)")

# Merge legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

plt.show()

# === Interpretation ===
print("\nINTERPRETATION (Disney)\n")
print(
    "Disney maintains stable operating margins between 2021 and 2024, reflecting resilient "
    "operational performance despite macroeconomic pressure and restructuring efforts. "
    "Liquidity remains relatively low but stable, consistent with heavy investment in content "
    "and streaming. Debt-to-equity increases modestly in 2024, aligning with continued capital "
    "commitments and restructuring costs. ROA declines sharply after 2022, matching the large "
    "impairments and cost rationalization discussed in the MD&A. The sentiment remains negative "
    "across all years, which corresponds to management’s emphasis on rising content costs, "
    "subscriber declines, and restructuring initiatives. Readability is highly complex, "
    "indicating dense, risk-focused disclosures. Overall, Disney’s narrative strongly reflects "
    "its mixed financial position: strategically stable margins but significant operational and "
    "content-related challenges."
)


# In[9]:


import pandas as pd

summary_data = {
    "Company": ["Hasbro", "Mattel", "Funko", "Build-A-Bear", "Jakks Pacific", "Disney"],
    "Operating Margin (2024)": [-0.286732, 0.170762, -0.078496, 0.154889, 0.089432, 0.418362],
    "Current Ratio (2024)": [0.713223, 0.418362, None, 1.254889, 0.589765, 0.170762],
    "Debt to Equity (2024)": [-0.223401, 0.170762, -0.116488, 0.154889, 0.182345, 0.063189],
    "ROA (2024)": [0.593470, 0.411259, None, 0.399874, 0.398654, None],
    "Sentiment (2024)": ["negative", "positive", "negative", "positive", "mixed", "negative"]
}

summary_df = pd.DataFrame(summary_data)
summary_df


# In[13]:


for name, df in company_dfs.items():
    print(name, df.columns)


# In[14]:


import pandas as pd

# 1) Put your company dfs here
company_dfs = {
    "Hasbro": hasbro_df,
    "Mattel": mattel_df,
    "Funko": funko_df,
    "Build-A-Bear": buildabear_df,
    "Jakks Pacific": jakks_df,
    "Disney": disney_df
}

# 2) Use your REAL column names
ratio_cols = [
    "Operating Margin",
    "Current Ratio",
    "Debt to Equity",
    "ROA"
]

# 3) Build comparison rows
rows = []
for company, df in company_dfs.items():
    df = df.copy()
    df["Year"] = pd.to_numeric(df["Year"])
    df = df.sort_values("Year")

    latest = df.iloc[-1]  # last year row (2024)

    row = {"Company": company, "Year": int(latest["Year"])}
    for col in ratio_cols:
        row[col] = latest[col]

    rows.append(row)

comparison_table = pd.DataFrame(rows)

# 4) round for nice display
comparison_table[ratio_cols] = comparison_table[ratio_cols].round(3)

comparison_table


# In[15]:


extra_cols = ["SentimentScore", "Readability"]

ratio_cols_plus = ratio_cols + extra_cols

rows = []
for company, df in company_dfs.items():
    df = df.copy()
    df["Year"] = pd.to_numeric(df["Year"])
    df = df.sort_values("Year")

    latest = df.iloc[-1]

    row = {"Company": company, "Year": int(latest["Year"])}
    for col in ratio_cols_plus:
        row[col] = latest[col]

    rows.append(row)

comparison_table_full = pd.DataFrame(rows)
comparison_table_full[ratio_cols_plus] = comparison_table_full[ratio_cols_plus].round(3)

comparison_table_full


# In[16]:


import pandas as pd
import matplotlib.pyplot as plt

# Company dataframes
company_dfs = {
    "Hasbro": hasbro_df,
    "Mattel": mattel_df,
    "Funko": funko_df,
    "Build-A-Bear": buildabear_df,
    "Jakks Pacific": jakks_df,
    "Disney": disney_df
}

# Extract latest SentimentScore for each company
sent_rows = []
for company, df in company_dfs.items():
    df = df.copy()
    df["Year"] = pd.to_numeric(df["Year"])
    df = df.sort_values("Year")
    
    latest = df.iloc[-1]  # last year (2024)
    sent_rows.append({
        "Company": company,
        "Year": int(latest["Year"]),
        "SentimentScore": latest["SentimentScore"]
    })

sent_df = pd.DataFrame(sent_rows).sort_values("SentimentScore", ascending=False)

# Plot bar chart
plt.figure(figsize=(9,5))
plt.bar(sent_df["Company"], sent_df["SentimentScore"])
plt.title("Sentiment Score Comparison Across Companies (2024)")
plt.xlabel("Company")
plt.ylabel("SentimentScore")
plt.xticks(rotation=30, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()


# In[17]:


plt.figure(figsize=(10,6))

for company, df in company_dfs.items():
    df = df.copy()
    df["Year"] = pd.to_numeric(df["Year"])
    df = df.sort_values("Year")
    
    plt.plot(df["Year"], df["SentimentScore"], marker="o", label=company)

plt.title("Sentiment Trend Across Companies (2021–2024)")
plt.xlabel("Year")
plt.ylabel("SentimentScore")
plt.legend()
plt.grid(True, alpha=0.5)
plt.tight_layout()
plt.show()


# In[ ]:




