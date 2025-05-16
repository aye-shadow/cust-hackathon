from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Observation(Base):
    __tablename__ = 'observations'
    id = Column(Integer, primary_key=True)
    species_name = Column(String)
    common_name = Column(String)
    date_observed = Column(Date)
    latitude = Column(Float)
    longitude = Column(Float)
    image_url = Column(String)
    notes = Column(String)
