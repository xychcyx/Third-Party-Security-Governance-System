# Third-Party Security Governance System

English | [繁體中文](#繁體中文)

A learning project that applies Python and data analysis to third-party
security governance. It uses audit, certificate, training, incident, asset,
and baseline data to produce vendor risk assessments and security reports.

This project is inspired by a third-party security governance framework used
in a telecommunications environment. It is a standalone demonstration, not a
production system.

For the project motivation, design decisions, and development process, see
[Project Context and Development Notes](docs/project-context.md).

## What it does

- Summarizes audit results, certificate validity, training activity, and
    protection-baseline compliance.
- Combines governance data into vendor risk levels and recommended actions.
- Retrieves recent HIGH and CRITICAL CVEs from the [NVD](https://nvd.nist.gov/)  API.
- Matches CVE descriptions with SBOM components and equipment inventories.
- Exports CSV reports and PNG charts to `report/`.

## Modules

| File | Description |
| --- | --- |
| `src/A-analysis_dashboard.py` | Builds the analysis dashboard reports and charts. |
| `src/B-vendor_risk_assessment.py` | Calculates vendor risk profiles and incident summaries. |
| `src/C1-cve_fetch.py` | Fetches recent CVEs from the [NVD](https://nvd.nist.gov/)  API and saves `10-CVE清單.csv`. |
| `src/C2-cve_matching.py` | Matches CVEs with third-party components and equipment. |

## How it works

```text
Governance data ──> [A] Dashboard ──────────> Compliance reports
      │
      └──────────> [B] Vendor risk ─────────> Risk reports

NVD API ──────────> [C1] CVE list ──────────> [C2] Match inventory
                                         │
                                         └──> Vulnerability reports
```

The first path turns governance data into dashboards and vendor risk reports.
The second path compares recent CVEs with components and equipment, then
produces vulnerability reports.

## Reports

Generated files are grouped by purpose:

```text
report/
├── A. Vendor Security Analysis Report/
│   ├── CSV summaries
│   └── chart/
├── B. Vendor Risk Assessment Report/
│   ├── 廠商綜合資安評估總表.csv
│   ├── 廠商事故通報統計.csv
│   └── 事故通報紀錄表.csv
└── C. Vulnerability Management Report/
    ├── 第三方元件漏洞分析.csv
    └── 設備漏洞分析.csv
```

## Requirements

- Python 3.10 or later
- The packages listed in `requirements.txt`

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Quick start

Run commands from the project root:

```bash
# Build compliance summaries and charts
python src/A-analysis_dashboard.py

# Build vendor risk and incident reports
python src/B-vendor_risk_assessment.py

# Refresh the CVE list from NVD
python src/C1-cve_fetch.py

# Match CVEs with components and equipment
python src/C2-cve_matching.py
```

`src/C1-cve_fetch.py` requires an internet connection. Run it before
`src/C2-cve_matching.py` whenever the
CVE list needs to be refreshed.

## Built with

- [pandas](https://pandas.pydata.org/) for CSV processing, aggregation, and
    report generation
- [NumPy](https://numpy.org/) for conditional risk classification
- [Matplotlib](https://matplotlib.org/) for dashboard charts
- [Requests](https://requests.readthedocs.io/) for [NVD](https://nvd.nist.gov/)  API access

## Project layout

```text
.
├── data/          Source CSV files and the CVE list
├── report/        Generated reports and charts
├── src/
│   ├── A-analysis_dashboard.py
│   ├── B-vendor_risk_assessment.py
│   ├── C1-cve_fetch.py
│   ├── C2-cve_matching.py
│   └── project_paths.py
├── requirements.txt
└── readme.md
```

## 繁體中文

這是一個以 Python 建立的第三方資安治理分析練習專案。程式讀取稽核、
證照、教育訓練、事故、設備與系統防護基準等 CSV 資料，產生廠商風險評估、
合規摘要、漏洞比對報告與圖表。

專案分為四個模組：

- `src/A-analysis_dashboard.py`：產生分析儀表板報表與圖表。
- `src/B-vendor_risk_assessment.py`：計算廠商風險等級、改善建議與事故摘要。
- `src/C1-cve_fetch.py`：從 [NVD](https://nvd.nist.gov/)  API 擷取 HIGH／CRITICAL CVE。
- `src/C2-cve_matching.py`：將 CVE 與第三方元件及設備清單進行比對。

這是學習與展示用途的獨立專案，並非正式上線系統。

## Contact

Jeanie Hsu - sheisyucheng@gmail.com