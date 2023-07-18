Module llmreflect.Utils.database
================================

Functions
---------

    
`upper_boundary_maximum_records(sql_cmd: str, max_present: int) ‑> str`
:   replace the LIMIT in a query
    Args:
        sql_cmd (str): original sql command
        max_present (max_present): maximum number of returned entries
    
    Returns:
        str: bounded sql command