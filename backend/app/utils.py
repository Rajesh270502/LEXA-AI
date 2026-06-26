import io
import json

from pypdf import PdfReader
import docx2txt

from google import genai

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)

from app.config import settings

print(
    "GEMINI KEY LOADED:",
    settings.GEMINI_API_KEY[:10]
    if settings.GEMINI_API_KEY
    else "NONE"
)

# Gemini Client
try:
    client = genai.Client(
        api_key=settings.GEMINI_API_KEY
    )
    print("Gemini client initialized successfully")
except Exception as e:
    print("Gemini initialization failed:", e)
    raise

# Qdrant Client
qdrant_client = QdrantClient(path=":memory:")

COLLECTION_NAME = "contracts"

# Gemini embedding model dimension = 768
EMBEDDING_SIZE = 3072

try:
    qdrant_client.get_collection(COLLECTION_NAME)
except Exception:
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=EMBEDDING_SIZE,
            distance=Distance.COSINE
        )
    )


def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    if filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))

        text = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text.append(page_text)

        return "\n".join(text)

    elif filename.endswith(".docx"):
        import tempfile

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".docx"
        ) as tmp:
            tmp.write(file_bytes)
            tmp.flush()

            return docx2txt.process(tmp.name)

    return ""


def clean_and_chunk_text(
    text: str,
    chunk_size=500,
    overlap=50
) -> list[str]:

    cleaned_text = " ".join(text.split())

    words = cleaned_text.split()

    chunks = []

    for i in range(
        0,
        len(words),
        chunk_size - overlap
    ):
        chunk = " ".join(
            words[i:i + chunk_size]
        )

        chunks.append(chunk)

        if i + chunk_size >= len(words):
            break

    return chunks


def get_embedding(text: str):
    response = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=text
    )

    return response.embeddings[0].values


def store_chunks_in_qdrant(
    document_id: int,
    chunks: list[str]
):

    points = []

    for idx, chunk in enumerate(chunks):

        vector = get_embedding(chunk)

        points.append(
            PointStruct(
                id=int(f"{document_id}{idx}"),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "text": chunk
                }
            )
        )

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )


def query_rag_system(
    document_id: int,
    query: str
) -> dict:

    query_vector = get_embedding(query)

    search_result = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=3
    ).points

    context_chunks = [
        hit.payload["text"]
        for hit in search_result
        if hit.payload["document_id"] == document_id
    ]

    combined_context = "\n\n".join(
        context_chunks
    )

    prompt = f"""
You are a legal AI assistant.

Answer ONLY from the context below.

Context:
{combined_context}

Question:
{query}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {
        "answer": response.text,
        "source_chunks": context_chunks
    }

def extract_clauses_and_assess_risk(
    document_id: int,
    full_text: str,
    db
) -> dict:

    sample_text = full_text[:12000]

    prompt = f"""
Analyze the contract and return ONLY valid JSON.

Required format:

{{
  "effective_date": "",
  "expiry_date": "",
  "payment_terms": "",
  "termination_clause": "",
  "confidentiality_clause": "",
  "governing_law": "",
  "risk_score": 0,
  "high_risks": "",
  "medium_risks": "",
  "low_risks": ""
}}

Contract:

{sample_text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_json = response.text.strip()

        if raw_json.startswith("```json"):
            raw_json = raw_json.replace(
                "```json",
                ""
            ).replace(
                "```",
                ""
            ).strip()

        analysis = json.loads(raw_json)

        from app import models

        db_clause = models.ExtractedClause(
            document_id=document_id,
            effective_date=analysis.get(
                "effective_date"
            ),
            expiry_date=analysis.get(
                "expiry_date"
            ),
            payment_terms=analysis.get(
                "payment_terms"
            ),
            termination_clause=analysis.get(
                "termination_clause"
            ),
            confidentiality_clause=analysis.get(
                "confidentiality_clause"
            ),
            governing_law=analysis.get(
                "governing_law"
            )
        )

        db.add(db_clause)

        db_risk = models.RiskAssessment(
            document_id=document_id,
            risk_score=analysis.get(
                "risk_score",
                0
            ),
            high_risks=analysis.get(
                "high_risks"
            ),
            medium_risks=analysis.get(
                "medium_risks"
            ),
            low_risks=analysis.get(
                "low_risks"
            )
        )

        db.add(db_risk)

        db.commit()

        return analysis

    except Exception as e:

        db.rollback()

        print(
            f"Error executing analysis: {e}"
        )

        return {}
