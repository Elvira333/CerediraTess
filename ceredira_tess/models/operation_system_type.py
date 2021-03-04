from sqlalchemy import Column, Integer, String

from ceredira_tess.database import Base


class OperationSystemType(Base):
    __tablename__ = 'operationsystemtype'
    id = Column(Integer, primary_key=True, autoincrement=True)
    osname = Column(String(64), nullable=False, unique=True)

    def __repr__(self):
        return f'{self.osname}'

    def __init__(self, osname):
        self.osname = osname
