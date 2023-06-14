import re
from langchain.sql_database import SQLDatabase


def upper_boundary_maxiunm_records(sql_cmd, max_present):
    re_pattern = 'LIMIT [0-9]*'
    limit_number_found = re.findall(re_pattern, sql_cmd, re.IGNORECASE)
    if len(limit_number_found) > 0:
        limit_number_sub = limit_number_found[0]
        limit_number = int(limit_number_sub.split("LIMIT")[-1])
        if limit_number > max_present:
            sql_cmd = re.sub(re_pattern, f"LIMIT {max_present}", sql_cmd)
    return sql_cmd
