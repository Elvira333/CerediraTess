from flask_security import RoleMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ceredira_tess.database import Base
from ceredira_tess.models import relationships


class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(255))
    agents = relationship("Agent", secondary=relationships.roles_agents, back_populates='roles')

    def __repr__(self):
        return f'{self.name}'

    def __init__(self, name):
        self.name = name
