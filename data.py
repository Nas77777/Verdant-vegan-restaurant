from app import db
from app import DietaryPreference, Experience, Pairing, EventPackage, EventAddOn

def populate_initial_data():    
    # Add dietary preferences
    dietary_preferences = [
        DietaryPreference(preference="Gluten-Free"),
        DietaryPreference(preference="Nut-Free"),
        DietaryPreference(preference="Soy-Free"),
        DietaryPreference(preference="Raw Options")
    ]
    
    db.session.bulk_save_objects(dietary_preferences)

    # Add experiences
    experiences = [
        Experience(name="Signature Journey", price=125),
        Experience(name="Cooking Class", price=95)
    ]
    db.session.bulk_save_objects(experiences)

    # Add pairings
    pairings = [
        Pairing(name="Caviar Service", price=85),
        Pairing(name="Artisanal Cheese Board", price=65)
    ]
    db.session.bulk_save_objects(pairings)

    # Add event packages
    event_packages = [
        EventPackage(name="Premium", price=125),
        EventPackage(name="Essential", price=75),
        EventPackage(name="Luxury", price=195)
    ]
    db.session.bulk_save_objects(event_packages)

    # Add event add-ons
    event_add_ons = [
        EventAddOn(name="Beverage Station", price=1300),
        EventAddOn(name="Premium Décor", price=2600),
        EventAddOn(name="Photographer", price=1600)
    ]
    db.session.bulk_save_objects(event_add_ons)

    db.session.commit()

# Call the function to populate data
populate_initial_data()