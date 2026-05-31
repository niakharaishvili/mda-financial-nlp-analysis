#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from textblob import TextBlob
from bs4 import BeautifulSoup
import seaborn as sns
import math
import os


# In[2]:


import sys
get_ipython().system('{sys.executable} -m pip install textblob bs4 seaborn')


# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from textblob import TextBlob
from bs4 import BeautifulSoup
import seaborn as sns
import math
import os


# In[2]:


import sys
get_ipython().system('{sys.executable} -m pip install seaborn bs4 textblob')


# In[3]:


# Required packages: pandas, numpy, matplotlib, seaborn, textblob, bs4


# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from textblob import TextBlob
from bs4 import BeautifulSoup
import seaborn as sns
import math
import os


# In[2]:


def clean_num(text):
    s = str(text).strip().replace(",", "").replace("$", "")
    if s in ["", "-", "—"]:
        return np.nan
    try:
        return float(s)
    except:
        return np.nan

# add sentiment, readability, topic modeling, etc.


# In[28]:


# ========================================
# HASBRO ANALYSIS
# ========================================


# In[9]:


import pandas as pd

# 4 Hasbro 10-K XBRL instance files you downloaded
files = [
    (2021, "hasbro-20211226_htm.xml"),
    (2022, "hasbro-20221225_htm.xml"),
    (2023, "hasbro-20231231_htm.xml"),
    (2024, "has-20241229_htm.xml"),   # note: file name starts with "has-"
]


# In[11]:


def extract_metrics(filename):
    ...


# In[12]:


import math
import pandas as pd
from bs4 import BeautifulSoup

# ---------- helper to clean numbers ----------
def clean_num(text):
    if text is None:
        return math.nan
    s = str(text).strip().replace(",", "").replace("$", "").replace("\u2212", "-")
    if s in ["", "—", "-", "na", "n/a", "NA"]:
        return math.nan
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return math.nan


# ---------- MAIN EXTRACT FUNCTION ----------
def extract_metrics(filename):

    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    facts = []
    for fact in soup.find_all():
        if not fact.has_attr("contextRef"):
            continue
        txt = fact.text.strip() if fact.text else ""
        if txt == "":
            continue
        facts.append({
            "qname": fact.name,
            "context": fact["contextRef"],
            "value_raw": txt,
        })

    df = pd.DataFrame(facts)

    def get_first(tag_list, pattern=None):
        if isinstance(tag_list, str):
            tag_list = [tag_list]
        sub = df[df["qname"].isin(tag_list)].copy()
        if pattern:
            sub = sub[sub["context"].str.contains(pattern, regex=True)]
        if sub.empty:
            return math.nan
        sub["val"] = sub["value_raw"].map(clean_num)
        sub = sub.dropna(subset=["val"])
        if sub.empty:
            return math.nan
        return float(sub.loc[sub["val"].abs().idxmax(), "val"])

    # ---------------- INCOME STATEMENT ----------------
    revenue = get_first(["Revenues", "SalesRevenueNet",
                         "RevenueFromContractWithCustomerExcludingAssessedTax"])

    cogs = get_first(["CostOfGoodsSold", "CostOfGoodsAndServicesSold"])

    sga = get_first(["SellingGeneralAndAdministrativeExpense"])

    net_income = get_first(["NetIncomeLoss"])

    op_income_direct = get_first(["OperatingIncomeLoss"])
    if not math.isnan(op_income_direct):
        operating_income = op_income_direct
    elif any(math.isnan(x) for x in [revenue, cogs, sga]):
        operating_income = math.nan
    else:
        operating_income = revenue - cogs - sga


    # ---------------- BALANCE SHEET ----------------
    instant = r"^[iI]"

    assets = get_first(["Assets"], pattern=instant)
    liab_current = get_first(["LiabilitiesCurrent"], pattern=instant)
    liab_noncurrent = get_first(["LiabilitiesNoncurrent"], pattern=instant)

    if math.isnan(liab_current) and math.isnan(liab_noncurrent):
        total_liab = math.nan
    else:
        total_liab = (0 if math.isnan(liab_current) else liab_current) + \
                     (0 if math.isnan(liab_noncurrent) else liab_noncurrent)

    equity = get_first(["StockholdersEquity",
                        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
                       pattern=instant)

    cash = get_first(["CashAndCashEquivalentsAtCarryingValue"], pattern=instant)

    inventory = get_first(["InventoryNet", "InventoriesNet"], pattern=instant)

    ppe = get_first(["PropertyPlantAndEquipmentNet"], pattern=instant)


    # ---------------- CASH FLOWS ----------------
    cfo = get_first(["NetCashProvidedByUsedInOperatingActivities"])
    cfi = get_first(["NetCashProvidedByUsedInInvestingActivities"])
    cff = get_first(["NetCashProvidedByUsedInFinancingActivities"])


    # ---------------- EPS ----------------
    eps_basic = get_first(["EarningsPerShareBasic"])
    eps_diluted = get_first(["EarningsPerShareDiluted"])


    # ---------------- DEBT ----------------
    debt = get_first(["DebtInstrumentCarryingAmount",
                      "LongTermDebtNoncurrent",
                      "DebtCurrent",
                      "DebtNoncurrent"], pattern=instant)


    # ---------------- TAX ----------------
    tax_expense = get_first(["IncomeTaxExpenseBenefit"])


    # ------------- RETURN DICTIONARY ---------------
    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": operating_income,
        "NetIncome": net_income,
        "TotalAssets": assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": equity,
        "Cash": cash,
        "Inventory": inventory,
        "PropertyPlantEquipment": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "Debt": debt,
        "TaxExpense": tax_expense,
    }


# In[16]:


rows = []

for year, fname in files:
    print(f"Processing {year} – {fname} ...")
    metrics = extract_metrics(fname)
    metrics["Year"] = year
    rows.append(metrics)

hasbro_results = pd.DataFrame(rows).set_index("Year")
hasbro_results


# In[17]:


import matplotlib.pyplot as plt
ax = hasbro_results[["CFO", "CFI", "CFF"]].div(1e6).plot(
    kind="bar", figsize=(10,6)
)
ax.set_title("Hasbro – Cash Flows (CFO, CFI, CFF)")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("USD (millions)")
plt.xticks(rotation=0)
plt.show()


# In[19]:


ax = hasbro_results[["TotalAssets", "TotalLiabilities", "TotalEquity"]]\
        .dropna().div(1e6).plot(
            kind="bar", figsize=(10,6)
        )
ax.set_title("Hasbro – Assets, Liabilities, Equity")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("USD (millions)")
plt.xticks(rotation=0)
plt.show()


# In[20]:


ax = hasbro_results[["EPS_Basic", "EPS_Diluted"]].plot(
    kind="bar", figsize=(8,5)
)
ax.set_title("Hasbro – EPS Basic vs Diluted")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("EPS (USD)")
plt.xticks(rotation=0)
plt.show()


# In[21]:


import math
import pandas as pd
from bs4 import BeautifulSoup

# ---------- helper to clean numbers ----------
def clean_num(text):
    if text is None:
        return math.nan
    s = str(text).strip().replace(",", "").replace("$", "").replace("\u2212", "-")
    if s in ["", "—", "-", "na", "n/a", "NA"]:
        return math.nan
    if s[0] == "(" and s[-1] == ")":
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return math.nan

# ---------- function that reads ONE 10-K iXBRL and extracts all metrics ----------
def extract_metrics(filename):
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    facts = []
    for fact in soup.find_all():
        if not fact.has_attr("contextRef"):
            continue
        txt = fact.text.strip() if fact.text else ""
        if txt == "":
            continue
        facts.append(
            {
                "qname": fact.name,
                "context": fact["contextRef"],
                "value_raw": txt,
            }
        )

    df = pd.DataFrame(facts)

    def get_first(tag_list, pattern=None):
        sub = df[df["qname"].isin(tag_list)].copy()
        if pattern:
            sub = sub[sub["context"].str.contains(pattern, regex=True)]
        if sub.empty:
            return math.nan
        sub["val"] = sub["value_raw"].map(clean_num)
        sub = sub.dropna(subset=["val"])
        if sub.empty:
            return math.nan
        return float(sub.loc[sub["val"].abs().idxmax(), "val"])

    # --- Income statement items ---
    revenue = get_first(
        ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues"]
    )
    cogs = get_first(["CostOfGoodsAndServicesSold", "CostOfSales"])
    sga = get_first(["SellingGeneralAndAdministrativeExpense"])
    net_income = get_first(["NetIncomeLoss"])

    if any(math.isnan(x) for x in [revenue, cogs, sga]):
        operating_income = math.nan
    else:
        operating_income = revenue - cogs - sga

    # --- Balance sheet items ---
    assets = get_first(["Assets"], pattern=r"^i_")
    cash = get_first(["CashAndCashEquivalentsAtCarryingValue"], pattern=r"^i_")
    inventory = get_first(["InventoryNet"], pattern=r"^i_")
    ppe = get_first(["PropertyPlantAndEquipmentNet"], pattern=r"^i_")
    liab_current = get_first(["LiabilitiesCurrent"], pattern=r"^i_")
    liab_noncurrent = get_first(
        ["OtherLiabilitiesNoncurrent", "LiabilitiesNoncurrent"], pattern=r"^i_"
    )
    total_liab = (
        (liab_current if not math.isnan(liab_current) else 0.0)
        + (liab_noncurrent if not math.isnan(liab_noncurrent) else 0.0)
    )
    if math.isnan(liab_current) and math.isnan(liab_noncurrent):
        total_liab = math.nan

    equity = get_first(
        [
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ],
        pattern=r"^i_",
    )

    eps_basic = get_first(["EarningsPerShareBasic"])
    eps_diluted = get_first(["EarningsPerShareDiluted"])

    cfo = get_first(
        [
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ]
    )
    cfi = get_first(
        [
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
        ]
    )
    cff = get_first(
        [
            "NetCashProvidedByUsedInFinancingActivities",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
        ]
    )
    net_change_cash = get_first(["CashAndCashEquivalentsPeriodIncreaseDecrease"])

    debt = get_first(
        [
            "LongTermDebtNoncurrent",
            "LongTermDebtCurrent",
            "LongTermDebtAndCapitalLeaseObligations",
            "DebtCurrent",
            "DebtNoncurrent",
            "DebtInstrumentCarryingAmount",
        ]
    )

    tax_expense = get_first(
        ["IncomeTaxExpenseBenefit", "IncomeTaxExpenseBenefitContinuingOperations"]
    )

    seg = df[df["qname"].isin(["RevenueFromContractWithCustomerExcludingAssessedTax"])].copy()
    seg["val"] = seg["value_raw"].map(clean_num)
    seg = seg.dropna(subset=["val"])

    seg_retail = seg[
        seg["context"].str.contains("RetailMember")
        & ~seg["context"].str.contains("GiftCardBreakageMember")
    ]["val"].sum()

    seg_commercial = seg[seg["context"].str.contains("CommercialProductAndServiceMember")][
        "val"
    ].sum()

    seg_international = seg[seg["context"].str.contains("InternationalFranchisingMember")][
        "val"
    ].sum()

    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": operating_income,
        "NetIncome": net_income,
        "TotalAssets": assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": equity,
        "Cash": cash,
        "Inventory": inventory,
        "PropertyPlantEquipment": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "NetChangeCash": net_change_cash,
        "Debt": debt,
        "TaxExpense": tax_expense,
        "SegRev_Retail": float(seg_retail) if not math.isnan(seg_retail) else math.nan,
        "SegRev_Commercial": float(seg_commercial) if not math.isnan(seg_commercial) else math.nan,
        "SegRev_International": float(seg_international)
        if not math.isnan(seg_international)
        else math.nan,
    }

# ---------- list of your files with the fiscal year label you want ----------
# ---------- list of your Disney files with the fiscal year label you want ----------
files = [
    (2021, "hasbro-20211226_htm.xml"),
    (2022, "hasbro-20221225_htm.xml"),
    (2023, "hasbro-20231231_htm.xml"),
    (2024, "has-20241229_htm.xml"),
]

rows = []
for year, fname in files:
    print(f"Processing {year} - {fname} ...")
    metrics = extract_metrics(fname)
    metrics["Year"] = year
    rows.append(metrics)

results = pd.DataFrame(rows).set_index("Year")
results


# In[22]:


results.head()
results.index


# In[23]:


import matplotlib.pyplot as plt

# Make sure the index is integer years (it already is, but just to be safe)
results.index = results.index.astype(int)

# Plot revenue
ax = results["Revenue"].plot(kind="line", marker="o", figsize=(10,5))

# Force x-axis ticks to be exactly the years in the index
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("Hasbro Revenue Over Time")
plt.xlabel("Year")
plt.ylabel("Revenue (USD)")
plt.grid(True)
plt.show()


# In[24]:


import matplotlib.pyplot as plt

# Ensure index is integer years
results.index = results.index.astype(int)

ax = results[["Revenue", "NetIncome"]].plot(
    kind="line", marker="o", figsize=(10,5)
)

# Force x-axis to show only actual years
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("Revenue & Net Income Over Time")
plt.xlabel("Year")
plt.ylabel("USD")
plt.grid(True)
plt.show()


# In[25]:


import matplotlib.pyplot as plt

# Ensure index is integer years
results.index = results.index.astype(int)

ax = results[["Revenue", "NetIncome"]].plot(
    kind="line", marker="o", figsize=(10,5)
)

# Force x-axis to show only actual years
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("Revenue & Net Income Over Time")
plt.xlabel("Year")
plt.ylabel("USD")
plt.grid(True)
plt.show()


# In[26]:


import matplotlib.pyplot as plt

# Ensure index is integer years
results.index = results.index.astype(int)

ax = results[["OperatingIncome", "NetIncome"]].plot(
    kind="line", marker="o", figsize=(10,5)
)

# Force x-axis to show only actual years
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("OperatingIncome & Net Income Over Time")
plt.xlabel("Year")
plt.ylabel("USD")
plt.grid(True)
plt.show()


# In[29]:


# ==========================================
# MATTEL ANALYSIS
# ==========================================


# In[30]:


import pandas as pd
import xml.etree.ElementTree as ET
import re
import numpy as np

# ---------------------------
# helper to clean numbers
# ---------------------------
def clean_num(x):
    if x is None:
        return np.nan
    s = str(x).strip().replace(",", "").replace("$", "").replace("(", "-").replace(")", "")
    s = re.sub(r"[^\d\.\-]", "", s)
    try:
        return float(s)
    except:
        return np.nan

# ---------------------------
# extract_metrics function
# ---------------------------
def extract_metrics(filename):
    print(f"Reading {filename} ...")
    tree = ET.parse(filename)
    root = tree.getroot()

    ns = {
        "us-gaap": "http://fasb.org/us-gaap/2021-01-31",
        "dei": "http://xbrl.sec.gov/dei/2021q4",
        "iso4217": "http://www.xbrl.org/2003/iso4217"
    }

    # find contexts
    durations = {}
    instants = {}
    for ctx in root.findall(".//{http://www.xbrl.org/2003/instance}context"):
        cid = ctx.attrib.get("id", "")
        period = ctx.find("{http://www.xbrl.org/2003/instance}period")

        if period.find("{http://www.xbrl.org/2003/instance}endDate") is not None:
            durations[cid] = True
        if period.find("{http://www.xbrl.org/2003/instance}instant") is not None:
            instants[cid] = True

    # small helper
    def get_first(tags, pattern_dict):
        for tag in tags:
            for elem in root.findall(f".//us-gaap:{tag}", ns):
                ctx = elem.attrib.get("contextRef", "")
                if ctx in pattern_dict:
                    return clean_num(elem.text)
        return np.nan

    # ==== INCOME STATEMENT ====
    revenue = get_first(
        ["Revenues", "SalesRevenueNet"],
        durations
    )
    cogs = get_first(
        ["CostOfGoodsSold", "CostOfRevenue"],
        durations
    )
    op_inc = get_first(
        ["OperatingIncomeLoss"],
        durations
    )
    net_inc = get_first(
        ["NetIncomeLoss"],
        durations
    )

    # ==== BALANCE SHEET ====
    total_assets = get_first(["Assets"], instants)
    total_liab   = get_first(["Liabilities"], instants)
    total_equity = get_first(["StockholdersEquity"], instants)
    cash         = get_first(["CashAndCashEquivalentsAtCarryingValue"], instants)
    inventory    = get_first(["InventoryNet"], instants)
    ppe          = get_first(["PropertyPlantAndEquipmentNet"], instants)

    # ==== EPS ====
    eps_basic  = get_first(["EarningsPerShareBasic"], durations)
    eps_diluted = get_first(["EarningsPerShareDiluted"], durations)

    # ==== CASH FLOW ====
    cfo = get_first(["NetCashProvidedByUsedInOperatingActivities"], durations)
    cfi = get_first(["NetCashProvidedByUsedInInvestingActivities"], durations)
    cff = get_first(["NetCashProvidedByUsedInFinancingActivities"], durations)

    # ==== OTHER ====
    debt = get_first(
        ["LongTermDebtNoncurrent", "LongTermDebtCurrent", "DebtCurrent"],
        instants
    )
    tax_expense = get_first(["IncomeTaxExpenseBenefit"], durations)

    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": op_inc,
        "NetIncome": net_inc,
        "TotalAssets": total_assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": total_equity,
        "Cash": cash,
        "Inventory": inventory,
        "PPE": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "Debt": debt,
        "TaxExpense": tax_expense
    }


# In[31]:


files = [
    (2021, "mattel-20211231_htm.xml"),
    (2022, "mattel-20221231_htm.xml"),
    (2023, "mattel-20231231_htm.xml"),
    (2024, "mattel-20241231_htm.xml")
]


# In[32]:


rows = []

for year, fname in files:
    print(f"Processing {year} – {fname} ...")
    metrics = extract_metrics(fname)
    metrics["Year"] = year
    rows.append(metrics)

mattel_results = pd.DataFrame(rows).set_index("Year")
mattel_results


# In[33]:


from bs4 import BeautifulSoup

fname = "mattel-20221231_htm.xml"  # MAT 2022
with open(fname, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml-xml")

tags = sorted({tag.name for tag in soup.find_all()})
tags[:100]


# In[34]:


contexts = sorted({tag["contextRef"] for tag in soup.find_all() if tag.has_attr("contextRef")})
contexts[:50]


# In[35]:


import math
import pandas as pd
from bs4 import BeautifulSoup

def clean_num(text):
    if text is None:
        return math.nan
    s = str(text).strip().replace(",", "").replace("$", "").replace("\u2212", "-")
    if s in ["", "—", "-", "na", "n/a", "NA"]:
        return math.nan
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return math.nan


def extract_metrics_mattel(filename):
    """Parse a Mattel 10-K iXBRL XML and return key metrics as a dict."""
    print("Reading", filename)
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    # collect all numeric facts that have a contextRef
    facts = []
    for fact in soup.find_all():
        if not fact.has_attr("contextRef"):
            continue
        txt = (fact.text or "").strip()
        if not txt:
            continue
        facts.append(
            {
                "qname": fact.name,            # e.g. Assets, CostOfGoodsAndServicesSold
                "context": fact["contextRef"], # e.g. i..._D20220101-20221231 or i..._I20221231
                "value_raw": txt,
            }
        )

    df = pd.DataFrame(facts)

    def get_first(tag_list, pattern=None):
        """Pick the largest (by absolute value) among given tags (optionally filtered by context)."""
        if isinstance(tag_list, str):
            tag_list = [tag_list]
        sub = df[df["qname"].isin(tag_list)].copy()
        if pattern:
            sub = sub[sub["context"].str.contains(pattern, regex=True)]
        if sub.empty:
            return math.nan
        sub["val"] = sub["value_raw"].map(clean_num)
        sub = sub.dropna(subset=["val"])
        if sub.empty:
            return math.nan
        return float(sub.loc[sub["val"].abs().idxmax(), "val"])

    # Mattel instant contexts look like iXXXX_I20221231 etc.
    instant_pattern = r"_I20"  # match all instants (I2021..., I2022..., I2023..., I2024...)

    # ============ INCOME STATEMENT ============
    revenue = get_first(
        [
            "Revenues",
            "SalesRevenueNet",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "NetSales",   # add a Mattel-style fallback just in case
        ]
    )

    cogs = get_first(
        ["CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfGoodsSold"]
    )

    sga = get_first(["SellingGeneralAndAdministrativeExpense"])

    net_income = get_first(["NetIncomeLoss", "ProfitLoss"])

    op_direct = get_first(["OperatingIncomeLoss"])
    if not math.isnan(op_direct):
        operating_income = op_direct
    elif any(math.isnan(x) for x in [revenue, cogs, sga]):
        operating_income = math.nan
    else:
        operating_income = revenue - cogs - sga

    # ============ BALANCE SHEET ============
    assets = get_first(["Assets"], pattern=instant_pattern)
    if math.isnan(assets):
        ac = get_first(["AssetsCurrent"], pattern=instant_pattern)
        an = get_first(["AssetsNoncurrent"], pattern=instant_pattern)
        if not math.isnan(ac) or not math.isnan(an):
            assets = (0 if math.isnan(ac) else ac) + (0 if math.isnan(an) else an)

    liab_total = get_first(["Liabilities"], pattern=instant_pattern)
    liab_current = get_first(["LiabilitiesCurrent"], pattern=instant_pattern)
    liab_noncurrent = get_first(["LiabilitiesNoncurrent"], pattern=instant_pattern)

    if not math.isnan(liab_total):
        total_liab = liab_total
    elif math.isnan(liab_current) and math.isnan(liab_noncurrent):
        total_liab = math.nan
    else:
        total_liab = (0 if math.isnan(liab_current) else liab_current) + (
            0 if math.isnan(liab_noncurrent) else liab_noncurrent
        )

    equity = get_first(
        [
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ],
        pattern=instant_pattern,
    )

    cash = get_first(
        [
            "CashAndCashEquivalentsAtCarryingValue",
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
        ],
        pattern=instant_pattern,
    )

    inventory = get_first(
        ["InventoryNet", "InventoriesNet"], pattern=instant_pattern
    )

    ppe = get_first(
        ["PropertyPlantAndEquipmentNet"], pattern=instant_pattern
    )

    # ============ CASH FLOWS ============
    cfo = get_first(
        [
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ]
    )
    cfi = get_first(
        [
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
        ]
    )
    cff = get_first(
        [
            "NetCashProvidedByUsedInFinancingActivities",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
        ]
    )

    # ============ EPS ============
    eps_basic = get_first(["EarningsPerShareBasic"])
    eps_diluted = get_first(["EarningsPerShareDiluted"])

    # ============ DEBT ============
    debt = get_first(
        ["DebtInstrumentCarryingAmount", "LongTermDebtNoncurrent", "DebtNoncurrent", "DebtCurrent"],
        pattern=instant_pattern,
    )

    # ============ TAX ============
    tax_expense = get_first(["IncomeTaxExpenseBenefit"])

    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": operating_income,
        "NetIncome": net_income,
        "TotalAssets": assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": equity,
        "Cash": cash,
        "Inventory": inventory,
        "PropertyPlantEquipment": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "Debt": debt,
        "TaxExpense": tax_expense,
    }


# In[36]:


files = [
    (2021, "mattel-20211231_htm.xml"),
    (2022, "mattel-20221231_htm.xml"),
    (2023, "mattel-20231231_htm.xml"),
    (2024, "mattel-20241231_htm.xml"),
]

rows = []

for year, fname in files:
    print(f"Processing {year} – {fname} ...")
    metrics = extract_metrics_mattel(fname)
    metrics["Year"] = year
    rows.append(metrics)

mattel_results = pd.DataFrame(rows).set_index("Year")
mattel_results


# In[37]:


import matplotlib.pyplot as plt

# Revenue
ax = mattel_results["Revenue"].div(1e6).plot(kind="line", marker="o", figsize=(8,5))
ax.set_title("Mattel – Revenue Over Time")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("Revenue (USD millions)")
ax.grid(True)
plt.show()


# In[38]:


ax = mattel_results["OperatingIncome"].div(1e6).plot(
    kind="line", marker="o", figsize=(8,5)
)
ax.set_title("Mattel – Operating Income Over Time")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("Operating Income (USD millions)")
ax.grid(True)
plt.show()


# In[39]:


ax = mattel_results["NetIncome"].div(1e6).plot(
    kind="line", marker="o", figsize=(8,5)
)
ax.set_title("Mattel – Net Income Over Time")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("Net Income (USD millions)")
ax.grid(True)
plt.show()


# In[40]:


columns_to_plot = ["CFO", "CFI", "CFF"]

ax = mattel_results[columns_to_plot].div(1e6).plot(
    kind="line", marker="o", figsize=(10,6)
)
ax.set_title("Mattel – Cash Flow Components")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("USD millions")
ax.grid(True)
plt.show()


# In[41]:


cols = ["TotalAssets", "TotalLiabilities", "TotalEquity"]

ax = mattel_results[cols].div(1e6).plot(
    kind="bar", figsize=(10,6)
)
ax.set_title("Mattel – Assets, Liabilities, and Equity")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("USD millions")
plt.xticks(rotation=0)
plt.show()


# In[42]:


cols = ["Cash", "Inventory", "PropertyPlantEquipment"]

ax = mattel_results[cols].div(1e6).plot(
    kind="bar", figsize=(10,6)
)
ax.set_title("Mattel – Cash, Inventory, PPE")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("USD millions")
plt.xticks(rotation=0)
plt.show()


# In[43]:


cols = ["EPS_Basic", "EPS_Diluted"]

ax = mattel_results[cols].plot(
    kind="bar", figsize=(8,5)
)
ax.set_title("Mattel – EPS Basic vs Diluted")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("EPS (USD)")
plt.xticks(rotation=0)
plt.show()


# In[45]:


import math
import pandas as pd
from bs4 import BeautifulSoup

# ---------- helper to clean numbers ----------
def clean_num(text):
    if text is None:
        return math.nan
    s = str(text).strip().replace(",", "").replace("$", "").replace("\u2212", "-")
    if s in ["", "—", "-", "na", "n/a", "NA"]:
        return math.nan
    if s[0] == "(" and s[-1] == ")":
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return math.nan

# ---------- function that reads ONE 10-K iXBRL and extracts all metrics ----------
def extract_metrics(filename):
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    facts = []
    for fact in soup.find_all():
        if not fact.has_attr("contextRef"):
            continue
        txt = fact.text.strip() if fact.text else ""
        if txt == "":
            continue
        facts.append(
            {
                "qname": fact.name,
                "context": fact["contextRef"],
                "value_raw": txt,
            }
        )

    df = pd.DataFrame(facts)

    def get_first(tag_list, pattern=None):
        sub = df[df["qname"].isin(tag_list)].copy()
        if pattern:
            sub = sub[sub["context"].str.contains(pattern, regex=True)]
        if sub.empty:
            return math.nan
        sub["val"] = sub["value_raw"].map(clean_num)
        sub = sub.dropna(subset=["val"])
        if sub.empty:
            return math.nan
        return float(sub.loc[sub["val"].abs().idxmax(), "val"])

    # --- Income statement items ---
    revenue = get_first(
        ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues"]
    )
    cogs = get_first(["CostOfGoodsAndServicesSold", "CostOfSales"])
    sga = get_first(["SellingGeneralAndAdministrativeExpense"])
    net_income = get_first(["NetIncomeLoss"])

    if any(math.isnan(x) for x in [revenue, cogs, sga]):
        operating_income = math.nan
    else:
        operating_income = revenue - cogs - sga

    # --- Balance sheet items ---
    assets = get_first(["Assets"], pattern=r"^i_")
    cash = get_first(["CashAndCashEquivalentsAtCarryingValue"], pattern=r"^i_")
    inventory = get_first(["InventoryNet"], pattern=r"^i_")
    ppe = get_first(["PropertyPlantAndEquipmentNet"], pattern=r"^i_")
    liab_current = get_first(["LiabilitiesCurrent"], pattern=r"^i_")
    liab_noncurrent = get_first(
        ["OtherLiabilitiesNoncurrent", "LiabilitiesNoncurrent"], pattern=r"^i_"
    )
    total_liab = (
        (liab_current if not math.isnan(liab_current) else 0.0)
        + (liab_noncurrent if not math.isnan(liab_noncurrent) else 0.0)
    )
    if math.isnan(liab_current) and math.isnan(liab_noncurrent):
        total_liab = math.nan

    equity = get_first(
        [
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ],
        pattern=r"^i_",
    )

    eps_basic = get_first(["EarningsPerShareBasic"])
    eps_diluted = get_first(["EarningsPerShareDiluted"])

    cfo = get_first(
        [
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ]
    )
    cfi = get_first(
        [
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
        ]
    )
    cff = get_first(
        [
            "NetCashProvidedByUsedInFinancingActivities",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
        ]
    )
    net_change_cash = get_first(["CashAndCashEquivalentsPeriodIncreaseDecrease"])

    debt = get_first(
        [
            "LongTermDebtNoncurrent",
            "LongTermDebtCurrent",
            "LongTermDebtAndCapitalLeaseObligations",
            "DebtCurrent",
            "DebtNoncurrent",
            "DebtInstrumentCarryingAmount",
        ]
    )

    tax_expense = get_first(
        ["IncomeTaxExpenseBenefit", "IncomeTaxExpenseBenefitContinuingOperations"]
    )

    seg = df[df["qname"].isin(["RevenueFromContractWithCustomerExcludingAssessedTax"])].copy()
    seg["val"] = seg["value_raw"].map(clean_num)
    seg = seg.dropna(subset=["val"])

    seg_retail = seg[
        seg["context"].str.contains("RetailMember")
        & ~seg["context"].str.contains("GiftCardBreakageMember")
    ]["val"].sum()

    seg_commercial = seg[seg["context"].str.contains("CommercialProductAndServiceMember")][
        "val"
    ].sum()

    seg_international = seg[seg["context"].str.contains("InternationalFranchisingMember")][
        "val"
    ].sum()

    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": operating_income,
        "NetIncome": net_income,
        "TotalAssets": assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": equity,
        "Cash": cash,
        "Inventory": inventory,
        "PropertyPlantEquipment": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "NetChangeCash": net_change_cash,
        "Debt": debt,
        "TaxExpense": tax_expense,
        "SegRev_Retail": float(seg_retail) if not math.isnan(seg_retail) else math.nan,
        "SegRev_Commercial": float(seg_commercial) if not math.isnan(seg_commercial) else math.nan,
        "SegRev_International": float(seg_international)
        if not math.isnan(seg_international)
        else math.nan,
    }

# ---------- list of your files with the fiscal year label you want ----------
# ---------- list of your Disney files with the fiscal year label you want ----------
files = [
    (2021, "mattel-20211231_htm.xml"),
    (2022, "mattel-20221231_htm.xml"),
    (2023, "mattel-20231231_htm.xml"),
    (2024, "mattel-20241231_htm.xml"),
]

rows = []
for year, fname in files:
    print(f"Processing {year} - {fname} ...")
    metrics = extract_metrics(fname)
    metrics["Year"] = year
    rows.append(metrics)

results = pd.DataFrame(rows).set_index("Year")
results


# In[46]:


results.head()
results.index


# In[47]:


import matplotlib.pyplot as plt

# Make sure the index is integer years (it already is, but just to be safe)
results.index = results.index.astype(int)

# Plot revenue
ax = results["Revenue"].plot(kind="line", marker="o", figsize=(10,5))

# Force x-axis ticks to be exactly the years in the index
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("Mattel Revenue Over Time")
plt.xlabel("Year")
plt.ylabel("Revenue (USD)")
plt.grid(True)
plt.show()


# In[48]:


import matplotlib.pyplot as plt

# Ensure index is integer years
results.index = results.index.astype(int)

ax = results[["Revenue", "NetIncome"]].plot(
    kind="line", marker="o", figsize=(10,5)
)

# Force x-axis to show only actual years
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("Revenue & Net Income Over Time")
plt.xlabel("Year")
plt.ylabel("USD")
plt.grid(True)
plt.show()


# In[49]:


import matplotlib.pyplot as plt

# Ensure index is integer years
results.index = results.index.astype(int)

ax = results[["OperatingIncome", "NetIncome"]].plot(
    kind="line", marker="o", figsize=(10,5)
)

# Force x-axis to show only actual years
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("OperatingIncome & Net Income Over Time")
plt.xlabel("Year")
plt.ylabel("USD")
plt.grid(True)
plt.show()


# In[50]:


# ==========================================
# BUILD-A-BEAR ANALYSIS
# ==========================================


# In[51]:


get_ipython().system('pip install beautifulsoup4 lxml pandas')


# In[52]:


import math
import pandas as pd
from bs4 import BeautifulSoup

# ---------- helper to clean numbers ----------
def clean_num(text):
    if text is None:
        return math.nan
    s = str(text).strip().replace(",", "").replace("$", "").replace("\u2212", "-")
    if s in ["", "—", "-", "na", "n/a", "NA"]:
        return math.nan
    if s[0] == "(" and s[-1] == ")":
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return math.nan

# ---------- function that reads ONE 10-K iXBRL and extracts all metrics ----------
def extract_metrics(filename):
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    facts = []
    for fact in soup.find_all():
        # keep only real numeric facts that have a contextRef
        if not fact.has_attr("contextRef"):
            continue
        txt = fact.text.strip() if fact.text else ""
        if txt == "":
            continue
        facts.append(
            {
                "qname": fact.name,             # tag name, e.g. Assets
                "context": fact["contextRef"],  # context id
                "value_raw": txt,               # raw string number
            }
        )

    df = pd.DataFrame(facts)

    def get_first(tag_list, pattern=None):
        """Pick the largest (by absolute value) number among the given tags."""
        sub = df[df["qname"].isin(tag_list)].copy()
        if pattern:
            sub = sub[sub["context"].str.contains(pattern, regex=True)]
        if sub.empty:
            return math.nan
        sub["val"] = sub["value_raw"].map(clean_num)
        sub = sub.dropna(subset=["val"])
        if sub.empty:
            return math.nan
        return float(sub.loc[sub["val"].abs().idxmax(), "val"])

    # --- Income statement items ---
    revenue = get_first(
        ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues"]
    )
    cogs = get_first(["CostOfGoodsAndServicesSold", "CostOfSales"])
    sga = get_first(["SellingGeneralAndAdministrativeExpense"])
    net_income = get_first(["NetIncomeLoss"])

    # Approximate operating income = Revenue – COGS – SG&A
    if any(math.isnan(x) for x in [revenue, cogs, sga]):
        operating_income = math.nan
    else:
        operating_income = revenue - cogs - sga

    # --- Balance sheet items (instant contexts start with 'i_') ---
    assets = get_first(["Assets"], pattern=r"^i_")
    cash = get_first(["CashAndCashEquivalentsAtCarryingValue"], pattern=r"^i_")
    inventory = get_first(["InventoryNet"], pattern=r"^i_")
    ppe = get_first(["PropertyPlantAndEquipmentNet"], pattern=r"^i_")
    liab_current = get_first(["LiabilitiesCurrent"], pattern=r"^i_")
    liab_noncurrent = get_first(
        ["OtherLiabilitiesNoncurrent", "LiabilitiesNoncurrent"], pattern=r"^i_"
    )
    total_liab = (
        (liab_current if not math.isnan(liab_current) else 0.0)
        + (liab_noncurrent if not math.isnan(liab_noncurrent) else 0.0)
    )
    if math.isnan(liab_current) and math.isnan(liab_noncurrent):
        total_liab = math.nan

    equity = get_first(
        [
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ],
        pattern=r"^i_",
    )

    # --- EPS ---
    eps_basic = get_first(["EarningsPerShareBasic"])
    eps_diluted = get_first(["EarningsPerShareDiluted"])

    # --- Cash flow statement (key lines) ---
    cfo = get_first(
        [
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ]
    )
    cfi = get_first(
        [
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
        ]
    )
    cff = get_first(
        [
            "NetCashProvidedByUsedInFinancingActivities",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
        ]
    )
    net_change_cash = get_first(["CashAndCashEquivalentsPeriodIncreaseDecrease"])

    # --- Debt (best available tag) ---
    debt = get_first(
        [
            "LongTermDebtNoncurrent",
            "LongTermDebtCurrent",
            "LongTermDebtAndCapitalLeaseObligations",
            "DebtCurrent",
            "DebtNoncurrent",
            "DebtInstrumentCarryingAmount",
        ]
    )

    # --- Tax expense ---
    tax_expense = get_first(
        ["IncomeTaxExpenseBenefit", "IncomeTaxExpenseBenefitContinuingOperations"]
    )

    # --- Segmented revenue: Retail / Commercial / International ---
    seg = df[df["qname"].isin(["RevenueFromContractWithCustomerExcludingAssessedTax"])].copy()
    seg["val"] = seg["value_raw"].map(clean_num)
    seg = seg.dropna(subset=["val"])

    seg_retail = seg[
        seg["context"].str.contains("RetailMember")
        & ~seg["context"].str.contains("GiftCardBreakageMember")
    ]["val"].sum()

    seg_commercial = seg[seg["context"].str.contains("CommercialProductAndServiceMember")][
        "val"
    ].sum()

    seg_international = seg[seg["context"].str.contains("InternationalFranchisingMember")][
        "val"
    ].sum()

    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": operating_income,
        "NetIncome": net_income,
        "TotalAssets": assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": equity,
        "Cash": cash,
        "Inventory": inventory,
        "PropertyPlantEquipment": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "NetChangeCash": net_change_cash,
        "Debt": debt,
        "TaxExpense": tax_expense,
        "SegRev_Retail": float(seg_retail) if not math.isnan(seg_retail) else math.nan,
        "SegRev_Commercial": float(seg_commercial) if not math.isnan(seg_commercial) else math.nan,
        "SegRev_International": float(seg_international)
        if not math.isnan(seg_international)
        else math.nan,
    }

# ---------- list of your files with the fiscal year label you want ----------
files = [
    (2020, "buildabear20210201_10k_htm.xml"),   # FY ending 2021-01-30
    (2021, "buildabear20220129_10k_htm.xml"),   # FY ending 2022-01-29
    (2022, "buildabear20231214_10k_htm.xml"),   # FY ending 2023-01-28
    (2023, "buildabear20240123_10k_htm.xml"),   # FY ending 2024-02-03
]

rows = []
for year, fname in files:
    print(f"Processing {year} - {fname} ...")
    metrics = extract_metrics(fname)
    metrics["Year"] = year
    rows.append(metrics)

results = pd.DataFrame(rows).set_index("Year")
results


# In[53]:


import matplotlib.pyplot as plt


# In[54]:


results[["SegRev_Retail", "SegRev_Commercial", "SegRev_International"]].plot(
    kind="bar", figsize=(12,6)
)
plt.title("Segment Revenues by Year")
plt.xlabel("Year")
plt.ylabel("USD")
plt.xticks(rotation=0)
plt.show()


# In[55]:


results["NetIncome"].plot(kind="bar", figsize=(8,5))
plt.title("Net Income by Year")
plt.xlabel("Year")
plt.ylabel("Net Income (USD)")
plt.xticks(rotation=0)
plt.show()


# In[56]:


plt.figure(figsize=(12,6))
plt.imshow(results, cmap="viridis", aspect="auto")
plt.colorbar()
plt.xticks(range(len(results.columns)), results.columns, rotation=90)
plt.yticks(range(len(results.index)), results.index)
plt.title("Financial Metrics Heatmap")
plt.show()


# In[57]:


get_ipython().system('pip install beautifulsoup4 html5lib')


# In[58]:


import math
import pandas as pd
from bs4 import BeautifulSoup

# ---------- helper to clean numbers ----------
def clean_num(text):
    if text is None:
        return math.nan
    s = str(text).strip().replace(",", "").replace("$", "").replace("\u2212", "-")
    if s in ["", "—", "-", "na", "n/a", "NA"]:
        return math.nan
    if s[0] == "(" and s[-1] == ")":
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return math.nan

# ---------- function that reads ONE 10-K iXBRL and extracts all metrics ----------
def extract_metrics(filename):
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    facts = []
    for fact in soup.find_all():
        if not fact.has_attr("contextRef"):
            continue
        txt = fact.text.strip() if fact.text else ""
        if txt == "":
            continue
        facts.append(
            {
                "qname": fact.name,
                "context": fact["contextRef"],
                "value_raw": txt,
            }
        )

    df = pd.DataFrame(facts)

    def get_first(tag_list, pattern=None):
        sub = df[df["qname"].isin(tag_list)].copy()
        if pattern:
            sub = sub[sub["context"].str.contains(pattern, regex=True)]
        if sub.empty:
            return math.nan
        sub["val"] = sub["value_raw"].map(clean_num)
        sub = sub.dropna(subset=["val"])
        if sub.empty:
            return math.nan
        return float(sub.loc[sub["val"].abs().idxmax(), "val"])

    # --- Income statement items ---
    revenue = get_first(
        ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues"]
    )
    cogs = get_first(["CostOfGoodsAndServicesSold", "CostOfSales"])
    sga = get_first(["SellingGeneralAndAdministrativeExpense"])
    net_income = get_first(["NetIncomeLoss"])

    if any(math.isnan(x) for x in [revenue, cogs, sga]):
        operating_income = math.nan
    else:
        operating_income = revenue - cogs - sga

    # --- Balance sheet items ---
    assets = get_first(["Assets"], pattern=r"^i_")
    cash = get_first(["CashAndCashEquivalentsAtCarryingValue"], pattern=r"^i_")
    inventory = get_first(["InventoryNet"], pattern=r"^i_")
    ppe = get_first(["PropertyPlantAndEquipmentNet"], pattern=r"^i_")
    liab_current = get_first(["LiabilitiesCurrent"], pattern=r"^i_")
    liab_noncurrent = get_first(
        ["OtherLiabilitiesNoncurrent", "LiabilitiesNoncurrent"], pattern=r"^i_"
    )
    total_liab = (
        (liab_current if not math.isnan(liab_current) else 0.0)
        + (liab_noncurrent if not math.isnan(liab_noncurrent) else 0.0)
    )
    if math.isnan(liab_current) and math.isnan(liab_noncurrent):
        total_liab = math.nan

    equity = get_first(
        [
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ],
        pattern=r"^i_",
    )

    eps_basic = get_first(["EarningsPerShareBasic"])
    eps_diluted = get_first(["EarningsPerShareDiluted"])

    cfo = get_first(
        [
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ]
    )
    cfi = get_first(
        [
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
        ]
    )
    cff = get_first(
        [
            "NetCashProvidedByUsedInFinancingActivities",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
        ]
    )
    net_change_cash = get_first(["CashAndCashEquivalentsPeriodIncreaseDecrease"])

    debt = get_first(
        [
            "LongTermDebtNoncurrent",
            "LongTermDebtCurrent",
            "LongTermDebtAndCapitalLeaseObligations",
            "DebtCurrent",
            "DebtNoncurrent",
            "DebtInstrumentCarryingAmount",
        ]
    )

    tax_expense = get_first(
        ["IncomeTaxExpenseBenefit", "IncomeTaxExpenseBenefitContinuingOperations"]
    )

    seg = df[df["qname"].isin(["RevenueFromContractWithCustomerExcludingAssessedTax"])].copy()
    seg["val"] = seg["value_raw"].map(clean_num)
    seg = seg.dropna(subset=["val"])

    seg_retail = seg[
        seg["context"].str.contains("RetailMember")
        & ~seg["context"].str.contains("GiftCardBreakageMember")
    ]["val"].sum()

    seg_commercial = seg[seg["context"].str.contains("CommercialProductAndServiceMember")][
        "val"
    ].sum()

    seg_international = seg[seg["context"].str.contains("InternationalFranchisingMember")][
        "val"
    ].sum()

    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": operating_income,
        "NetIncome": net_income,
        "TotalAssets": assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": equity,
        "Cash": cash,
        "Inventory": inventory,
        "PropertyPlantEquipment": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "NetChangeCash": net_change_cash,
        "Debt": debt,
        "TaxExpense": tax_expense,
        "SegRev_Retail": float(seg_retail) if not math.isnan(seg_retail) else math.nan,
        "SegRev_Commercial": float(seg_commercial) if not math.isnan(seg_commercial) else math.nan,
        "SegRev_International": float(seg_international)
        if not math.isnan(seg_international)
        else math.nan,
    }

# ---------- list of your files with the fiscal year label you want ----------
files = [
    (2020, "buildabear20210201_10k_htm.xml"),
    (2021, "buildabear20220129_10k_htm.xml"),
    (2022, "buildabear20231214_10k_htm.xml"),
    (2023, "buildabear20240123_10k_htm.xml"),
]

rows = []
for year, fname in files:
    print(f"Processing {year} - {fname} ...")
    metrics = extract_metrics(fname)
    metrics["Year"] = year
    rows.append(metrics)

results = pd.DataFrame(rows).set_index("Year")


# In[59]:


results.head()
results.index


# In[60]:


import matplotlib.pyplot as plt

# Make sure the index is integer years (it already is, but just to be safe)
results.index = results.index.astype(int)

# Plot revenue
ax = results["Revenue"].plot(kind="line", marker="o", figsize=(10,5))

# Force x-axis ticks to be exactly the years in the index
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("Build-A-Bear Revenue Over Time")
plt.xlabel("Year")
plt.ylabel("Revenue (USD)")
plt.grid(True)
plt.show()


# In[61]:


import matplotlib.pyplot as plt

# Ensure index is integer years
results.index = results.index.astype(int)

ax = results[["Revenue", "NetIncome"]].plot(
    kind="line", marker="o", figsize=(10,5)
)

# Force x-axis to show only actual years
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("Revenue & Net Income Over Time")
plt.xlabel("Year")
plt.ylabel("USD")
plt.grid(True)
plt.show()


# In[62]:


# ==========================================
# FUNKO ANALYSIS
# ==========================================


# In[63]:


import os
os.listdir()


# In[64]:


files = [
    (2021, "funko-20211231_htm.xml"),
    (2022, "funko-20221231_htm.xml"),
    (2023, "funko-20231231_htm.xml"),
    (2024, "funko-20241231_htm.xml"),
]


# In[65]:


import math
import pandas as pd
from bs4 import BeautifulSoup

# ---------- helper to clean numbers ----------
def clean_num(text):
    if text is None:
        return math.nan
    s = str(text).strip().replace(",", "").replace("$", "").replace("\u2212", "-")
    if s in ["", "—", "-", "na", "n/a", "NA"]:
        return math.nan
    if s[0] == "(" and s[-1] == ")":
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return math.nan

# ---------- MAIN EXTRACT FUNCTION ----------
def extract_metrics(filename):
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    # collect all facts with contextRef
    facts = []
    for fact in soup.find_all():
        if not fact.has_attr("contextRef"):
            continue
        txt = fact.text.strip() if fact.text else ""
        if txt == "":
            continue
        facts.append({
            "qname": fact.name,
            "context": fact["contextRef"],
            "value_raw": txt,
        })

    df = pd.DataFrame(facts)

    def get_first(tag_list, pattern=None):
        if isinstance(tag_list, str):
            tag_list = [tag_list]
        sub = df[df["qname"].isin(tag_list)].copy()
        if pattern:
            sub = sub[sub["context"].str.contains(pattern, regex=True)]
        if sub.empty:
            return math.nan
        sub["val"] = sub["value_raw"].map(clean_num)
        sub = sub.dropna(subset=["val"])
        if sub.empty:
            return math.nan
        return float(sub.loc[sub["val"].abs().idxmax(), "val"])

    # ---------------- INCOME STATEMENT ----------------
    revenue = get_first(["Revenues", "SalesRevenueNet",
                         "RevenueFromContractWithCustomerExcludingAssessedTax"])
    cogs = get_first(["CostOfGoodsSold", "CostOfGoodsAndServicesSold"])
    sga = get_first(["SellingGeneralAndAdministrativeExpense"])
    net_income = get_first(["NetIncomeLoss"])

    op_income_direct = get_first(["OperatingIncomeLoss"])
    if not math.isnan(op_income_direct):
        operating_income = op_income_direct
    elif any(math.isnan(x) for x in [revenue, cogs, sga]):
        operating_income = math.nan
    else:
        operating_income = revenue - cogs - sga

    # ---------------- BALANCE SHEET ----------------
    instant = r"^[iI]"  # match Disney + BABW + Funko

    assets = get_first(["Assets"], pattern=instant)
    liab_current = get_first(["LiabilitiesCurrent"], pattern=instant)
    liab_noncurrent = get_first(["LiabilitiesNoncurrent"], pattern=instant)

    if math.isnan(liab_current) and math.isnan(liab_noncurrent):
        total_liab = math.nan
    else:
        total_liab = (0 if math.isnan(liab_current) else liab_current) + \
                     (0 if math.isnan(liab_noncurrent) else liab_noncurrent)

    equity = get_first(["StockholdersEquity",
                        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
                       pattern=instant)
    cash = get_first(["CashAndCashEquivalentsAtCarryingValue"], pattern=instant)
    inventory = get_first(["InventoryNet", "InventoriesNet"], pattern=instant)
    ppe = get_first(["PropertyPlantAndEquipmentNet"], pattern=instant)

    # ---------------- CASH FLOW ----------------
    cfo = get_first(["NetCashProvidedByUsedInOperatingActivities"])
    cfi = get_first(["NetCashProvidedByUsedInInvestingActivities"])
    cff = get_first(["NetCashProvidedByUsedInFinancingActivities"])

    # ---------------- EPS ----------------
    eps_basic = get_first(["EarningsPerShareBasic"])
    eps_diluted = get_first(["EarningsPerShareDiluted"])

    # ---------------- DEBT ----------------
    debt = get_first(["DebtInstrumentCarryingAmount",
                      "LongTermDebtNoncurrent",
                      "DebtNoncurrent",
                      "DebtCurrent"], pattern=instant)

    # ---------------- TAX ----------------
    tax_expense = get_first(["IncomeTaxExpenseBenefit"])

    # ---------------- RETURN DICT ----------------
    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": operating_income,
        "NetIncome": net_income,
        "TotalAssets": assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": equity,
        "Cash": cash,
        "Inventory": inventory,
        "PropertyPlantEquipment": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "Debt": debt,
        "TaxExpense": tax_expense,
    }


# In[66]:


rows = []

for year, fname in files:
    print(f"Processing {year} – {fname} ...")
    metrics = extract_metrics(fname)
    metrics["Year"] = year
    rows.append(metrics)

funko_results = pd.DataFrame(rows).set_index("Year")
funko_results


# In[67]:


import matplotlib.pyplot as plt


# In[68]:


ax = funko_results[["CFO", "CFI", "CFF"]].div(1e6).plot(
    kind="bar", figsize=(10,6)
)
ax.set_title("Funko – Cash Flows (CFO, CFI, CFF)")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("USD (millions)")
plt.xticks(rotation=0)
plt.show()


# In[69]:


ax = funko_results[["TotalAssets", "TotalLiabilities", "TotalEquity"]]\
        .dropna().div(1e6).plot(
            kind="bar", figsize=(10,6)
        )
ax.set_title("Funko – Assets, Liabilities, Equity")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("USD (millions)")
plt.xticks(rotation=0)
plt.show()


# In[70]:


ax = funko_results[["EPS_Basic", "EPS_Diluted"]].plot(
    kind="bar", figsize=(8,5)
)
ax.set_title("Funko – EPS Basic vs Diluted")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("Earnings Per Share (USD)")
plt.xticks(rotation=0)
plt.show()


# In[71]:


import math
import pandas as pd
from bs4 import BeautifulSoup

# ---------- helper to clean numbers ----------
def clean_num(text):
    if text is None:
        return math.nan
    s = str(text).strip().replace(",", "").replace("$", "").replace("\u2212", "-")
    if s in ["", "—", "-", "na", "n/a", "NA"]:
        return math.nan
    if s[0] == "(" and s[-1] == ")":
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return math.nan

# ---------- function that reads ONE 10-K iXBRL and extracts all metrics ----------
def extract_metrics(filename):
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    facts = []
    for fact in soup.find_all():
        if not fact.has_attr("contextRef"):
            continue
        txt = fact.text.strip() if fact.text else ""
        if txt == "":
            continue
        facts.append(
            {
                "qname": fact.name,
                "context": fact["contextRef"],
                "value_raw": txt,
            }
        )

    df = pd.DataFrame(facts)

    def get_first(tag_list, pattern=None):
        sub = df[df["qname"].isin(tag_list)].copy()
        if pattern:
            sub = sub[sub["context"].str.contains(pattern, regex=True)]
        if sub.empty:
            return math.nan
        sub["val"] = sub["value_raw"].map(clean_num)
        sub = sub.dropna(subset=["val"])
        if sub.empty:
            return math.nan
        return float(sub.loc[sub["val"].abs().idxmax(), "val"])

    # --- Income statement items ---
    revenue = get_first(
        ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues"]
    )
    cogs = get_first(["CostOfGoodsAndServicesSold", "CostOfSales"])
    sga = get_first(["SellingGeneralAndAdministrativeExpense"])
    net_income = get_first(["NetIncomeLoss"])

    if any(math.isnan(x) for x in [revenue, cogs, sga]):
        operating_income = math.nan
    else:
        operating_income = revenue - cogs - sga

    # --- Balance sheet items ---
    assets = get_first(["Assets"], pattern=r"^i_")
    cash = get_first(["CashAndCashEquivalentsAtCarryingValue"], pattern=r"^i_")
    inventory = get_first(["InventoryNet"], pattern=r"^i_")
    ppe = get_first(["PropertyPlantAndEquipmentNet"], pattern=r"^i_")
    liab_current = get_first(["LiabilitiesCurrent"], pattern=r"^i_")
    liab_noncurrent = get_first(
        ["OtherLiabilitiesNoncurrent", "LiabilitiesNoncurrent"], pattern=r"^i_"
    )
    total_liab = (
        (liab_current if not math.isnan(liab_current) else 0.0)
        + (liab_noncurrent if not math.isnan(liab_noncurrent) else 0.0)
    )
    if math.isnan(liab_current) and math.isnan(liab_noncurrent):
        total_liab = math.nan

    equity = get_first(
        [
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ],
        pattern=r"^i_",
    )

    eps_basic = get_first(["EarningsPerShareBasic"])
    eps_diluted = get_first(["EarningsPerShareDiluted"])

    cfo = get_first(
        [
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ]
    )
    cfi = get_first(
        [
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
        ]
    )
    cff = get_first(
        [
            "NetCashProvidedByUsedInFinancingActivities",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
        ]
    )
    net_change_cash = get_first(["CashAndCashEquivalentsPeriodIncreaseDecrease"])

    debt = get_first(
        [
            "LongTermDebtNoncurrent",
            "LongTermDebtCurrent",
            "LongTermDebtAndCapitalLeaseObligations",
            "DebtCurrent",
            "DebtNoncurrent",
            "DebtInstrumentCarryingAmount",
        ]
    )

    tax_expense = get_first(
        ["IncomeTaxExpenseBenefit", "IncomeTaxExpenseBenefitContinuingOperations"]
    )

    seg = df[df["qname"].isin(["RevenueFromContractWithCustomerExcludingAssessedTax"])].copy()
    seg["val"] = seg["value_raw"].map(clean_num)
    seg = seg.dropna(subset=["val"])

    seg_retail = seg[
        seg["context"].str.contains("RetailMember")
        & ~seg["context"].str.contains("GiftCardBreakageMember")
    ]["val"].sum()

    seg_commercial = seg[seg["context"].str.contains("CommercialProductAndServiceMember")][
        "val"
    ].sum()

    seg_international = seg[seg["context"].str.contains("InternationalFranchisingMember")][
        "val"
    ].sum()

    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": operating_income,
        "NetIncome": net_income,
        "TotalAssets": assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": equity,
        "Cash": cash,
        "Inventory": inventory,
        "PropertyPlantEquipment": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "NetChangeCash": net_change_cash,
        "Debt": debt,
        "TaxExpense": tax_expense,
        "SegRev_Retail": float(seg_retail) if not math.isnan(seg_retail) else math.nan,
        "SegRev_Commercial": float(seg_commercial) if not math.isnan(seg_commercial) else math.nan,
        "SegRev_International": float(seg_international)
        if not math.isnan(seg_international)
        else math.nan,
    }

# ---------- list of your files with the fiscal year label you want ----------
# ---------- list of your Disney files with the fiscal year label you want ----------
# ---------- list of your Funko files with the fiscal year label you want ----------
files = [
    (2021, "funko-20211231_htm.xml"),
    (2022, "funko-20221231_htm.xml"),
    (2023, "funko-20231231_htm.xml"),
    (2024, "funko-20241231_htm.xml"),
]

rows = []
for year, fname in files:
    print(f"Processing {year} - {fname} ...")
    metrics = extract_metrics(fname)
    metrics["Year"] = year
    rows.append(metrics)

results = pd.DataFrame(rows).set_index("Year")
results


# In[72]:


results.head()
results.index


# In[73]:


import matplotlib.pyplot as plt

# Make sure the index is integer years (it already is, but just to be safe)
results.index = results.index.astype(int)

# Plot revenue
ax = results["Revenue"].plot(kind="line", marker="o", figsize=(10,5))

# Force x-axis ticks to be exactly the years in the index
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("Funko Revenue Over Time")
plt.xlabel("Year")
plt.ylabel("Revenue (USD)")
plt.grid(True)
plt.show()


# In[74]:


import matplotlib.pyplot as plt

# Ensure index is integer years
results.index = results.index.astype(int)

ax = results[["Revenue", "NetIncome"]].plot(
    kind="line", marker="o", figsize=(10,5)
)

# Force x-axis to show only actual years
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("Revenue & Net Income Over Time")
plt.xlabel("Year")
plt.ylabel("USD")
plt.grid(True)
plt.show()


# In[75]:


import matplotlib.pyplot as plt

# Ensure index is integer years
results.index = results.index.astype(int)

ax = results[["OperatingIncome", "NetIncome"]].plot(
    kind="line", marker="o", figsize=(10,5)
)

# Force x-axis to show only actual years
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("OperatingIncome & Net Income Over Time")
plt.xlabel("Year")
plt.ylabel("USD")
plt.grid(True)
plt.show()


# In[76]:


# ==========================================
# JAKKS PACIFIC ANALYSIS
# ==========================================


# In[77]:


def extract_metrics(filename):
    ...


# In[78]:


files = [
    (2021, "jakkspacif20211231_10k_htm.xml"),
    (2022, "jakkspacif20221231_10k_htm.xml"),
    (2023, "jakkspacif20231231_10k_htm.xml"),
    (2024, "jakkspacific24_htm.xml"),   # corrected spelling
]


# In[79]:


import math
import pandas as pd
from bs4 import BeautifulSoup

# ---------- helper ----------
def clean_num(text):
    if text is None:
        return math.nan
    s = str(text).strip().replace(",", "").replace("$", "").replace("\u2212", "-")
    if s in ["", "—", "-", "na", "n/a", "NA"]:
        return math.nan
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return math.nan


def extract_metrics(filename):
    """Return a dict of key financial metrics for one iXBRL XML file.
       This function NEVER returns None, only a dict with numbers/NaNs.
    """
    print("Reading", filename)
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    facts = []
    for fact in soup.find_all():
        if not fact.has_attr("contextRef"):
            continue
        txt = fact.text.strip() if fact.text else ""
        if txt == "":
            continue
        facts.append({
            "qname": fact.name,
            "context": fact["contextRef"],
            "value_raw": txt,
        })

    df = pd.DataFrame(facts)

    def get_first(tag_list, pattern=None):
        if isinstance(tag_list, str):
            tag_list = [tag_list]
        sub = df[df["qname"].isin(tag_list)].copy()
        if pattern:
            sub = sub[sub["context"].str.contains(pattern, regex=True)]
        if sub.empty:
            return math.nan
        sub["val"] = sub["value_raw"].map(clean_num)
        sub = sub.dropna(subset=["val"])
        if sub.empty:
            return math.nan
        return float(sub.loc[sub["val"].abs().idxmax(), "val"])

    # ============ INCOME STATEMENT ============
    revenue = get_first(["Revenues", "SalesRevenueNet",
                         "RevenueFromContractWithCustomerExcludingAssessedTax"])
    cogs = get_first(["CostOfGoodsSold", "CostOfGoodsAndServicesSold"])
    sga = get_first(["SellingGeneralAndAdministrativeExpense"])
    net_income = get_first(["NetIncomeLoss"])

    op_income_direct = get_first(["OperatingIncomeLoss"])
    if not math.isnan(op_income_direct):
        operating_income = op_income_direct
    elif any(math.isnan(x) for x in [revenue, cogs, sga]):
        operating_income = math.nan
    else:
        operating_income = revenue - cogs - sga

    # ============ BALANCE SHEET ============
    instant = r"^[iI]"   # contextRef for instant balances in most of your filings

    assets = get_first(["Assets"], pattern=instant)
    liab_current = get_first(["LiabilitiesCurrent"], pattern=instant)
    liab_noncurrent = get_first(["LiabilitiesNoncurrent"], pattern=instant)

    if math.isnan(liab_current) and math.isnan(liab_noncurrent):
        total_liab = math.nan
    else:
        total_liab = (0 if math.isnan(liab_current) else liab_current) + \
                     (0 if math.isnan(liab_noncurrent) else liab_noncurrent)

    equity = get_first(["StockholdersEquity",
                        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
                       pattern=instant)

    cash = get_first(["CashAndCashEquivalentsAtCarryingValue"], pattern=instant)
    inventory = get_first(["InventoryNet", "InventoriesNet"], pattern=instant)
    ppe = get_first(["PropertyPlantAndEquipmentNet"], pattern=instant)

    # ============ CASH FLOWS ============
    cfo = get_first(["NetCashProvidedByUsedInOperatingActivities",
                     "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"])
    cfi = get_first(["NetCashProvidedByUsedInInvestingActivities",
                     "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations"])
    cff = get_first(["NetCashProvidedByUsedInFinancingActivities",
                     "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations"])

    # ============ EPS ============
    eps_basic = get_first(["EarningsPerShareBasic"])
    eps_diluted = get_first(["EarningsPerShareDiluted"])

    # ============ DEBT ============
    debt = get_first(["DebtInstrumentCarryingAmount",
                      "LongTermDebtNoncurrent",
                      "DebtNoncurrent",
                      "DebtCurrent"], pattern=instant)

    # ============ TAX ============
    tax_expense = get_first(["IncomeTaxExpenseBenefit"])

    # FINAL guaranteed dict (never None)
    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": operating_income,
        "NetIncome": net_income,
        "TotalAssets": assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": equity,
        "Cash": cash,
        "Inventory": inventory,
        "PropertyPlantEquipment": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "Debt": debt,
        "TaxExpense": tax_expense,
    }


# In[80]:


import math
import pandas as pd
from bs4 import BeautifulSoup

def clean_num(text):
    if text is None:
        return math.nan
    s = str(text).strip().replace(",", "").replace("$", "").replace("\u2212", "-")
    if s in ["", "—", "-", "na", "n/a", "NA"]:
        return math.nan
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return math.nan


def extract_metrics(filename):
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    facts = []
    for fact in soup.find_all():
        if not fact.has_attr("contextRef"):
            continue
        txt = fact.text.strip() if fact.text else ""
        if not txt:
            continue
        facts.append(
            {
                "qname": fact.name,
                "context": fact["contextRef"],
                "value_raw": txt,
            }
        )

    df = pd.DataFrame(facts)

    def get_first(tag_list, pattern=None):
        if isinstance(tag_list, str):
            tag_list = [tag_list]
        sub = df[df["qname"].isin(tag_list)].copy()
        if pattern:
            sub = sub[sub["context"].str.contains(pattern, regex=True)]
        if sub.empty:
            return math.nan
        sub["val"] = sub["value_raw"].map(clean_num)
        sub = sub.dropna(subset=["val"])
        if sub.empty:
            return math.nan
        return float(sub.loc[sub["val"].abs().idxmax(), "val"])

    instant = r"^[iI]"  # instant contexts for most filings

    # ============ INCOME STATEMENT ============
    revenue = get_first(
        ["Revenues", "SalesRevenueNet", "RevenueFromContractWithCustomerExcludingAssessedTax"]
    )
    cogs = get_first(["CostOfGoodsSold", "CostOfGoodsAndServicesSold"])
    sga = get_first(["SellingGeneralAndAdministrativeExpense"])
    net_income = get_first(["NetIncomeLoss", "ProfitLoss"])

    op_direct = get_first(["OperatingIncomeLoss"])
    if not math.isnan(op_direct):
        operating_income = op_direct
    elif any(math.isnan(x) for x in [revenue, cogs, sga]):
        operating_income = math.nan
    else:
        operating_income = revenue - cogs - sga

    # ============ BALANCE SHEET ============
    # Assets: try total; then current+noncurrent; then no pattern fallback
    assets = get_first(["Assets"], pattern=instant)
    if math.isnan(assets):
        ac = get_first(["AssetsCurrent"], pattern=instant)
        an = get_first(["AssetsNoncurrent"], pattern=instant)
        if not math.isnan(ac) or not math.isnan(an):
            assets = (0 if math.isnan(ac) else ac) + (0 if math.isnan(an) else an)
    if math.isnan(assets):
        assets = get_first(["Assets"])  # no pattern fallback

    # Liabilities: total if available, otherwise current+noncurrent
    liab_total = get_first(["Liabilities"], pattern=instant)
    liab_current = get_first(["LiabilitiesCurrent"], pattern=instant)
    liab_noncurrent = get_first(["LiabilitiesNoncurrent"], pattern=instant)

    if not math.isnan(liab_total):
        total_liab = liab_total
    elif math.isnan(liab_current) and math.isnan(liab_noncurrent):
        total_liab = math.nan
    else:
        total_liab = (0 if math.isnan(liab_current) else liab_current) + (
            0 if math.isnan(liab_noncurrent) else liab_noncurrent
        )

    if math.isnan(total_liab):
        total_liab = get_first(["Liabilities"])  # final fallback

    # Equity
    equity = get_first(
        [
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ],
        pattern=instant,
    )
    if math.isnan(equity):
        equity = get_first(
            [
                "StockholdersEquity",
                "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            ]
        )

    # Cash
    cash = get_first(
        ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsAndShortTermInvestments"],
        pattern=instant,
    )
    if math.isnan(cash):
        cash = get_first(
            ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsAndShortTermInvestments"]
        )

    # Inventory
    inventory = get_first(["InventoryNet", "InventoriesNet"], pattern=instant)
    if math.isnan(inventory):
        inventory = get_first(["InventoryNet", "InventoriesNet"])

    # PPE
    ppe = get_first(
        ["PropertyPlantAndEquipmentNet", "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetNet"],
        pattern=instant,
    )
    if math.isnan(ppe):
        ppe = get_first(
            ["PropertyPlantAndEquipmentNet", "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetNet"]
        )

    # ============ CASH FLOWS ============
    cfo = get_first(
        [
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ]
    )
    cfi = get_first(
        [
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
        ]
    )
    cff = get_first(
        [
            "NetCashProvidedByUsedInFinancingActivities",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
        ]
    )

    # ============ EPS ============
    eps_basic = get_first(["EarningsPerShareBasic"])
    eps_diluted = get_first(["EarningsPerShareDiluted"])

    # ============ DEBT ============
    debt = get_first(
        ["DebtInstrumentCarryingAmount", "LongTermDebtNoncurrent", "DebtNoncurrent", "DebtCurrent"],
        pattern=instant,
    )
    if math.isnan(debt):
        debt = get_first(["DebtInstrumentCarryingAmount", "LongTermDebtNoncurrent", "DebtNoncurrent", "DebtCurrent"])

    # ============ TAX ============
    tax_expense = get_first(["IncomeTaxExpenseBenefit"])

    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": operating_income,
        "NetIncome": net_income,
        "TotalAssets": assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": equity,
        "Cash": cash,
        "Inventory": inventory,
        "PropertyPlantEquipment": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "Debt": debt,
        "TaxExpense": tax_expense,
    }


# In[81]:


rows = []

for year, fname in files:
    print(f"Processing {year} – {fname} ...")
    metrics = extract_metrics(fname)
    metrics["Year"] = year
    rows.append(metrics)

jakks_results = pd.DataFrame(rows).set_index("Year")
jakks_results


# In[82]:


import matplotlib.pyplot as plt


# In[85]:


ax = jakks_results[["CFO", "CFI", "CFF"]].div(1e6).plot(
    kind="bar", figsize=(10,6)
)
ax.set_title("JAKKS Pacific – Cash Flows")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("USD (millions)")
plt.xticks(rotation=0)
plt.show()


# In[86]:


ax = jakks_results[["TotalAssets", "TotalLiabilities", "TotalEquity"]]\
        .dropna().div(1e6).plot(
            kind="bar", figsize=(10,6)
        )
ax.set_title("JAKKS Pacific – Assets, Liabilities, Equity")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("USD (millions)")
plt.xticks(rotation=0)
plt.show()


# In[87]:


ax = jakks_results[["EPS_Basic", "EPS_Diluted"]].plot(
    kind="bar", figsize=(8,5)
)
ax.set_title("JAKKS Pacific – EPS Basic vs Diluted")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("EPS (USD)")
plt.xticks(rotation=0)
plt.show()


# In[88]:


import math
import pandas as pd
from bs4 import BeautifulSoup

# ---------- helper to clean numbers ----------
def clean_num(text):
    if text is None:
        return math.nan
    s = str(text).strip().replace(",", "").replace("$", "").replace("\u2212", "-")
    if s in ["", "—", "-", "na", "n/a", "NA"]:
        return math.nan
    if s[0] == "(" and s[-1] == ")":
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return math.nan

# ---------- function that reads ONE 10-K iXBRL and extracts all metrics ----------
def extract_metrics(filename):
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    facts = []
    for fact in soup.find_all():
        if not fact.has_attr("contextRef"):
            continue
        txt = fact.text.strip() if fact.text else ""
        if txt == "":
            continue
        facts.append(
            {
                "qname": fact.name,
                "context": fact["contextRef"],
                "value_raw": txt,
            }
        )

    df = pd.DataFrame(facts)

    def get_first(tag_list, pattern=None):
        sub = df[df["qname"].isin(tag_list)].copy()
        if pattern:
            sub = sub[sub["context"].str.contains(pattern, regex=True)]
        if sub.empty:
            return math.nan
        sub["val"] = sub["value_raw"].map(clean_num)
        sub = sub.dropna(subset=["val"])
        if sub.empty:
            return math.nan
        return float(sub.loc[sub["val"].abs().idxmax(), "val"])

    # --- Income statement items ---
    revenue = get_first(
        ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues"]
    )
    cogs = get_first(["CostOfGoodsAndServicesSold", "CostOfSales"])
    sga = get_first(["SellingGeneralAndAdministrativeExpense"])
    net_income = get_first(["NetIncomeLoss"])

    if any(math.isnan(x) for x in [revenue, cogs, sga]):
        operating_income = math.nan
    else:
        operating_income = revenue - cogs - sga

    # --- Balance sheet items ---
    assets = get_first(["Assets"], pattern=r"^i_")
    cash = get_first(["CashAndCashEquivalentsAtCarryingValue"], pattern=r"^i_")
    inventory = get_first(["InventoryNet"], pattern=r"^i_")
    ppe = get_first(["PropertyPlantAndEquipmentNet"], pattern=r"^i_")
    liab_current = get_first(["LiabilitiesCurrent"], pattern=r"^i_")
    liab_noncurrent = get_first(
        ["OtherLiabilitiesNoncurrent", "LiabilitiesNoncurrent"], pattern=r"^i_"
    )
    total_liab = (
        (liab_current if not math.isnan(liab_current) else 0.0)
        + (liab_noncurrent if not math.isnan(liab_noncurrent) else 0.0)
    )
    if math.isnan(liab_current) and math.isnan(liab_noncurrent):
        total_liab = math.nan

    equity = get_first(
        [
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ],
        pattern=r"^i_",
    )

    eps_basic = get_first(["EarningsPerShareBasic"])
    eps_diluted = get_first(["EarningsPerShareDiluted"])

    cfo = get_first(
        [
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ]
    )
    cfi = get_first(
        [
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
        ]
    )
    cff = get_first(
        [
            "NetCashProvidedByUsedInFinancingActivities",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
        ]
    )
    net_change_cash = get_first(["CashAndCashEquivalentsPeriodIncreaseDecrease"])

    debt = get_first(
        [
            "LongTermDebtNoncurrent",
            "LongTermDebtCurrent",
            "LongTermDebtAndCapitalLeaseObligations",
            "DebtCurrent",
            "DebtNoncurrent",
            "DebtInstrumentCarryingAmount",
        ]
    )

    tax_expense = get_first(
        ["IncomeTaxExpenseBenefit", "IncomeTaxExpenseBenefitContinuingOperations"]
    )

    seg = df[df["qname"].isin(["RevenueFromContractWithCustomerExcludingAssessedTax"])].copy()
    seg["val"] = seg["value_raw"].map(clean_num)
    seg = seg.dropna(subset=["val"])

    seg_retail = seg[
        seg["context"].str.contains("RetailMember")
        & ~seg["context"].str.contains("GiftCardBreakageMember")
    ]["val"].sum()

    seg_commercial = seg[seg["context"].str.contains("CommercialProductAndServiceMember")][
        "val"
    ].sum()

    seg_international = seg[seg["context"].str.contains("InternationalFranchisingMember")][
        "val"
    ].sum()

    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": operating_income,
        "NetIncome": net_income,
        "TotalAssets": assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": equity,
        "Cash": cash,
        "Inventory": inventory,
        "PropertyPlantEquipment": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "NetChangeCash": net_change_cash,
        "Debt": debt,
        "TaxExpense": tax_expense,
        "SegRev_Retail": float(seg_retail) if not math.isnan(seg_retail) else math.nan,
        "SegRev_Commercial": float(seg_commercial) if not math.isnan(seg_commercial) else math.nan,
        "SegRev_International": float(seg_international)
        if not math.isnan(seg_international)
        else math.nan,
    }

# ---------- list of your files with the fiscal year label you want ----------
# ---------- list of your Disney files with the fiscal year label you want ----------
files = [
    (2021, "jakkspacif20211231_10k_htm.xml"),
    (2022, "jakkspacif20221231_10k_htm.xml"),
    (2023, "jakkspacif20231231_10k_htm.xml"),
    (2024, "jakkspacific24_htm.xml"),
]

rows = []
for year, fname in files:
    print(f"Processing {year} - {fname} ...")
    metrics = extract_metrics(fname)
    metrics["Year"] = year
    rows.append(metrics)

results = pd.DataFrame(rows).set_index("Year")
results


# In[89]:


results.head()
results.index


# In[90]:


import matplotlib.pyplot as plt

# Make sure the index is integer years (it already is, but just to be safe)
results.index = results.index.astype(int)

# Plot revenue
ax = results["Revenue"].plot(kind="line", marker="o", figsize=(10,5))

# Force x-axis ticks to be exactly the years in the index
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("Jakks Pacific Revenue Over Time")
plt.xlabel("Year")
plt.ylabel("Revenue (USD)")
plt.grid(True)
plt.show()


# In[91]:


import matplotlib.pyplot as plt

# Ensure index is integer years
results.index = results.index.astype(int)

ax = results[["OperatingIncome", "NetIncome"]].plot(
    kind="line", marker="o", figsize=(10,5)
)

# Force x-axis to show only actual years
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("OperatingIncome & Net Income Over Time")
plt.xlabel("Year")
plt.ylabel("USD")
plt.grid(True)
plt.show()


# In[92]:


import matplotlib.pyplot as plt

# Ensure index is integer years
results.index = results.index.astype(int)

ax = results[["Revenue", "NetIncome"]].plot(
    kind="line", marker="o", figsize=(10,5)
)

# Force x-axis to show only actual years
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("Revenue & Net Income Over Time")
plt.xlabel("Year")
plt.ylabel("USD")
plt.grid(True)
plt.show()


# In[93]:


# ==========================================
# DISNEY ANALYSIS
# ==========================================


# In[94]:


get_ipython().system('pip install beautifulsoup4 lxml pandas')


# In[95]:


from bs4 import BeautifulSoup

fname = "disney-20221001_htm.xml"

with open(fname, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml-xml")

tags = sorted(set([tag.name for tag in soup.find_all()]))
print(len(tags))
tags[:100]


# In[96]:


contexts = set()
for tag in soup.find_all():
    if tag.has_attr("contextRef"):
        contexts.add(tag["contextRef"])

sorted(contexts)[:50]


# In[97]:


from bs4 import BeautifulSoup

fname = "disney-20221001_htm.xml"

with open(fname, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml-xml")

tags = sorted(set([tag.name for tag in soup.find_all()]))
print(len(tags))
tags[:150]


# In[98]:


contexts = sorted(list({tag["contextRef"] for tag in soup.find_all() if tag.has_attr("contextRef")}))
contexts[:50]


# In[99]:


def extract_metrics(filename):
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")
    ...


# In[100]:


def extract_metrics(filename):
    import math
    from bs4 import BeautifulSoup
    import pandas as pd

    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    # -------- collect facts (same as before) --------
    facts = []
    for fact in soup.find_all():
        if not fact.has_attr("contextRef"):
            continue
        txt = fact.text.strip() if fact.text else ""
        if txt == "":
            continue
        facts.append(
            {
                "qname": fact.name,             # e.g. Assets, RevenueFromContract...
                "context": fact["contextRef"],  # context id
                "value_raw": txt,
            }
        )

    df = pd.DataFrame(facts)

    def get_first(tag_list, pattern=None):
        """Pick the largest (by absolute value) number among the given tags."""
        if isinstance(tag_list, str):
            tag_list = [tag_list]

        sub = df[df["qname"].isin(tag_list)].copy()
        if pattern:
            sub = sub[sub["context"].str.contains(pattern, regex=True)]

        if sub.empty:
            return math.nan
        sub["val"] = sub["value_raw"].map(clean_num)
        sub = sub.dropna(subset=["val"])
        if sub.empty:
            return math.nan
        return float(sub.loc[sub["val"].abs().idxmax(), "val"])

    # ---------------- INCOME STATEMENT ----------------
    revenue = get_first(
        ["RevenueFromContractWithCustomerExcludingAssessedTax",
         "SalesRevenueNet",
         "Revenues"]           # add generic 'Revenues' for Disney
    )
    cogs = get_first(["CostOfGoodsAndServicesSold", "CostOfSales"])
    sga = get_first(["SellingGeneralAndAdministrativeExpense",
                     "SellingMarketingAndAdministrativeExpense"])
    net_income = get_first(["NetIncomeLoss", "ProfitLoss"])

    # Operating income approximation if tag not present directly
    op_income_direct = get_first(["OperatingIncomeLoss"])
    if not math.isnan(op_income_direct):
        operating_income = op_income_direct
    elif any(math.isnan(x) for x in [revenue, cogs, sga]):
        operating_income = math.nan
    else:
        operating_income = revenue - cogs - sga

    # ---------------- BALANCE SHEET ----------------
    # Disney & BAB both use instant contexts starting with 'i' or 'I'
    instant_pattern = r"^[iI]"

    assets = get_first(["Assets"], pattern=instant_pattern)
    cash = get_first(["CashAndCashEquivalentsAtCarryingValue",
                      "CashCashEquivalentsAndShortTermInvestments"],
                     pattern=instant_pattern)
    inventory = get_first(["InventoryNet", "InventoriesNet"],
                          pattern=instant_pattern)
    ppe = get_first(["PropertyPlantAndEquipmentNet",
                     "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetNet",
                     "PropertyPlantAndEquipmentGross"],
                    pattern=instant_pattern)

    liab_current = get_first(["LiabilitiesCurrent"], pattern=instant_pattern)
    liab_noncurrent = get_first(["LiabilitiesNoncurrent",
                                 "OtherLiabilitiesNoncurrent",
                                 "DeferredTaxAndOtherLiabilitiesNoncurrent"],
                                pattern=instant_pattern)

    if math.isnan(liab_current) and math.isnan(liab_noncurrent):
        total_liab = math.nan
    else:
        total_liab = (0 if math.isnan(liab_current) else liab_current) + \
                     (0 if math.isnan(liab_noncurrent) else liab_noncurrent)

    equity = get_first(["StockholdersEquity",
                        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
                       pattern=instant_pattern)

    # ---------------- EPS ----------------
    eps_basic = get_first(["EarningsPerShareBasic"])
    eps_diluted = get_first(["EarningsPerShareDiluted",
                             "EarningsPerShareDilutedContinuingOperations"])

    # ---------------- CASH FLOW ----------------
    cfo = get_first(["NetCashProvidedByUsedInOperatingActivities",
                     "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"])
    cfi = get_first(["NetCashProvidedByUsedInInvestingActivities",
                     "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations"])
    cff = get_first(["NetCashProvidedByUsedInFinancingActivities",
                     "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations"])
    net_change_cash = get_first(["CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
                                 "CashAndCashEquivalentsPeriodIncreaseDecrease"])

    # ---------------- DEBT ----------------
    debt = get_first(["LongTermDebtNoncurrent",
                      "LongTermDebtCurrent",
                      "DebtCurrent",
                      "DebtNoncurrent",
                      "DebtInstrumentCarryingAmount"],
                     pattern=instant_pattern)

    # ---------------- TAX EXPENSE ----------------
    tax_expense = get_first(["IncomeTaxExpenseBenefit",
                             "CurrentIncomeTaxExpenseBenefit"])

    # ---------------- SEGMENT REVENUES (optional) ----------------
    # If Disney has segment tags similar to BAB, they will be picked up here.
    seg = df[df["qname"].isin(
        ["RevenueFromContractWithCustomerExcludingAssessedTax",
         "SalesRevenueNet",
         "Revenues"]
    )].copy()
    seg["val"] = seg["value_raw"].map(clean_num)
    seg = seg.dropna(subset=["val"])

    seg_retail = math.nan
    seg_commercial = math.nan
    seg_intl = math.nan
    # (You can extend this later if you want specific Disney segment members.)

    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": operating_income,
        "NetIncome": net_income,
        "TotalAssets": assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": equity,
        "Cash": cash,
        "Inventory": inventory,
        "PropertyPlantEquipment": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "NetChangeCash": net_change_cash,
        "Debt": debt,
        "TaxExpense": tax_expense,
        "SegRev_Retail": seg_retail,
        "SegRev_Commercial": seg_commercial,
        "SegRev_International": seg_intl,
    }


# In[101]:


rows = []

for year, fname in files:
    print(f"Processing {year} – {fname} ...")
    metrics = extract_metrics(fname)
    metrics["Year"] = year
    rows.append(metrics)

disney_results = pd.DataFrame(rows).set_index("Year")
disney_results


# In[102]:


import matplotlib.pyplot as plt


# In[103]:


ax = disney_results[["CFO", "CFI", "CFF"]].div(1e9).plot(
    kind="bar", figsize=(10,6)
)
ax.set_title("Disney Cash Flows (CFO, CFI, CFF)")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("USD (billions)")
plt.xticks(rotation=0)
plt.show()


# In[106]:


get_ipython().system('pip install beautifulsoup4 html5lib')


# In[108]:


import math
import pandas as pd
from bs4 import BeautifulSoup

# ---------- helper to clean numbers ----------
def clean_num(text):
    if text is None:
        return math.nan
    s = str(text).strip().replace(",", "").replace("$", "").replace("\u2212", "-")
    if s in ["", "—", "-", "na", "n/a", "NA"]:
        return math.nan
    if s[0] == "(" and s[-1] == ")":
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return math.nan

# ---------- function that reads ONE 10-K iXBRL and extracts all metrics ----------
def extract_metrics(filename):
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    facts = []
    for fact in soup.find_all():
        if not fact.has_attr("contextRef"):
            continue
        txt = fact.text.strip() if fact.text else ""
        if txt == "":
            continue
        facts.append(
            {
                "qname": fact.name,
                "context": fact["contextRef"],
                "value_raw": txt,
            }
        )

    df = pd.DataFrame(facts)

    def get_first(tag_list, pattern=None):
        sub = df[df["qname"].isin(tag_list)].copy()
        if pattern:
            sub = sub[sub["context"].str.contains(pattern, regex=True)]
        if sub.empty:
            return math.nan
        sub["val"] = sub["value_raw"].map(clean_num)
        sub = sub.dropna(subset=["val"])
        if sub.empty:
            return math.nan
        return float(sub.loc[sub["val"].abs().idxmax(), "val"])

    # --- Income statement items ---
    revenue = get_first(
        ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues"]
    )
    cogs = get_first(["CostOfGoodsAndServicesSold", "CostOfSales"])
    sga = get_first(["SellingGeneralAndAdministrativeExpense"])
    net_income = get_first(["NetIncomeLoss"])

    if any(math.isnan(x) for x in [revenue, cogs, sga]):
        operating_income = math.nan
    else:
        operating_income = revenue - cogs - sga

    # --- Balance sheet items ---
    assets = get_first(["Assets"], pattern=r"^i_")
    cash = get_first(["CashAndCashEquivalentsAtCarryingValue"], pattern=r"^i_")
    inventory = get_first(["InventoryNet"], pattern=r"^i_")
    ppe = get_first(["PropertyPlantAndEquipmentNet"], pattern=r"^i_")
    liab_current = get_first(["LiabilitiesCurrent"], pattern=r"^i_")
    liab_noncurrent = get_first(
        ["OtherLiabilitiesNoncurrent", "LiabilitiesNoncurrent"], pattern=r"^i_"
    )
    total_liab = (
        (liab_current if not math.isnan(liab_current) else 0.0)
        + (liab_noncurrent if not math.isnan(liab_noncurrent) else 0.0)
    )
    if math.isnan(liab_current) and math.isnan(liab_noncurrent):
        total_liab = math.nan

    equity = get_first(
        [
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ],
        pattern=r"^i_",
    )

    eps_basic = get_first(["EarningsPerShareBasic"])
    eps_diluted = get_first(["EarningsPerShareDiluted"])

    cfo = get_first(
        [
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ]
    )
    cfi = get_first(
        [
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
        ]
    )
    cff = get_first(
        [
            "NetCashProvidedByUsedInFinancingActivities",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
        ]
    )
    net_change_cash = get_first(["CashAndCashEquivalentsPeriodIncreaseDecrease"])

    debt = get_first(
        [
            "LongTermDebtNoncurrent",
            "LongTermDebtCurrent",
            "LongTermDebtAndCapitalLeaseObligations",
            "DebtCurrent",
            "DebtNoncurrent",
            "DebtInstrumentCarryingAmount",
        ]
    )

    tax_expense = get_first(
        ["IncomeTaxExpenseBenefit", "IncomeTaxExpenseBenefitContinuingOperations"]
    )

    seg = df[df["qname"].isin(["RevenueFromContractWithCustomerExcludingAssessedTax"])].copy()
    seg["val"] = seg["value_raw"].map(clean_num)
    seg = seg.dropna(subset=["val"])

    seg_retail = seg[
        seg["context"].str.contains("RetailMember")
        & ~seg["context"].str.contains("GiftCardBreakageMember")
    ]["val"].sum()

    seg_commercial = seg[seg["context"].str.contains("CommercialProductAndServiceMember")][
        "val"
    ].sum()

    seg_international = seg[seg["context"].str.contains("InternationalFranchisingMember")][
        "val"
    ].sum()

    return {
        "Revenue": revenue,
        "COGS": cogs,
        "OperatingIncome": operating_income,
        "NetIncome": net_income,
        "TotalAssets": assets,
        "TotalLiabilities": total_liab,
        "TotalEquity": equity,
        "Cash": cash,
        "Inventory": inventory,
        "PropertyPlantEquipment": ppe,
        "EPS_Basic": eps_basic,
        "EPS_Diluted": eps_diluted,
        "CFO": cfo,
        "CFI": cfi,
        "CFF": cff,
        "NetChangeCash": net_change_cash,
        "Debt": debt,
        "TaxExpense": tax_expense,
        "SegRev_Retail": float(seg_retail) if not math.isnan(seg_retail) else math.nan,
        "SegRev_Commercial": float(seg_commercial) if not math.isnan(seg_commercial) else math.nan,
        "SegRev_International": float(seg_international)
        if not math.isnan(seg_international)
        else math.nan,
    }

# ---------- list of your files with the fiscal year label you want ----------
# ---------- list of your Disney files with the fiscal year label you want ----------
files = [
    (2021, "disney-20211002_htm.xml"),
    (2022, "disney-20221001_htm.xml"),
    (2023, "disney-20230930_htm.xml"),
    (2024, "disney-20240928_htm.xml"),
]

rows = []
for year, fname in files:
    print(f"Processing {year} - {fname} ...")
    metrics = extract_metrics(fname)
    metrics["Year"] = year
    rows.append(metrics)

results = pd.DataFrame(rows).set_index("Year")
results


# In[109]:


results.head()
results.index


# In[110]:


import matplotlib.pyplot as plt

# Make sure the index is integer years (it already is, but just to be safe)
results.index = results.index.astype(int)

# Plot revenue
ax = results["Revenue"].plot(kind="line", marker="o", figsize=(10,5))

# Force x-axis ticks to be exactly the years in the index
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("Disney Revenue Over Time")
plt.xlabel("Year")
plt.ylabel("Revenue (USD)")
plt.grid(True)
plt.show()


# In[111]:


import matplotlib.pyplot as plt

# Ensure index is integer years
results.index = results.index.astype(int)

ax = results[["Revenue", "NetIncome"]].plot(
    kind="line", marker="o", figsize=(10,5)
)

# Force x-axis to show only actual years
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("Revenue & Net Income Over Time")
plt.xlabel("Year")
plt.ylabel("USD")
plt.grid(True)
plt.show()


# In[112]:


import matplotlib.pyplot as plt

# Ensure index is integer years
results.index = results.index.astype(int)

ax = results[["OperatingIncome", "NetIncome"]].plot(
    kind="line", marker="o", figsize=(10,5)
)

# Force x-axis to show only actual years
ax.set_xticks(results.index)
ax.set_xticklabels(results.index.astype(str))

plt.title("OperatingIncome & Net Income Over Time")
plt.xlabel("Year")
plt.ylabel("USD")
plt.grid(True)
plt.show()


# In[113]:


# ==========================================
# COMPARISON
# ==========================================


# In[114]:


import os

os.listdir()


# In[115]:


company_files = {
    "Hasbro": "hasbro 2021-2024.html",
    "Mattel": "mattel 2021-2024.html",
    "Jakks Pacific": "jakkspacific 2021-2024.html",
    "Funko": "funko 2021-2024.html",
    "Build-A-Bear": "buildabear2021-2024.html",
    "Disney": "disney2021-2024.html",
}


# In[117]:


for name, path in company_files.items():
    try:
        with open(path, "r") as f:
            print(f"OK: Found {path}")
    except:
        print(f"ERROR: Could not find {path}")


# In[119]:


import pandas as pd

def clean_df(df):
    """Flatten multi-level columns and clean the Year column."""
    df.columns = [c[0] for c in df.columns]   # take first level of MultiIndex
    df = df.rename(columns={"Unnamed: 0_level_0": "Year"})
    df = df.drop_duplicates(subset=["Year"], keep="last")
    df["Year"] = df["Year"].astype(int)
    return df

def add_ratios(df):
    """Compute key ratios."""
    out = df.copy()
    
    # Profitability
    out["GrossMargin"]     = (out["Revenue"] - out["COGS"]) / out["Revenue"]
    out["OperatingMargin"] = out["OperatingIncome"] / out["Revenue"]
    out["NetMargin"]       = out["NetIncome"] / out["Revenue"]

    # Leverage
    out["DebtToEquity"] = out["TotalLiabilities"] / out["TotalEquity"]

    # Efficiency
    out["AssetTurnover"] = out["Revenue"] / out["TotalAssets"]

    # Returns
    out["ROA"] = out["NetIncome"] / df["TotalAssets"]
    out["ROE"] = out["NetIncome"] / df["TotalEquity"]

    return out

def load_with_ratios(path):
    """Read the HTML file, grab the table, clean it, and add ratios."""
    html = open(path, "r", encoding="utf-8").read()
    df = pd.read_html(html)[0]
    df = clean_df(df)
    df = add_ratios(df)
    return df


# In[120]:


company_files = {
    "Hasbro": "hasbro 2021-2024.html",
    "Mattel": "mattel 2021-2024.html",
    "Jakks Pacific": "jakkspacific 2021-2024.html",
    "Funko": "funko 2021-2024.html",
    "Build-A-Bear": "buildabear2021-2024.html",
    "Disney": "disney2021-2024.html",
}


# In[121]:


all_rows = []

for company, path in company_files.items():
    df_company = load_with_ratios(path)
    df_company["Company"] = company
    all_rows.append(
        df_company[[
            "Company", "Year",
            "GrossMargin", "OperatingMargin", "NetMargin",
            "DebtToEquity", "AssetTurnover", "ROA", "ROE"
        ]]
    )

ratio_df = pd.concat(all_rows, ignore_index=True)
ratio_df = ratio_df.sort_values(["Company", "Year"])

ratio_df


# In[122]:


hasbro = (
    ratio_df[ratio_df["Company"] == "Hasbro"]
    .sort_values("Year")
    .set_index("Year")
)

hasbro


# In[123]:


peers = ["Hasbro", "Mattel", "Jakks Pacific", "Funko"]

peers_2024 = (
    ratio_df[(ratio_df["Year"] == 2024) & (ratio_df["Company"].isin(peers))]
    .set_index("Company")
)

peers_2024


# In[124]:


# Profitability comparison
peers_2024[["GrossMargin", "OperatingMargin", "NetMargin"]].plot(kind="bar")
plt.title("Profitability – 2024 Peer Comparison")
plt.ylabel("Ratio")
plt.xticks(rotation=45)
plt.show()

# Returns
peers_2024[["ROA", "ROE"]].plot(kind="bar")
plt.title("ROA & ROE – 2024 Peer Comparison")
plt.ylabel("Ratio")
plt.xticks(rotation=45)
plt.show()

# Leverage & efficiency
peers_2024[["DebtToEquity", "AssetTurnover"]].plot(kind="bar")
plt.title("Leverage & Asset Turnover – 2024 Peer Comparison")
plt.ylabel("Ratio")
plt.xticks(rotation=45)
plt.show()


# In[124]:


# Profitability comparison
peers_2024[["GrossMargin", "OperatingMargin", "NetMargin"]].plot(kind="bar")
plt.title("Profitability – 2024 Peer Comparison")
plt.ylabel("Ratio")
plt.xticks(rotation=45)
plt.show()

# Returns
peers_2024[["ROA", "ROE"]].plot(kind="bar")
plt.title("ROA & ROE – 2024 Peer Comparison")
plt.ylabel("Ratio")
plt.xticks(rotation=45)
plt.show()

# Leverage & efficiency
peers_2024[["DebtToEquity", "AssetTurnover"]].plot(kind="bar")
plt.title("Leverage & Asset Turnover – 2024 Peer Comparison")
plt.ylabel("Ratio")
plt.xticks(rotation=45)
plt.show()


# In[7]:


# ==========================================
# PREDICTION
# ==========================================


# In[8]:


import pandas as pd

def clean_df(df):
    df.columns = [c[0] for c in df.columns]
    df = df.rename(columns={"Unnamed: 0_level_0": "Year"})
    df = df.drop_duplicates(subset=["Year"], keep="last")
    df["Year"] = df["Year"].astype(int)
    return df

def add_ratios(df):
    out = df.copy()
    out["GrossMargin"]     = (out["Revenue"] - out["COGS"]) / out["Revenue"]
    out["OperatingMargin"] = out["OperatingIncome"] / out["Revenue"]
    out["NetMargin"]       = out["NetIncome"] / out["Revenue"]
    out["DebtToEquity"]    = out["TotalLiabilities"] / out["TotalEquity"]
    out["AssetTurnover"]   = out["Revenue"] / out["TotalAssets"]
    out["ROA"]             = out["NetIncome"] / out["TotalAssets"]
    out["ROE"]             = out["NetIncome"] / out["TotalEquity"]
    return out

def load_with_ratios(path):
    html = open(path, "r", encoding="utf-8").read()
    df = pd.read_html(html)[0]
    df = clean_df(df)
    df = add_ratios(df)
    return df


# In[9]:


company_files = {
    "Hasbro": "hasbro 2021-2024.html",
    "Mattel": "mattel 2021-2024.html",
    "Jakks Pacific": "jakkspacific 2021-2024.html",
    "Funko": "funko 2021-2024.html",
    "Build-A-Bear": "buildabear2021-2024.html",
    "Disney": "disney2021-2024.html",
}


# In[10]:


all_rows = []

for company, path in company_files.items():
    df_company = load_with_ratios(path)
    df_company["Company"] = company
    all_rows.append(
        df_company[[
            "Company", "Year",
            "GrossMargin", "OperatingMargin", "NetMargin",
            "DebtToEquity", "AssetTurnover", "ROA", "ROE"
        ]]
    )

ratio_df = pd.concat(all_rows, ignore_index=True)
ratio_df = ratio_df.sort_values(["Company", "Year"])

ratio_df


# In[11]:


hasbro = (
    ratio_df[ratio_df["Company"] == "Hasbro"]
    .sort_values("Year")
    .set_index("Year")
)

hasbro


# In[12]:


import numpy as np

X = hasbro.index.values.reshape(-1, 1)
y = hasbro["OperatingMargin"].values

X, y


# In[13]:


from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X, y)

print("Slope per year:", model.coef_[0])
print("Intercept:", model.intercept_)
print("R^2:", model.score(X, y))


# In[14]:


import numpy as np  # already imported, but safe

year_forecast = np.array([[2025]])
forecast_2025 = model.predict(year_forecast)[0]

print("Forecasted Operating Margin for 2025:", forecast_2025)


# In[15]:


import matplotlib.pyplot as plt

# Actual
years_actual = hasbro.index.values
om_actual = hasbro["OperatingMargin"].values

# Extended years 2021–2025
years_extended = np.append(years_actual, 2025)

# Regression line for all years (including 2025)
om_pred_line = model.predict(years_extended.reshape(-1, 1))

plt.plot(years_actual, om_actual, marker="o", label="Actual Operating Margin")
plt.plot(years_extended, om_pred_line, linestyle="--", label="Regression Line")
plt.scatter([2025], [forecast_2025], color="red", marker="x", s=80, label="Forecast 2025")

plt.title("Hasbro – Operating Margin Forecast to 2025")
plt.xlabel("Year")
plt.ylabel("Operating Margin")
plt.legend()
plt.grid(True)
plt.show()


# In[ ]:




