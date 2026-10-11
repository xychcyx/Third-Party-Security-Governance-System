# Project Context and Development Notes

This document explains why this project was built, how it was developed, and
what I learned from it. The main README remains focused on setup and usage.

## Motivation

Third-party suppliers are part of many organizations' security boundaries.
Their audit results, certificates, training records, incidents, software
components, and equipment inventories are often stored in separate files. That
makes it difficult to see which suppliers need attention first.

Inspired by the third-party security governance framework I designed for the
telecommunications company where I currently work, this project demonstrates
how analytical, monitoring, and reporting workflows can be implemented
programmatically. I built it to explore how a small Python system could connect
these inputs into a repeatable governance workflow. The implementation is an
independent learning project and does not contain production data or
production integrations.

## The problem

The project focuses on four practical questions:

1. How can governance data from different CSV files be combined into a
   supplier-level view?
2. How can simple, explainable rules classify supplier risk and suggest a
   follow-up action?
3. How can recently published HIGH and CRITICAL CVEs be compared with known
   software components and equipment?
4. How can the results be exported in a form that is easy to review?

The goal is not to replace a full governance platform. It is to build a small,
transparent reference implementation that makes the workflow concrete.

## Design approach

The project is divided into four focused modules:

- `A-analysis_dashboard.py` aggregates audit, certificate, training, and
  protection-baseline data into CSV summaries and PNG charts.
- `B-vendor_risk_assessment.py` combines governance indicators and incident
  history into supplier risk profiles.
- `C1-cve_fetch.py` retrieves CVE data from the NVD API, filters for HIGH and
  CRITICAL severity, and writes a local CVE list.
- `C2-cve_matching.py` searches CVE descriptions against SBOM component and
  equipment terms, then assigns suggested remediation deadlines.

Together, these modules form a realistic model of how Python can support
outsourced vendor management, supply-chain vulnerability monitoring, and
ISO 27001-aligned governance processes.

The modules communicate through files in `data/` and `report/`. This keeps the
intermediate results visible and makes each step easy to run and inspect on its
own. The scoring rules are deliberately explicit so that a reviewer can trace
why a supplier received a particular risk level.

## How I built it

I built the project incrementally:

1. Defined small CSV datasets for audits, certificates, training, incidents,
   protection baselines, components, equipment, and CVEs.
2. Used pandas to load, clean, group, and export the data.
3. Added NumPy conditional logic for risk classification and recommended
   actions.
4. Added Matplotlib charts for audit, certificate, and compliance summaries.
5. Added Requests and JSON parsing for NVD API retrieval.
6. Matched vulnerability descriptions with inventory terms and assigned
   remediation windows based on severity.
7. Reorganized the scripts under `src/`, added shared path handling, and
   documented the repeatable command-line workflow.

The project applies concepts from the University of Pennsylvania's
[Introduction to Programming with Python and Java Specialization](https://www.coursera.org/specializations/programming-python-java),
including Python programming, file I/O, data analysis, JSON parsing,
visualization, and modular design.

## What I learned

- Data processing becomes easier to review when input, transformation, and
  output responsibilities are separated.
- Risk rules should be simple enough to explain to a non-programmer.
- A report is more useful when it combines a summary with the underlying
  supplier or incident details.
- External API data needs normalization before it can be compared with local
  inventory data.
- Project structure and documentation are part of the engineering work, not
  an afterthought.

## Limitations and next steps

This is a reference side project rather than a production system. It currently
uses CSV files, keyword matching, and rule-based scoring. It does not provide
authentication, a database, scheduled execution, complete version-aware CVE
matching, or a web interface.

Possible next steps include:

- Add automated tests for scoring and CVE matching edge cases.
- Replace CSV storage with a database or a small data pipeline.
- Improve component matching with package identifiers and version ranges.
- Add configuration for risk thresholds and remediation deadlines.
- Add scheduled NVD updates and a browser-based report view.