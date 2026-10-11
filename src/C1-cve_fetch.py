import requests
import pandas as pd
from datetime import datetime, timedelta
from project_paths import DATA_DIR

def fetch_data(base_url):
    today = datetime.now()

    end_date = today - timedelta(days=14)
    start_date = end_date - timedelta(days=60)
    start_str = start_date.strftime("%Y-%m-%dT%H:%M:%S.000")
    end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S.000")

    params = {
        "pubStartDate": start_str,
        "pubEndDate": end_str,
        "resultsPerPage": 300,
        "startIndex": 0
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    return data["vulnerabilities"]

def save_data(vulnerabilities, filename):
    records = []

    for v in vulnerabilities:
        cve = v["cve"]
        desc = " ".join([x["value"] for x in cve["descriptions"] if x["lang"] == "en"])
        desc = desc.replace("\n", " ")
        desc = desc.replace(",", " ")
        metrics = cve["metrics"]
        if not "cvssMetricV40" in metrics and not "cvssMetricV31" in metrics:
            continue
        metricVersion = "cvssMetricV40" if "cvssMetricV40" in metrics else "cvssMetricV31"
        cvssData = metrics[metricVersion][0]["cvssData"]
        severity = cvssData["baseSeverity"]
        if severity != "CRITICAL" and severity != "HIGH":
            continue
        records.append({
            "CVE_ID": cve["id"],
            "CVSS_Score": cvssData["baseScore"],
            "Severity": severity,
            "Description": desc
        })

    df_cve = pd.DataFrame(records)
    df_cve.to_csv(DATA_DIR / filename, index=False)

def main():
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    vulnerabilities = fetch_data(base_url)
    save_data(vulnerabilities, "10-CVE清單.csv")
    
if __name__ == "__main__":
    main()