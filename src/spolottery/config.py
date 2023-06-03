import os


max_delegators_allowed = 3000


def get_blockfrost_project_id() -> str:
    blockfront_project_id = os.environ.get(
        "BLOCKFROST_PROJECT_ID", "xxxx")
    return blockfront_project_id


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 5433 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "xxxx")
    user = os.environ.get("DB_USER", "postgres")
    db_name = "cardanospo"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5005 if host == "localhost" else 80
    return f"http://{host}:{port}"
