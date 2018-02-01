from sqlalchemy import Column, ForeignKey, Integer, String
from slqalchemy.ext.declarative import declarative_base
from sqlalcemy.orm import relationship
from slqalchemy import create_engine


Base = declarative_base()

class Users(Base):
    __tablename__= 'users'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
            'picture': self.picture
        }


class Brewery(Base):
    __tablename__ = 'brewery'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    user_id = Column(Integer, ForeignKey('users'))
    user = relationship(Users)

    @property
    def serialize():
        return {
            'name': self.name,
            'id': self.id
        }

class Beer(Base):
    __tablename__ = 'beer'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    description = Column(String(250))
    style = Column(String(80))
    user_id = Column(Integer, ForeignKey('users'))
    user = relationship(Users)
    brewery_id = Column(Integer, ForeignKey('brewery'))
    brewery = relationship(Brewery)

    @property
    def serialize():
        return {
            'name': self.name,
            'id': self.name,
            'style': self.style,
            'description': self.description
        }


engine = create_engine('sqlite:///brewerycatalog.db')
Base.metadata.create_all(engine)
