from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    email = Column(String, unique=True)
    role = Column(String)

    branch = Column(String)

    cgpa = Column(String)

    internship = Column(String)

    ppo = Column(String)

    placement_status = Column(String)

    company_name = Column(String)

    package = Column(String)