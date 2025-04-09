from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import pickle
from app.config import Config

async def get_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    if Config.VECTOR_STORE_PATH.exists():
        return await FAISS.aload_local(
            str(Config.VECTOR_STORE_PATH),
            embeddings,
            allow_dangerous_deserialization=True
        )
    
    with open(Config.DOCUMENTS_PATH, "rb") as f:
        documents = pickle.load(f)
    
    vector_store = await FAISS.afrom_texts(
        texts=[doc["content"] for doc in documents],
        embedding=embeddings,
        metadatas=[doc["metadata"] for doc in documents]
    )
    await vector_store.save_local(str(Config.VECTOR_STORE_PATH))
    return vector_store