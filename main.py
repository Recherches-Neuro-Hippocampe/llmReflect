from Scripts import database_question, database_answer, database_sql_grading

questions = database_question.run(n_questions=5)
for q in questions:
    result = database_answer.run(q, return_cmd=True)
    cmd = result['cmd']
    summary = result['summary']
    grading = database_sql_grading.run(
        request=q,
        sql_cmd=cmd,
        db_summary=summary
    )
    print(q)
    print(result['cmd'])
    print(result['summary'])
    print(grading)
    print("=============================")
