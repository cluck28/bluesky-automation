from typing import Dict, List

import pandas as pd


def build_schedule(schedule: List[Dict], rules: List[Dict]):
    return


def get_saved_schedule() -> List[Dict]:
    return [{}]


def update_saved_schedule(new_order: List = []):
    rules = get_queue_rules()
    if new_order:
        build_schedule(new_order, rules)
    schedule = get_saved_schedule()
    build_schedule(schedule, rules)
    return


def get_queue_rules() -> List[Dict]:
    return [{}]


def update_queue_rules(new_rule: Dict):
    pass
