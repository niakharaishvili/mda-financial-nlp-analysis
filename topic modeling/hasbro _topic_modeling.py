#!/usr/bin/env python
# coding: utf-8

# In[1]:


with open("hasbro mda.txt", "r", encoding="utf-8") as f:
    text = f.read()

print(text[:500])
print("Word count:", len(text.split()))


# In[2]:


import re

def clean_text(t):
    t = t.lower()
    t = re.sub(r"[^a-z\s]", " ", t)      # remove numbers/punct.
    t = re.sub(r"\s+", " ", t).strip()  # remove extra spaces
    return t

cleaned = clean_text(text)


# In[3]:


documents = text.split("\n\n")                 # split by paragraphs
documents = [clean_text(d) for d in documents] # clean each paragraph
documents = [d for d in documents if len(d.split()) > 30]  # remove tiny ones

print("Paragraph-documents:", len(documents))
print(documents[0][:300])


# In[4]:


from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# LDA (COUNT + bigrams)
count_vec = CountVectorizer(
    stop_words="english",
    max_features=2000,
    ngram_range=(1,2)   # <-- bigrams fix
)
X_count = count_vec.fit_transform(documents)

# NMF (TF-IDF + bigrams)
tfidf_vec = TfidfVectorizer(
    stop_words="english",
    max_features=2000,
    ngram_range=(1,2)
)
X_tfidf = tfidf_vec.fit_transform(documents)


# In[5]:


from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# LDA (COUNT + bigrams)
count_vec = CountVectorizer(
    stop_words="english",
    max_features=2000,
    ngram_range=(1,2)   # <-- bigrams fix
)
X_count = count_vec.fit_transform(documents)

# NMF (TF-IDF + bigrams)
tfidf_vec = TfidfVectorizer(
    stop_words="english",
    max_features=2000,
    ngram_range=(1,2)
)
X_tfidf = tfidf_vec.fit_transform(documents)


# In[6]:


from sklearn.decomposition import LatentDirichletAllocation

lda = LatentDirichletAllocation(n_components=4, random_state=42)
lda.fit(X_count)


# In[7]:


from sklearn.decomposition import NMF

nmf = NMF(n_components=4, random_state=42)
nmf.fit(X_tfidf)


# In[8]:


def show_topics(model, feature_names, n_words=12):
    for i, topic in enumerate(model.components_):
        words = [feature_names[j] for j in topic.argsort()[-n_words:]]
        print(f"\nTOPIC {i+1}: {', '.join(words)}")

print("🔷 LDA Topics:")
show_topics(lda, count_vec.get_feature_names_out())

print("\n🔶 NMF Topics:")
show_topics(nmf, tfidf_vec.get_feature_names_out())


# In[9]:


import pandas as pd

data = {
    "Topic #": [1, 2, 3, 4],
    "Topic Name": [
        "Impairments & Intangibles",
        "Core Business (Toys, Games, Digital, IP)",
        "Liquidity, Cash Flow, FX & Obligations",
        "Revenues, Products & Film/TV Segments"
    ],
    "Top Words": [
        "impairment, intangible assets, goodwill, credit, value, assets, tax",
        "ip, digital games, toys, hasbro, licensing, brands, entertainment",
        "future, inventory, obligations, foreign, cash, year, activities",
        "products, expense, film tv, tax, revenues, segment, compared"
    ],
    "Meaning": [
        "Focus on goodwill impairments and valuation of intangible assets.",
        "Management emphasis on core brands, toys, digital gaming, and licensing.",
        "Discussion of cash flow, foreign currency exposure, and financial obligations.",
        "Explanation of segment-level revenues, cost trends, and entertainment business."
    ]
}

df = pd.DataFrame(data)
df


# In[ ]:




