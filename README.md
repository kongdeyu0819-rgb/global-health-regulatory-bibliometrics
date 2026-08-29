# Global health regulatory reliance, harmonization, and medicines access: bibliometric & thematic analysis (2000–2025)

Companion data and reproducible code for a bibliometric and thematic review of
global health **regulatory reliance**, **harmonization**, and **medicines access**
(2000–2025), submitted to *Health Policy and Planning*.

## What is in this repository

| Path | Contents |
|------|----------|
| `data/paperA_corpus.csv` | Derived corpus of **2,063** included records (bibliographic metadata only). Local-library provenance is anonymized to `local_policy_library`. |
| `data/prisma_transparency.json` | PRISMA 2020 flow transparency file (identification → screening → inclusion counts). |
| `data/top_*.csv`, `data/*_communities.json`, `data/thematic_evolution.json`, `data/annual_counts.json`, `data/burst_keywords.csv`, `data/keyword_clusters.csv`, `data/country_*.csv|.json`, `data/paperA_bibliometrix.csv` | Bibliometric, co-citation/co-country, thematic-map, and burst-analysis outputs used in the manuscript figures. |
| `code/` | Curated Python pipeline (acquisition → corpus assembly → bibliometric/network analysis → PRISMA). |
| `manuscript/manuscript.md` | Preprint of the submitted manuscript (HPP structured abstract + Key messages + Sections 1–5 + References). |
| `.zenodo.json` | Zenodo deposition metadata (populated automatically when archived via the GitHub–Zenodo integration). |

## Data dictionary — `data/paperA_corpus.csv`

`title, year, authors, journal, doi, pmid, source, source_detail, abstract, keywords, access_lens, citations, norm`

- `source`: originating database(s), e.g. `pubmed`, `europepmc`, `who_iris`, `who_iris_policy`, `epmc_policy`, or `local` (local policy library, 50 records).
- `source_detail`: for `local` records this is anonymized as `local_policy_library`; for database records it may carry a sub-collection tag.
- `access_lens`: analytical lens tag used in the thematic coding (access / equity / LMIC medicines; vaccines / QA; health systems / financing).
- `citations`, `norm`: citation count and normalized citation metric as retrieved.

## Reproduce

```bash
# 1. Acquire source records (requires network; not needed if reusing data/)
python code/fetch_pubmed.py
python code/fetch_europepmc.py
python code/fetch_openalex.py
python code/fetch_who_iris.py
python code/fetch_policy_sources.py
#    local records are imported via code/extract_local.py from a local library
#    (confidential; not distributed — source_detail is anonymized in data/)

# 2. Assemble & de-duplicate the corpus
python code/build_corpus.py

# 3. Bibliometric + network + PRISMA analysis
python code/analyze_bibliometrics.py
python code/analyze_networks.py
python code/build_country_data.py
python code/compute_prisma.py
```

Dependencies: Python 3.9+, `pandas`, `requests`, `networkx` (and `matplotlib` for figure generation). The exact figure scripts used for the manuscript are in the project root (`figures/`), not required to reproduce the tabular outputs.

## Excluded from this repository

- `data/raw/*` — large raw API dumps (not needed to reproduce the published derived snapshot).
- `data/reference_examples/*` — copyrighted *Health Policy and Planning* example PDFs used only to set reference style; **not redistributed**.
- Local policy-library source PDFs — confidential; only anonymized metadata are published.

## License

Code and data are released under **CC BY 4.0** — see [`LICENSE`](LICENSE).
Attribution: cite this repository and the accompanying manuscript.

## How to cite

> Kong D, et al. Bibliometric and thematic analysis of global health regulatory
> reliance, harmonization, and medicines access (2000–2025): derived data and code.
> GitHub: https://github.com/kongdeyu0819-rgb/global-health-regulatory-bibliometrics
> [Zenodo DOI to be added after archiving].

A versioned DOI is minted automatically via the GitHub–Zenodo integration when a
release is published (see `.zenodo.json`).

## Notes for the authors (finalize before archiving)

- `.zenodo.json` `creators` / `contributors` and the related GitHub URL are placeholders — update with the final author list and confirm the repository name.
- The manuscript author list, affiliations, and ORCIDs in `manuscript/manuscript.md` are placeholders to be completed before submission.
