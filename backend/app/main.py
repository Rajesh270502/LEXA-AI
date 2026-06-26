import json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models, schemas, auth, utils

# Generate Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Legal Contract Assistant"
)

# Your routes below
@app.get("/")
def root():
    return {"message": "API is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Legal Contract Platform API. Go to /docs for interactive testing!"}

@app.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    hashed_pw = auth.get_password_hash(user.password)

    new_user = models.User(
        username=user.username,
        hashed_password=hashed_pw
    )

    db.add(new_user)
    db.commit()

    access_token = auth.create_access_token(
        data={"sub": new_user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/upload")
async def upload_contract(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        if not (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
            raise HTTPException(
                status_code=400,
                detail="Invalid format. Provide PDF or DOCX."
            )

        file_bytes = await file.read()

        raw_text = utils.extract_text_from_bytes(
            file_bytes,
            file.filename
        )

        if not raw_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Document text extraction failed or file empty."
            )

        db_doc = models.Document(
            filename=file.filename,
            user_id=current_user.id
        )

        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)

        chunks = utils.clean_and_chunk_text(raw_text)

        utils.store_chunks_in_qdrant(
            db_doc.id,
            chunks
        )

        return {
            "document_id": db_doc.id,
            "filename": db_doc.filename,
            "message": "Successfully chunked and indexed."
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/chat/{document_id}")
def chat_with_contract(
    document_id: int, 
    query: str, 
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        result = utils.query_rag_system(document_id, query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))