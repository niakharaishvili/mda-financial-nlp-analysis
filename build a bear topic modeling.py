#!/usr/bin/env python
# coding: utf-8

# In[1]:


with open("build a bear mda.txt", "r", encoding="utf-8") as f:
    text = f.read()

print(text[:600])                 # preview
print("Word count:", len(text.split()))


# In[2]:


import re

def clean_text(t):
    t = t.lower()
    t = re.sub(r"[^a-z\s]", " ", t)      # remove numbers/punctuation
    t = re.sub(r"\s+", " ", t).strip()  # remove extra spaces
    return t

cleaned_full = clean_text(text)


# In[3]:


documents = text.split("\n\n")                  # paragraph split
documents = [clean_text(d) for d in documents]  # clean each paragraph
documents = [d for d in documents if len(d.split()) > 30]  # keep real paragraphs

print("Paragraph documents:", len(documents))
print(documents[0][:300])


# In[4]:


from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

count_vec = CountVectorizer(
    stop_words="english",
    max_features=2000,
    ngram_range=(1,2)   # bigrams help in MD&A
)
X_count = count_vec.fit_transform(documents)

tfidf_vec = TfidfVectorizer(
    stop_words="english",
    max_features=2000,
    ngram_range=(1,2)
)
X_tfidf = tfidf_vec.fit_transform(documents)


# In[5]:


from sklearn.decomposition import LatentDirichletAllocation, NMF

lda = LatentDirichletAllocation(n_components=4, random_state=42)
lda.fit(X_count)

nmf = NMF(n_components=4, random_state=42)
nmf.fit(X_tfidf)


# In[6]:


def show_topics(model, feature_names, n_words=12):
    topics_out = []
    for i, topic in enumerate(model.components_):
        words = [feature_names[j] for j in topic.argsort()[-n_words:]]
        topics_out.append((i+1, words))
        print(f"\nTOPIC {i+1}: {', '.join(words)}")
    return topics_out

print("🔷 LDA Topics (Build-A-Bear):")
lda_topics = show_topics(lda, count_vec.get_feature_names_out())

print("\n🔶 NMF Topics (Build-A-Bear):")
nmf_topics = show_topics(nmf, tfidf_vec.get_feature_names_out())


# In[7]:


# 1) start from cleaned_full you already made
sent_docs = [s.strip() for s in cleaned_full.split(".") if len(s.split()) > 8]

print("Sentence docs:", len(sent_docs))


# In[8]:


from sklearn.feature_extraction.text import CountVectorizer

count_vec = CountVectorizer(
    stop_words="english",
    max_features=1500,
    ngram_range=(1,2),
    min_df=2,      # must appear in at least 2 docs
    max_df=0.8     # ignore words in >80% of docs
)

X_count = count_vec.fit_transform(sent_docs)


# In[ ]:


count_vec = CountVectorizer(
    stop_words="english",
    ngram_range=(1,2)
)

X_count = count_vec.fit_transform(sent_docs)


# In[9]:


from sklearn.decomposition import LatentDirichletAllocation

lda = LatentDirichletAllocation(n_components=3, random_state=42)
lda.fit(X_count)


# In[11]:


def show_topics(model, feature_names, n_words=12):
    for i, topic in enumerate(model.components_):
        words = [feature_names[j] for j in topic.argsort()[-n_words:]]
        print(f"\nTOPIC {i+1}: {', '.join(words)}")

print("🔷 LDA Topics (Build-A-Bear):")
show_topics(lda, count_vec.get_feature_names_out())


# In[12]:


from sklearn.feature_extraction.text import CountVectorizer

count_vec = CountVectorizer(
    stop_words="english",
    ngram_range=(1,2)
)

X_count = count_vec.fit_transform(sent_docs)


# In[13]:


from sklearn.decomposition import LatentDirichletAllocation

lda = LatentDirichletAllocation(n_components=3, random_state=42)
lda.fit(X_count)


# In[14]:


def show_topics(model, feature_names, n_words=12):
    for i, topic in enumerate(model.components_):
        words = [feature_names[j] for j in topic.argsort()[-n_words:]]
        print(f"\nTOPIC {i+1}: {', '.join(words)}")

print("🔷 LDA Topics (Build-A-Bear):")
show_topics(lda, count_vec.get_feature_names_out())


# In[15]:


# ===== Build-A-Bear topic modeling summary =====

bab_topic_numbers = [1, 2, 3, 4]

bab_topic_names = [
    "Experiential Retail & Brand Engagement",
    "Digital Commerce & Omnichannel Growth",
    "Partner-Operated & International Expansion",
    "Licensing, New Categories & Adult/Teen Market"
]

bab_top_words = [
    "experience, build bear, locations, digital, retail, consumer, products, brand",
    "digital, commerce, growing, online, consumer, locations, marketing",
    "partner operated, international, formats, stores, franchise, expansion",
    "licensing, categories, collections, tweens, adults, plush, collectibles"
]

bab_meanings = [
    "Focus on experiential retail model and emotional brand engagement.",
    "Emphasis on digital commerce, omnichannel strategy, and online engagement.",
    "Growth through partner-operated stores, franchising, and international expansion.",
    "Expansion into licensing, new product categories, and older demographics."
]


# In[16]:


import pandas as pd

bab_df = pd.DataFrame({
    "Topic #": bab_topic_numbers,
    "Topic Name": bab_topic_names,
    "Top Words": bab_top_words,
    "Meaning": bab_meanings
})

bab_df


# In[17]:


import pandas as pd

pd.set_option("display.max_colwidth", None)   # don’t cut long cells
pd.set_option("display.max_rows", 100)
pd.set_option("display.max_columns", 20)

bab_df


# In[ ]:




