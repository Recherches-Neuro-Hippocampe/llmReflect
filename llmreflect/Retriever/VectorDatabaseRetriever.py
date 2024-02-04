
import boto3
from botocore.exceptions import ClientError
import json
from langchain_community.llms import Bedrock
from llama_index.embeddings import LangchainEmbedding
from langchain_community.embeddings import BedrockEmbeddings
import s3fs
from llama_index.node_parser import SentenceSplitter
from llama_index import SimpleDirectoryReader, ServiceContext, \
    GPTVectorStoreIndex
from llama_index import load_indices_from_storage, SummaryIndex
from llama_index.storage.storage_context import StorageContext
from tqdm import tqdm
import os
from llama_index.vector_stores import PGVectorStore
import shutil
from time import sleep
import psycopg2
from sqlalchemy import make_url
from psycopg2 import sql
from llama_index.query_engine import CitationQueryEngine
from typing import List, Tuple
from pydantic import BaseModel
from llama_index.indices.base import BaseIndex
from llmreflect.Utils.log import get_logger


def get_secret(
        secret_name: str = "dev/bedrock",
        region_name: str = "us-west-2"
) -> dict:
    """
    Retrieve secrete values from AWS secret manager.
    Input:
        secret_name: str, secret name
        region_name: str, which region
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    secret_dict = json.loads(get_secret_value_response['SecretString'])
    return secret_dict


def get_vector_store(
        user_name: str = "",
        password: str = "",
        host: str = "",
        port: str = "",
):
    """
    Return an instance of the vector store.
    Args:
        user_name: str = "",
        password: str = "",
        host: str = "",
        port: str = ""
    Output:
        vector_store: PGVectorStore
        cursor: cursor for vector db (used only for check status)
    """
    logger = get_logger(name="VectorRetriever")
    if user_name or password or host or port:
        if password and host and port:
            logger.info("Using manual setting to connect to vector db")
        else:
            logger.warning(
                (
                    "To use manual settings to connect to vector db, you"
                    "have to provide all: user_name, password, host, and port"
                )
            )
            secrets = get_secret(secret_name="vectordb")
            user_name = secrets.get("username")
            password = secrets.get("password")
            host = secrets.get("host")
            port = secrets.get("port")
    else:
        logger.info("Using secret manager vars to connect to vector db")
        secrets = get_secret(secret_name="vectordb")
        user_name = secrets.get("username")
        password = secrets.get("password")
        host = secrets.get("host")
        port = secrets.get("port")

    connection_string = f"postgresql://{user_name}:{password}@{host}:{port}"
    db_name = "vector_db"
    conn = psycopg2.connect(connection_string)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("SELECT datname FROM pg_database;")

    list_database = cursor.fetchall()

    database_exists = (db_name,) in list_database

    # If the database doesn't exist, create it
    if not database_exists:
        cursor.execute(
            sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(db_name)
            )
        )
    cursor.close()
    conn = psycopg2.connect(
        database=db_name,
        user=user_name,
        password=password,
        host=host,
        port="5432"
    )
    cursor = conn.cursor()

    url = make_url(connection_string)

    vector_store = PGVectorStore.from_params(
        database=db_name,
        host=url.host,
        password=url.password,
        port=url.port,
        user=url.username,
        table_name="text",
        embed_dim=1536
    )

    return vector_store, cursor


def list_all_files_boto(
        bucket_name: str,
        exts: list = [
            "docx",
            "txt",
            "ppt",
            "pptx",
            "pptm",
            "md",
            "pdf",
            "epub"]
) -> list:
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    contents = []

    try:
        for page in paginator.paginate(Bucket=bucket_name):
            for item in page.get('Contents', []):
                if any(item['Key'].endswith("." + ext) for ext in exts):
                    contents.append(item['Key'])
    except Exception as e:
        print(e)  # Handle the exception according to your needs

    return contents


def download_files(bucket_name, file_keys, download_dir):
    s3 = boto3.client('s3')

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    total_files = len(file_keys)
    for i in tqdm(range(0, total_files)):
        key = file_keys[i]
        file_path = os.path.join(download_dir, key.split('/')[-1])
        try:
            s3.download_file(bucket_name, key, file_path)
            # print(f"Downloaded {key} to {file_path}")
        except Exception as e:
            print(f"Error downloading {key}: {e}")


def get_service_context():
    # Setup bedrock
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-west-2",
    )

    model_id = "amazon.titan-text-express-v1"
    llm = Bedrock(
        client=bedrock_runtime,
        model_id=model_id
    )
    llm.model_kwargs = {"temperature": 0.1, "maxTokenCount": 4096}

    # create embeddings
    bedrock_embedding = BedrockEmbeddings(
        client=bedrock_runtime,
        model_id="amazon.titan-embed-text-v1",
    )

    # load in Bedrock embedding model from langchain
    embed_model = LangchainEmbedding(bedrock_embedding)

    service_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embed_model
    )
    return service_context


def get_fs_persistent(
        secret_name: str = "dev/bedrock",
        region_name: str = "us-west-2"
) -> s3fs.S3FileSystem:
    secret_dict = get_secret(
        secret_name=secret_name,
        region_name=region_name
    )
    fs = s3fs.S3FileSystem(
        key=secret_dict.get("AWS_ACCESS_KEY_ID"),
        secret=secret_dict.get("AWS_SECRET_ACCESS_KEY")
    )
    return fs


def get_storage_context(
        vector_store: PGVectorStore,
        fs: s3fs.S3FileSystem,
        persist_dir: str = "dev-rnh-llamaindex/storage",
) -> StorageContext:

    if len(fs.listdir(persist_dir)) == 0:
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
        )
    else:
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            persist_dir=persist_dir,
            fs=fs
        )
    return storage_context


def process_files_in_batches(
        file_paths: list,
        parser: SentenceSplitter,
        fs: s3fs.S3FileSystem,
        service_context: ServiceContext,
        persist_dir: str = "dev-rnh-llamaindex/storage",
        batch_size: int = 256,
        bucket_name: str = "dev-rnh1337-business-files",
        tmp_folder: str = "tmp",
        index_types: list = [
            GPTVectorStoreIndex,
            SummaryIndex,
        ]
):

    total_files = len(file_paths)
    for i in tqdm(range(0, total_files, batch_size)):
        vector_store, cursor = get_vector_store()
        batch = file_paths[i:i + batch_size]
        shutil.rmtree(tmp_folder)
        os.mkdir(tmp_folder)

        try:
            storage_context = get_storage_context(
                vector_store=vector_store,
                fs=fs
            )
            download_files(
                bucket_name=bucket_name,
                file_keys=batch,
                download_dir=tmp_folder
            )
            extra_metadata_dict = {}
            for key in batch:
                file_name = key.split("/")[-1]
                extra_metadata_dict[file_name] = {
                    "file_path": key,
                    "bucket": bucket_name
                }
            docs = SimpleDirectoryReader("tmp").load_data(show_progress=True)
            nodes = parser.get_nodes_from_documents(docs, show_progress=True)
            print(f"Found nodes:{len(nodes)}")
            for node in nodes:
                extra_info = extra_metadata_dict[node.metadata["file_name"]]
                for key in extra_info.keys():
                    node.metadata[key] = extra_info[key]

            if len(fs.listdir(persist_dir)) == 0:
                index_kwargs = {
                    "nodes": nodes,
                    "service_context": service_context,
                    "storage_context": storage_context,
                    "show_progress": True
                }
                for index_type in index_types:
                    index = index_type(**index_kwargs)
                    storage_context.persist(
                        persist_dir=persist_dir,
                        fs=fs
                    )
            else:
                indices = load_indices_from_storage(
                    storage_context=storage_context,
                    service_context=service_context,
                )
                for index in indices:
                    index.insert_nodes(nodes)
                    storage_context.persist(
                        persist_dir=persist_dir,
                        fs=fs
                    )
        except Exception as e:
            print(e)
            sleep(20)
            with open("error_logs.txt", "a+") as f:
                f.writelines(batch)

        check_db_size(cursor)
        vector_store.close()
        cursor.close()


def check_db_size(cursor):

    # SQL query to get the total size of the database
    query = """
        SELECT COUNT(*) from data_text;
    """
    # Execute the query
    cursor.execute(query)
    # Fetch the result
    total_size = cursor.fetchone()[0]
    # Close the cursor and the connection

    query2 = """
        SELECT metadata_
        FROM data_text
        LIMIT 1;
