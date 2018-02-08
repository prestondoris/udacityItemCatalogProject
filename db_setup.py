from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()

# Creates the Users table
class Users(Base):
    __tablename__= 'users'

    # The email and picture will be pulled from the google signin through OAuth
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))

    # method for API endpoint
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

    # This uses the user id as a ForeignKey to allow people to update/delete
    # items that they created.
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(Users)
    beer = relationship(Beer, cascade='all, delete_orphan')

    # method for API endpoint
    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
        }

class Beer(Base):
    __tablename__ = 'beer'

    # This uses the user id as a ForeignKey to allow people to update/delete
    # items that they created. This uses the brewery id as a ForeignKey to
    # identify which brewery it belongs to.
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    description = Column(String(250))
    style = Column(String(80))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(Users)
    brewery_id = Column(Integer, ForeignKey('brewery.id'))
    brewery = relationship(Brewery)

    # method for API endpoint
    @property
    def serialize(self):
        return {
            'brewery': self.brewery.serialize,
            'name': self.name,
            'id': self.id,
            'style': self.style,
            'description': self.description
        }


engine = create_engine('sqlite:///brewerycatalog.db')
Base.metadata.create_all(engine)
