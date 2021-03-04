from datetime import datetime

from flask_security import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship, backref

from ceredira_tess.database import Base
from ceredira_tess.models import relationships


class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    username = Column(String(64), nullable=False, unique=True)
    email = Column(String(255), unique=True)
    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    password = Column(String(150), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    confirmed_at = Column(DateTime())
    active = Column(Boolean())
    roles = relationship("Role", secondary=relationships.roles_users, backref=backref('users', lazy='dynamic'))

    def __repr__(self):
        return f'{self.username}'

    # Required for administrative interface
    def __unicode__(self):
        return self.username

    # def add_role(self, role):
    #     self.roles.append(role)
    #
    # def add_roles(self, roles):
    #     self.roles.extend(roles)
    #
    # def set_password(self, password):
    #     self.password = hash_password(password)
    #
    # def check_password(self, password):
    #     return verify_password(password, self.password)

    # Flask - Login
    # @property
    # def is_authenticated(self):
    #     return True
    #
    # @property
    # def is_active(self):
    #     return True
    #
    # @property
    # def is_anonymous(self):
    #     return False
    #
    # def get_id(self):
    #     return self.id

    # Flask-Security
    # def has_role(self, *args):
    #     return set(args).issubset({role.name for role in self.roles})
