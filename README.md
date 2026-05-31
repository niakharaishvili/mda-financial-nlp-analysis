# mda-financial-nlp-analysis

NLP and financial analysis of toy industry 10-K filings.

## Overview

This project examines whether the **narrative tone** of a company's annual report
(the Management's Discussion & Analysis section, or "MD&A") lines up with its
**actual financial performance**. Using six US-listed toy and entertainment companies,
it combines a quantitative financial analysis with text analysis of the MD&A, then
compares the two: when the numbers get worse, does the language get more negative,
more complex, or more evasive?

**Companies analysed:** Hasbro, Mattel, Funko, Build-A-Bear, Jakks Pacific, and Disney
**Period:** Fiscal years 2021–2024

## Data

All data comes from public filings on the U.S. Securities and Exchange Commission's
[EDGAR](https://www.sec.gov/edgar) system:

- **Financial figures** were extracted from each company's 10-K XBRL instance documents
  (machine-readable financial statement data).
- **Narrative text** comes from the MD&A section of the same 10-K filings.

The raw filing files are not included in this repository. They can be downloaded
directly from EDGAR using each company's filings page.

## Methods

The analysis has three parts:

1. **Quantitative financial analysis** — parse XBRL filings to pull revenue, cost of
   goods sold, operating and net income, balance-sheet items, cash flows, EPS, and
   debt; compute profitability, leverage, efficiency, and return ratios (gross/operating/
   net margin, debt-to-equity, asset turnover, ROA, ROE); compare companies; and run a
   simple linear-regression forecast of operating margin.

2. **Narrative analysis of the MD&A** — topic modeling with LDA and NMF to surface the
   themes management emphasises; readability scoring (Flesch Reading Ease,
   Flesch–Kincaid, Gunning Fog, SMOG, Dale–Chall, ARI) to measure how dense the
   disclosure is; and sentiment scoring of the tone.

3. **Quant + qual comparison** — bring the financial ratios and the narrative signals
   together per company and across the peer group to see how closely they move together.

## Repository structure

```
analysis/          Financial extraction, ratios, peer comparison, and forecasting
readability/       Readability and complexity scoring across the six MD&A sections
topic modeling/    Per-company LDA / NMF topic modeling of the MD&A text
README.md
requirements.txt
```

## Running it

The scripts were written as Jupyter notebooks and exported to `.py`. To reproduce:

```bash
pip install -r requirements.txt
```

Then download the relevant 10-K XBRL and MD&A files from EDGAR, place them alongside
the scripts (the filenames each script expects are set at the top of the file), and
run the cells in order.

## Tools

Python, pandas, NumPy, scikit-learn, matplotlib, seaborn, NLTK, textstat, TextBlob,
BeautifulSoup, pypdf.

## Authors

Course group project (Group 5), Constructor University Bremen.
*Add your teammates' names here so they're credited.*

## Notes

This was an academic project. The financial extraction relies on companies tagging
their XBRL filings consistently; where a tag is missing or named differently, some
figures may be incomplete. The qualitative labels (sentiment, readability bands) are
analyst interpretations of the model output, not automated classifications.
