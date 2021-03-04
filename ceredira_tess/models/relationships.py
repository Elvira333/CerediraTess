from sqlalchemy import Column, Integer, ForeignKey, Table

from ceredira_tess.database import Base

roles_users = Table('roles_users', Base.metadata,
                    Column('user_id', Integer(), ForeignKey('user.id')),
                    Column('role_id', Integer(), ForeignKey('role.id'))
                    )

roles_agents = Table('roles_agents', Base.metadata,
                     Column('role_id', Integer, ForeignKey('role.id')),
                     Column('agent_id', Integer, ForeignKey('agent.id'))
                     )

agents_scripts = Table('agents_scripts', Base.metadata,
                       Column('agent_id', Integer, ForeignKey('agent.id')),
                       Column('script_id', Integer, ForeignKey('script.id'))
                       )
