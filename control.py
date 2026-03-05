def build_post_impl_task_map(ws_tasks, change_id_col="A", task_id_col="P", task_type_col="Q",
                            wanted_type="Post Implementation Review",
                            start_row=DATA_START_ROW, max_empty=50):
    """
    Returns dict: change_id -> task_id (or joined list if multiple)
    Filters rows where task_type_col == wanted_type (case-insensitive)
    """
    mapping = {}
    empty_streak = 0
    r = start_row

    wanted = wanted_type.strip().lower()

    while True:
        chg_id = getv(ws_tasks, change_id_col, r)
        if is_empty(chg_id):
            empty_streak += 1
            if empty_streak >= max_empty:
                break
            r += 1
            continue

        empty_streak = 0
        task_type = getv(ws_tasks, task_type_col, r)
        if normalize_lower(task_type) == wanted:
            tid = getv(ws_tasks, task_id_col, r)
            chg_key = normalize_str(chg_id)

            if not is_empty(tid):
                # si jamais plusieurs tasks PIR pour le même change, on concatène
                if chg_key in mapping and not is_empty(mapping[chg_key]):
                    mapping[chg_key] = f"{mapping[chg_key]}, {normalize_str(tid)}"
                else:
                    mapping[chg_key] = normalize_str(tid)

        r += 1

    return mapping



post_impl_task_map = build_post_impl_task_map(
    ws_task,
    change_id_col="A",
    task_id_col="P",
    task_type_col="Q",
    wanted_type="Post Implementation Review"
)


# K = ID de la task Post Implementation Review (List of tasks: Q filtré + P)
k_val = post_impl_task_map.get(change_id_str, None)
setv(ws_dest, "K", r, k_val)
setv(ws_dest, "L", r, note_0_if_filled_1_if_empty(k_val))