"""
    cursor.execute(query2)
    # total_unique_files = cursor.fetchone()[0]
    # Fetching the results
    schema = cursor.fetchall()

    # Printing the schema
    for column in schema:
        print(column)

    cursor.close()

    # Print the total database size
    print(f"Total database size: {total_size}")


def get_indices(
        fs: s3fs.S3FileSystem,
        user_name: str = "",
        password: str = "",
        host: str = "",
        port: str = ""
) -> Tuple[BaseIndex, BaseIndex]:
    """
    Get indices, including a Summary index and a vector index.
    Notice that the summary index is not used for now.
    Input:
        fs: the s3 bucket file system
        secret_name: str = "vectordb",
        user_name: str = "",
        password: str = "",
        host: str = "",
        port: str = "",
        db_name: str = ""
    Return:
        Tuple[BaseIndex, BaseIndex]:
            index_summary: BaseIndex
            index_vector: BaseIndex

    """
    vector_store, _ = get_vector_store(
        user_name=user_name,
        password=password,
        host=host,
        port=port
    )
    storage_context = get_storage_context(
        vector_store=vector_store,
        fs=fs
    )
    service_context = get_service_context()
    indices = load_indices_from_storage(
        storage_context=storage_context,
        service_context=service_context,
    )
    index_summary = None
    index_vector = None
    for index in indices:
        index_name_raw = str(index.__class__)
        if "summaryindex" in index_name_raw.lower():
            index_summary = index
        else:
            index_vector = index
    return index_summary, index_vector


class Citation(BaseModel):
    text: str  # Text content of the citation
    file_path: str
    bucket: str
    page: int


class SearchResult(BaseModel):
    response: str  # Model response to user's question
    citations: List[Citation]  # Citations used for answering question


class VectorDatabaseRetriever:
    def __init__(
            self,
            secret_name: str = "dev/bedrock",
            region_name: str = "us-west-2",
            similarity_top_k: int = 10,
            hnsw_ef_search: int = 1000,
            ivfflat_probes: int = 20,
            citation_chunk_size: int = 1024,
            user_name: str = "",
            password: str = "",
            host: str = "",
            port: str = "") -> None:
        """
        Retriever class based on BasicRetriever.
        This class leverage the functionality of llamaindex
        to retrive relavent documents based on user's query.
        Args:
            secret_name: str = "dev/bedrock"
                secret name used to log into pgvector database.
            region_name: str = "us-west-2",
                Which region, us-west-2 is the only region
                to use for bedrock.
            similarity_top_k: int = 10,
            hnsw_ef_search: int = 1000,
                number of candidates for retrieving results.
                The bigger the slower the better.
            ivfflat_probes: int = 20,
                The bigger the slower the better.
            citation_chunk_size: int = 1024
        """
        super().__init__()
        self.secret_name = secret_name
        self.region_name = region_name
        self.file_system = get_fs_persistent(
            secret_name=secret_name,
            region_name=region_name
        )
        self.hnsw_ef_search = hnsw_ef_search
        self.ivfflat_probes = ivfflat_probes
        self.similarity_top_k = similarity_top_k
        self.citation_chunk_size = citation_chunk_size

        self._index_summary, self._index_vector = get_indices(
            self.file_system,
            user_name=user_name,
            password=password,
            host=host,
            port=port
        )
        self._retriever = self._index_vector.as_retriever(
            similarity_top_k=self.similarity_top_k,
            vector_store_kwargs={
                "hnsw_ef_search": self.hnsw_ef_search,
                "ivfflat_probes": self.ivfflat_probes
            },
        )
        self.engine = CitationQueryEngine.from_args(
            index=self._index_vector,
            retriever=self._retriever,
            citation_chunk_size=self.citation_chunk_size
        )

    def retrieve(self, user_question: str) -> SearchResult:
        """
        Search vector database based on user's question.
        Input:
            user_question: str, user's natural language question
        Output:
            SearchResult
                response: str, model's answer to user's question.
                citations: List[Citation], references to the source
                Including file_path, bucket, text, page.
        """
        response = self.engine.query(user_question)
        res_txt = str(response)
        citations = []
        n_source_nodes = len(response.source_nodes)
        for i in range(n_source_nodes):
            metadata = response.source_nodes[i].node.metadata
            citations.append(
                Citation(
                    text=response.source_nodes[i].node.get_text(),
                    page=metadata.get("page_label", -1),
                    file_path=metadata.get("file_path", ""),
                    bucket=metadata.get("bucket", "")
                )
            )
        return SearchResult(
            response=res_txt,
            citations=citations
        )
