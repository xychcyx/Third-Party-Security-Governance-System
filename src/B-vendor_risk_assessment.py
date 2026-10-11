import pandas as pd
import numpy as np
from project_paths import DATA_DIR, RISK_REPORT_DIR

REPORT_DIR = RISK_REPORT_DIR

def count_value(series, value):
    return int(series.eq(value).sum())

def percentage(value, total, digit = 0):
    if total == 0:
        return f"{0:.{digit}f}%"
    return f"{value / total * 100:.{digit}f}%"

def build_risk_report(filename):
    df_audit = pd.read_csv(DATA_DIR / "4-委外稽核紀錄.csv")
    df_baseline = pd.read_csv(DATA_DIR / "7-系統防護基準.csv").fillna("X")

    df_risk = df_audit[["委外廠商名稱"]].copy()

    df_risk["專案代碼"] = df_audit["Project Code_專案名稱"].apply(lambda x: x.split("_")[0])

    supplier_columns = df_baseline.columns[7:]
    statistics = pd.DataFrame({"防護等級": [column[-2] for column in supplier_columns]})
    df_risk["防護等級"] = statistics["防護等級"]
    df_risk["不符合項"] = df_audit["不符合數量"]

    df_cert = pd.read_csv(DATA_DIR / "5-證照清單.csv")
    df_risk["證照數"] = df_risk["委外廠商名稱"].apply(lambda x: count_value(df_cert["委外廠商名稱"], x))

    df_valid_cert = df_cert[df_cert["證書是否有效(Y/N)"] == "Y"]
    df_risk["有效證照"] = df_risk["委外廠商名稱"].apply(lambda x: count_value(df_valid_cert["委外廠商名稱"], x))

    df_training = pd.read_csv(DATA_DIR / "6-教育訓練.csv")
    df_risk["訓練人次"] = df_risk["委外廠商名稱"].apply(lambda x: count_value(df_training["委外廠商名稱"], x))

    df_training_sum = df_training.groupby("委外廠商名稱").agg(訓練時數=("訓練時數(小時)", "sum"))
    df_risk = df_risk.set_index("委外廠商名稱")
    df_risk["訓練時數"] = df_training_sum["訓練時數"]

    df_incident = pd.read_csv(DATA_DIR / "3-事故通報紀錄.csv")
    df_incident_count = df_incident.groupby("委外廠商名稱").agg(事故次數=("委外廠商名稱", len))
    df_risk["事故次數"] = df_incident_count["事故次數"]

    df_supplier = df_baseline[df_baseline.columns[7:]]
    df_match = df_supplier.apply(lambda series: count_value(series, "符合"))
    df_not_match = df_supplier.apply(lambda series: count_value(series, "不符合"))
    df_stats = pd.DataFrame([df_match, df_not_match], index=["符合", "不符合"])

    df_rate = df_stats.apply(lambda series: series["符合"] / (series["符合"] + series["不符合"]))
    df_risk.loc[["宏遠資訊股份有限公司", "捷通科技有限公司"], ["專案代碼", "防護等級"]]
    df_rate.index = df_risk.index
    df_risk["防護合規率"] = df_rate
    df_risk["證照有效率"] = df_risk["有效證照"] / df_risk["證照數"]

    conditions = [(df_risk["不符合項"] >= 3) | (df_risk["防護合規率"] < 0.85), (df_risk["不符合項"] >= 1) | (df_risk["防護合規率"] < 0.9)]
    choices = ["高風險", "中風險"]
    df_risk["風險等級"] = np.select(conditions, choices, default="低風險")

    conditions = [df_risk["風險等級"] == "高風險", df_risk["風險等級"] == "中風險", df_risk["風險等級"] == "低風險"]
    choices = ["優先改善", "持續追蹤", "維持現狀"]
    df_risk["建議"] = np.select(conditions, choices, default="維持現狀")
    df_risk["防護合規率"] = df_risk["防護合規率"].apply(lambda x: f"{x * 100:.1f}%")
    df_risk["證照有效率"] = df_risk["證照有效率"].apply(lambda x: f"{x * 100:.1f}%")

    df_risk.to_csv(REPORT_DIR / filename, index=True)

def build_incident_report(filename):
    df_incident = pd.read_csv(DATA_DIR / "3-事故通報紀錄.csv")
    df_incident_report = df_incident[["Project Code_專案名稱", "委外廠商名稱"]].copy()
    df_incident_report.columns = ["專案名稱", '廠商']
    df_incident_report["事故等級"] = df_incident["事故等級"]
    df_incident_report["事件主旨"] = df_incident["事件主旨"]

    df_incident["事故發生日期"] = pd.to_datetime(df_incident["事故發生日期"])
    df_incident["事故發現日期"] = pd.to_datetime(df_incident["事故發現日期"])
    df_incident["事故復原日期"] = pd.to_datetime(df_incident["事故復原日期"])
    df_incident["事故處理結案日"] = pd.to_datetime(df_incident["事故處理結案日"])

    df_incident_report["發生時間"] = df_incident["事故發生日期"]
    df_incident_report["發現分鐘數"] = df_incident["事故發現日期"] - df_incident["事故發生日期"]
    df_incident_report["發現分鐘數"] = df_incident_report["發現分鐘數"] // pd.Timedelta(minutes=1)
    df_incident_report["復原時間"] = df_incident["事故復原日期"]
    df_incident_report["復原小時數"] = df_incident["事故復原日期"] - df_incident["事故發現日期"]
    df_incident_report["結案日"] = df_incident["事故處理結案日"]
    df_incident_report["狀態"] = "已結案"
    df_incident_report.loc[df_incident_report["結案日"].isna(), "狀態"] = "未結案"
    df_incident_report["發現時間"] = df_incident["事故發現日期"]
    df_incident_report["結案天數"] = df_incident_report["結案日"] - df_incident_report["發現時間"]
    
    df_supplier_report = df_incident_report.groupby("廠商").agg(
        事故數=("專案名稱", len),
        已結案=("結案日", lambda series: series.notna().sum()),
        未結案=("結案日", lambda series: series.isna().sum()),
        平均發現分鐘數=("發現分鐘數", lambda series: series.mean()),
        平均復原小時數=("復原小時數", lambda series: series.mean()),
        平均結案天數=("結案天數", lambda series: series.mean()),
        最近事故日=("發現時間", lambda series: series.max())
    )

    df_supplier_report["平均復原小時數"] = df_supplier_report["平均復原小時數"].apply(lambda x: f"{x // pd.Timedelta(hours=1):02}:{x.components.minutes:02}:{x.components.seconds:02}")
    df_supplier_report.to_csv(REPORT_DIR / "廠商事故通報統計.csv", index=True)

    df_incident_report.drop(["發現時間", "結案天數"], axis=1, inplace=True)
    df_incident_report["發生時間"] = df_incident_report["發生時間"].dt.strftime("%Y/%m/%d %H:%M")
    df_incident_report["復原時間"] = df_incident_report["復原時間"].dt.strftime("%Y/%m/%d %H:%M")

    df_hour = df_incident_report["復原小時數"] // pd.Timedelta(hours=1)
    df_minute = (df_incident_report["復原小時數"] % pd.Timedelta(hours=1)) // pd.Timedelta(minutes=1)
    df_incident_report["復原小時數"] = df_hour.astype("str") + "h " + df_minute.astype("str") + "m"
    df_incident_report["發現分鐘數"] = df_incident_report["發現分鐘數"].astype("str") + "m"

    df_incident_report.to_csv(REPORT_DIR / "事故通報紀錄表.csv", index=False)


def main():
    REPORT_DIR.mkdir(exist_ok=True, parents=True)
    build_risk_report("廠商綜合資安評估總表.csv")
    build_incident_report("事故通報紀錄表.csv")

if __name__ == "__main__":
    main()