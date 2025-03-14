import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter
from VARIABLES import FILTERS, SECTORS, REGIONS


def convert(x):
    if pd.isna(x) or x == "":
        return 0
    x = x.split("/")[0][-1]
    return int(x)




def read_file():
    df = pd.read_csv("../ops_result/ops_cache_response.csv", encoding="cp1252", index_col="id")

    df["used_filters"] = df["used_filters"].apply(json.loads)
    df["modified_at"] = df["modified_at"].apply(lambda x: pd.to_datetime(x.split(" ")[0]))
    df["created_at"] = df["created_at"].apply(lambda x: pd.to_datetime(x.split(" ")[0]))
    df["insights1_confidence_level"] = df["insights1_confidence_level"].apply(convert)
    df["insights2_confidence_level"] = df["insights2_confidence_level"].apply(convert)
    df["insights3_confidence_level"] = df["insights3_confidence_level"].apply(convert)
    df["avg_insight"] = (df["insights1_confidence_level"] + df["insights2_confidence_level"] + df["insights3_confidence_level"]) / 3

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
    plt.savefig("../ops_visualization/ops_insight_freq.png")

    plt.close()
    # df_avg = df.set_index("created_at").reindex(full_dates).reset_index()
    # print(df_avg.head)
    # plt.plot(df_avg.index, df_avg["avg_insight"], marker="x", label="average insight")
    # plt.ylabel("OPS learning count")
    # plt.xlabel("Date")
    # plt.legend()
    # plt.title("Frequency of OPS learning insight generation")
    # plt.savefig("../ops_visualization/average_insight_progress.png")
    # plt.close()



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
        fil.extend([f"{FILTERS.get(filter)} suc", f"{FILTERS.get(filter)} fail"])
        count.extend([int(success), int(failed)])
    colors = ["blue", "red"]
    plt.figure(figsize=(15, 8))
    bars = plt.bar(fil, count, color=[colors[i % 2] for i in range(len(df))])

    # Add text labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        content = round(height / len(df) * 100, 1)
        plt.text(bar.get_x() + bar.get_width()/2, height, f"{content}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.xticks(rotation=90)
    plt.xlabel("Filter Category")
    plt.ylabel("Usage Count")

    plt.subplots_adjust(bottom=0.16, left=0.09)
    plt.title("Filter Category Usage and Effectivity")
    legend_patches = [
        mpatches.Patch(color="red", label="Failed to generate Insight"),
        mpatches.Patch(color="blue", label="Successfully generated Insight"),
    ]

    plt.legend(handles=legend_patches, title="Effectivity")

    plt.savefig("../ops_visualization/filter_effectivity.png")
    plt.close()


def category_specific_frequency(df, lim):
    filter_cols = df.columns.tolist()[lim:]
    common = {}
    for filter in filter_cols:
        x = df[filter].astype(str)
        x = x.str.split(",")
        flat_list = sum(x, [])
        element_count = Counter(flat_list)
        count_df = pd.DataFrame(element_count.items(), columns=["Element", "Count"])
        count_df = count_df[count_df["Element"] != ""]
        sorted_df = count_df.sort_values(by="Count", ascending=False)
        sorted_df = sorted_df.reset_index(drop=True)
        common[filter] = sorted_df
    return common

def generate_bar_chart(df, title, type=1):
    plt.figure(figsize=(15, 8))

    bars = plt.bar(df["Element"][:10], df["Count"][:10], color="#0db9ff")

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height, f"{height}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    plt.title(f"{title} Top 10 used items")
    if type == 2:
        plt.xticks(rotation=90)
        plt.subplots_adjust(bottom=0.35)
    else:
        plt.xticks(rotation=30)
        plt.subplots_adjust(bottom=0.18)
    
    plt.xlabel("Item")
    plt.ylabel("Frequency")
    plt.savefig(f"../ops_visualization/{title}.png")
    plt.close()


def main():
    df = read_file()
    plot_tool_freq(df)
    expanded_df = expand_filter(df)
    filter_insight(expanded_df, len(df.columns))
    cat_ele_freq = category_specific_frequency(expanded_df, len(df.columns))
    for key, cat_df in cat_ele_freq.items():
        if key == "sector_validated__in":
            cat_df["Element"] = cat_df["Element"].apply(lambda x: SECTORS[int(x)])
        if key == "appeal_code__region":
            cat_df["Element"] = cat_df["Element"].apply(lambda x: REGIONS[int(x)])
        if key == "appeal_code__country__in":
            temp = pd.read_csv("../aux_data/country.csv", index_col="id")
            cat_df["Element"] = cat_df["Element"].apply(lambda x: temp["content"][int(x)])
        if key == "appeal_code__dtype__in":
            temp = pd.read_csv("../aux_data/disaster_type.csv", index_col="id")
            cat_df["Element"] = cat_df["Element"].apply(lambda x: temp["content"][int(x)])
        if key == "per_component_validated__in":
            temp = pd.read_csv("../aux_data/per-formcomponent.csv", index_col="id")
            cat_df["Element"] = cat_df["Element"].apply(lambda x: temp["content"][int(x)])
            generate_bar_chart(cat_df, key, 2)
            continue

        generate_bar_chart(cat_df, key)

if __name__ == "__main__":
    main()