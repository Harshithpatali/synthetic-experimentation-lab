# Real behavioral reference data

This folder contains a small real-data benchmark sample used to test whether the
synthetic population reproduces observable customer transaction behavior.

## Source

**UCI Online Retail II**

Daqing Chen. *Online Retail II* [Dataset]. UCI Machine Learning Repository.

- UCI dataset: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- DOI: https://doi.org/10.24432/C5CG6D
- License: **CC BY 4.0**
- Original data: 1,067,371 transaction rows from a UK-based registered
  non-store online retailer covering 2009-12-01 through 2011-12-09.

## Bundled sample

online_retail_real_sample.csv contains **1,950 real transaction rows** from
the public UCI dataset. No rows were generated or synthetically augmented.

The sample is included only as a lightweight benchmark so the deployed
application does not need to ship the full 43.5 MB workbook.

The reference is **not Indian**. It is used because it is a verified-real
e-commerce transaction dataset with customer IDs, orders, prices and dates.
The benchmark therefore tests transferable transaction behavior, not India
specific demographics, geography or device usage.

## How the application uses it

The application reconstructs customer-level reference profiles:

- order frequency
- average order value
- recency
- lifecycle composition

Synthetic-vs-real comparison uses empirical distribution distance. AOV is
compared by relative distribution shape because the source currency is GBP
while the synthetic application represents AOV in INR.

The benchmark is a **behavioral alignment check**, not a claim that the
synthetic customers are statistically representative of Indian consumers.

## Attribution

If this reference data is redistributed or reused, retain the UCI attribution
and CC BY 4.0 terms above.
