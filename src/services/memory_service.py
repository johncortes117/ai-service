import os
from ..core.config import CHECKPOINT_PATH
from langgraph.checkpoint.sqlite import SqliteSaver

def get_sqlite_checkpointer(db_path: str = CHECKPOINT_PATH) -> SqliteSaver:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    uri = f"sqlite:///{db_path}"
    
    return SqliteSaver.from_conn_string(uri)