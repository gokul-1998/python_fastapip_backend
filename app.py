from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# SQLAlchemy setup
DATABASE_URL = "sqlite:///data.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Pydantic model for request validation
class ValueCreate(BaseModel):
    current_value: int
    default_value: int

class ValueUpdate(BaseModel):
    current_value: int
    default_value: int

# SQLAlchemy model
class Values(Base):
    __tablename__ = "values"
    
    id = Column(Integer, primary_key=True, index=True)
    current_value = Column(Integer)
    default_value = Column(Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "current_value": self.current_value,
            "default_value": self.default_value
        }

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}

@app.get("/get_values")
def get_values(db: SessionLocal = Depends(get_db)):
    values = db.query(Values).all()
    return {"values": [value.to_dict() for value in values]}

@app.put("/update_value/{value_id}")
def update_value(
    value_id: int, 
    value_data: ValueUpdate, 
    db: SessionLocal = Depends(get_db)
):
    value = db.query(Values).filter(Values.id == value_id).first()
    if not value:
        raise HTTPException(status_code=404, detail="Value not found")
    
    value.current_value = value_data.current_value
    value.default_value = value_data.default_value
    db.commit()
    db.refresh(value)
    return {"message": "Value updated successfully", "value": value.to_dict()}

@app.put("/restore_default/{value_id}")
def restore_default(
    value_id: int, 
    db: SessionLocal = Depends(get_db)
):
    value = db.query(Values).filter(Values.id == value_id).first()
    if not value:
        raise HTTPException(status_code=404, detail="Value not found")
    
    value.current_value = value.default_value
    db.commit()
    db.refresh(value)
    return {"message": "Default value restored successfully", "value": value.to_dict()}


@app.post("/create_value")
def create_value(
    value_data: ValueCreate, 
    db: SessionLocal = Depends(get_db)
):
    value = Values(
        current_value=value_data.current_value,
        default_value=value_data.default_value
    )
    db.add(value)
    db.commit()
    db.refresh(value)
    return {"message": "Value created successfully", "value": value.to_dict()}