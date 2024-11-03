from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List

# Database setup
DATABASE_URL = "sqlite:///./portfolio.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False)
    works = relationship("Work", back_populates="owner")

class Work(Base):
    __tablename__ = "works"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="works")

Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class UserCreate(BaseModel):
    username: str

class UserResponse(UserCreate):
    id: int

    class Config:
        orm_mode = True

class WorkCreate(BaseModel):
    title: str
    description: str

class WorkResponse(WorkCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User CRUD operations
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Work CRUD operations
@app.post("/works/", response_model=WorkResponse)
async def create_work(work: WorkCreate, db: Session = Depends(get_db)):
    db_work = Work(title=work.title, description=work.description, user_id=1)  # Assuming user_id=1 for simplicity
    db.add(db_work)
    db.commit()
    db.refresh(db_work)
    return db_work

@app.get("/works/", response_model=List[WorkResponse])
async def read_works(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    works = db.query(Work).offset(skip).limit(limit).all()
    return works

@app.get("/works/{work_id}", response_model=WorkResponse)
async def read_work(work_id: int, db: Session = Depends(get_db)):
    work = db.query(Work).filter(Work.id == work_id).first()
    if work is None:
        raise HTTPException(status_code=404, detail="Work not found")
    return work

@app.put("/works/{work_id}", response_model=WorkResponse)
async def update_work(work_id: int, work: WorkCreate, db: Session = Depends(get_db)):
    db_work = db.query(Work).filter(Work.id == work_id).first()
    if db_work is None:
        raise HTTPException(status_code=404, detail="Work not found")
    db_work.title = work.title
    db_work.description = work.description
    db.commit()
    db.refresh(db_work)
    return db_work

@app.delete("/works/{work_id}", response_model=WorkResponse)
async def delete_work(work_id: int, db: Session = Depends(get_db)):
    db_work = db.query(Work).filter(Work.id == work_id).first()
    if db_work is None:
        raise HTTPException(status_code=404, detail="Work not found")
    db.delete(db_work)
    db.commit()
    return db_work