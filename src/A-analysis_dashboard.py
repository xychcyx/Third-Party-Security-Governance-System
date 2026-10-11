import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from project_paths import DATA_DIR, DASHBOARD_REPORT_DIR

plt.rcParams["font.sans-serif"] = "Microsoft JhengHei"

REPORT_DIR = DASHBOARD_REPORT_DIR

def read_data(filename):
    return pd.read_csv(DATA_DIR / filename)

def save_report(frame, filename, index = False):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    frame.to_csv(REPORT_DIR / filename, index=index)

def count_value(series, value):
    return int(series.eq(value).sum())

def percentage(value, total, digit = 0):
    if total == 0:
        return f"{0:.{digit}f}%"
    return f"{value / total * 100:.{digit}f}%"


def build_audit_report():

    audit = read_data("4-委外稽核紀錄.csv")
    result = audit["通過/限期改善"]

    pass_count = count_value(result, "通過")
    fail_count = count_value(result, "限期改善")

    p_pass = percentage(pass_count, len(audit))
    p_fail = percentage(fail_count, len(audit))

    summary = pd.DataFrame({
        "稽核結果": ["通過", "限期改善", "總不符合項目數"],
        "數量": [pass_count, fail_count, audit["不符合數量"].sum()],
        "百分比": [p_pass, p_fail, ""]
    })

    save_report(summary, "1-稽核結果統計.csv")

    by_project = audit.groupby("Project Code_專案名稱").agg(
        通過廠商數量=("通過/限期改善", lambda series: count_value(series, "通過")),
        限期改善廠商數量=("通過/限期改善", lambda series: count_value(series, "限期改善"))
    )

    save_report(by_project, "4-各專案廠商稽核結果.csv", True)

def build_cert_report():

    cert = read_data("5-證照清單.csv")
    status = cert["證書是否有效(Y/N)"]

    Y_count = count_value(status, "Y")
    N_count = count_value(status, "N")

    p_Y = percentage(Y_count, len(status))
    p_N = percentage(N_count, len(status))    

    summary = pd.DataFrame({
        "狀態": ["有效 (Y)", "失效 (N)", "總證照數"],
        "數量": [Y_count, N_count, len(status)],
        "百分比": [p_Y, p_N, ""]
    })

    save_report(summary, "2-證照有效性分析.csv")

    by_type = cert.groupby(["發證單位", "證照名稱"]).agg(
        證照數=("證書是否有效(Y/N)", len),
        有效數=("證書是否有效(Y/N)", lambda series: count_value(series, "Y"))
    )

    save_report(by_type, "5-證照類型分布.csv", True)

def build_training_report():

    training = read_data("6-教育訓練.csv")

    total_hr = f"{training["訓練時數(小時)"].sum():.1f}"
    avg_hr = f"{training["訓練時數(小時)"].sum() / len(training):.1f}"

    stats = pd.DataFrame({
        "指標": ["總訓練人次", "總訓練時數", "平均每人時數"],
        "數值": [len(training), total_hr, avg_hr],
        "單位": ["人次", "小時", "小時"]
    })

    save_report(stats, "3-教育訓練統計.csv")

    by_supplier = training.groupby(["委外廠商名稱", "訓練機構名稱"]).agg(
        訓練人次=("訓練時數(小時)", len),
        總時數=("訓練時數(小時)", "sum")
    )

    save_report(by_supplier, "6-教育訓練統計.csv", True)

def build_baseline_report():

    baseline = read_data("7-系統防護基準.csv")
    supplier = baseline[baseline.columns[7:]]

    match = supplier.apply(lambda series: count_value(series, "符合"))
    not_match = supplier.apply(lambda series: count_value(series, "不符合"))
    other = supplier.apply(lambda series: count_value(series, "不適用"))

    stats = pd.DataFrame([match, not_match, other], index=["符合", "不符合", "不適用"])

    rate = stats.apply(lambda series: percentage(series["符合"] / (series["符合"] + series["不符合"]), 1))
    level = stats.apply(lambda s: s.name[-2])

    summary = pd.DataFrame([level, match, not_match, other, rate], index=["防護等級", "符合", "不符合", "不適用", "合規率"])
    summary = summary.transpose()
    summary.index.name = "廠商名稱"

    save_report(summary, "7-系統防護基準合規分析.csv", True)
    return summary

def build_chart(baseline_summary):

    CHART_DIR = REPORT_DIR / "chart"
    CHART_DIR.mkdir(exist_ok=True, parents=True)

    def save_pie(labels, values, title, filename):
        plt.figure(figsize=(4,4), dpi=200)
        plt.pie(values, autopct=lambda x: f"{x:.0f}%", startangle=90, counterclock=False)
        plt.title(title)
        plt.legend(labels=labels, frameon=False, ncols=len(labels), loc="lower center", handlelength=0.7)
        plt.tight_layout()
        plt.savefig(CHART_DIR / filename)
        plt.close()

    audit = read_data("4-委外稽核紀錄.csv")
    result = audit["通過/限期改善"]

    pass_count = count_value(result, "通過")
    fail_count = count_value(result, "限期改善")

    labels = ["有效(Y)", "失效(N)"]
    values = [pass_count, fail_count]


    save_pie(labels, values, "稽核結果分布", "稽核結果分布.png")


    cert = read_data("5-證照清單.csv")
    status = cert["證書是否有效(Y/N)"]

    Y_count = count_value(status, "Y")
    N_count = count_value(status, "N")
    
    labels = ["有效(Y)", "失效(N)"]
    values = [Y_count, N_count]

    save_pie(labels, values, "證照有效性分布", "證照有效性分布.png")


    cert_counts = cert.groupby("證照名稱").agg(
        證照數=("證書是否有效(Y/N)", len),
        有效數=("證書是否有效(Y/N)", lambda series: count_value(series, "Y"))
    )

    labels = list(cert_counts.index)
    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(15, 6), dpi=200)
    plt.bar(x - width / 2, cert_counts["證照數"], width)
    plt.bar(x + width / 2, cert_counts["有效數"], width)
    plt.xticks(x, labels, rotation=45)
    plt.legend(labels=["證照數", "有效數"], frameon=False, ncols=len(labels), handlelength=0.7)
    plt.title("各發證單位證照數量與有效性", fontsize=30)
    plt.ylabel("證照數")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(CHART_DIR / "各發證單位證照數量與有效性.png")
    plt.close()


    baseline_summary["合規率"] = baseline_summary["合規率"].apply(lambda x: float(x[:-1]))

    average_rate = baseline_summary.groupby("防護等級").agg(
        平均合規率=("合規率", lambda s: s.sum() / len(s))
    )

    labels = list(average_rate.index)
    values = list(average_rate["平均合規率"])

    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(3, 4), dpi=200)
    bars = ax.bar(labels, values)
    ax.bar_label(bars, fmt='{:,.1f}%', padding=3)
    plt.xticks(x, labels)
    plt.title("各防護等級廠商平均合規率")
    plt.ylabel("合規率")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(CHART_DIR / "各防護等級廠商平均合規率.png")
    plt.close()


def main():
    build_audit_report()
    build_cert_report()
    build_training_report()
    baseline_summary = build_baseline_report()
    build_chart(baseline_summary)


if __name__ == "__main__":
    main()
