
# SHL Assessment Recommendation System (GenAI-Powered)

This system uses Generative AI to recommend SHL assessments based on natural language job descriptions or queries. It utilizes Google Gemini models via LangChain for reasoning, extraction, and retrieval-augmented generation.

---

## 🧠 Core GenAI Components

The heart of the system lies in the `AssessmentModel` class, which powers:

- Job description extraction from raw URLs or queries
- Retrieval of relevant documents using semantic search
- LLM-powered reasoning to recommend SHL assessments

---

## 🧩 Key Libraries & Why They’re Used

### 🔍 `langchain`

LangChain provides abstraction layers to simplify integration between:
- Language models
- Vector stores
- Retrieval and chaining logic

We use it to:
- Connect LLMs to a `RetrievalQA` pipeline
- Handle prompt chains
- Invoke LLMs asynchronously

**Usage in code:**
```python
from langchain.schema import HumanMessage
from langchain.chains.retrieval_qa.base import RetrievalQA
```

---

### 🤖 `langchain_google_genai.ChatGoogleGenerativeAI`

Used to invoke **Google Gemini models (e.g., gemini-1.5-flash)** with custom instructions. This library simplifies communication with Google's GenAI APIs.

**Two Gemini-based agents are used:**
- `jd_extraction_llm`: Extracts structured job descriptions from queries
- `qa_chain`: Recommends SHL assessments based on a query and vector search

**Why it's used:**
- Gemini models are fast and instruction-tuned
- Supports streaming, function-calling, and JSON output
- Reliable for structured task completion

**Example:**
```python
ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.6,
    google_api_key= os.getenv('GOOGLE_API_KEY'),
    system_instruction="You are an AI assistant..."
)
```

---

### 🧠 `langchain_community.embeddings.HuggingFaceEmbeddings`

This is used to **convert SHL product catalog content into embeddings** for semantic search.

**Model used:**  
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`  
Chosen for:
- Multilingual support
- Lightweight and fast
- High-quality semantic similarity

```python
HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
```

---

### 🧠 `langchain_community.vectorstores.FAISS`

Used as the **vector database** backend to store and retrieve document embeddings. FAISS is:
- Fast
- In-memory
- Ideal for small-to-medium scale vector search

```python
self.vector_store = FAISS.load_local("app/data/vector_db", embeddings, allow_dangerous_deserialization=True)
```

---

### 🌐 `langchain_community.tools.DuckDuckGoSearchResults`

This enables **web search integration**. When a user enters a URL, this tool fetches search results which are passed to the LLM for job description extraction.

```python
search = DuckDuckGoSearchResults()
search_results = search.invoke(final_query)
```

---

### 🌎 `urllib.parse`

Used to:
- Sanitize or encode URLs
- Parse whether a query is a valid URL

```python
from urllib.parse import urlparse, quote
```

---

### 🧪 `dotenv` and `os`

Used to **securely load the Google API key** from an `.env` file.

```python
load_dotenv()
os.getenv('GOOGLE_API_KEY')
```

---

### 📋 `pydantic.BaseModel`

Used to define the shape of input data (in this case, a natural language query).

```python
class QueryRequest(BaseModel):
    query: str
```

---

### 🛠️ Custom Logic

#### `process_data()`

This function (defined in `app/utils/data_processing.py`) likely handles:
- Preprocessing of the SHL assessment CSV data
- Embedding generation
- Storing it into the FAISS vector store

---

### 🔁 `RetrievalQA` Flow

This LangChain utility takes in:
- An LLM (`ChatGoogleGenerativeAI`)
- A retriever (vector store)
- A chain type (`stuff` — combines documents before sending to LLM)

```python
RetrievalQA.from_chain_type(
    llm=..., 
    retriever=..., 
    return_source_documents=True
)
```

---

## ⚙️ Architecture Overview

```text
[User Query]
   ↓
Check if URL?
   ↓
Yes → Search + JD Extraction (Gemini)
No  → Direct Query
   ↓
↓
LLM + RetrievalQA (Gemini + FAISS)
   ↓
Structured Recommendations (JSON)
```

---

## 📦 Folder Structure (GenAI Relevant)
```
app/
│
├── model.py                 # Contains AssessmentModel class (GenAI logic)
├── config.py                # Paths to data and vector store
├── utils/
│   └── data_processing.py   # Preprocessing and embedding logic
├── data/
│   ├── Total_data.csv       # SHL catalog
│   ├── vector_db/           # FAISS vector index
│   └── *.pkl                # Pickled docs and url maps
```

---

## ✅ Summary

This system leverages:
- Google Gemini LLMs for structured reasoning and extraction
- LangChain for chaining and retrieval
- HuggingFace for sentence embeddings
- FAISS for semantic vector search

It transforms a natural language job description into accurate, explainable SHL assessment recommendations using Generative AI.
