from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.model import AssessmentModel
import uvicorn
import logging
import json
import urllib.parse
from langchain.schema import HumanMessage
from langchain_community.tools import DuckDuckGoSearchResults
from urllib.parse import urlparse
app = FastAPI()
model = AssessmentModel()
logger = logging.getLogger("uvicorn.error")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except:
        return False
def structure_content(raw_content):
    structured = {}
    lines = [line.strip() for line in raw_content.split('\n') if line.strip()]
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            if key == 'product_name':
                structured['productName'] = value
            elif key == 'description':
                structured['description'] = value
            elif key == 'job_levels':
                structured.setdefault('keyDetails', {})['jobLevels'] = [v.strip() for v in value.rstrip(',').split(',')]
            elif key == 'languages':
                structured.setdefault('keyDetails', {})['languages'] = [v.strip() for v in value.rstrip(',').split(',')]
            elif key == 'assessment_length':
                try:
                    time = int(value.split('=')[1].strip())
                except:
                    time = None
                structured.setdefault('keyDetails', {})['assessment'] = {
                    'completionTime': time,
                    'unit': 'minutes'
                }
            elif key == 'test_types':
                structured.setdefault('keyDetails', {})['testTypes'] = [v.strip() for v in value.split(',')]
            elif key == 'downloads':
                try:
                    downloads = eval(value) 
                    structured['downloads'] = [{
                        'name': d['name'],
                        'url': urllib.parse.quote(d['url'], safe=':/')
                    } for d in downloads]
                except:
                    structured['downloads'] = []
    structured.setdefault('additionalInfo', {})['configurations'] = "Multiple configurations available"
    return structured
class QueryRequest(BaseModel):
    query: str
@app.on_event("startup")
async def startup_event():
    try:
        await model.initialize()
    except Exception as e:
        raise
@app.post("/recommend")
async def recommend_assessment(request: QueryRequest):
    try:
        final_query = request.query
        if is_url(final_query):
            search=DuckDuckGoSearchResults()
            search_results = search.invoke(final_query)
            extracted_jd = await model.jd_extraction_llm.ainvoke(
                [HumanMessage(content=search_results)]
            )
            final_query = extracted_jd
        final_query = final_query.lower()
        result = await model.qa_chain.ainvoke(final_query)
        return process_results(result, model.url_map)
    except Exception as e:
        logger.error(f"Recommendation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/healthy")
async def health():
    return {"status": "healthy"}
def process_results(result, url_map):
    source_documents = result.get('source_documents', [])
    urls = []
    for doc in source_documents:
        url = doc.metadata.get('url')
        if url:
            urls.append(url)
    response = {
        "query": result.get('query', ''),
        "result_summary": result.get('result', ''),
        "documents": [
            {
                "url": doc.metadata.get('url', ''),
                "content": structure_content(doc.page_content),
                "source": doc.metadata.get('source', ''),
                "metadata": {
                    "id": doc.id,
                    "remote_testing": doc.metadata.get('remote_testing', False)
                }
            }
            for doc in result.get('source_documents', [])
            if doc.metadata.get('url') 
        ]
    }
    return response
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)