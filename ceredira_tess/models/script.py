from sqlalchemy import Column, Integer, String, Text

from ceredira_tess.database import Base


class Script(Base):
    __tablename__ = 'script'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(2048), nullable=False, unique=True)
    description = Column(Text)

    def __repr__(self):
        return f'{self.name}'
