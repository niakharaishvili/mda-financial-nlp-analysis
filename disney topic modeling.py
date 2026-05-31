#!/usr/bin/env python
# coding: utf-8

# In[1]:


filename = "disney mda.txt"

with open(filename, "r", encoding="utf-8", errors="ignore") as f:
    raw_text = f.read()

print(raw_text[:800])
print("Word count:", len(raw_text.split()))


# In[2]:


import re

def clean_text(t):
    t = t.lower()
    t = re.sub(r"[^a-z\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

cleaned_full = clean_text(raw_text)


# In[3]:


# 1 — Try paragraphs
documents = raw_text.split("\n\n")
documents = [clean_text(d) for d in documents]
documents = [d for d in documents if len(d.split()) > 25]

print("Paragraph docs:", len(documents))

# 2 — If too few, fallback to sentences
if len(documents) < 10:
    documents = [s.strip() for s in cleaned_full.split(".") if len(s.split()) > 8]
    print("Switched to sentence docs:", len(documents))

# 3 — If still too few, chunk text
if len(documents) < 10:
    words = cleaned_full.split()
    chunk_size = 80
    documents = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    print("Forced chunk docs:", len(documents))

print("\nSample document (first 250 chars):\n", documents[0][:250])


# In[4]:


from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

count_vec = CountVectorizer(
    stop_words="english",
    max_features=2500,
    ngram_range=(1,1),
    max_df=0.90
)
X_count = count_vec.fit_transform(documents)

tfidf_vec = TfidfVectorizer(
    stop_words="english",
    max_features=2500,
    ngram_range=(1,1),
    max_df=0.90
)
X_tfidf = tfidf_vec.fit_transform(documents)

print("X_count shape:", X_count.shape)
print("X_tfidf shape:", X_tfidf.shape)
print("Vocab size:", len(count_vec.get_feature_names_out()))


# In[5]:


from sklearn.decomposition import LatentDirichletAllocation, NMF

n_topics = 4

lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
lda.fit(X_count)

nmf = NMF(n_components=n_topics, random_state=42, init="nndsvd")
nmf.fit(X_tfidf)

print("Topics used:", n_topics)


# In[6]:


def show_topics(model, feature_names, n_words=12):
    topics_out = []
    for i, topic in enumerate(model.components_):
        words = [feature_names[j] for j in topic.argsort()[-n_words:]]
        print(f"\nTOPIC {i+1}: {', '.join(words)}")
        topics_out.append((i+1, words))
    return topics_out

print("🔷 LDA Topics (Disney):")
lda_topics = show_topics(lda, count_vec.get_feature_names_out())

print("\n🔶 NMF Topics (Disney):")
nmf_topics = show_topics(nmf, tfidf_vec.get_feature_names_out())


# In[8]:


import pandas as pd

data = {
    "Topic #": [1, 2, 3, 4],
    "Topic Name": [
        "Advertising, Programming Costs & Revenue Mix",
        "Impairment Testing, Fair Value & Asset Carrying Values",
        "Streaming (Disney+/Hulu) Subscribers & SVOD Economics",
        "Segment Results, Operating Income & Tax/One-Time Items"
    ],
    "Top Words": [
        "offset, advertising, increase, impact, lower, decrease, revenues, production, revenue, higher, programming, costs",
        "assessment, group, carrying, company, asset, assets, flows, fair, impairment, reporting, value, cash",
        "hulu, multi, service, svod, revenue, average, monthly, product, subscriber, subscribers, paid, disney",
        "excluded, supplemental, tax, prior, segment, items, results, related, year, operating, income, million"
    ],
    "Meaning": [
        "Focus on changes in advertising performance, content/programming costs, and how these offset or drive revenue changes across the business.",
        "Discussion of goodwill/asset impairment assessments, fair-value measurement, and cash-flow based valuation of reporting groups.",
        "Emphasis on Disney’s streaming platforms (Disney+ / Hulu), subscriber trends, monthly ARPU/revenue drivers, and SVOD service performance.",
        "Covers segment-level operating income results, year-over-year comparisons, and the impact of tax or supplemental/one-time items on performance."
    ]
}

disney_df = pd.DataFrame(data)

pd.set_option("display.max_colwidth", None)
disney_df



# In[ ]:




