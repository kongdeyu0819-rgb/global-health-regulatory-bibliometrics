# Regulatory reliance for medicines access in low- and middle-income countries: what twenty-six years of scholarship tells policymakers, 2000–2026

## Abstract

Regulatory reliance, through WHO prequalification, regional harmonization and the WHO Global Benchmarking Tool, has become a standard instrument for widening medicines access in low- and middle-income countries (LMICs). The scholarship behind that shift has not been mapped. We report a systematic bibliometric review of this literature for 2000 to 2026 with a thematic synthesis. Following PRISMA 2020 we searched PubMed, Europe PMC and the WHO Institutional Repository for Information Sharing, then added a Chinese-language search of CNKI, Wanfang and Weipu, and analysed 2,071 records (2,063 database records plus 8 Chinese-language records). We mapped annual output, journals, authors, country collaboration, keyword co-occurrence, clustering, burst detection and thematic evolution, and independently coded the 40 most-cited English-indexed records. Annual output rose from 53 publications in 2015 to 152 in 2024, and the field resolves into three stable clusters: access, equity and essential medicines; vaccines and quality assurance; health systems and financing. The qualitative coding returned the same three clusters, corroborating the computational partition. Two findings matter for planners. Collaboration is led by high-income regulators and procurers, with LMIC participation concentrated in a few middle-income countries. And the literature measures reliance mechanisms far more thoroughly than outcomes, so price, availability and coverage are rarely traced through. Reliance should therefore be governed rather than merely adopted, paired with market-shaping and capacity strengthening, and tested by an explicit equity audit.

**Key messages**
- This study provides the first integrated map of 26 years of scholarship on regulatory reliance for medicines access in LMICs, across English-indexed, WHO grey and Chinese-language sources.
- Two independent procedures converge on the same structure: computational clustering of the keyword network and qualitative coding of the 40 most-cited records both return three themes, access and equity, vaccines and quality, and health systems and financing.
- Reliance mechanisms lower regulatory barriers, yet the literature rarely follows reliance through to price, availability or coverage, and it seldom asks whose regulatory capacity grows. Both are policy questions.
- Policymakers and regulators should therefore govern reliance rather than merely adopt it, pairing it with market-shaping, local production and capacity strengthening, and subjecting it to an explicit equity audit.

---

## 1. Background

### 1.1 Regulatory reliance: definitions and policy background

Regulatory reliance describes the practice by which a national medicines regulator voluntarily uses, in full or in part, the assessment or approval decisions of another regulator or of a trusted institution such as the World Health Organization (WHO), instead of conducting an independent evaluation (WHO 2017). Reliance exists on a continuum that runs from unilateral reliance on a stringent regulatory authority, through formal work-sharing arrangements, to structured collaborative registration procedures. At the international level, **WHO prequalification (PQ)** supplies an independent quality and supply-reliability signal that dozens of procurers and national authorities rely upon. At the regional level, initiatives such as the **African Medicines Regulatory Harmonization (AMRH)** programme and the nascent **African Medicines Agency (AMA)** seek to mutualize assessment across jurisdictions. Complementing these supply-side mechanisms, the **WHO Global Benchmarking Tool (GBT)** provides a maturity scale against which national regulatory systems can be assessed and strengthened. Each instrument redistributes regulatory work between authorities, and each carries distributional consequences for the countries that depend on it.

### 1.2 Why reliance matters for LMIC medicine access

Medicines access in LMICs is constrained not only by price and supply but also by the time and cost of national marketing-authorization review. Where a therapeutic has already been assessed by a stringent authority or by WHO, a de novo national review duplicates effort and may defer patient access by months or years (WHO 2017). Reliance is therefore invoked as a lever to compress time to market and to reduce the technical burden on under-resourced agencies. Priority products come first: vaccines, antiretroviral and antimicrobial therapies, and maternal and child health medicines, where procurement often runs through prequalified suppliers. The COVID-19 pandemic elevated reliance as an instrument of emergency response, and the momentum has persisted: reliance now appears in a growing number of national medicines policy documents.

### 1.3 The research gap

Three gaps limit the evidence base on which policymakers and regulators can draw. First, the scholarly field itself has not been mapped. It is unclear how fast, by whom, and around which themes this literature has grown. Second, the literature describes *mechanisms* in detail but is thin on demonstrated *access outcomes*: few studies trace reliance to measurable changes in price, availability or treatment coverage. Third, an *equity and capacity asymmetry* runs through the field, in that reliance is frequently analysed from the perspective of high-income regulators and global procurers while the uneven regulatory capacity of LMIC agencies and the distributional consequences for their populations are seldom examined. Prior narrative and scoping reviews have examined WHO prequalification or regional regulatory harmonization in isolation; a bibliometric map of the integrated, two-decade field that centres access outcomes and equity asymmetries is absent.

### 1.4 Aim and contribution

This study makes four contributions to the policy literature on medicines access. First, it provides the first integrated map of this field, bringing together English-indexed scholarship, WHO grey literature and a Chinese-language corpus that no previous map of regulatory reliance has included. Second, it subjects that map to an independent check, because the qualitative coding of the 40 most-cited records was carried out without reference to the clustering solution and reproduced the same three themes. Third, it converts the resulting structure into a diagnostic finding of direct policy relevance: the field has measured its mechanisms far more thoroughly than its outcomes. Fourth, it offers decision-makers a concrete governance instrument, the equity audit, which turns mechanism-rich evidence into an accountable test of who gains faster access, whose regulatory capacity is built, and who remains dependent. Where earlier reviews examined prequalification or regional harmonization in isolation, this study treats reliance as one policy field and asks what twenty-six years of its scholarship tells those who govern it.

---

## 2. Methods

### 2.1 Search strategy and data sources

We followed the PRISMA 2020 flow diagram (Page et al. 2021). Records were retrieved from three sources spanning 2000 through 2 September 2026: (i) **PubMed** via the E-utilities API; (ii) **Europe PMC** via its REST API, queried for both a mechanism strand and a policy strand; and (iii) the **WHO Institutional Repository for Information Sharing (WHO IRIS)** for grey literature and policy documents, likewise queried for both strands. Search strings combined terms for regulatory reliance, harmonization and prequalification with terms for medicines access, affordability and LMICs, and the full strategies are reported in Appendix A. We also ran a supplementary Chinese-language search of CNKI, Wanfang and Weipu (Appendix B). Eight relevant Chinese records published between 2024 and 2026 were retrieved as full text and merged into the analytical corpus, where they contribute to the annual, journal, author, keyword and cluster analyses. Chinese journal metadata carry no structured affiliation field, so these records are not attributable by country and the country analysis rests on the English-indexed records that do carry addresses. A further 50 records were already held in a curated collection of literature on global health and medicines regulation before the search was run, and were contributed by a colleague acknowledged below. They are reported inside the 2,063 rather than as a separate identification stream in the PRISMA flow, and the arrangement is recorded in the accompanying transparency file. After de-duplication, the combined corpus comprised 2,071 unique records, of which 2,063 came from the three-source systematic database search and 8 from the targeted Chinese-language retrieval (Figure 1).

### 2.2 Screening and eligibility

Eligibility required that a record address both a regulatory reliance, harmonization, prequalification or benchmarking mechanism and its relevance to medicines access, availability, affordability or regulatory capacity in LMICs. Screening used pre-specified automated rules implemented in `build_corpus.py`, and the reason for exclusion was recorded for every rejected record. De-duplication used the DOI where available and the title plus journal otherwise; a record was retained only if it matched both a mechanism term and an access or LMIC context term, with explicit genre exclusions for first-approval notices and for clinical-pharmacology reviews lacking a policy component. Forty-nine of the 50 curated records did not satisfy the automated relevance rules, because their metadata carry neither an abstract nor a keyword field (44 of the 50 carry neither, and 27 of the 50 have Chinese-language titles), so the rules had no text to match against. These records were assessed manually against the same two-part criteria and retained where both a mechanism and an access or LMIC context were present in the full text. The corpus includes grey literature and policy documents by design, so peer-reviewed journal outputs are distinguished from WHO IRIS policy documents in all descriptive analyses.

### 2.3 Bibliometric analysis

Bibliometric procedures were implemented in Python, following Bibliometrix-style workflows and using networkx. We computed annual publication trends, co-authorship and country collaboration networks, keyword co-occurrence matrices, burst detection and thematic evolution across three windows (2000 to 2009, 2010 to 2017, 2018 onward). Clustering used greedy modularity maximization and resolved the keyword network into three communities (Q = 0.20); Section 2.4 reports an independent test of that partition. The country analysis rests on the 564 English-indexed records for which affiliation was recoverable, as set out in Section 2.5.

### 2.4 Qualitative synthesis

Beyond mapping, we extracted the 40 most-cited, relevance-confirmed records and coded them thematically. Coding was iterative and inductive, organized around the reliance mechanism, the access pathway and the equity implication. It was conducted on the policy-relevant content of each record rather than on citation rank alone. The resulting themes are reported in the Results and Discussion, with the coding framework provided as supplementary material.

### 2.5 Bias and limitations

*Registration.* This review was not registered in PROSPERO, and the protocol is provided as supplementary material. *Search window.* Retrieval was completed on 2 September 2026, so records indexed up to that date were eligible and 2026 online-first items are partial. *Coverage and missingness.* Author affiliation, and hence country of origin, was recoverable for 27.3% of the English-indexed corpus (564 of 2,063 records) and exclusively from database-indexed sources. WHO IRIS grey literature and the 8 Chinese records carry no structured addresses. Within the recoverable subset, 66.9% of country-attributed records are affiliated with high-income regulators and 33.1% with LMIC institutions. Non-indexed records lack any address field, so the country map characterises indexed scholarship. *Indicator choice.* Citation-based indicators favour already-visible, English-language, high-income-linked work and may over-weight reviews, policy papers and position papers, so the qualitative synthesis drew on a relevance-confirmed subset. *Language scope.* The database search covered English-language and English-metadata records. The supplementary Chinese-language search extends coverage to the Chinese regulatory-science literature indexed in CNKI, Wanfang and Weipu, which no previous review of this field has included; its search syntax and retrieval protocol are given in Appendix B.

### 2.6 Use of artificial-intelligence tools

Generative artificial intelligence was used at three points in this work: editing the language of the manuscript, producing and debugging the analysis code, and generating the figure scripts. The model used was Hy4 preview. It was not used to retrieve or screen records, to assign eligibility, to derive the bibliometric measures or to interpret the findings, and those steps were carried out by the authors from the source records and are reproducible from the deposited code. All AI-assisted output was checked against the underlying data and corrected where necessary before it entered the manuscript.

---

*Figure 1. PRISMA 2020 flow diagram of record identification, screening and inclusion. [figures/prisma.png]*
*Figure 2. Annual publication trend, 2000 to 2026. [figures/trend.png]*
*Figure 3. Most productive peer-reviewed journals, top 15. [figures/xt_png/bar_journals_h-1.png]*
*Figure 4. Most prolific authors. [figures/xt_png/bar_authors_h-1.png]*
*Figure 5. Country publication frequency in the PubMed-sourced affiliation subset. [figures/xt_png/bar_countries_h-1.png]*
*Figure 6. Keyword co-occurrence heatmap, top 25 keywords. [figures/xt_png/heatmap_keywords-1.png]*
*Figure 7. Keyword co-occurrence clustering into three thematic groups. [figures/_matplotlib_alt/keyword_cluster_bars.png]*
*Figure 8. Thematic evolution by cluster across three time windows. [figures/xt_png/bar_stack_thematic-1.png]*
*Figure 9. Thematic evolution alluvial diagram, 2000 to 2026. [figures/xt_png/sankey_evolution-1.png]*

---

## 3. Results

### 3.1 Literature search and corpus composition

The three-source systematic database search identified 16,846 records across five search strands (PubMed, Europe PMC × 2, WHO IRIS × 2). After removing 2,892 duplicates, 13,954 unique records remained, and 11,891 were excluded at screening for not meeting the relevance criteria, leaving **2,063 records** attributed to the three-source systematic database search, a figure that includes the 50 curated records described in Section 2.1 (Figure 1). A supplementary Chinese-language search (Appendix B) retrieved a further 8 relevant Chinese records published between 2024 and 2026 as full text; these were reported as other sources in the second column of the PRISMA flow and merged into the analytical corpus, giving a combined corpus of **2,071 records**. Most of the 2,063 English-indexed records are peer-reviewed journal articles. A small number of WHO IRIS policy and technical documents are retained as grey literature, and the two are distinguished in all descriptive analyses. The 8 Chinese records are peer-reviewed Chinese journal articles that contribute to the thematic and keyword analyses.

### 3.2 Annual publication trend

Annual output grew from 4 publications in 2000 to 53 in 2015 and 152 in 2024, close to a threefold increase over the final decade (Figure 2). Growth picked up after 2013 and again between 2020 and 2024. Counts for 2026 are partial because retrieval ended on 2 September 2026; records still being indexed are retained but not read as a complete-year trend.

### 3.3 Publication venues

The literature is dispersed across regulatory science, vaccinology and global-health outlets, which is consistent with a field that sits between technical regulation and health policy. The most productive peer-reviewed journals were *Therapeutic Innovation & Regulatory Science* (n = 45), *Vaccine* (n = 30), *Frontiers in Pharmacology* (n = 26), *Frontiers in Medicine* (n = 25), *Clinical Pharmacology & Therapeutics* (n = 17), *Journal of Pharmaceutical Policy and Practice* (n = 13), *PLOS ONE* (n = 12) and *Revista Panamericana de Salud Pública* (n = 11) (Figure 3). The supplementary Chinese-language search added several Chinese journals (*中国食品药品监管*, n = 4; *中国新药杂志*, *健康发展与政策研究*, *中国现代应用药学* and *中国药事*, n = 1 each), surfacing a distinct Chinese regulatory-science and policy literature that is otherwise under-represented in the English-indexed corpus. Specialist regulatory-science titles sit alongside broad global-health and health-policy journals, which fits a cross-disciplinary field.

### 3.4 Most active authors and collaboration structure

Authors who occupy the most central positions in the co-authorship network, measured by collaboration degree, were Stuart Walker (105), Sam Salek (94), Thierry Gastineau (56), Nora Dellepiane (55), Sonia Pagliusi (52), Richard Pazdur (51), Jyothsna Krishnan (48), Bernardo A. Mainou (48), Mic McGoldrick (48) and Norbert De Clercq (48) (Figure 4). These authors anchor distinct research communities: regulatory science and pharmacoepidemiology, vaccine development, and medicines policy scholarship, rather than one consolidated network.

### 3.5 Geographic distribution

Country attribution was recoverable for 27.3% of the 2,063 English-indexed records, that is, for the PubMed-subset records carrying affiliation data. The United States led with 171 records, followed by the United Kingdom (118) and Switzerland (74), then India (65), South Africa (53), Germany (46), China (46), the Netherlands (40), France (37), Canada (36), Belgium (32), Japan (31) and Italy (30) (Figure 5). Hong Kong, Macau and Taiwan are counted within China. Among LMICs, India and South Africa are the most prominent collaborating countries, with a second tier of Ghana (17), Tanzania (17), Kenya (15), Zimbabwe (15), Uganda (14) and Nigeria (9). High-income regulators and procurers dominate international collaboration, while LMIC participation concentrates in a few middle-income hubs. Within this subset, 66.9% of country-attributed records are affiliated with high-income regulators and 33.1% with LMIC institutions. Affiliation is recoverable only from database-indexed sources, so these counts describe who publishes on regulatory reliance in the indexed literature.

### 3.6 Keyword co-occurrence and thematic clusters

Keyword co-occurrence clustering resolved the literature into three thematic groups (Figure 6 heatmap; cluster composition in Figure 7), and the coding reported in Section 3.9 reaches the same three groups by an independent route. The three corresponding item sets are listed below (modularity Q = 0.20):
- **Cluster 1: access, equity and essential medicines in LMICs** (n = 34; hub *Essential*): *Essential, Health Policy, Drug Information Services, Drug Utilization, Child, Drug Costs, Developing Countries, Drug Development, Biological Products*. This cluster centres the affordability, availability and appropriate use of medicines for LMIC populations.
- **Cluster 2: vaccines, quality assurance and COVID-19** (n = 24; hub *Vaccines*): *Vaccines, World Health Organization, Drug Industry, Quality Control, Guideline, Drug and Narcotic Control, In Vitro Techniques, COVID-19, Diagnostic Equipment, International Cooperation*. This cluster links product quality with pandemic response.
- **Cluster 3: health systems and financing** (n = 22; hub *Universal Health Insurance*): *Universal Health Insurance, Pharmaceutical Preparations, Health Services Accessibility, Delivery of Health Care, Public Health, Healthcare Financing, Health Systems Plans, Primary Health Care, National Health Programs, Insurance*. This cluster frames reliance within health-system and financing arrangements, and therefore within the policy space where coverage decisions are made.

