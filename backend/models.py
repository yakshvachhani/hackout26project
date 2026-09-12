from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz
from database import Base

def get_ist_time():
    return datetime.now(pytz.timezone('Asia/Kolkata'))

class Microgrid(Base):
    __tablename__ = 'microgrids'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    population = Column(Integer)
    connected_households = Column(Integer)
    operating_mode = Column(String, default='LIVE')
    last_updated = Column(DateTime, default=get_ist_time)
    
    assets = relationship('Asset', back_populates='microgrid')
    daily_logs = relationship('DailyLog', back_populates='microgrid')

class Asset(Base):
    __tablename__ = 'assets'

    id = Column(Integer, primary_key=True, index=True)
    microgrid_id = Column(Integer, ForeignKey('microgrids.id'))
    asset_type = Column(String)
    name = Column(String)
    capacity_kw = Column(Float)
    capacity_kwh = Column(Float, nullable=True)
    current_status = Column(String, default='Offline')
    efficiency = Column(Float, default=1.0)
    
    microgrid = relationship('Microgrid', back_populates='assets')

class DailyLog(Base):
    __tablename__ = 'daily_logs'

    id = Column(Integer, primary_key=True, index=True)
    microgrid_id = Column(Integer, ForeignKey('microgrids.id'))
    date = Column(String)
    uptime_percentage = Column(Float)
    renewable_share = Column(Float)
    diesel_dependency = Column(Float)
    diesel_only_cost = Column(Float)
    optimized_cost = Column(Float)
    saved_co2_kg = Column(Float)
    
    microgrid = relationship('Microgrid', back_populates='daily_logs')
