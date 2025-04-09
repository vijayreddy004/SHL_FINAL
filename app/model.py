from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.retrieval_qa.base import RetrievalQA
from app.config import Config
from app.utils.data_processing import process_data
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
from fastapi import HTTPException
load_dotenv()
class AssessmentModel:
    def __init__(self):
        self.vector_store = None
        self.url_map = None
        self.qa_chain = None
        self.search_tool = None
        self.jd_extraction_llm = None
    async def initialize(self):
        try:
            Config.check_paths()
            await process_data()
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            self.vector_store = FAISS.load_local("app/data/vector_db", embeddings ,allow_dangerous_deserialization=True)            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    temperature=0.6,
                    google_api_key= os.getenv('GOOGLE_API_KEY'),
                    system_instruction = """You are an AI assistant specialized in recommending SHL assessments based on job descriptions and queries.
                    INSTRUCTIONS:
                    APPROXIMATE RESULTS ARE GOOD.
                    1. Carefully analyze the user's query, which may be a natural language question or job description.
                    2. Extract the job description from the query.
                    3. Return  most relevant SHL assessments that match the job description from our db.
                    4. Format your response as a structured JSON with recommendations array.
                    5. Each recommendation must include: assessment_name, url, remote_testing, adaptive_support, duration, test_type, relevance_score, and relevance_explanation.
                    6. ONLY return assessments that match time constraints if specified.
                    7. Sort recommendations by relevance score in descending order.
                    9. Always return valid JSON that can be parsed programmatically.
                    10. Do not include any text outside the JSON object.
                    11. Ensure all required fields are included for each recommendation.""",
                ),
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 9}),
                return_source_documents=True
            )
            self.jd_extraction_llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.6,
                google_api_key= os.getenv('GOOGLE_API_KEY'),
                    system_instruction="""You are an AI assistant that extracts job descriptions from user queries.
                    INSTRUCTIONS:
                    1. Carefully analyze the user's query, which may be a natural language question or a job posting.
                    2. Extract only the job description portion, including role title experience level if available.
                    3. Ignore irrelevant or general text.
                    4. Return the extracted job description in structured JSON format.
                    5. Format:
                    {
                    "job_description": "Extracted text here"
                    }
                    6. Only include text that is directly part of the job description.
                    7. Ignore the summary.
                    8. Do not include any explanatory text outside the JSON object.
                    9. Always return a valid JSON that can be parsed programmatically."""
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Initialization failed: {str(e)}"
            )