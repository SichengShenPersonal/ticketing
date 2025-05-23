from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

engine = create_engine("sqlite:///data/example.db")
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)
