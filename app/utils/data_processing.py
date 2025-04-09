import pandas as pd
import json
import pickle
from pathlib import Path
from app.config import Config

async def process_data():
    if Config.DOCUMENTS_PATH.exists() and Config.URL_MAP_PATH.exists():
        return
    
    df = pd.read_csv(Config.DATA_PATH)
    documents = []
    url_map = {}

    def process_row(row):
        downloads = []
        if pd.notna(row['downloads']):
            try:
                downloads = json.loads(row['downloads'].replace("'", '"'))
            except json.JSONDecodeError:
                try:
                    downloads = [item.strip() for item in row['downloads'].split(',')]
                except:
                    downloads = []
        content = f"""
        Product Name: {row['name']}
        Description: {row['description']}
        Job Levels: {row['job_levels']}
        Languages: {row['languages']}
        Assessment Length: {row['assessment_length']}
        Test Types: {row['test_types']}
        Downloads: {downloads}
        """
        metadata = {
            "url": row['url'],
            "remote_testing": row['remote_testing']
        }

        doc = {
            "content": content,
            "metadata": metadata
        }
        url_map[row['url']] = {
            "product_name": row['name'],
            "job_levels": row['job_levels'],
            "languages": row['languages'],
            "assessment_length": row['assessment_length'],
            "test_types": row['test_types'],
            "downloads": downloads,
            "remote_testing": row['remote_testing']
        }
        return doc
    
    documents = [process_row(row) for _, row in df.iterrows()]
    
    with open(Config.DOCUMENTS_PATH, "wb") as f:
        pickle.dump(documents, f)
    with open(Config.URL_MAP_PATH, "wb") as f:
        pickle.dump(url_map, f)