from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
REPORT_DIR = PROJECT_ROOT / "report"
DASHBOARD_REPORT_DIR = REPORT_DIR / "A. Vendor Security Analysis Report"
RISK_REPORT_DIR = REPORT_DIR / "B. Vendor Risk Assessment Report"
VULNERABILITY_REPORT_DIR = REPORT_DIR / "C. Vulnerability Management Report"