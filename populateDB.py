from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Users, Brewery, Beer, Base

engine = create_engine('sqlite:///brewerycatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Delete all items in the Brewery table
allBreweries = session.query(Brewery).all()
for brewery in allBreweries:
    session.delete(brewery)
    session.commit()

# Delete all items in Beers table
allBeers = session.query(Beer).all()
for beer in allBeers:
    session.delete(beer)
    session.commit()

# Delete all items in the Users table
allUsers = session.query(Users).all()
for users in allUsers:
    session.delete(users)
    session.commit()


originalUser = Users(name='Preston Doris',
    email = 'prestondoris@gmail.com',
    picture='https://lh4.googleusercontent.com/-Hs9d2xbVGlA/AAAAAAAAAAI/AAAAAAAAAFw/CO3e-KX2o5Y/photo.jpg')
session.add(originalUser)
session.commit()


# Add Breweries to the DB
# Brewery 1
brewery1 = Brewery(name='21st Amendment Brewery', user_id=1)
session.add(brewery1)
session.commit()
# Brewery 1 Beers
b1beer1 = Beer(
    name = 'Brew Free! or Die IPA',
    description = '''BREW FREE! OR DIE IPA is brewed with some serious west
        coast attitude. This aromatic golden IPA starts with three different
        hops to the nose, quickly balanced by a solid malt backbone supporting
        the firm bitterness. Our top selling beer at the pub, this IPA starts
        big and finishes clean leaving you wanting more.''',
    style = 'IPA',
    brewery_id = 1,
    brewery = brewery1,
    user_id=1
)
session.add(b1beer1)
session.commit()

b1beer2 = Beer(
    name = 'Blah Blah Blah Imperial IPA',
    description = '''We are huge fans of IPA and love our hops like anyone else,
        but we also like to have fun. Our Blah Blah Blah IPA is a
        tongue-in-cheek commentary on the popularity of this style and all the
        sub-styles that have become part of craft beer conversations and
        offerings.''',
    style = 'IPA',
    brewery_id = 1,
    brewery = brewery1,
    user_id=1
)
session.add(b1beer2)
session.commit()

b1beer3 = Beer(
    name = 'Hell or High Watermelon Wheat',
    description = '''Like Lady Liberty, we stand for independence and
            perseverance. In the pursuit of innovative beer, there is no
            obstacle too great. No journey too long. No fruit too gigantic.
            This American wheat beer is brewed with real watermelon, for a
            flavor that's surprisingly crisp, dry and refreshing summer
            in a can.''',
    style = 'Wheat Beer',
    brewery_id = 1,
    brewery = brewery1,
    user_id=1
)
session.add(b1beer3)
session.commit()

brewery2 = Brewery(name='Sierra Nevada', user_id=1)
session.add(brewery2)
session.commit()
# Brewery 2 Beers
b2beer1 = Beer(
    name = 'Pale Ale',
    description = '''Pale Ale began as a home brewer's dream, grew into an icon,
        and inspired countless brewers to follow a passion of their own. Its
        unique piney and grapefruit aromas from the use of whole-cone American
        hops have fascinated beer drinkers for decades and made this beer a
        classic, yet it remains new, complex and surprising to thousands of
        beer drinkers every day. It is all natural, bottle conditioned and
        refreshingly bold. ''',
    style = 'Pale Ale',
    brewery_id = 2,
    brewery = brewery2,
    user_id=1
)
session.add(b2beer1)
session.commit()

b2beer2 = Beer(
    name = 'Torpedo IPA',
    description = '''Sierra Nevada and hops go hand in hand. What began as a
        crazy idea scribbled in a pub eventually became our newest year-round
        hop bomb, Torpedo Extra IPA. The first beer to feature our
        "Hop Torpedo"-a revolutionary dry-hopping device that controls how much
        hop aroma is imparted into beer without adding additional bitterness.
        Torpedo Extra IPA is an aggressive yet balanced beer with massive hop
        aromas of citrus, pine, and tropical fruit.''',
    style = 'IPA',
    brewery_id = 2,
    brewery = brewery2,
    user_id=1
)
session.add(b2beer2)
session.commit()

b2beer3 = Beer(
    name = 'Stout',
    description = '''Before Sierra Nevada was a reality, our founders brewed
    beer at home and dreamed of building a brewery one day. Back then, they
    brewed the beers they wanted to drink-bold and full of flavor. Stouts had
    always been a favorite, so when we needed a big and rich beer to test out
    the brewing system at our fledgling brewery, stout was the obvious choice.
    Thirty years later, not much has changed. We're still brewing the beers we
    want to drink and our classic Stout is the same as it's ever been-big,
    rich, bold, black as night and filled with the wild-eyed passion of which
    dreams are made.''',
    style = 'Stout',
    brewery_id = 2,
    brewery = brewery2,
    user_id=1
)
session.add(b2beer3)
session.commit()


brewery3 = Brewery(name='Faction', user_id=1)
session.add(brewery3)
session.commit()
# Brewery 3 beers
b3beer1 = Beer(
    name = 'Pale Ale',
    description = 'Year-round pale ale generously hopped with Simcoe, Columbus and Mosaic',
    style = 'Pale Ale',
    brewery_id = 3,
    brewery = brewery3,
    user_id=1
)
session.add(b3beer1)
session.commit()

b3beer2 = Beer(
    name = 'A-Town Pale',
    description = 'American style Pale Ale hopped with Cascade,Simcoe and Centennial. Only available in Alameda',
    style = 'Pale Ale',
    brewery_id = 3,
    brewery = brewery3,
    user_id=1
)
session.add(b3beer2)
session.commit()

b3beer3 = Beer(
    name = 'McCrary Pale- Maiden Voyage ',
    description = 'Pale ale brewed with Admiral Maltings Maiden Voyage malt ',
    style = 'Pale Ale',
    brewery_id = 3,
    brewery = brewery3,
    user_id=1
)
session.add(b3beer3)
session.commit()

brewery4 = Brewery(name='Stone', user_id=1)
session.add(brewery4)
session.commit()
# Brewery 4 beers
b4beer1 = Beer(
    name = 'IPA',
    description = '''One of the most well-respected and best-selling IPAs
        in the country, this golden beauty explodes with tropical, citrusy,
        piney hop flavors and aromas, all perfectly balanced by a subtle malt
        character. This crisp, extra hoppy brew is hugely refreshing on a hot
        day, but will always deliver no matter when you choose to drink it.''',
    style = 'IPA',
    brewery_id = 4,
    brewery = brewery4,
    user_id=1
)
session.add(b4beer1)
session.commit()

b4beer2 = Beer(
    name = 'Ruination Double IPA',
    description = '''We employ dry hopping and hop bursting to squeeze every
        last drop of piney, citrusy, tropical essence from the hops that give
        this beer its incredible character. We've also updated the name to
        Stone Ruination Double IPA 2.0 to reflect the imperial-level intensity
        that's evident in every sip. Join us in cheering this, the second stanza
        in our "Liquid Poem to the Glory of the Hop." ''',
    style = 'Double IPA',
    brewery_id = 4,
    brewery = brewery4,
    user_id=1
)
session.add(b4beer2)
session.commit()

b4beer3 = Beer(
    name = 'Go To IPA',
    description = '''For Stone Go To IPA, we embrace our hop obsession in a new
        way, funneling an abundance of lupulin-borne bitterness into a session
        IPA that delivers all the fruity, piney character of a much
        bigger IPA. ''',
    style = 'Session IPA',
    brewery_id = 4,
    brewery = brewery4,
    user_id=1
)
session.add(b4beer3)
session.commit()

brewery5 = Brewery(name='Lagunitas', user_id=1)
session.add(brewery5)
session.commit()
# Brewery 5 beers
b5beer1 = Beer(
    name = 'IPA',
    description = 'A well-rounded, highly drinkable IPA. A bit of Caramel Malt barley provides the richness that mellows out the twang of the hops.',
    style = 'IPA',
    brewery_id = 5,
    brewery = brewery5,
    user_id=1
)
session.add(b5beer1)
session.commit()

b5beer2 = Beer(
    name = '12th of Never Ale',
    description = '''The magical, mystical 12th of Never is a blend of Old and
        New School hops that play bright citrus, rich coconut, and papaya-esque
        flavors, all on a solid stage of English puffed wheat. Tropically hoppy.
        Light, yet full-bodied. Bright and citrusy. The 12th of Never Ale is
        everything we've learned about making hop-forward beer expressed in a
        moderate voice. Pale, cold, slightly alcoholic and bitter.
        It's all we know.''',
    style = 'Pale Ale',
    brewery_id = 5,
    brewery = brewery5,
    user_id=1
)
session.add(b5beer2)
session.commit()

b5beer3 = Beer(
    name = 'Pils',
    description = '''Our only Unlimited Lager, brewed with loads of imported
        Saaz hops and a bottom-fermenting yeast strain that leaves it Light and
        Crisp and Easy to Slam, yet full of real flavor and all the things
        you yearn for.''',
    style = 'Pilsner',
    brewery_id = 5,
    brewery = brewery5,
    user_id=1
)
session.add(b5beer3)
session.commit()
