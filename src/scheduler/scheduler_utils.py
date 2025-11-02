from typing import Dict, List

import numpy as np
import pandas as pd


def _build_schedule(file_path: str, schedule: List[Dict], rules: List[Dict]):
    # We want to save the schedule as a dataframe
    # We want to make sure to compute all the dates
    # We want to make sure we deduplicate against the uploads
    # We want to make sure every row has an upload
    df = pd.DataFrame(schedule)
    # Fill dates
    df["date"] = pd.to_datetime(df["date"])
    if df["date"].isna().all():
        current_max = pd.Timestamp.today()
    else:
        current_max = df["date"].max(skipna=True)
    for i in range(len(df)):
        if pd.isna(df.at[i, "date"]):
            current_max += pd.Timedelta(days=1)
            df.at[i, "date"] = current_max
    # Define conditions
    df["days_diff"] = (df["date"] - pd.Timestamp.today()).dt.days
    conditions = [
        df["days_diff"] < 1,
        (df["days_diff"] >= 1) & (df["days_diff"] <= 7),
        df["days_diff"] > 7,
    ]

    # Corresponding values for each condition
    values = ["Next Day!", "Coming Soon.", "A Long Way Off..."]

    # Default value if none of the conditions match
    df["status"] = np.select(conditions, values, default="A Long Way Off...")
    df[["path", "text", "date", "status"]].to_csv(file_path, index=False)
    return


def get_saved_schedule(file_path: str) -> List[Dict]:
    df = pd.read_csv(file_path)
    return df.to_dict(orient="records")


def update_saved_schedule(file_path: str, queue_file_path: str, new_order: List = []):
    rules = get_queue_rules(queue_file_path)
    if new_order:
        _build_schedule(file_path, new_order, rules)
    schedule = get_saved_schedule(file_path)
    _build_schedule(file_path, schedule, rules)
    return


def get_queue_rules(file_path: str) -> List[Dict]:
    df = pd.read_csv(file_path)
    return df.to_dict(orient="records")


def update_queue_rules(file_path: str, new_rule: Dict):
    pass