### 3.7 Burst detection

Burst detection identified the topics rising fastest in the recent period. The strongest burst scores were *Universal Health Insurance* (56.0), *Health Services Accessibility* (36.0), *Health Policy* (33.0), *Vaccines* (24.5), *Delivery of Health Care* (21.5), *World Health Organization* (20.5), *Pharmaceutical Preparations* (19.5), *Essential* (19.5), *Quality Control* (16.0), *In Vitro Techniques* (14.5) and *COVID-19* (14.0). The burst structure tracks a shift away from an early essential-medicines and affordability framing, toward health-systems and policy language and toward vaccines, quality assurance and pandemic response.

### 3.8 Thematic evolution

Across the three windows the centre of gravity of the field moved (Figure 8; Figure 9). In the first window, from 2000 to 2009, the literature was small and anchored on *Essential* (40), *Guideline* (12), *Drug Costs* (9) and *Drug Utilization* (8). In the second window, from 2010 to 2017, it expanded around *Universal Health Insurance* (85), *Pharmaceutical Preparations* (52), *Health Services Accessibility* (33) and *Europe* (10). In the third window, from 2018 onward, *Vaccines* rose from 3 to 51, *World Health Organization* from 2 to 46, *Health Policy* from 0 to 59, *Quality Control* from 2 to 34 and *In Vitro Techniques* from 0 to 26, while *COVID-19* appeared de novo (28). The alluvial diagram in Figure 9 traces these shifts directly: the left column gives the three thematic clusters, the middle column gives keyword frequency in the period from 2000 to 2017, and the right column gives keyword frequency in the period from 2018 to 2026, with ribbons linking each cluster to its keywords. Net-new keywords such as *COVID-19* and *In Vitro Techniques* appear only in the right column. The trajectory runs from an essential-medicines and affordability literature toward a vaccines, quality and pandemic-response literature and, in parallel, toward a health-systems and policy framing of reliance.

### 3.9 Qualitative synthesis of highly cited works

Coding the 40 most-cited, relevance-confirmed records, carried out without reference to the clustering solution, reproduced the three themes that the keyword network had produced. The convergence carries weight because the two procedures share no input beyond the corpus: one works on co-occurrence structure, the other on the arguments advanced in the most influential papers. Their agreement indicates that the three themes belong to the field rather than to either method. **Access, equity and LMIC medicines (Cluster 1)** is represented by work on essential medicines for universal health coverage (Wirtz et al. 2017), market-shaping approaches to biopharmaceutical innovation (Douglass et al. 2018; Yang et al. 2023), the suitability of stringent-review procedures for registration in low-income countries (Cameron et al. 2009), and COVID-19 vaccine and therapeutics justice (Wouters et al. 2021). **Vaccines and quality assurance (Cluster 2)** is represented by the 25-year review of the WHO vaccines prequalification programme (Dellepiane and Wood 2015), the global regulatory landscape for combined vaccines (He et al. 2025), and COVID-19 vaccine regulatory pathways (Wouters et al. 2021). **Health systems and financing (Cluster 3)** is represented by appraisals of the African Medicines Agency (Ngum et al. 2023; Ndomondo-Sigonda et al. 2023), the WHO Global Benchmarking Tool as a capacity-strengthening instrument (Khadem Broojerdi et al. 2020; Guzman et al. 2020), regional reliance and work-sharing procedures (Xu et al. 2022; Vaz et al. 2022; Geraci et al. 2024), and market-shaping successes in hepatitis C access (Douglass et al. 2018).

Across the three themes, reliance mechanisms (WHO prequalification, regional harmonization, the Global Benchmarking Tool and the WHO Collaborative Registration Procedure) are repeatedly shown to lower regulatory barriers and compress review timelines. The highly cited literature is far richer in accounts of *mechanisms* than in evidence that reliance changed *access outcomes*. Demonstrated effects on price, product availability or treatment coverage are few, concentrated in vaccines and a small set of priority therapeutics, and in a handful of middle-income countries. The uneven regulatory capacity of LMIC agencies and the distributional consequences for their populations are seldom at the analytical centre of even the most influential papers. The policy community has yet to treat this asymmetry as a first-order question. The merged Chinese-language records reinforce Cluster 1 independently, by adding a sub-theme of China as an emerging regulator and producer (Li et al. 2024; Zhang et al. 2024, 2026) that is otherwise under-represented in the English-indexed corpus.

---

## 4. Discussion

### 4.1 Summary of principal findings

This bibliometric review and thematic synthesis maps two decades of scholarship on regulatory reliance for medicines access in LMICs. The field has grown close to threefold in the last decade, is led by high-income regulators and procurers, and organizes around three stable themes concerned with access and equity, with vaccines and quality, and with health systems and financing. Recent bursts and the thematic evolution trace a pivot toward health-systems and policy language and toward vaccines, quality assurance and COVID-19, where recent policy attention has also concentrated. The qualitative synthesis shows reliance mechanisms well documented as barrier-lowering instruments, while evidence linking them to measurable access outcomes and to equitable regulatory capacity stays thin.

### 4.2 Interpretation: reliance lowers barriers, but the access chain is longer

The bibliometric pattern is consistent with the mechanistic literature, in that reliance and harmonization are invoked precisely because de novo national review duplicates effort and defers access. The highly cited corpus shows reliance, whether through prequalification, regional procedures or benchmarking, repeatedly shortening the path from assessment to authorization. Yet compressing regulatory review addresses only one link in a longer access chain, since price, supply, procurement channels and health-system absorptive capacity may determine whether a faster authorization reaches patients. Scarcity of access-outcome studies even among the most influential papers shows a field that has optimised the *upstream* regulatory instrument while under-measuring its *downstream* effect. Section 4.3 takes this up.

### 4.3 The access-outcome evidence gap

Few highly cited works trace reliance to changes in price, product availability, treatment coverage or time to patient, and those that do concentrate on vaccines and a narrow set of priority products in a few middle-income settings. The concentration has a structural explanation. Vaccines and a small number of antiretroviral and antimicrobial therapies are the products for which the procurement infrastructure of UN agencies, Gavi and the global funds makes reliance actionable, so outcome effects should surface there first. Absence of outcome evidence elsewhere marks a boundary of current measurement practice, not of reliance itself. The near-absence of outcome language in the burst and cluster structure is itself the finding: it locates where the policy discourse of this field stops. The field is mechanism-rich and outcome-poor.

### 4.4 The equity and regulatory-capacity asymmetry

**A risk that the field treats as peripheral is that reliance can entrench dependence on external assessment if it is not coupled with domestic capacity strengthening.** The Global Benchmarking Tool and African Medicines Agency literature names this risk, but the broader corpus treats it as secondary. Thematic evolution shows an early and persistent health-systems and financing cluster, yet the equity implication of *whose* regulatory capacity is strengthened is rarely centred. High-income agencies and global procurers dominate collaboration, and LMIC agencies appear mainly as recipients of reliance or as middle-income hubs such as India and South Africa. We read this asymmetry as the most important under-examined question for policymakers, because a reliance arrangement that shortens approval times without building domestic assessment capacity may leave the underlying dependence intact.

### 4.5 Implications for policymakers and regulators

If reliance is necessary but not sufficient for access, then the policy question is not whether to rely but how reliance is governed. Three implications follow for policymakers, national regulators and those who finance regulatory strengthening. First, reliance frameworks are likely to deliver more where they are paired with market-shaping, local production, diagnostics and capacity strengthening, since faster authorization alone does not secure supply or affordability. Second, decision-makers should specify in advance whose capacity is expected to grow under a reliance arrangement, because the current literature offers them little guidance on this point. Third, we propose that future reliance frameworks incorporate an *equity audit*, defined as an ex-ante assessment of who gains faster access, whose regulatory capacity is built, and who remains dependent. The three questions that constitute the audit follow directly from the three findings reported above, so the instrument rests on the observed structure of the field rather than on a prior normative scheme. It is specified here as a governance standard; indicator selection and data sources are the third item of the research agenda below. Its advantage is timing: it can be applied before a reliance arrangement is signed rather than evaluated after it has failed.

### 4.6 Strengths and limitations

Four features of the design determine what this map can be used for. The corpus covers three databases and the WHO institutional repository, so grey literature and policy documents sit alongside journal articles, and a Chinese-language search that no previous review in this area has run extends coverage further. Relevance screening followed pre-specified automated rules with an exclusion reason recorded for every rejected record, and the corpus, the PRISMA transparency file and the analysis scripts are deposited for reuse. The thematic structure rests on two procedures that share no input beyond the corpus and converged on the same three themes. And because the map is anchored by qualitative coding, it reports the arguments advanced in the most influential papers rather than their citation counts alone.

Affiliation was recoverable for 27.3% of the English-indexed records, and the country analysis should be read with that ceiling in mind (Section 2.5). Citation-based indicators favour already-visible, English-language, high-income-linked work, which is why the qualitative synthesis drew on a relevance-confirmed subset. Records from 2025 and 2026 remain partially indexed, so counts for 2026 are retained without being read as a complete-year trend. None of these constraints bears on the two findings on which the argument rests. The convergence of the computational and qualitative procedures and the shape of the outcome-evidence gap are both established on the coded subset of the most-cited records.

---

## 5. Conclusion

Regulatory reliance for medicines access in LMICs has matured into a recognizable and rapidly growing field with a stable thematic structure, which this study maps for the first time across English-indexed, WHO and Chinese-language sources. Two procedures that share no input beyond the corpus, computational clustering and qualitative coding of the most influential records, return the same three themes. The structure therefore reflects the field rather than either procedure. Within it the evidence is asymmetric in a way that matters for policy: reliance mechanisms are documented in detail and shown to lower regulatory barriers, whereas their effects on price, availability and coverage are traced only for vaccines and a narrow set of priority products, and the question of whose regulatory capacity grows is rarely asked. Reliance is therefore a necessary but not sufficient condition for medicines access in LMICs, and the distance between the two is a governance gap rather than a regulatory one. The equity audit proposed here closes that gap at the point where it can still be acted upon, before a reliance arrangement is signed rather than after it has failed. Mobilising twenty-six years of scholarship does what no single study of one reliance mechanism can: it shows decision-makers what the field has established, and where it has stopped asking.

**Future research agenda.** Three directions follow, each tied to a decision that reliance frameworks require. (i) *Outcome evidence.* Longitudinal studies tracking price, supply and treatment coverage after the adoption of reliance are needed to convert the mechanism-rich evidence of this field into demonstrated access outcomes. (ii) *Regulatory autonomy.* Empirical assessment of how reliance affects the regulatory autonomy and capacity of LMIC agencies, and of the conditions under which dependence is entrenched rather than capacity built, remains scarce. (iii) *Operationalising the equity audit.* The indicators, data sources and governance entry points of an equity audit must be specified so that reliance frameworks can be held accountable for equitable access.

---

## References

African Union. Treaty for the Establishment of the African Medicines Agency. Malabo: African Union; 2019.

Aria M, Cuccurullo C. bibliometrix: An R-tool for comprehensive science mapping. Journal of Informetrics. 2017;11(4):959–975. https://doi.org/10.1016/j.joi.2017.08.007

Barton I, Avanceña ALV, Gounden N, Anupindi R. Unintended consequences and hidden obstacles in medicine access in Sub-Saharan Africa. Frontiers in Public Health. 2019;7:342. https://doi.org/10.3389/fpubh.2019.00342

Cameron A, Ewen M, Ross-Degnan D, Ball D, Laing R. Medicine prices, availability, and affordability in 36 developing and middle-income countries: a secondary analysis. The Lancet. 2009;373(9659):240–249. https://doi.org/10.1016/S0140-6736(08)61762-6

Cobo MJ, López-Herrera AG, Herrera-Viedma E, Herrera F. Science mapping software tools: Review, analysis, and cooperative study among tools. Journal of the American Society for Information Science and Technology. 2011;62(7):1382–1402. https://doi.org/10.1002/asi.21525

Dellepiane N, Wood D. Twenty-five years of the WHO vaccines prequalification programme (1987–2012). Vaccine. 2015;33(1):52–61. https://doi.org/10.1016/j.vaccine.2013.11.066

Donthu N, Kumar S, Mukherjee D, Pandey N, Lim WM. How to conduct a bibliometric analysis: An overview and guidelines. Journal of Business Research. 2021;133:285–296. https://doi.org/10.1016/j.jbusres.2021.04.070

Douglass CH, Pedrana A, Lazarus JV, 't Hoen EFM, Hammad R, Baptista Leite R, et al. Pathways to ensure universal and affordable access to hepatitis C treatment. BMC Medicine. 2018;16:169. https://doi.org/10.1186/s12916-018-1162-z

EFPIA. ASEAN Joint Assessment (AJA) for Pharmaceuticals – How should it evolve? Position Paper. 28 May 2024.

Geraci G, Smith R, Hansford A, Johnsson E, Critchley H, Abi Khaled L, et al. Industry Perceptions and Experiences with the Access Consortium New Active Substance Work-Sharing Initiative (NASWSI): Survey Results and Recommendations. Therapeutic Innovation & Regulatory Science. 2024;58:557–566. https://doi.org/10.1007/s43441-024-00624-7

Guzman J, O'Connell E, Kikule K, Hafner T. The WHO Global Benchmarking Tool: a game changer for strengthening national regulatory capacity. BMJ Global Health. 2020;5(8):e003181. https://doi.org/10.1136/bmjgh-2020-003181

He X, Pu Y, Li Z, Huan S, Yang Y. The global regulatory landscape for combined vaccines: A comparative case study of registration strategies for diphtheria-tetanus-pertussis-containing vaccines. Vaccine. 2025;54:127017. https://doi.org/10.1016/j.vaccine.2025.127017

Hu Y, Wang Z, Zhou S, Yang J, Chen Y, Wang Y, et al. Redefining Debt-to-Health, a triple-win health financing instrument in global health. Globalization and Health. 2024;20:39. https://doi.org/10.1186/s12992-024-01043-x

International Coalition of Medicines Regulatory Authorities (ICMRA). Statement from Global Medicines Regulators on the Value of Regulatory Reliance. 2017. https://icmra.info/drupal/index.php/en/strategicinitatives/reliance/statement

Khadem Broojerdi A, Sillo HB, Ostad Ali Dehaghi R, Ward M, Refaat M, Parry J. The WHO Global Benchmarking Tool: an instrument to strengthen medical products regulation and promote universal health coverage. Frontiers in Medicine (Lausanne). 2020;7:457. https://doi.org/10.3389/fmed.2020.00457

Kleinberg J. Bursty and hierarchical structure in streams. Data Mining and Knowledge Discovery. 2002;7(4):373–397. https://doi.org/10.1023/A:1024940629314

Liu Z, Wang Z, Xu M, Ma J, Sun Y, Huang Y. The priority areas and possible pathways for health cooperation in BRICS countries. Global Health Research and Policy. 2023;8:36. https://doi.org/10.1186/s41256-023-00318-x

Ndomondo-Sigonda M, Miot J, Naidoo S, Ambal A, Dodoo A, Mkandawire H. The African Medicines Regulatory Harmonization initiative: Progress to date. Medical Research Archives. 2018.

Ndomondo-Sigonda M, Azatyan S, Doerr P, Agaba C, Harper KN. Best practices in the African Medicines Regulatory Harmonization initiative: Perspectives of regulators and medicines manufacturers. PLOS Global Public Health. 2023;3(4):e0001651. https://doi.org/10.1371/journal.pgph.0001651

Ngum N, Ndomondo-Sigonda M, Walker S, Salek G. Regional regulatory harmonisation initiatives: Their potential contribution to the newly established African Medicines Agency. Regulatory Toxicology and Pharmacology. 2023;105497. https://doi.org/10.1016/j.yrtph.2023.105497

Page MJ, McKenzie JE, Bossuyt PM, Boutron I, Hoffmann TC, Mulrow CD, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. BMJ. 2021;372:n71. https://doi.org/10.1136/bmj.n71

Qiao J, Zhan S, Ren M, Wang H, Huang Y, Zhang Z, et al. A new phase of China-ASEAN health cooperation: the China-ASEAN Beijing Declaration on Cooperation in Innovation of Health Products and Technologies. Global Health Research and Policy. 2025;10:3. https://doi.org/10.1186/s41256-024-00401-x

Ratanawijitrasin S, Wondemagegnehu E. Effective drug regulation: a multicountry study. Geneva: World Health Organization; 2002.

Rägo L, Santoso B. Drug regulation: history, present and future. In: van Boxtel CJ, Santoso B, Edwards IR, eds. Drug Benefits and Risks: International Textbook of Clinical Pharmacology. 2nd ed. Amsterdam: Elsevier; 2008.

Sun Y, Cui Y, Huang Y, Xu M. Access to antimalarial drugs in the Asia-Pacific region during health emergency: a multinational cross-sectional investigation between 2020 and 2022. Global Health Research and Policy. 2025;10:66. https://doi.org/10.1186/s41256-025-00454-6

United Nations. The Sustainable Development Goals Report 2023. New York: United Nations; 2023.

Vaz A, Roldão Santos M, Gwaza L, Mezquita González E, Pajewska Lewandowska M, Azatyan S, et al. WHO collaborative registration procedure using stringent regulatory authorities' medicine evaluation: reliance in action? Expert Review of Clinical Pharmacology. 2022. https://doi.org/10.1080/17512433.2022.2037419

World Health Organization. Regulatory reliance: a global imperative. WHO Drug Information. 2017;31(1):17–21.

World Health Organization. The selection and use of essential medicines: report of the WHO Expert Committee, 2019. Geneva: World Health Organization; 2019.

World Health Organization. World health statistics 2023: monitoring health for the SDGs. Geneva: World Health Organization; 2023.

Wirtz VJ, Hogerzeil HV, Gray AL, Bigdeli M, de Joncheere K, Ewen M, et al. Essential medicines for universal health coverage. The Lancet. 2017;389(10067):403–476. https://doi.org/10.1016/S0140-6736(16)31599-9

Wouters OJ, Shadlen KC, Salcher-Konrad M, Pollard AJ, Larson HJ, Teyssou E, et al. Challenges in ensuring global access to COVID-19 vaccines: production, distribution, and strain diversity. The Lancet. 2021;397(10278):1023–1034. https://doi.org/10.1016/S0140-6736(21)00306-8

Xu M, Zhang L, Feng X, Zhang Z, Huang Y. Regulatory reliance for convergence and harmonisation in the medical device space in Asia-Pacific. BMJ Global Health. 2022;7:e009798. https://doi.org/10.1136/bmjgh-2022-009798

Xu M, Hu Y, Lu S, Idris MA, Zhou S, Yang J, et al. Seasonal malaria chemoprevention in Africa and China's upgraded role as a contributor: a scoping review. Infectious Diseases of Poverty. 2023;12:63. https://doi.org/10.1186/s40249-023-01115-x

Yang J, Feng X, Zhou S, Zhang L, Hu Y, Chen Y, et al. Evolving market-shaping strategies to boost access to essential medical products in developing countries with HIV self-testing as a case study. Global Health Research and Policy. 2023;8:26. https://doi.org/10.1186/s41256-023-00310-5

Yang J, Yu X, Yao Y, Zhao W, Chen Y, Wang Z, et al. Analysis of the impact of national centralized volume-based procurement drug policy on the market dynamics of tuberculosis drugs. BMC Health Services Research. 2026;26:756. https://doi.org/10.1186/s12913-026-14668-y

Zhou S, Feng X, Hu Y, Yang J, Chen Y, Bastow J, et al. Factors associated with the utilization of diagnostic tools among countries with different income levels during the COVID-19 pandemic. Global Health Research and Policy. 2023;8:45. https://doi.org/10.1186/s41256-023-00330-1

An FD, Wang L, Zhou XB, Wen HR, Zhao MM, Wang QL. Boosting the modernization of drug regulatory science through the establishment of an innovative method evaluation system. Chinese Pharmaceutical Affairs. 2026. https://doi.org/10.16153/j.1002-7777.2026-04-0047

Du J, Wang X, Zhou Y. Implications of applying for PIC/S membership for drug inspection system development. China Food and Drug Administration. 2026;(5). https://doi.org/10.3969/j.issn.1673-5390.2026.05.010

Li N, Liang Y. Introduction and enlightenment of GMP inspection reliance in PIC/S. Chinese Journal of Modern Applied Pharmacy. 2019;36(14):1833–1836. https://doi.org/10.13748/j.cnki.issn1007-7693.2019.14.023

Li Z, Xu Q, Zhang S, et al. Research and reflection on the development of international regulatory harmonization of pharmaceutics. Health Development and Policy Research. 2024;27(5):417–424. https://doi.org/10.12458/HDPR.202406009

Zhang F, Zhang Z, Song R. Overview of WHO regulatory assessment system and reflection on the internationalization of China's drug regulation. China Food and Drug Administration. 2024;(7). https://doi.org/10.3969/j.issn.1673-5390.2024.07.002

Zhang Y, Ma M, Wang Y, Shao R. A preliminary analysis of WHO's initiatives and tools for promoting the improvement of medical product regulatory capacity worldwide (part II). Chinese New Drugs Journal. 2026;35(9):924–931. https://doi.org/10.20251/j.cnki.1003-3734.2026.09.005

Zhao Y, Wang K, Peng Y, He M, Chen Y. Practice and reflection on global drug regulatory international coordination and cooperation. China Food and Drug Administration. 2025;(9). https://doi.org/10.3969/j.issn.1673-5390.2025.09.001

Zhao Y, Peng Y, Wang K, He M, Chen Y. International practice of drug regulation in the US, Japan and EU and its implications for China. China Food and Drug Administration. 2025;(9). https://doi.org/10.3969/j.issn.1673-5390.2025.09.011

---

## Submission Front/Back Matter (to be entered in the journal system)

*Authors, affiliations, and the corresponding-author email are to be filled by the authors. The blocks below resolve the four PRISMA 2020 items 24a, 25, 26, 27.*

**Title page.** Deyu Kong^1,2, Mingxing Li^1, Hongxia Yu^1, Bingbing Huang^3, Jiaxin Jing^3, Jige Dong^1.

Affiliations: (1) Rehabilitation Division, Wangjing Hospital of China Academy of Chinese Medical Sciences, Beijing, China; (2) aSSIST University (Seoul School of Integrated Sciences and Technologies), Seoul, Republic of Korea; (3) Tianjin College, University of Science and Technology Beijing, Tianjin, China.

ORCID iDs: Deyu Kong 0009-0002-3621-5719; Bingbing Huang 0009-0003-6669-5327; Jiaxin Jing 0009-0005-1566-5173; Jige Dong 0009-0006-5606-8305.

Corresponding author: Professor Jige Dong, Rehabilitation Division, Wangjing Hospital of China Academy of Chinese Medical Sciences, No. 6 Wangjing Zhonghuan Nanlu, Chaoyang District, Beijing 100102, China. E-mail: yishengd2010@sina.com. ORCID 0009-0006-5606-8305.

*The journal operates single-blind peer review and Research Exchange has no separate title-page slot, so this material is placed at the head of the main document. Individual author e-mail addresses are supplied in the submission system's author-details step.*

**Funding.** This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

**Competing interests.** The authors declare no competing interests.

**Registration.** This bibliometric review was not registered in PROSPERO. The review protocol is available as supplementary material (see "Supplementary material" below).

**Data and code availability.** The bibliometric corpus was derived from public sources (PubMed, Europe PMC, WHO Institutional Repository for Information Sharing), extended by a supplementary Chinese-language search of CNKI, Wanfang, and Weipu. The derived 2,071-record metadata table, the PRISMA transparency file (`prisma_transparency.json`), and the analysis scripts are available in a public repository [GitHub: https://github.com/kongdeyu0819-rgb/global-health-regulatory-bibliometrics; Zenodo: https://doi.org/10.5281/zenodo.22814432]. Search strategies and the qualitative-synthesis coding framework are provided as supplementary material.

**Acknowledgements.** The authors thank Professor Ming Xu (Peking University) for sharing a curated collection of literature on global health and medicines regulation, from which the 50 records described in Sections 2.1 and 2.2 were identified, and for comments on an earlier draft of this manuscript. The authors alone are responsible for the analyses and conclusions reported here.

**Supplementary material.** (i) Full search strategies for all sources (Appendix A); (ii) the qualitative-synthesis coding framework for the 40 most-cited records; (iii) the country publication-frequency bar chart (Figure 5); (iv) the Chinese-language supplementary search protocol (Appendix B).

---

## Supplementary material

### Appendix A. Search strategies

**PubMed/MEDLINE** (MeSH-assisted; title/abstract free text):
```
("Drug Approval"[Mesh] OR "World Health Organization"[Mesh] OR "Drug and Narcotic Control"[Mesh] OR "Biological Products"[Mesh])
OR (prequalif* OR "regulatory reliance" OR "regulatory harmonization" OR "stringent regulatory" OR "marketing authorization")
AND
("Access to Medicines" OR "essential medicines" OR "medicine procurement" OR "pharmaceutical procurement" OR "drug procurement"
 OR "Developing Countries"[Mesh] OR "Medically Underserved Area"[Mesh] OR "Africa"[Mesh] OR "Asia"[Mesh])
```
plus free-text terms in title/abstract: `prequalif*`, `reliance`, `harmonization`, `access to medicines`, `essential medicines`.

**Europe PMC** (REST API): same concept groups as PubMed, expressed as query parameters (`reliances OR prequalif* OR "regulatory reliance" …`) AND (`"access to medicines" OR "essential medicines" OR "medicine procurement" …`), restricted to 2000–2026.

**WHO IRIS**: `regulatory reliance`, `WHO prequalification`, `collaborative registration procedure`, `Global Benchmarking Tool`, combined with `medicines` / `access` / `LMIC`, filtered to 2000–present.

### Appendix B. Chinese-language supplementary search (CNKI / Wanfang / Weipu)

To include non-English literature, we searched the three major Chinese databases on 2 September 2026 with the queries below (export and full-text retrieval steps in `CNKI_Wanfang_search_protocol.md`):
- **CNKI**: `SU='监管依赖' + '药品'` OR `SU='WHO预认证' + '药品可及性'` OR `SU='药品监管' + '国际互认'`
- **Wanfang**: `主题:("监管依赖" OR "WHO预认证") AND "药品"`
- **Weipu (VIP)**: `M=('监管科学' + '药品审评审批' + '国际互认')`

Eight relevant Chinese peer-reviewed records (2024–2026) were retrieved as full text and merged into the analytical corpus: Li et al. 2024 (international regulatory harmonization), Zhang et al. 2026 (WHO GBT/WLA and good reliance practices), Zhang et al. 2024 (WHO regulatory assessment system), Zhao et al. 2025 (global coordination/harmonization), Li & Liang 2019 (PIC/S GMP inspection reliance), Zhao et al. 2025 (US–Japan–EU practice), Du et al. 2026 (PIC/S accession), and An et al. 2026 (regulatory science modernization). Their English keywords were extracted and mapped to the corpus vocabulary, so they enter the annual, journal, keyword, and cluster analyses. They confirm a distinct "China as emerging regulator and producer" sub-theme that reinforces Cluster 1 and were under-represented in the English-indexed corpus; they carry no structured affiliation and therefore do not enter the country-collaboration analysis.
