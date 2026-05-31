#!/usr/bin/env python
# coding: utf-8

# In[ ]:


filename = "jakks pacific mda.txt"

with open(filename, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

print(text[:800])
print("\nWord count:", len(text.split()))


# In[ ]:


import re

def clean_text(t):
    t = t.lower()
    t = re.sub(r"[^a-z\s]", " ", t)      # remove numbers/punctuation
    t = re.sub(r"\s+", " ", t).strip()  # collapse whitespace
    return t

cleaned_full = clean_text(text)


# In[ ]:


# Paragraph docs
documents = text.split("\n\n")
documents = [clean_text(d) for d in documents]
documents = [d for d in documents if len(d.split()) > 30]

print("Paragraph documents:", len(documents))

# If too short, switch to sentences
if len(documents) < 10:
    documents = [s.strip() for s in cleaned_full.split(".") if len(s.split()) > 8]
    print("Switched to sentence docs:", len(documents))


# In[ ]:


from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

short_text = len(documents) < 20

count_vec = CountVectorizer(
    stop_words="english",
    max_features=1000 if short_text else 2000,
    ngram_range=(1,1) if short_text else (1,2)
)
X_count = count_vec.fit_transform(documents)

tfidf_vec = TfidfVectorizer(
    stop_words="english",
    max_features=1000 if short_text else 2000,
    ngram_range=(1,1) if short_text else (1,2)
)
X_tfidf = tfidf_vec.fit_transform(documents)

print("short_text =", short_text)
print("X_count shape:", X_count.shape)
print("X_tfidf shape:", X_tfidf.shape)


# In[ ]:


from sklearn.decomposition import LatentDirichletAllocation, NMF

n_topics = 3 if short_text else 4

lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
lda.fit(X_count)

nmf = NMF(n_components=n_topics, random_state=42)
nmf.fit(X_tfidf)

print("Topics used:", n_topics)


# In[ ]:


def show_topics(model, feature_names, n_words=12):
    for i, topic in enumerate(model.components_):
        words = [feature_names[j] for j in topic.argsort()[-n_words:]]
        print(f"\nTOPIC {i+1}: {', '.join(words)}")

print("🔷 LDA Topics (Jakks Pacific):")
show_topics(lda, count_vec.get_feature_names_out())

print("\n🔶 NMF Topics (Jakks Pacific):")
show_topics(nmf, tfidf_vec.get_feature_names_out())


# In[2]:


import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF

filename = "jakks pacific mda.txt"

# --- load ---
with open(filename, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# --- clean ---
def clean_text(t):
    t = t.lower()
    t = re.sub(r"[^a-z\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

cleaned_full = clean_text(text)

# --- split into docs (force sentences because Jakks is short) ---
documents = [s.strip() for s in cleaned_full.split(".") if len(s.split()) > 5]

print("DOC COUNT:", len(documents))
print("SAMPLE DOC:", documents[0][:200] if documents else "EMPTY")

# --- vectorize (tiny settings for short text) ---
count_vec = CountVectorizer(stop_words="english", max_features=500, ngram_range=(1,1))
X_count = count_vec.fit_transform(documents)

tfidf_vec = TfidfVectorizer(stop_words="english", max_features=500, ngram_range=(1,1))
X_tfidf = tfidf_vec.fit_transform(documents)

print("X_count shape:", X_count.shape)
print("X_tfidf shape:", X_tfidf.shape)
print("VOCAB SIZE:", len(count_vec.get_feature_names_out()))

# --- fit models with 2 topics ---
lda = LatentDirichletAllocation(n_components=2, random_state=42)
lda.fit(X_count)

nmf = NMF(n_components=2, random_state=42)
nmf.fit(X_tfidf)

# --- show topics ---
def show_topics(model, feature_names, n_words=12):
    for i, topic in enumerate(model.components_):
        words = [feature_names[j] for j in topic.argsort()[-n_words:]]
        print(f"\nTOPIC {i+1}: {', '.join(words)}")

print("\n🔷 LDA Topics (Jakks):")
show_topics(lda, count_vec.get_feature_names_out())

print("\n🔶 NMF Topics (Jakks):")
show_topics(nmf, tfidf_vec.get_feature_names_out())


# In[4]:


import pandas as pd

# ====== JAKKS PACIFIC TOPIC TABLE (fill these) ======

jakks_topic_numbers = [1, 2, 3]   # use 2 topics if you modeled 2

jakks_topic_names = [
    "TOPIC NAME 1",
    "TOPIC NAME 2",
    "TOPIC NAME 3"
]

jakks_top_words = [
    "paste your Topic 1 words here",
    "paste your Topic 2 words here",
    "paste your Topic 3 words here"
]

jakks_meanings = [
    "write 1 sentence meaning for topic 1",
    "write 1 sentence meaning for topic 2",
    "write 1 sentence meaning for topic 3"
]

jakks_df = pd.DataFrame({
    "Topic #": jakks_topic_numbers,
    "Topic Name": jakks_topic_names,
    "Top Words": jakks_top_words,
    "Meaning": jakks_meanings
})

pd.set_option("display.max_colwidth", None)
jakks_df


# In[6]:


# extract NMF topics into a variable
nmf_topics = []

for i, topic in enumerate(nmf.components_):
    words = [tfidf_vec.get_feature_names_out()[j] 
             for j in topic.argsort()[-12:]]
    nmf_topics.append((i+1, words))
    print(f"TOPIC {i+1}: {', '.join(words)}")


# In[7]:


import pandas as pd

topic_numbers = [t[0] for t in nmf_topics]
top_words_list = [", ".join(t[1]) for t in nmf_topics]

topic_names = ["NAME ME"] * len(topic_numbers)
meanings     = ["ADD MEANING"] * len(topic_numbers)

jakks_df = pd.DataFrame({
    "Topic #": topic_numbers,
    "Topic Name": topic_names,
    "Top Words": top_words_list,
    "Meaning": meanings
})

pd.set_option("display.max_colwidth", None)
jakks_df


# In[8]:


filename = "jakks pacific mda.txt"

with open(filename, "r", encoding="utf-8", errors="ignore") as f:
    raw_text = f.read()

print(raw_text[:800])
print("\nWord count:", len(raw_text.split()))


# In[9]:


import re

def clean_text(t):
    t = t.lower()
    t = re.sub(r"[^a-z\s]", " ", t)      # remove numbers/punctuation
    t = re.sub(r"\s+", " ", t).strip()  # collapse whitespace
    return t

cleaned_full = clean_text(raw_text)


# In[10]:


# Try paragraph docs first
documents = raw_text.split("\n\n")
documents = [clean_text(d) for d in documents]
documents = [d for d in documents if len(d.split()) > 30]

print("Paragraph docs:", len(documents))

# If too few paragraphs, switch to sentence docs
if len(documents) < 10:
    documents = [s.strip() for s in cleaned_full.split(".") if len(s.split()) > 5]
    print("Switched to sentence docs:", len(documents))

print("Sample document:\n", documents[0][:250] if documents else "EMPTY")


# In[11]:


from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

short_text = len(documents) < 20

count_vec = CountVectorizer(
    stop_words="english",
    max_features=500 if short_text else 2000,
    ngram_range=(1,1) if short_text else (1,2)
)
X_count = count_vec.fit_transform(documents)

tfidf_vec = TfidfVectorizer(
    stop_words="english",
    max_features=500 if short_text else 2000,
    ngram_range=(1,1) if short_text else (1,2)
)
X_tfidf = tfidf_vec.fit_transform(documents)

print("short_text:", short_text)
print("X_count shape:", X_count.shape)
print("X_tfidf shape:", X_tfidf.shape)
print("Vocab size:", len(count_vec.get_feature_names_out()))


# In[12]:


from sklearn.decomposition import LatentDirichletAllocation, NMF

n_topics = 2 if short_text else 4   # Jakks usually needs 2–3 topics

lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
lda.fit(X_count)

nmf = NMF(n_components=n_topics, random_state=42)
nmf.fit(X_tfidf)

print("Topics used:", n_topics)


# In[13]:


def show_topics(model, feature_names, n_words=12):
    topics_out = []
    for i, topic in enumerate(model.components_):
        words = [feature_names[j] for j in topic.argsort()[-n_words:]]
        topics_out.append((i+1, words))
        print(f"\nTOPIC {i+1}: {', '.join(words)}")
    return topics_out

print("🔷 LDA Topics (Jakks Pacific):")
lda_topics = show_topics(lda, count_vec.get_feature_names_out())

print("\n🔶 NMF Topics (Jakks Pacific):")
nmf_topics = show_topics(nmf, tfidf_vec.get_feature_names_out())


# In[14]:


import pandas as pd

data = {
    "Topic #": [1, 2],
    "Topic Name": [
        "Fair Value Accounting & Measurement Inputs",
        "Asset Recoverability, Market Risks & Consolidated Operations"
    ],
    "Top Words": [
        "accounting, amounts, assets, liabilities, use, based, current, expected, financial, inputs, value, fair",
        "assets, value, results, participants, markets, utilize, time, recoverable, operations, consolidated, risk, measurement"
    ],
    "Meaning": [
        "Discussion of fair value measurement, accounting inputs, expected values, and valuation techniques for assets and liabilities.",
        "Emphasis on recoverability of assets, market-related risks, measurement uncertainty, and consolidated operational factors."
    ]
}

jakks_df = pd.DataFrame(data)

# show full text (no ...)
pd.set_option("display.max_colwidth", None)

jakks_df


# In[ ]:




