from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from sqlalchemy.sql import func
import bcrypt
from flask_login import current_user, login_user, logout_user, UserMixin, LoginManager, login_required
from datetime import datetime, timedelta
import os
from flask_sqlalchemy import SQLAlchemy
from wtforms import PasswordField
from flask_admin.form import ImageUploadField
from sqlalchemy import func, extract, cast, Date

db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///VerdantDatabase.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static/uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.permanent_session_lifetime = timedelta(days=1)

db = SQLAlchemy(app)

# Initialize other Flask extensions after SQLAlchemy
login = LoginManager(app)
login.login_view = 'login'
admin = Admin(app, name='Verdant Design', template_mode='bootstrap3')
migrate = Migrate(app, db)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")
    reservations = db.relationship("Reservation", back_populates="user")
    memberships = db.relationship("Membership", back_populates="user") 


class Reservation(db.Model):
    __tablename__ = "reservations"  
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reservation_type = db.Column(db.String(50), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)
    availability_id = db.Column(db.Integer, db.ForeignKey("availabilities.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Maintain the foreign key columns in Reservation
    experience_id = db.Column(db.Integer, db.ForeignKey("experiences.id"), nullable=True)
    pairing_id = db.Column(db.Integer, db.ForeignKey("pairings.id"), nullable=True)
    event_package_id = db.Column(db.Integer, db.ForeignKey("event_packages.id"), nullable=True)
    event_add_on_id = db.Column(db.Integer, db.ForeignKey("event_add_ons.id"), nullable=True)
    dining_area_id = db.Column(db.Integer, db.ForeignKey("dining_areas.id"), nullable=True)
    
    # Basic relationships 
    user = db.relationship("User", back_populates="reservations")
    location = db.relationship("Location", back_populates="reservations")
    availability = db.relationship("Availability", back_populates="reservations")
    
    # Updated relationships with explicit foreign_keys
    experience = db.relationship("Experience", back_populates="reservations", foreign_keys=[experience_id])
    pairing = db.relationship("Pairing", back_populates="reservations", foreign_keys=[pairing_id])
    event_package = db.relationship("EventPackage", back_populates="reservations", foreign_keys=[event_package_id])
    event_add_on = db.relationship("EventAddOn", back_populates="reservations", foreign_keys=[event_add_on_id])
    dining_area = db.relationship("DiningArea", back_populates="reservations", foreign_keys=[dining_area_id])
    
    dietary_preferences = db.relationship("DietaryPreference", back_populates="reservation")
    memberships = db.relationship("Membership", back_populates="reservation", foreign_keys="Membership.reservation_id")
    guest_info = db.relationship("GuestInfo", back_populates="reservation")
    
    # added columns to the reservation table to store the total price of each package and addon selected by the user
    total_price = db.Column(db.Integer, nullable=True)
    event_package_price = db.Column(db.Integer, nullable=True)
    dining_area_price = db.Column(db.Integer, nullable=True)
    experience_price = db.Column(db.Integer, nullable=True)
    add_on_price = db.Column(db.Integer, nullable=True)
    pairing_price = db.Column(db.Integer, nullable=True)

class GuestInfo(db.Model):
    __tablename__ = "guest_info"
    id = db.Column(db.Integer, primary_key=True)
    # Add this line to create the foreign key to reservation
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservations.id"), nullable=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    numberofguests = db.Column(db.Integer, nullable=False)
    specialrequests = db.Column(db.String(100), nullable=True)

    # Keep the relationship definition
    reservation = db.relationship("Reservation", back_populates="guest_info")

class Location(db.Model):
    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    operating_hours = db.Column(db.String(50), nullable=True)
    contact_number = db.Column(db.String(15), nullable=True)
    tags1 = db.Column(db.String(50), nullable=True)
    tags2 = db.Column(db.String(50), nullable=True)
    tags3 = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(100), nullable=True)
    availability_status = db.Column(db.Boolean, default=True)
    reservations = db.relationship("Reservation", back_populates="location")

# Standard Dining Availability

class Availability(db.Model):
    __tablename__ = "availabilities"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    reservation_type = db.Column(db.String(50), nullable=False)  # "standard_dining", "chefs_tasting", "private_event"
    reservations = db.relationship("Reservation", back_populates="availability")
    
    @property
    def formatted_start_time(self):
        """Return the start time in 12-hour format with AM/PM."""
        return self.start_time.strftime("%I:%M %p").lstrip("0")

    @property
    def formatted_end_time(self):
        """Return the end time in 12-hour format with AM/PM."""
        return self.end_time.strftime("%I:%M %p").lstrip("0")
    

class DietaryPreference(db.Model):
    __tablename__ = "dietary_preferences"
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservations.id"), nullable=False)
    preference = db.Column(db.String(50), nullable=False)  # "Gluten-Free", "Nut-Free", "Soy-Free", "Raw Options"
    reservation = db.relationship("Reservation", back_populates="dietary_preferences")
    

class Experience(db.Model):
    __tablename__ = "experiences"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    reservations = db.relationship("Reservation", back_populates="experience", foreign_keys="[Reservation.experience_id]")

    

class Pairing(db.Model):
    __tablename__ = "pairings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    # No reservation_id column here
    
    # Change relationship to one-to-many (plural)
    reservations = db.relationship("Reservation", back_populates="pairing", foreign_keys="[Reservation.pairing_id]")

class EventPackage(db.Model):
    __tablename__ = "event_packages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    # No reservation_id column here
    
    # Change relationship to one-to-many (plural)
    reservations = db.relationship("Reservation", back_populates="event_package", foreign_keys="[Reservation.event_package_id]")


class EventAddOn(db.Model):
    __tablename__ = "event_add_ons"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    # No reservation_id column here
    
    # Change relationship to one-to-many (plural)
    reservations = db.relationship("Reservation", back_populates="event_add_on", foreign_keys="[Reservation.event_add_on_id]")


class DiningArea(db.Model):  
    __tablename__ = "dining_areas"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    # No reservation_id column here
    
    # Change relationship to one-to-many (plural)
    reservations = db.relationship("Reservation", back_populates="dining_area", foreign_keys="[Reservation.dining_area_id]")

class Membership(db.Model):
    __tablename__ = "memberships"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    membership_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservations.id"), nullable=True)  # Changed to nullable=True
    user = db.relationship("User", back_populates="memberships")
    reservation = db.relationship("Reservation", back_populates="memberships", foreign_keys=[reservation_id])
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="active")

class MenuItem(db.Model):
    __tablename__ = "menu_items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(100), nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    tag1 = db.Column(db.String(50), nullable=True) 
    tag2 = db.Column(db.String(50), nullable=True) 
    tag3 = db.Column(db.String(50), nullable=True)

class NewsletterSignup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(120), unique=True, nullable=False)
    signup_date = db.Column(db.DateTime, default=datetime.utcnow)

@login.user_loader
def load_user(user_id):
    print("Loading user with ID:", user_id) 
    return User.query.get(int(user_id))

class AvailabilityView(ModelView):
    column_formatters = {
        'start_time': lambda v, c, m, p: m.formatted_start_time,
        'end_time': lambda v, c, m, p: m.formatted_end_time,
    }

class AdminMixin:
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

    def on_model_change(self, form, model, is_created):
        if is_created and hasattr(model, 'creator_id'):
            model.creator_id = current_user.id
        return super(MyModelView, self).on_model_change(form, model, is_created)

class AvailabilityView(AdminMixin, ModelView):
    column_formatters = {
        'start_time': lambda v, c, m, p: m.formatted_start_time,
        'end_time': lambda v, c, m, p: m.formatted_end_time,
    }

class ProductAdminView(MyModelView):
    form_extra_fields = {
        'image_url': ImageUploadField('Image', base_path=app.config['UPLOAD_FOLDER'], allowed_extensions=app.config['ALLOWED_EXTENSIONS'])
    }

class locationAdminView(MyModelView):
    form_extra_fields = {
        'image_url': ImageUploadField('Image', base_path=app.config['UPLOAD_FOLDER'], allowed_extensions=app.config['ALLOWED_EXTENSIONS'])
    }

class UserAdminView(MyModelView):
    column_list = ('id', 'name', 'email', 'phone', 'role')
    form_columns = ('name', 'email', 'phone','role')
    column_searchable_list = ('name', 'email', 'phone')
    column_filters = ('role',)

    form_extra_fields = {
        'new_password': PasswordField('Password')
    }


admin.add_view(ProductAdminView(MenuItem, db.session))
admin.add_view(UserAdminView(User, db.session)) 
admin.add_view(MyModelView(NewsletterSignup, db.session))
admin.add_view(MyModelView(Reservation, db.session))
admin.add_view(locationAdminView(Location, db.session))
admin.add_view(MyModelView(Availability, db.session))
admin.add_view(MyModelView(DiningArea, db.session))  
admin.add_view(MyModelView(Membership, db.session)) 
admin.add_view(MyModelView(Experience, db.session))
admin.add_view(MyModelView(EventAddOn, db.session))
admin.add_view(MyModelView(EventPackage, db.session))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/confirmation/reservation', methods=['GET', 'POST'])
@login_required
def confirmation():
    # Define these variables at the beginning, so they're available for all request methods
    
    selected_location = session.get("selected_location", "Not selected")
    dining_area = session.get('dining_area', "Not selected")
    selected_date = session.get('selected_date', "Not selected")
    selected_time = session.get('selected_time', "Not selected")
    
    # Get the guest info dictionary
    guest_info = session.get('guest_info', {})
    dietary_prefs = session.get('dietaryPreferences', [])
    input_value = session.get('guest_info', {}).get('numberofguests', '1')  # Default to 1 if not provided

    # Convert input_value to integer with fallback
    try:
        guests_count = int(input_value)
    except (ValueError, TypeError):
        guests_count = 1

    # reservation type 
    reservation_type = session.get('reservation_type', 'Not provided')

    # packages and addon that will show in the reservation summary with their price
    dining_area = session.get('dining_area', "Not selected")
    event_package = session.get('event_package', None)
    experience = session.get('experience', None)
    add_on = session.get('add_on', None)

    # Debug what values we have
    print("DEBUG VALUES FROM SESSION:")
    print(f"- reservation_type: '{reservation_type}'")
    print(f"- event_package: '{event_package}'")
    print(f"- experience: '{experience}'")
    print(f"- add_on: '{add_on}'")
    print(f"- guests_count: {guests_count}")

    # Initialize an empty dictionary to store reservation summary
    reservation_summary = {} 
    total_price = 0

    # Calculate costs based on reservation type - case-insensitive comparison
    if reservation_type and "private" in reservation_type.lower() and event_package:
        print(f"Calculating Private Events package for: {event_package}")
        package = EventPackage.query.filter_by(name=event_package).first()
        if package:
            print(f"Found package: {package.name} with price: ${package.price}")
            package_price = package.price
            package_id = package.id
            private_event_total_price = package_price * guests_count
            reservation_summary[package.name] = f"${private_event_total_price:.2f}"
            total_price += private_event_total_price
        else:
            print(f"No package found with name: {event_package}")

    if reservation_type and ("chef" in reservation_type.lower() or "table" in reservation_type.lower()):
        print(f"Calculating Chef's Table Experience for: {experience}")
        if experience:
            experience_data = Experience.query.filter_by(name=experience).first()
            if experience_data:
                print(f"Found experience: {experience_data.name} with price: ${experience_data.price}")
                experience_price = experience_data.price
                experience_id = experience_data.id
                experience_total_price = experience_price * guests_count
                reservation_summary[experience_data.name] = f"${experience_total_price:.2f}"
                total_price += experience_total_price
            else:
                print(f"No experience found with name: {experience}")

        # Handle add-ons - could be a string or a list
        if add_on:
            if isinstance(add_on, list):
                # Handle multiple add-ons
                print(f"Processing multiple add-ons: {add_on}")
                for addon_name in add_on:
                    print(f"Looking up add-on: {addon_name}")
                    addon = EventAddOn.query.filter_by(name=addon_name).first()
                    if addon:
                        print(f"Found add-on: {addon.name} with price: ${addon.price}")
                        add_on_price = addon.price
                        add_on_total_price = add_on_price * guests_count
                        reservation_summary[addon.name] = f"${add_on_total_price:.2f}"
                        total_price += add_on_total_price
                    else:
                        print(f"No add-on found with name: {addon_name}")
            else:
                # Handle single add-on
                addon = EventAddOn.query.filter_by(name=add_on).first()
                if addon:
                    print(f"Found add-on: {addon.name} with price: ${addon.price}")
                    add_on_price = addon.price
                    add_on_total_price = add_on_price * guests_count
                    reservation_summary[addon.name] = f"${add_on_total_price:.2f}"
                    total_price += add_on_total_price
                else:
                    print(f"No add-on found with name: {add_on}")

    if reservation_type and "standard" in reservation_type.lower() and dining_area:
        # Debug the dining area search
        print(f"Searching for dining area with name: '{dining_area}'")
        all_dining_areas = DiningArea.query.all()
        print(f"All available dining areas: {[area.name for area in all_dining_areas]}")
        
        # Use case-insensitive search to find the dining area
        dining = DiningArea.query.filter(DiningArea.name.ilike(f"%{dining_area}%")).first()
        if dining:
            print(f"Found dining area: {dining.name} with price: ${dining.price}")
            dining_price = dining.price
            dining_id = dining.id
            dining_total_price = dining_price * guests_count
            reservation_summary[dining.name] = f"${dining_total_price:.2f}"
            total_price += dining_total_price
        else:
            print(f"No matching dining area found for: {dining_area}")

            reservation_summary["Dining Area"] = "Price not available"

    reservation_summary['Total'] = f"${total_price:.2f}"

    if request.method == 'GET':
        print("All session variables:")
        for key, value in session.items():
            print(f"- {key}: {value}")
            
        print(f"\nGuest info in confirmation route: {guest_info}")
        print(f"Dietary preferences: {dietary_prefs}")
        print(f"Selected value: {input_value}")
        print(f"reservation_type: {reservation_type}")
        print(f"Selected location: {selected_location}")
        print(f"Selected dining area: {dining_area}")
        print(f"Reservation summary: {reservation_summary}")
        
    print(f"Reservation summary type: {type(reservation_summary)}")
    if hasattr(reservation_summary, 'items'):
        print("reservation_summary has items() method")
        for k, v in reservation_summary.items():
            print(f"Key: {k}, Value: {v}")

    # when button is clicked(you know that if you recieve "confirmation button clicked" thru JSON) check for no null values in the reservation summary if there is a null value save it in a variable and return it to the user to select the needed package, addon or info etc....  if not you save everything to the database and redirect to the thank you/ confirmation page
    print(f"Reservation summary type: {type(reservation_summary)}")
    if hasattr(reservation_summary, 'items'):
        print("reservation_summary has items() method")
        for k, v in reservation_summary.items():
            print(f"Key: {k}, Value: {v}")

    # POST request handling - fixed indentation to be at the same level as the GET handler
    if request.method == 'POST':
        btn_status = None
        if request.content_type == 'application/json':
            data = request.get_json()
            btn_status = data.get('btn_status')
            
        if btn_status == "confirmation button clicked":
            # Your validation code...
            missing_info = []
            # Check for required fields
            if not selected_location or selected_location == "Not selected":
                missing_info.append("Location")
            if not selected_date or selected_date == "Not selected":
                missing_info.append("Date")
            if not selected_time or selected_time == "Not selected":
                missing_info.append("Time")
                
            # Check guest info
            required_fields = ["fullName", "emailAddress", "phoneNumber", "numberofguests"]  # FIXED SPELLING
            for field in required_fields:
                if field not in guest_info or not guest_info.get(field):
                    missing_info.append(f"{field}")
                        
            if missing_info:
                return jsonify({"success": False, "missing_info": missing_info}), 400
                
            try:
                # First, get the location object from the database
                location = Location.query.filter_by(name=selected_location).first()
                if not location:
                    return jsonify({"success": False, "message": "Selected location not found"}), 400

                try:
                    availability_id = int(selected_time)
                    availability = Availability.query.get(availability_id)
                    if not availability:
                        availability = None
                except (ValueError, TypeError):
                    # If not a valid ID, try to find by formatted time
                    availability = None
                    
                    # Try multiple time formats
                    time_formats = ['%I:%M %p', '%H:%M', '%I:%M']
                    for fmt in time_formats:
                        try:
                            time_obj = datetime.strptime(selected_time, fmt).time()
                            # Look for availability with matching date AND time
                            availability = Availability.query.filter_by(
                                date=datetime.strptime(selected_date, '%Y-%m-%d').date(),
                                start_time=time_obj,
                                is_available=True
                            ).first()
                            if availability:
                                break
                        except ValueError:
                            continue
                
                # If still not found, give up
                if not availability:
                    return jsonify({
                        "success": False,
                        "message": f"Time slot not available for {selected_date} at {selected_time}."
                    }), 404
                    
                # Check if the time is still available
                if not availability.is_available:
                    return jsonify({
                        "success": False,
                        "message": "Sorry, this time slot has just been booked by someone else. Please select another time."
                    }), 409  # Conflict

                # Handle user authentication - use session user if available, otherwise create a guest user
                user_id = session.get('user_id')
                if not user_id and current_user.is_authenticated:
                    user_id = current_user.id

                # Create guest info record
                guest_info_record = GuestInfo(
                    fullname=guest_info.get('fullName'),
                    email=guest_info.get('emailAddress'),  # Updated from emailAdress to emailAddress
                    phone=guest_info.get('phoneNumber'),
                    numberofguests=int(guest_info.get('numberofguests', 1)),
                    specialrequests=guest_info.get('specialrequests', '')
                )
                db.session.add(guest_info_record)
                db.session.flush() 

                # Create reservation based on type

                user_id = session.get('user_id')
                if not user_id and current_user.is_authenticated:
                    user_id = current_user.id

                if not user_id:
                    user_id = 1 

                if "standard" in reservation_type.lower():
                    dining_area_obj = DiningArea.query.filter(DiningArea.name.ilike(f"%{dining_area}%")).first()
                    dining_area_price = dining_area_obj.price * int(guest_info.get('numberofguests', 1)) if dining_area_obj else 0
                    
                    new_reservation = Reservation(
                        user_id=user_id,
                        reservation_type=reservation_type,
                        location_id=location.id,
                        availability_id=availability.id,
                        dining_area_id=dining_area_obj.id if dining_area_obj else None,
                        dining_area_price=dining_area_price,
                        total_price=total_price,
                        guest_info=[guest_info_record]
                    )

                elif "private" in reservation_type.lower():
                    package_obj = EventPackage.query.filter_by(name=event_package).first()
                    package_price = package_obj.price * int(guest_info.get('numberofguests', 1)) if package_obj else 0
                    
                    new_reservation = Reservation(
                        user_id=user_id,
                        reservation_type=reservation_type,
                        location_id=location.id,
                        availability_id=availability.id,
                        event_package_id=package_obj.id if package_obj else None,
                        event_package_price=package_price,
                        total_price=total_price,
                        guest_info=[guest_info_record]
                    )

                elif "chef" in reservation_type.lower() or "table" in reservation_type.lower():
                    experience_obj = Experience.query.filter_by(name=experience).first()
                    experience_price = experience_obj.price * int(guest_info.get('numberofguests', 1)) if experience_obj else 0
                    
                    # Handle add-ons - properly handling both single string and list values
                    addon_obj = None
                    addon_price = 0
                    
                    if add_on:
                        print(f"Processing add-on: {add_on} (type: {type(add_on)})")
                        
                        if isinstance(add_on, list) and len(add_on) > 0:
                            # For multiple add-ons, just use the first one for now
                            addon_name = add_on[0]
                            print(f"Looking up add-on from list: {addon_name}")
                            addon_obj = EventAddOn.query.filter_by(name=addon_name).first()
                        else:
                            # Single add-on as string
                            print(f"Looking up single add-on: {add_on}")
                            addon_obj = EventAddOn.query.filter_by(name=add_on).first()
                        
                        # Calculate addon price if found
                        if addon_obj:
                            print(f"Found add-on: {addon_obj.name} with price: ${addon_obj.price}")
                            addon_price = addon_obj.price * int(guest_info.get('numberofguests', 1))
                        else:
                            print(f"Add-on not found in database")
                    
                    # Create the reservation with explicit price values
                    new_reservation = Reservation(
                        user_id=user_id or 1,  # Default to user ID 1 if none available
                        reservation_type=reservation_type,
                        location_id=location.id,
                        availability_id=availability.id,
                        experience_id=experience_obj.id if experience_obj else None,
                        experience_price=experience_price,
                        event_add_on_id=addon_obj.id if addon_obj else None,
                        add_on_price=addon_price, 
                        total_price=total_price,
                        guest_info=[guest_info_record]
                    )
                    
                    # Add debugging log 
                    print(f"Created reservation with add-on price: ${addon_price}")

                # Add dietary preferences
                if dietary_prefs:
                    for pref in dietary_prefs:
                        dietary = DietaryPreference(preference=pref)
                        new_reservation.dietary_preferences.append(dietary)
                
                # Save to database
                db.session.add(new_reservation)
                availability.is_available = False
                print(f"Marked availability ID {availability.id} as unavailable")
                db.session.commit()
                
                return jsonify({"success": True, "redirect": url_for('thank_you')})
                
            except Exception as e:
                db.session.rollback()
                print(f"Error creating reservation: {str(e)}")
                return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

    return render_template('Step-5.html', 
                          selected_location=selected_location, 
                          dining_area=dining_area, 
                          selected_date=selected_date, 
                          selected_time=selected_time,
                          guest_info=guest_info,
                          dietary_preferences=dietary_prefs, 
                          input_value=input_value, 
                          reservation_type=reservation_type,
                          event_package=event_package,
                          experience=experience, 
                          add_on=add_on, 
                          reservation_summary=reservation_summary)

""""@app.route('/send')
def send_confirmation_email():

    reservation = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.id.desc()).first()
    guest_infos = GuestInfo.query.filter_by(reservation_id=reservation.id).all() if reservation else []
    user_emails = [guest_info.email for guest_info in guest_infos]
    user_name = guest_infos[0].fullname if guest_infos else "Guest"
    phone_number = guest_infos[0].phone if guest_infos else "Not provided"
    number_of_guests = guest_infos[0].numberofguests if guest_infos else "Not provided"
    special_requests = guest_infos[0].specialrequests if guest_infos else "Not provided"
    reservation_type = reservation.reservation_type if reservation else "Not provided"
    
    message = Message(
        subject="Reservation Confirmation",
        recipients=[user_emails],)
    if current_user.is_authenticated:
        message.body = render_template('email_template.html', name=current_user)
    else:
        message.body = render_template('email_template.html', name="Guest")
    mail.send(message)"""

@app.route('/thank-you')
def thank_you():
    user_id = session.get('user_id')
    if current_user.is_authenticated:
        user_id = current_user.id
    
    # Try to get the reservation from the database
    reservation = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.id.desc()).first()
    
    # If no reservation found in database, use session data
    if not reservation:
        return render_template('confirmation.html',
            Date=session.get('selected_date', 'Not provided'),
            Time=session.get('selected_time', 'Not provided'),
            guests=session.get('guest_info', {}).get('numberofguests', 'Not provided'),
            location=session.get('selected_location', 'Not provided')
        )
    
    # If reservation found, use database data
    else:
        # Get the availability details
        availability = Availability.query.get(reservation.availability_id)
        location = Location.query.get(reservation.location_id)
        
        # Get guest info
        guest_info = reservation.guest_info[0] if reservation.guest_info else None
        
        return render_template('confirmation.html',
            Date=availability.date.strftime('%B %d, %Y') if availability else 'Not provided',
            Time=availability.start_time.strftime('%I:%M %p') if availability else 'Not provided',
            guests=guest_info.numberofguests if guest_info else 'Not provided',
            location=location.name if location else 'Not provided'
        )
    
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    user = User.query.get(current_user.id)
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    status = {reservation.id: reservation.status for reservation in reservations}
    
    # Get detailed information for all reservations
    reservation_details = []
    
    for reservation in reservations:
        location = Location.query.get(reservation.location_id) if reservation.location_id else None
        availability = Availability.query.get(reservation.availability_id) if reservation.availability_id else None
        guest_info = reservation.guest_info[0] if reservation.guest_info else None
        
        # Get specific package details based on reservation type
        package_details = {}
        if reservation.reservation_type and "standard" in reservation.reservation_type.lower():
            if reservation.dining_area_id:
                dining = DiningArea.query.get(reservation.dining_area_id)
                package_details['name'] = dining.name if dining else "Standard Dining"
                package_details['price'] = reservation.dining_area_price or 0
                
        elif reservation.reservation_type and "private" in reservation.reservation_type.lower():
            if reservation.event_package_id:
                package = EventPackage.query.get(reservation.event_package_id)
                package_details['name'] = package.name if package else "Private Event"
                package_details['price'] = reservation.event_package_price or 0
                
        elif reservation.reservation_type and ("chef" in reservation.reservation_type.lower() or "table" in reservation.reservation_type.lower()):
            if reservation.experience_id:
                exp = Experience.query.get(reservation.experience_id)
                package_details['name'] = exp.name if exp else "Chef's Table"
                package_details['price'] = reservation.experience_price or 0
            
            # Add add-on details if any
            if reservation.event_add_on_id:
                addon = EventAddOn.query.get(reservation.event_add_on_id)
                package_details['addon'] = addon.name if addon else "Add-on"
                package_details['addon_price'] = reservation.add_on_price or 0
        
        # Get dietary preferences
        dietary_prefs = [pref.preference for pref in reservation.dietary_preferences] if hasattr(reservation, 'dietary_preferences') else []
        
        # Format date and time
        formatted_date = availability.date.strftime('%B %d, %Y') if availability and hasattr(availability, 'date') else "Not specified"
        formatted_time = availability.formatted_start_time if availability and hasattr(availability, 'formatted_start_time') else "Not specified"
        
        # Create detailed info dictionary
        details = {
            'id': reservation.id,
            'location': location.name if location else "Not specified",
            'date': formatted_date,
            'time': formatted_time,
            'type': reservation.reservation_type or "Standard Reservation",
            'guests': guest_info.numberofguests if guest_info else "Not specified",
            'status': reservation.status or "Pending",
            'total_price': reservation.total_price or 0,
            'package': package_details.get('name', 'None'),
            'package_price': package_details.get('price', 0),
            'dietary_preferences': ', '.join(dietary_prefs) if dietary_prefs else "None",
            'special_requests': guest_info.specialrequests if guest_info and hasattr(guest_info, 'specialrequests') else "None"
        }
        
        # Add add-on if exists
        if 'addon' in package_details:
            details['addon'] = package_details['addon']
            details['addon_price'] = package_details.get('addon_price', 0)
            
        reservation_details.append(details)

    if request.method == 'POST':
        # Handle profile update logic here
        pass
    
    return render_template('profile.html', user=user, reservations=reservation_details , status=status )

@app.route('/location/reservation', methods=['GET', 'POST'])
@login_required
def location(): 
    locations = Location.query.all()
    reservation_type = session.get('reservation_type', '')
    
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = request.get_json()
                if data and 'location_name' in data:
                    session["selected_location"] = data.get("location_name")
                    print("Selected location name:", data.get("location_name"))
                    return jsonify({"success": True, "message": "Location selected successfully"}), 200
                else:
                    return jsonify({"success": False, "message": "Missing location data"}), 400
            except Exception as e:
                print(f"Error processing JSON: {str(e)}")
                return jsonify({"success": False, "message": "Error processing request"}), 500
        else:
            return jsonify({"success": False, "message": "Invalid content type. Please send JSON data."}), 400
        
    return render_template('step.html', locations=locations, reservation_type=reservation_type)

@app.route('/type/reservation', methods=['GET', 'POST'])
@login_required
def reservation_type():
    if request.method == 'POST': 
        if not request.is_json:
            return jsonify({"message": "Invalid content type. Please send JSON data.", "success": False}), 400
        data = request.get_json()
        reservation_type = data.get('type')

        if not reservation_type:
            return jsonify({"message": "Missing reservation type data", "success": False}), 400
        
        session['reservation_type'] = reservation_type
        print(f"Selected reservation type: {reservation_type}")
        return jsonify({"message": reservation_type, "success": True})
    return render_template('make-res.html')

@app.route('/event_packages/reservation', methods=['GET', 'POST'])
def event_packages():
    if request.method == 'POST':
        data = request.json
        event_package = data.get('package')

        if not event_package:
            return jsonify({"message": "Missing event package data", "success": False}), 400
        
        print(f"Selected event package: {event_package}")
        session['event_package'] = event_package

        return jsonify({"message": event_package, "success": True})
    return render_template('event-packages.html')

@app.route('/experience/reservation', methods=['GET', 'POST'])
def experience(): 
    if request.method == 'POST':
        data = request.json
        experience = data.get('experience', None)
        add_on = data.get('add_on', None)

        if request.is_json:
            if not experience and not add_on:
                return jsonify({"message": "Missing experience or add-on data", "success": False}), 400

            if experience:
                session['experience'] = experience
                print(f"Selected experience: {experience}")

            if add_on:
                session['add_on'] = add_on
                print(f"Selected add-on: {add_on}")

            return jsonify({"message": "Experience and/or add-on selected successfully", "success": True})
        else:
            return jsonify({"message": "Invalid content type. Please send JSON data.", "success": False}), 400

    return render_template('experience.html')


@app.route('/dining-area/reservation', methods=['GET', 'POST'])
def reserve_dining_area():
    if request.method == 'POST':
        data = request.json
        dining_area = data.get('dining_area')

        if not dining_area:
            return jsonify({"message": "Missing dining area data", "success": False}), 400

        # Save the selected dining area to the session
        session['dining_area'] = dining_area

        return jsonify({"message": dining_area, "success": True})
    return render_template('step2.html')

@app.route('/get-available-times')
def get_available_times():
    date = request.args.get('date')
    
    print(f"Received date: {date}")
    
    if not date:
        print("No date provided")
        return jsonify({"times": []})

    try:
        parsed_date = datetime.strptime(date, '%Y-%m-%d').date()
        print(f"Parsed date: {parsed_date}")

        # Debug: Print all database records
        all_availabilities = Availability.query.filter_by(is_available=True).all()
        print(f"Total availabilities in database: {len(all_availabilities)}")
        
        for avail in all_availabilities:
            print(f"Availability record: Date={avail.date}, Start Time={avail.start_time}, End Time={avail.end_time}, Available={avail.is_available}")

        # Query for availabilities
        availabilities = Availability.query.filter_by(date=parsed_date, is_available=True).all()
        print(f"Found {len(availabilities)} available slots for {parsed_date}")

        # If no availabilities, explicitly return an empty list
        if not availabilities:
            print("No availabilities found for this date")
            return jsonify({"times": []})

        # Convert availabilities to slots
        available_slots = []
        for availability in availabilities:
            slot = {
                'start_time': availability.start_time.strftime('%I:%M %p'),
                'id': availability.id
            }
            print(f"Formatted slot: {slot}")
            available_slots.append(slot)

        return jsonify({"times": available_slots})

    except ValueError as e:
        print(f"Error parsing date: {e}")
        return jsonify({"times": [], "error": "Invalid date format"})

# Create a separate route to render the template
@app.route('/date-and-time')
@login_required
def date_and_time_page():
    reservation_type = session.get('reservation_type', '')
    return render_template('date&time-3.html', reservation_type=reservation_type)

@app.route('/select-time', methods=['POST'])
@login_required
def select_time():
    # Ensure the request is a POST request
    if request.method != 'POST':
        return jsonify({"success": False, "message": "Invalid request method"}), 405  # Method Not Allowed

    # Get the JSON data sent from the frontend
    data = request.get_json()

    # Check if data is provided
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    # Extract date and time from the data
    date = data.get('date')
    time = data.get('time')  # This will be None if only the date is sent

    # Validate that the date is provided
    print(f"Picked Date: {date}, Picked Time: {time}")
    all_availabilities = Availability.query.all()
    print(f"Total availabilities in database: {len(all_availabilities)}")
    if not date:
        return jsonify({"success": False, "message": "Date is required"}), 400

    # Store the selected date and time in the session
    session['selected_date'] = date
    if time:
        session['selected_time'] = time

    # Return a success response
    return jsonify({
        "success": True,
        "message": "Date and time selected successfully",
        "date": date,
        "time": time
    }), 200


@app.route('/details/reservation', methods=['GET', 'POST'])
@login_required
def reservation_details():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            field = data.get('field')
            input_value = data.get('inputValue')
            selected_value = data.get('selectedValue')
            dietary_preferences = data.get('dietaryPreferences')

            selected_location = session.get("selected_location", "Not selected")
            dining_area = session.get('dining_area', "Not selected")
            selected_date = session.get('selected_date', "Not selected")
            selected_time = session.get('selected_time', "Not selected")
            print(f"Passing to template - Location: {selected_location}, Area: {dining_area}, Date: {selected_date}, Time: {selected_time}")

                
            print(f"Received data: field={field}, input_value={input_value}, selected_value={selected_value}")
            if dietary_preferences:
                print(f"Received dietary preferences: {dietary_preferences}")
            
            if 'guest_info' not in session:
                session['guest_info'] = {}
            
            # Handle regular form fields
            if field == 'fullName':
                session['guest_info']['fullName'] = input_value
            elif field == 'emailAddress':  # Fix the spelling - was 'emailAdress'
                session['guest_info']['emailAddress'] = input_value
            elif field == 'phone':
                session['guest_info']['phoneNumber'] = input_value
            elif field == 'guests':
                session['guest_info']['numberofguests'] = selected_value or input_value
            elif field == 'specialRequests':
                session['guest_info']['specialrequests'] = input_value
            elif field == 'diet':
                # If we received dietary preferences, replace the entire array
                if dietary_preferences:
                    session['dietaryPreferences'] = dietary_preferences

            session.modified = True
            
            """        # Debug prints
            print(f"Updated session guest info: {session.get('guest_info', {})}")
            print(f"Updated session dietary preferences: {session.get('dietaryPreferences', [])}")
            """
            
            return jsonify({
                "success": True,
                "message": f"Data for {field} saved successfully"
            })

    selected_location = session.get("selected_location", "Not selected")
    dining_area = session.get('dining_area', "Not selected")
    selected_date = session.get('selected_date', "Not selected")
    selected_time = session.get('selected_time', "Not selected")
    guest_info_data = session.get('guest_info', {})
    dietary_prefs = session.get('dietaryPreferences', [])
    return render_template('details-4.html', guest_info=guest_info_data, dietary_preferences=dietary_prefs, selected_location=selected_location, dining_area=dining_area, selected_date=selected_date, selected_time=selected_time)



@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        
        print(f"Received form data: {name}, {email}, {phone}")
        
        if password != confirm_password:
            error = "Passwords do not match."
            return render_template("signup.html", error=error)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            if User.query.filter((User.email == email)).first():
                error = "Email already exists. Please try another."
                return render_template("signup.html", error=error)

            new_user = User(name=name, email=email, password_hash=hashed_password, phone=phone)
            
            db.session.add(new_user)
            db.session.commit()
            print(f"User created: {new_user.id}, {new_user.name}")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user: {e}")
            error = "An error occurred while creating your account. Please try again."
            return render_template("signup.html", error=error)

    return render_template("signup.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        
        print(f"Attempting login with: {email}")
        
        user = User.query.filter_by(email=email).first()
        
        if user is None:
            flash("Invalid email or password.", "danger")
            return render_template("Login.html")  # FIXED: removed "templates\"

        try:
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
                session['user_id'] = user.id
                login_user(user)
                flash("Logged in successfully!", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid email or password.", "danger")
                return render_template("Login.html") # FIXED: removed "templates\"
        except Exception as e:
            print(f"Login error: {e}")
            flash("Invalid email or password.", "danger")
            return render_template("Login.html")  # FIXED: removed "templates\"
    return render_template("Login.html")

"""@app.route('/staff/reservation', methods=['GET', 'POST'])
@login_required
def staff_reservation():
    if current_user.role != 'admin':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home_page'))
    
    reservations = []
    selected_date = None  
    if request.method == 'POST':
        select_date_str = request.form.get('selected_date')
        if select_date_str:
            selected_date = datetime.strptime(select_date_str, '%Y-%m-%d').date()

            
            reservations = Reservation.query.join(Availability).filter(
                Availability.date == selected_date
            ).all()

            
            reservations_details = []
            for reservation in reservations:
                user = User.query.get(reservation.user_id)  
                reservations_details.append({
                    "id": reservation.id,
                    "user_name": user.name if user else "N/A",
                    "number_of_guests": reservation.number_of_guests,
                    "special_requests": reservation.special_requests,
                    "start_time": reservation.availability.formatted_start_time,
                    "end_time": reservation.availability.formatted_end_time,
                    "status": reservation.status,
                })

            reservations = reservations_details  

    return render_template('staff_reservations.html', reservations=reservations, selected_date=selected_date)
"""


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    products = MenuItem.query.all()

    return render_template("menu.html", products=products)

@app.route('/contact_us', methods=['GET', 'POST'])
def contact():
    return render_template('contact-page.html')

@app.route('/about_us', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/references', methods=['GET', 'POST'])
def references():  # Updated spelling
    return render_template('reference-page.html')  

@app.route('/reservations')
@login_required
def get_reservations():
    if current_user.role != 'admin':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home'))
    
    try:
        reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
        reservation_data = []
        
        for res in reservations:
            # Safely get values with fallbacks
            guest_name = "Unknown"
            if res.user:
                guest_name = res.user.name
            
            date = "Unknown"
            if res.created_at:
                date = res.created_at.strftime('%Y-%m-%d %H:%M')
            
            party_size = "Unknown"
            if res.guest_info and len(res.guest_info) > 0:
                party_size = str(res.guest_info[0].numberofguests)
            
            # Build dictionary with only simple types
            reservation_data.append({
                "id": res.id,
                "guest_name": guest_name,
                "date": date,
                "status": res.status or "Unknown",
                "total_price": float(res.total_price) if res.total_price is not None else 0,
                "party_size": party_size
            })
        
        return render_template('reservations.html', reservations=reservation_data)
    
    except Exception as e:
        import traceback
        print(f"Error in reservations endpoint: {str(e)}")
        print(traceback.format_exc())  # Print the full stack trace for debugging
        flash("Failed to retrieve reservations.", "danger")
        return redirect(url_for('home'))


@app.route('/debug/template-path')
def debug_template_path():
    import os
    from flask import current_app
    
    template_folder = current_app.template_folder
    static_folder = current_app.static_folder
    root_path = current_app.root_path
    
    templates_exist = os.path.exists(template_folder)
    templates_list = os.listdir(template_folder) if templates_exist else []
    
    return jsonify({
        'template_folder': template_folder,
        'templates_exist': templates_exist,
        'templates_list': templates_list,
        'static_folder': static_folder,
        'root_path': root_path
    })

@app.route('/logout')
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('home'))

@app.route('/', methods=['GET', 'POST'] )
@app.route('/home_page', methods=['GET', 'POST'])
def home():
    featured_products = MenuItem.query.filter_by(is_featured=1).all()
    regular_products = MenuItem.query.filter_by(is_featured=0).all()
    return render_template('main-page.html', featured_products=featured_products, regular_products=regular_products)

if __name__ == '__main__':
  app.run()