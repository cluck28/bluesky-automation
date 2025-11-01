from typing import Dict, List

import pandas as pd


def _build_schedule(file_path: str, schedule: List[Dict], rules: List[Dict]):
    # We want to save the schedule as a dataframe
    # We want to make sure to compute all the dates
    # We want to make sure we deduplicate against the uploads
    # We want to make sure every row has an upload
    df = pd.DataFrame(schedule)
    df.to_csv(file_path, index=False)
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
