import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
matplotlib.use("QtAgg", force=True)

def tmp_use():
    grading_csv_path = "/home/frank/llmReflect/llmreflect/logs/self_grading.csv"
    unique_errors_path = '/home/frank/llmReflect/llmreflect/logs/unique_errors.csv'
    df = pd.read_csv(grading_csv_path)
    # Show the first few rows of the dataframe
    df.head()
    # Plot distribution of scores
    # Rename the columns for better understanding
    df.columns = ["Request", "SQL Command", "Result", "Score", "Feedback"]

    # Display summary statistics for numeric columns
    numeric_summary = df.describe()

    # Count unique requests and SQL commands
    unique_requests = df["Request"].nunique()
    unique_sql_commands = df["SQL Command"].nunique()

    # Count of different Results
    result_counts = df["Result"].value_counts()

    # Display the summaries
    # print(unique_requests)
    print(df["Request"].value_counts()[df["Request"].value_counts() > 1])
    df["Request"].value_counts()[df["Request"].value_counts() > 1].to_csv("/home/frank/llmReflect/llmreflect/logs/repeated_request.csv")
    # print(numeric_summary, unique_requests, unique_sql_commands, result_counts)

    # plt.figure(figsize=(10, 6))
    # sns.histplot(df["Score"], kde=True, bins=20)
    # plt.title('Distribution of Scores')
    # plt.xlabel('Score')
    # plt.ylabel('Frequency')
    # plt.grid(True)
    # plt.show()

    # # Top 10 most common results
    # top_results = result_counts[:10]

    # plt.figure(figsize=(10, 6))
    # sns.barplot(x=top_results.values, y=top_results.index, orient='h')
    # plt.title('Top 10 Most Common Results')
    # plt.xlabel('Count')
    # plt.ylabel('Result')
    # plt.show()

    # # Number of unique SQL commands per request
    # df_grouped = df.groupby("Request")["SQL Command"].nunique()

    # plt.figure(figsize=(10, 6))
    # sns.histplot(df_grouped, kde=True, bins=20)
    # plt.title('Number of Unique SQL Commands per Request')
    # plt.xlabel('Number of Unique SQL Commands')
    # plt.ylabel('Frequency')
    # plt.grid(True)
    # plt.show()
    error_df = pd.read_csv(unique_errors_path)

    # Extract short error names after 'psycopg2.errors.' in the 'Unique Error' column
    error_df['Error Name'] = error_df['Unique Error'].apply(lambda x: x.split('psycopg2.errors.')[-1].split(")")[0] if 'psycopg2.errors.' in x else x)
    error_df['Error Name'] = error_df['Error Name'].apply(lambda x: "EmptyResponseError" if "Empty response" in x else x)

    df['Error Name'] = df['Result'].apply(lambda x: x.split('psycopg2.errors.')[-1].split(")")[0] if 'psycopg2.errors.' in x else x)
    df['Error Name'] = df['Error Name'].apply(lambda x: "EmptyResponseError" if "Empty response" in x else x)
    df['Error Name'] = df['Error Name'].apply(lambda x: "SuccessfulRun" if "You retrieved" in x else x)
    print(df.columns)
    print(df)
    df = df.sort_values("Error Name", ignore_index=False)
    print(df)
    df = df.assign(Index=range(len(df))).set_index('Index')
    # df.to_csv("/home/frank/llmReflect/llmreflect/logs/all_errors.csv")
    error_df = df[df["Error Name"] != "SuccessfulRun"]
    error_df = error_df[error_df["Request"] != "No questions requested."]
    error_df = error_df[error_df["Request"] != "No questions were requested."]
    error_df = error_df.reset_index(drop=True)
    error_df.to_csv("/home/frank/llmReflect/llmreflect/logs/all_errors.csv")
    error_count = error_df["Error Name"].value_counts()
    print(error_count)

    plt.figure(figsize=(10, 8))
    sns.barplot(x=error_count.index, y=error_count.values)
    plt.title('Distribution of all type of errors')
    plt.xlabel('Count')
    plt.ylabel('Error Name')
    plt.grid(True)
    plt.show()

    subclasses_errors = error_df[error_df["Error Name"] != "EmptyResponseError"]
    error_count = subclasses_errors["Error Name"].value_counts()
    plt.figure(figsize=(10, 8))
    sns.barplot(x=error_count.index, y=error_count.values)
    plt.title('Distribution of errors excluding EmptyResponse')
    plt.xlabel('Count')
    plt.ylabel('Error Name')
    plt.grid(True)
    plt.show()
