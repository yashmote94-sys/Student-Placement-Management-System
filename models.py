from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Common Fields
    name = Column(String)
    email = Column(String)
    role = Column(String)

    # Student Fields
    branch = Column(String)
    cgpa = Column(String)
    internship = Column(String)
    ppo = Column(String)
    placement_status = Column(String)
    company_name = Column(String)
    package = Column(String)

    # Trainer Fields
    department = Column(String)
    subject = Column(String)
    experience = Column(String)
    batch_assigned = Column(String)

    # Admin Fields
    employee_id = Column(String)
    designation = Column(String)


class LoginUser(Base):
    __tablename__ = "login_users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True)
    password = Column(String)

    role = Column(String)
