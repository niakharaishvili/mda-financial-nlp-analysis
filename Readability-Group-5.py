#!/usr/bin/env python
# coding: utf-8

# In[1]:


# ============================================
# FULL MD&A READABILITY + COMPARISON ANALYSIS
# Using a single PDF: Mdas.pdf
# ============================================

get_ipython().system('pip install textstat pypdf nltk matplotlib seaborn --quiet')

import os
import re
import pypdf
import textstat
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- NLTK downloads (with safety) ----------
for pkg in ["punkt", "punkt_tab"]:
    try:
        if pkg == "punkt":
            nltk.data.find("tokenizers/punkt")
        else:
            nltk.data.find("tokenizers/punkt_tab/english")
    except LookupError:
        nltk.download(pkg)


# ============================================
# 1. PDF → TEXT
# ============================================
PDF_FILE = "Mdas.pdf"   # <-- your combined MD&A file

def extract_pdf_text(path):
    """Extract all text from a PDF file using pypdf."""
    reader = pypdf.PdfReader(path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

full_text = extract_pdf_text(PDF_FILE)
print("✅ PDF text extracted (length:", len(full_text), "characters )")


# ============================================
# 2. Split text into companies
# ============================================
# 🔴 VERY IMPORTANT:
# These markers must match how the company names appear in Mdas.pdf.
# Adjust them if needed (e.g. "THE WALT DISNEY COMPANY" instead of DISNEY)
COMPANY_MARKERS = {
    "Hasbro": "HASBRO",
    "Mattel": "MATTEL",
    "Funko": "FUNKO",
    "BuildABear": "BUILD A BEAR",   # maybe "BUILD-A-BEAR" in your PDF
    "JakksPacific": "JAKKS",
    "Disney": "DISNEY"              # maybe "THE WALT DISNEY COMPANY"
}

def split_by_company(text, markers):
    """Split the big MD&A text into per-company sections using name markers."""
    upper_text = text.upper()
    positions = []

    for company, marker in markers.items():
        idx = upper_text.find(marker)
        if idx != -1:
            positions.append((idx, company))

    # sort by position in the text
    positions.sort(key=lambda x: x[0])

    sections = {}
    for i, (start_idx, company) in enumerate(positions):
        end_idx = positions[i+1][0] if i+1 < len(positions) else len(text)
        sections[company] = text[start_idx:end_idx]

    return sections

company_sections = split_by_company(full_text, COMPANY_MARKERS)

print("\n📌 Companies detected in PDF:")
for name in company_sections:
    print(" -", name, "(chars:", len(company_sections[name]), ")")


# ============================================
# 3. Readability + complexity analysis
# ============================================
def analyze_text(text):
    # Basic cleaning
    text = re.sub(r"\s+", " ", text).strip()

    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())

    # Filter out punctuation-only tokens
    word_tokens = [w for w in words if re.search(r"[a-zA-Z]", w)]

    word_count = len(word_tokens)
    sentence_count = len(sentences)
    avg_sentence_len = word_count / max(sentence_count, 1)

    # Complex words: 3+ syllables (using textstat)
    complex_count = 0
    for w in word_tokens:
        if textstat.syllable_count(w) >= 3:
            complex_count += 1
    complex_pct = complex_count / max(word_count, 1) * 100

    # Most common words (excluding stopwords-ish short words)
    filtered_words = [w for w in word_tokens if len(w) > 3]
    top_words = Counter(filtered_words).most_common(8)

    # Readability scores
    fres = textstat.flesch_reading_ease(text)
    fk = textstat.flesch_kincaid_grade(text)
    fog = textstat.gunning_fog(text)
    dale = textstat.dale_chall_readability_score(text)
    smog = textstat.smog_index(text)
    ari = textstat.automated_readability_index(text)

    # Estimated reading time assuming 200 wpm
    reading_time_min = round(word_count / 200, 2)

    return {
        "Word Count": word_count,
        "Sentence Count": sentence_count,
        "Avg Sentence Length": round(avg_sentence_len, 2),
        "Complex Word Count": complex_count,
        "Complex Word %": round(complex_pct, 2),
        "Flesch Reading Ease": round(fres, 2),
        "Flesch-Kincaid Grade": round(fk, 2),
        "Gunning Fog": round(fog, 2),
        "SMOG Index": round(smog, 2),
        "Dale-Chall Score": round(dale, 2),
        "Automated Readability Index": round(ari, 2),
        "Estimated Reading Time (min)": reading_time_min,
        "Top Words": top_words
    }


# ============================================
# 4. Run analysis for each company
# ============================================
results = {}
for company, text in company_sections.items():
    print(f"\n🔍 Analyzing MD&A for {company} ...")
    results[company] = analyze_text(text)

df = pd.DataFrame(results).T

print("\n===== READABILITY COMPARISON TABLE =====\n")
print(df)

df.to_csv("readability_comparison_companies.csv")
print("\n💾 Saved table as readability_comparison_companies.csv")


# ============================================
# 5. Graphs for comparisons
# ============================================
sns.set(style="whitegrid")

# Helper to plot a bar chart for any numeric column
def plot_metric(column, ylabel=None, title=None):
    plt.figure(figsize=(8, 5))
    df_sorted = df.sort_values(column, ascending=False)
    sns.barplot(x=df_sorted.index, y=df_sorted[column])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel(ylabel if ylabel else column)
    plt.title(title if title else column)
    plt.tight_layout()
    plt.show()

# A few useful comparison plots:
plot_metric("Word Count", "Words", "Word Count by Company (MD&A)")
plot_metric("Avg Sentence Length", "Words per Sentence", "Average Sentence Length by Company")
plot_metric("Flesch-Kincaid Grade", "Grade Level", "Flesch-Kincaid Grade (Higher = Harder)")
plot_metric("Gunning Fog", "Fog Index", "Gunning Fog Index (Higher = More Complex)")
plot_metric("Complex Word %", "% Complex Words", "Complex Word Percentage by Company")


# In[ ]:




