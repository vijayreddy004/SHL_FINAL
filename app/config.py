from pathlib import Path
class Config:
    DATA_PATH = Path("app/data/Total_data.csv")
    VECTOR_STORE_PATH = Path("app/data/vector_db")
    DOCUMENTS_PATH = Path("app/data/alt_documents.pkl")
    URL_MAP_PATH = Path("app/data/url_map.pkl")
    @classmethod
    def check_paths(cls):
        if not cls.DATA_PATH.exists():
            raise FileNotFoundError(f"Data file not found at {cls.DATA_PATH}")