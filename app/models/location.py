from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    name_ta = Column(String(100))
    name_hi = Column(String(100))
    code = Column(String(10), unique=True)
    is_active = Column(Boolean, default=True)

    districts = relationship("District", back_populates="state")


class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    name = Column(String(100), nullable=False)
    name_ta = Column(String(100))
    name_hi = Column(String(100))

    state = relationship("State", back_populates="districts")
    taluks = relationship("Taluk", back_populates="district")

    __table_args__ = (Index("ix_district_state", "state_id"),)


class Taluk(Base):
    __tablename__ = "taluks"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    name = Column(String(100), nullable=False)

    district = relationship("District", back_populates="taluks")
    pincodes = relationship("Pincode", back_populates="taluk")


class Pincode(Base):
    __tablename__ = "pincodes"

    id = Column(Integer, primary_key=True, index=True)
    pincode = Column(String(6), nullable=False, unique=True, index=True)
    post_office = Column(String(200))
    taluk_id = Column(Integer, ForeignKey("taluks.id"))
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    is_active = Column(Boolean, default=True)

    taluk = relationship("Taluk", back_populates="pincodes")
    district = relationship("District")
    state = relationship("State")

    __table_args__ = (Index("ix_pincode_district", "district_id"),)
