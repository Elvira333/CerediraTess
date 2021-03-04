import config

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(config.Config.SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from ceredira_tess.models.agent import Agent
    from ceredira_tess.models.operation_system_type import OperationSystemType
    from ceredira_tess.models.role import Role
    from ceredira_tess.models.script import Script
    from ceredira_tess.models.user import User
    from ceredira_tess.models import relationships

    Base.metadata.create_all(bind=engine)
