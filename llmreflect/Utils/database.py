import re


def upper_boundary_maximum_records(sql_cmd: str, max_present: int) -> str:
    """
    replace the LIMIT in a query
    Args:
        sql_cmd (str): original sql command
        max_present (max_present): maximum number of returned entries

    Returns:
        str: bounded sql command
    """
    re_pattern = 'LIMIT [0-9]*'
    limit_number_found = re.findall(re_pattern, sql_cmd, re.IGNORECASE)
    if len(limit_number_found) > 0:
        limit_number_sub = limit_number_found[0]
        limit_number = int(limit_number_sub.split(" ")[-1])
        if limit_number > max_present:
            sql_cmd = re.sub(re_pattern, f"LIMIT {max_present}", sql_cmd)
    return sql_cmd
