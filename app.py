from flask import Flask, render_template, request, redirect, url_for
from pony.orm import db_session, select
from models import Apartment, Reservation
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

navbar_data = [
    {'url': 'dolazak', 'title': 'U dolasku'},
    {'url': 'odlazak', 'title': 'U odlasku'}
]

def format_date(date_obj, date_format):
    if isinstance(date_obj, datetime.date):
        return date_obj.strftime(date_format)
    return ''

app.jinja_env.filters['format_date'] = format_date

@app.route('/')
@db_session
def index():
    apartments = select(a for a in Apartment)[:]
    location_filter = request.args.get('location')
    if location_filter:
        filtered_apartments = select(a for a in Apartment if a.location == location_filter)[:]
    else:
        filtered_apartments = apartments
    return render_template('index.html', apartments=apartments, filtered_apartments=filtered_apartments, endpoint='index', apartment=None)

@app.route('/add_apartment', methods=['GET', 'POST'])
@db_session
def add_apartment():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        description = request.form['description']
        image_url = request.form['image_url']
        Apartment(name=name, location=location, description=description, image_url=image_url)
        return redirect(url_for('index'))
    return render_template('add_apartment.html')

@app.route('/<int:apartment_id>')
@db_session
def manage_apartment(apartment_id):
    apartment = Apartment.get(id=apartment_id)
    reservations = select(r for r in Reservation if r.apartment.id == apartment_id)[:]
    return render_template('manage_apartment.html', apartment=apartment, reservations=reservations)

@app.route('/<int:apartment_id>/delete', methods=['POST'])
@db_session
def delete_apartment(apartment_id):
    apartment = Apartment.get(id=apartment_id)
    if apartment:
        apartment.delete()
    return redirect(url_for('index'))

@app.route('/<int:apartment_id>/add_reservation', methods=['POST'])
@db_session
def add_reservation(apartment_id):
    full_name = request.form['full_name']
    num_of_people = int(request.form['num_of_people'])
    arrival_date = request.form['arrival_date']
    departure_date = request.form['departure_date']
    apartment = Apartment.get(id=apartment_id)
    if apartment:
        Reservation(apartment=apartment, full_name=full_name, num_of_people=num_of_people, arrival_date=arrival_date, departure_date=departure_date)
    return redirect(url_for('manage_apartment', apartment_id=apartment_id))

@app.route('/<int:apartment_id>/reservation/<int:reservation_id>/delete', methods=['POST'])
@db_session
def delete_reservation(apartment_id, reservation_id):
    reservation = Reservation.get(id=reservation_id)
    if reservation:
        reservation.delete()
    return redirect(url_for('manage_apartment', apartment_id=apartment_id))

@app.route('/<int:apartment_id>/reservation/<int:reservation_id>/edit', methods=['GET', 'POST'])
@db_session
def edit_reservation(apartment_id, reservation_id):
    reservation = Reservation.get(id=reservation_id)
    if request.method == 'POST':
        reservation.full_name = request.form['full_name']
        reservation.num_of_people = int(request.form['num_of_people'])
        reservation.arrival_date = request.form['arrival_date']
        reservation.departure_date = request.form['departure_date']
        return redirect(url_for('manage_apartment', apartment_id=apartment_id))
    return render_template('edit_reservation.html', apartment_id=apartment_id, reservation=reservation)

@app.route('/dolazak')
@db_session
def dolazak():
    today = datetime.date.today()
    today_reservations = select(r for r in Reservation if r.arrival_date == today)[:]
    today_apartment_ids = [r.apartment.id for r in today_reservations]
    today_apartments = select(a for a in Apartment if a.id in today_apartment_ids)[:]
    return render_template('dolazak.html', reservations=today_reservations, navbar_data=navbar_data, apartment=today_apartments[0] if today_apartments else None)

@app.route('/odlazak')
@db_session
def odlazak():
    today = datetime.date.today()
    today_reservations = select(r for r in Reservation if r.departure_date == today)[:]
    today_apartment_ids = [r.apartment.id for r in today_reservations]
    today_apartments = select(a for a in Apartment if a.id in today_apartment_ids)[:]
    return render_template('odlazak.html', reservations=today_reservations, navbar_data=navbar_data, apartment=today_apartments[0] if today_apartments else None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
