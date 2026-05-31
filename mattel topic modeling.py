#!/usr/bin/env python
# coding: utf-8

# In[1]:


filename = "mattel mda.txt"

with open(filename, "r", encoding="utf-8", errors="ignore") as f:
    raw_text = f.read()

print(raw_text[:900])
print("\nWord count:", len(raw_text.split()))


# In[2]:


import re

def clean_text(t):
    t = t.lower()
    t = re.sub(r"[^a-z\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

cleaned_full = clean_text(raw_text)


# In[3]:


# Paragraph documents
documents = raw_text.split("\n\n")
documents = [clean_text(d) for d in documents]
documents = [d for d in documents if len(d.split()) > 30]

print("Paragraph docs:", len(documents))

# If too few paragraphs, fallback to sentence docs
if len(documents) < 10:
    documents = [s.strip() for s in cleaned_full.split(".") if len(s.split()) > 8]
    print("Switched to sentence docs:", len(documents))

print("\nSample doc:\n", documents[0][:250] if documents else "EMPTY")


# In[4]:


from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

short_text = len(documents) < 20  # Mattel likely False

count_vec = CountVectorizer(
    stop_words="english",
    max_features=2000 if not short_text else 800,
    ngram_range=(1,2) if not short_text else (1,1),
    max_df=0.85
)
X_count = count_vec.fit_transform(documents)

tfidf_vec = TfidfVectorizer(
    stop_words="english",
    max_features=2000 if not short_text else 800,
    ngram_range=(1,2) if not short_text else (1,1),
    max_df=0.85
)
X_tfidf = tfidf_vec.fit_transform(documents)

print("short_text:", short_text)
print("X_count shape:", X_count.shape)
print("X_tfidf shape:", X_tfidf.shape)
print("Vocab size:", len(count_vec.get_feature_names_out()))


# In[5]:


filename = "mattel mda.txt"

with open(filename, "r", encoding="utf-8", errors="ignore") as f:
    raw_text = f.read()

print(raw_text[:600])
print("Word count:", len(raw_text.split()))


# In[6]:


import re

def clean_text(t):
    t = t.lower()
    t = re.sub(r"[^a-z\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

cleaned_full = clean_text(raw_text)


# In[7]:


# 1) Try paragraph docs
documents = raw_text.split("\n\n")
documents = [clean_text(d) for d in documents]
documents = [d for d in documents if len(d.split()) > 20]
print("Paragraph docs:", len(documents))

# 2) If paragraphs too few → use sentences
if len(documents) < 5:
    documents = [s.strip() for s in cleaned_full.split(".") if len(s.split()) > 8]
    print("Switched to sentence docs:", len(documents))

# 3) If STILL too few → split every 40–60 words
if len(documents) < 5:
    words = cleaned_full.split()
    chunk_size = 50
    documents = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    documents = [d for d in documents if len(d.split()) > 10]
    print("Forced chunk docs:", len(documents))

print("\nSample document:\n", documents[0][:250] if documents else "EMPTY")


# In[8]:


from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

count_vec = CountVectorizer(
    stop_words="english",
    max_features=1500,
    ngram_range=(1,1)
)
X_count = count_vec.fit_transform(documents)

tfidf_vec = TfidfVectorizer(
    stop_words="english",
    max_features=1500,
    ngram_range=(1,1)
)
X_tfidf = tfidf_vec.fit_transform(documents)

print("X_count shape:", X_count.shape)
print("X_tfidf shape:", X_tfidf.shape)
print("Vocab Size:", len(count_vec.get_feature_names_out()))


# In[9]:


from sklearn.decomposition import LatentDirichletAllocation, NMF

n_topics = 4

lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
lda.fit(X_count)

nmf = NMF(n_components=n_topics, random_state=42, init="nndsvd")
nmf.fit(X_tfidf)

print("Topics used:", n_topics)


# In[10]:


from sklearn.decomposition import LatentDirichletAllocation, NMF

n_topics = 4

lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
lda.fit(X_count)

nmf = NMF(n_components=n_topics, random_state=42, init="nndsvd")
nmf.fit(X_tfidf)

print("Topics used:", n_topics)


# In[11]:


def show_topics(model, feature_names, n_words=12):
    topics_out = []
    for i, topic in enumerate(model.components_):
        words = [feature_names[j] for j in topic.argsort()[-n_words:]]
        print(f"\nTOPIC {i+1}: {', '.join(words)}")
        topics_out.append((i+1, words))
    return topics_out

print("🔷 LDA Topics (Mattel):")
lda_topics = show_topics(lda, count_vec.get_feature_names_out())

print("\n🔶 NMF Topics (Mattel):")
nmf_topics = show_topics(nmf, tfidf_vec.get_feature_names_out())


# In[14]:


import pandas as pd

data = {
    "Topic #": [1, 2, 3, 4],
    "Topic Name": [
        "Cash Flow, Share Repurchases & Operational Performance",
        "Brand Growth, IP Expansion & Entertainment Strategy",
        "Cost Management, OPG Program & Operational Efficiency",
        "Brand Identity, Consumer Engagement & Portfolio Positioning"
    ],
    "Top Words": [
        "compared, repurchases, operations, billion, offset, increased, mattel, flows, share, year, cash, million",
        "grow, driven, franchise, brands, mattel, entertainment, offering, ip, expand, growing, toy, business",
        "reflects, opg, costs, profitable, declined, deflation, efficiencies, management, cost, compared, benefits, program",
        "owner, overview, family, fans, focused, following, world, iconic, leading, creates, portfolios, mattel"
    ],
    "Meaning": [
        "Focus on operating cash flow, share repurchases, and year-over-year movements in cash generation and financial performance.",
        "Emphasis on brand-led growth, expansion of IP, and Mattel’s strategy to strengthen entertainment offerings and franchises.",
        "Discussion of cost-saving initiatives, OPG program efficiencies, favorable cost trends, and management’s profitability actions.",
        "Highlights Mattel’s brand identity, consumer engagement, and emphasis on iconic, portfolio-driven experiences for global audiences."
    ]
}

mattel_df = pd.DataFrame(data)

pd.set_option("display.max_colwidth", None)
mattel_df


# In[ ]:




