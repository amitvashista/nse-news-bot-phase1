
import os
from pathlib import Path
from src.data_fetch import load_config
from src.storage.db import NewsDB

def test_can_load_config():
    cfg = load_config()
    assert "feeds" in cfg

def test_can_create_db(tmp_path):
    dbp = tmp_path / "news.db"
    db = NewsDB(str(dbp))
    db.create_tables()
    assert dbp.exists()
