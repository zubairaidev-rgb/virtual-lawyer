"""
MongoDB connection layer for the Lawmate backend.

Provides a small, process-wide cached client and accessors used by
``db.repository``. Connection string and database name are read from the
environment (typically ``.env`` at the repository root).
"""
import os
from functools import lru_cache

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING", "").strip()
MONGODB_DATABASE_NAME = os.environ.get("MONGODB_DATABASE_NAME", "FYP_VirtualLawyer").strip() or "FYP_VirtualLawyer"


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    """Return a singleton ``MongoClient`` with sane timeouts for Atlas / remote hosts."""
    if not MONGODB_CONNECTION_STRING:
        raise RuntimeError("MONGODB_CONNECTION_STRING is not set. Please configure it in .env")
    return MongoClient(
        MONGODB_CONNECTION_STRING,
        retryWrites=True,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=15000,
    )


@lru_cache(maxsize=1)
def get_database():
    """Default database handle (name from ``MONGODB_DATABASE_NAME``)."""
    return get_client()[MONGODB_DATABASE_NAME]


def get_collection(name: str):
    """Named collection on the default database; all repository code uses this."""
    return get_database()[name]
