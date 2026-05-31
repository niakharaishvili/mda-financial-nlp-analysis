#!/usr/bin/env python
# coding: utf-8

# In[1]:


with open("funko mda.txt", "r", encoding="utf-8") as f:
    text = f.read()

print(text[:600])
print("Word count:", len(text.split()))


# In[2]:


import re

def clean_text(t):
    t = t.lower()
    t = re.sub(r"[^a-z\s]", " ", t)      # remove numbers/punctuation
    t = re.sub(r"\s+", " ", t).strip()  # extra spaces
    return t

cleaned_full = clean_text(text)


# In[3]:


documents = text.split("\n\n")                  # paragraph split
documents = [clean_text(d) for d in documents]  # clean each
documents = [d for d in documents if len(d.split()) > 30]  # keep real paragraphs

print("Paragraph documents:", len(documents))
print(documents[0][:300])


# In[6]:


from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

count_vec = CountVectorizer(
    stop_words="english",
    max_features=2000,
    ngram_range=(1,2)   # bigrams help MD&A
)
X_count = count_vec.fit_transform(documents)

tfidf_vec = TfidfVectorizer(
    stop_words="english",
    max_features=2000,
    ngram_range=(1,2)
)
X_tfidf = tfidf_vec.fit_transform(documents)


# In[7]:


from sklearn.decomposition import LatentDirichletAllocation, NMF

lda = LatentDirichletAllocation(n_components=4, random_state=42)
lda.fit(X_count)

nmf = NMF(n_components=4, random_state=42, init="nndsvd")
nmf.fit(X_tfidf)


# In[8]:


from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

count_vec = CountVectorizer(
    stop_words="english",
    max_features=1000,     # smaller vocab for short text
    ngram_range=(1,1)      # unigrams only
)
X_count = count_vec.fit_transform(documents)

tfidf_vec = TfidfVectorizer(
    stop_words="english",
    max_features=1000,
    ngram_range=(1,1)
)
X_tfidf = tfidf_vec.fit_transform(documents)


# In[9]:


from sklearn.decomposition import LatentDirichletAllocation, NMF

lda = LatentDirichletAllocation(n_components=3, random_state=42)
lda.fit(X_count)

nmf = NMF(n_components=3, random_state=42)
nmf.fit(X_tfidf)


# In[10]:


def show_topics(model, feature_names, n_words=12):
    for i, topic in enumerate(model.components_):
        words = [feature_names[j] for j in topic.argsort()[-n_words:]]
        print(f"\nTOPIC {i+1}: {', '.join(words)}")

print("🔷 LDA Topics (Funko):")
show_topics(lda, count_vec.get_feature_names_out())

print("\n🔶 NMF Topics (Funko):")
show_topics(nmf, tfidf_vec.get_feature_names_out())


# In[11]:


import pandas as pd

funko_topic_numbers = [1, 2, 3]

funko_topic_names = [
    "Macroeconomic & Retail Demand Pressure",
    "Political/Geopolitical Instability & Financial Risk",
    "Global Footprint, Licensing Model & International Exposure"
]

funko_top_words = [
    "fan, macroeconomic, inventory, sales, margin, products, net, income, culture, america",
    "unrest, political, instability, financial, retail, orders, gross, remain, factors",
    "geographies, retailers, procure, uncertainty, asia, international, impact, overview, israel, hamas"
]

funko_meanings = [
    "Highlights inflation, interest rates, tariffs and retail slowdown impacting sales, margins, and inventory.",
    "Stresses geopolitical/political instability as a risk to financial performance and retailer ordering behavior.",
    "Describes Funko’s global licensed pop-culture model and exposure to international markets/sourcing."
]

funko_df = pd.DataFrame({
    "Topic #": funko_topic_numbers,
    "Topic Name": funko_topic_names,
    "Top Words": funko_top_words,
    "Meaning": funko_meanings
})

pd.set_option("display.max_colwidth", None)
funko_df


# In[ ]:




