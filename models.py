from pony.orm import Database, Required, Set
from datetime import date

db = Database()

class Apartment(db.Entity):
    name = Required(str)
    location = Required(str)
    description = Required(str)
    image_url = Required(str)
    reservations = Set('Reservation')

class Reservation(db.Entity):
    apartment = Required('Apartment')
    full_name = Required(str)
    num_of_people = Required(int)
    arrival_date = Required(date)
    departure_date = Required(date)

db.bind(provider='sqlite', filename='apartments.sqlite', create_db=True)
db.generate_mapping(create_tables=True)
