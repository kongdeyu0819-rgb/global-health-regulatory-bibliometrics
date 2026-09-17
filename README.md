# Regulatory reliance for medicines access in low- and middle-income countries: derived data and reproducible code (2000–2026)

Companion data and reproducible code for a bibliometric and thematic review of
regulatory reliance for **medicines access in low- and middle-income countries (LMICs)**,
2000–2026, submitted to *Health Policy and Planning*.

Corpus: **2,071 records** = 2,063 from a three-source systematic database search
(PubMed, Europe PMC, WHO IRIS) + 8 from a supplementary Chinese-language retrieval
(CNKI, Wanfang, Weipu), reported as "other sources" in the PRISMA 2020 flow.

## What is in this repository

| Path | Contents |
|------|----------|
| `data/paperA_corpus.csv` | Derived corpus of **2,071** included records (bibliographic metadata only). |
| `data/prisma_transparency.json` | PRISMA 2020 two-column flow transparency file (identification → screening → inclusion counts, plus the Chinese-language "other sources" arm). |
| `data/top_*.csv`, `data/*_communities.json`, `data/thematic_evolution.json`, `data/annual_counts.json`, `data/burst_keywords.csv`, `data/keyword_clusters.csv`, `data/country_*.csv|.json`, `data/paperA_bibliometrix.csv` | Bibliometric, co-authorship/country, thematic-map, and burst-detection outputs behind the manuscript figures. |
| `figures/` | The nine manuscript figures, including `prisma.png` (PRISMA 2020 flow diagram). |
| `code/` | Curated Python pipeline (acquisition → corpus assembly → bibliometric/network analysis → PRISMA → style QA). |
| `manuscript/manuscript.md`, `manuscript/paper_HPP.docx` | Manuscript source and generated submission file. |
| `.zenodo.json` | Zenodo deposition metadata (consumed by the GitHub–Zenodo integration). |

## Provenance of the corpus — read before citing the counts

`source` records one or more origins per record, joined by `|`:

| `source` value | Meaning | Records |
|---|---|---|
| `pubmed` | PubMed / MEDLINE via E-utilities | part of the 2,063 |
| `europepmc`, `epmc_policy` | Europe PMC REST API (mechanism and policy strands) | part of the 2,063 |
| `who_iris`, `who_iris_policy` | WHO Institutional Repository for Information Sharing (grey literature and policy documents) | part of the 2,063 |
| `local` | Records held in a curated institutional document collection before searching; **folded into the 2,063 count** rather than reported as a separate PRISMA stream | 50 |
| `chinese` | Supplementary Chinese-language retrieval (CNKI / Wanfang / Weipu), reported as Column 2 "other sources" in the PRISMA flow | 8 |

The 50 `local` records are reported inside the 2,063 figure in order to keep the PRISMA
flow free of a fourth identification stream. `prisma_transparency.json` records this under
`local_in_corpus`. Independent readers who wish to reproduce the analysis **without** those
records can filter them out; see `Notes for the authors` below.

`source_detail`: for `chinese` records this names the originating Chinese databases; for
database records it may carry a sub-collection tag; for `local` records it carries an
internal collection label.

## Data dictionary — `data/paperA_corpus.csv`

`title, year, authors, journal, doi, pmid, source, source_detail, abstract, keywords, access_lens, citations, norm`

- `access_lens`: analytical lens tag used in the thematic coding (access / equity / LMIC medicines; vaccines / QA; health systems / financing).
- `citations`, `norm`: citation count and normalized citation metric as retrieved.

## Reproduce

```bash
# 1. Acquire source records (requires network; skip if reusing data/)
python code/fetch_pubmed.py
python code/fetch_europepmc.py
python code/fetch_openalex.py
python code/fetch_who_iris.py
python code/fetch_policy_sources.py
#    supplementary Chinese-language records are retrieved manually per
#    search_strategy.md (Appendix B) — see the protocol in the root directory.

# 2. Assemble & de-duplicate the corpus
python code/build_corpus.py

# 3. Bibliometric + network + PRISMA analysis
python code/analyze_bibliometrics.py
python code/analyze_networks.py
python code/build_country_data.py
python code/compute_prisma.py   # -> figures/prisma.png + data/prisma_transparency.json

# 4. (optional) Journal-style QA against the target journal's measured writing profile
python code/audit_manuscript_hpp.py path/to/manuscript.md
```

Dependencies: Python 3.9+, `pandas`, `requests`, `networkx` (and `matplotlib` for figure generation).

## Excluded from this repository

- `data/raw/*` — large raw API dumps (not needed to reproduce the published derived snapshot).
- `data/reference_examples/*` — copyrighted *Health Policy and Planning* example PDFs used only to calibrate writing style; **not redistributed**.
- Full texts and PDFs of the `local` records — only the extracted bibliographic metadata above are distributed.

## License

Code and data are released under **CC BY 4.0** — see [`LICENSE`](LICENSE).
Attribution: cite this repository and the accompanying manuscript.

## How to cite

> Kong D, et al. Regulatory reliance for medicines access in low- and middle-income
> countries: derived data and reproducible code (2000–2026).
> GitHub: https://github.com/kongdeyu0819-rgb/global-health-regulatory-bibliometrics
> [Zenodo DOI to be added after archiving].

A versioned DOI is minted automatically via the GitHub–Zenodo integration when a
release is published (see `.zenodo.json`).

## Notes for the authors (finalize before archiving)

- `.zenodo.json` `creators` must be checked against the final author list before archiving.
- **Zenodo DOI not yet minted.** Releases exist on GitHub, but a Zenodo DOI requires a one-time
  action by the depositor: log in at <https://zenodo.org> with the GitHub account, authorise the
  Zenodo GitHub App, enable this repository, then press *Publish* on the release to archive.
- The 50 `local` records are disclosed in Methods §2.1 and §2.2 of the manuscript and counted
  inside the 2,063; see `local_in_corpus` in `prisma_transparency.json`.
- `manuscript/paper_HPP_new.docx` is a stale intermediate build from the lock-file workaround;
  delete before publishing the repository.
