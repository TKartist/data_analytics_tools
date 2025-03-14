import pandas as pd
import json
import matplotlib.pyplot as plt 

def read_file():
    df = pd.read_csv("../ops_result/ops_cache_response.csv", encoding="cp1252", index_col="id")
    total_valid_cache = len(df)

    df["used_filters"] = df["used_filters"].apply(json.loads)
    df["modified_at"] = df["modified_at"].apply(lambda x: pd.to_datetime(x.split(" ")[0]))
    df["created_at"] = df["created_at"].apply(lambda x: pd.to_datetime(x.split(" ")[0]))

    return df

def tool_use_freq(df, full_dates):
    count = df["created_at"].value_counts().reset_index()
    count.columns = ["created_at", "Count"]
    count_sorted = count.sort_values(by="created_at").reset_index()
    df_full = count_sorted.set_index("created_at").reindex(full_dates).reset_index()

    df_full.fillna(0, inplace=True)  # Fill missing values with 0
    return df_full


def plot_tool_freq(df):
    full_dates = pd.date_range(start=df['created_at'].min(), end=df['created_at'].max(), freq='D')
    df_failed = df[df["status"] == 4]
    df_success = df[df["status"] == 3]
    total = tool_use_freq(df, full_dates)
    failed = tool_use_freq(df_failed, full_dates)
    success = tool_use_freq(df_success, full_dates)

    plt.figure(figsize=(15, 9))
    plt.plot(total["level_0"], total["Count"], marker="x", label="total")
    plt.plot(failed["level_0"], failed["Count"], label="failed")
    plt.plot(success["level_0"], success["Count"], label="successful")

    plt.xticks(rotation=45)
    plt.ylabel("OPS learning count")
    plt.xlabel("Date")
    plt.legend()
    plt.title("Frequency of OPS learning insight generation")
    plt.savefig("ops_insight_freq.png")

    plt.close()


def expand_filter(df):
    copy_df = df.copy()
    all_keys = set()
    for filters in df["used_filters"]:
        all_keys.update(filters.keys())

    for key in all_keys:
        if key not in copy_df.columns:
            copy_df[key] = "" 

    def expand_row(row):
        for key, val in row["used_filters"].items():
            row[key] = val
        return row

    copy_df = copy_df.apply(expand_row, axis=1)
    copy_df.to_csv("../try.csv")
    return copy_df

def filter_insight(df, lim):
    fil, count = [], []
    filter_cols = df.columns.tolist()[lim:]
    for filter in filter_cols:
        all = (df[filter] != "").sum()
        failed = ((df[filter] != "") & (df["status"] == 4)).sum()
        success = all - failed
        fil.extend([f"{filter} success", f"{filter} failed"])
        count.extend([int(success), int(failed)])
    colors = ["blue", "red"]
    plt.figure(figsize=(14, 8))
    bars = plt.bar(df["Category"], df["Values"], color=[colors[i % 2] for i in range(len(df))])

    # Add text labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height, str(height), ha="center", va="bottom", fontsize=12, fontweight="bold")

    plt.xticks(rotation=80)
    plt.subplots_adjust(bottom=0.4)
    plt.title("Filter Effectivity")
    plt.savefig("filter_effectivity.png")
    plt.close()


def main():
    df = read_file()
    plot_tool_freq(df)
    expanded_df = expand_filter(df)
    filter_insight(expanded_df, len(df.columns))

if __name__ == "__main__":
    main()