import pandas as pd
from project_paths import DATA_DIR, VULNERABILITY_REPORT_DIR

REPORT_DIR = VULNERABILITY_REPORT_DIR

def query_matches_in_cve(df_cve, keywords):
    mask = pd.Series(True, index=df_cve.index)
    for keyword in keywords:
        mask = mask & df_cve["Description_Lower"].str.contains(keyword.lower())
    return df_cve[mask].copy()

def merge_cve_back(df_cve, row, source_col):
    result = query_matches_in_cve(df_cve, row[source_col].split())
    critical_count = sum(result["Severity"] == "CRITICAL")
    
    if critical_count >= 2:
        result["建議期限"] = "3天內"
    else:
        result["建議期限"] = "14天內"
        result.loc[result["Severity"] == "HIGH", "建議期限"] = "60天內"
    
    for col in row.index[1:9]:
        result[col] = row[col]
    return result

def process_cve_matches(df_cve, df_source, query_col, filename):
    results = df_source.apply(lambda row: merge_cve_back(df_cve, row, query_col), axis=1)
    df_results = pd.concat(list(results))
    new_cols = list(df_source.columns[1:9]) + ["CVE_ID","CVSS_Score","Severity","Description","建議期限"]
    df_results = df_results[new_cols]
    df_results.to_csv(REPORT_DIR / filename, index=False)

def main():
    REPORT_DIR.mkdir(exist_ok=True, parents=True)

    df_cve = pd.read_csv(DATA_DIR / "10-CVE清單.csv")
    df_cve["Description_Lower"] = df_cve["Description"].str.lower()

    df_package = pd.read_csv(DATA_DIR / "8-第三方元件清單.csv")
    df_equipment = pd.read_csv(DATA_DIR / "9-設備清單.csv")

    process_cve_matches(df_cve, df_package, "元件名稱", "第三方元件漏洞分析.csv")
    process_cve_matches(df_cve, df_equipment, "設備型號", "設備漏洞分析.csv")

if __name__ == "__main__":
    main()