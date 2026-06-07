from geopy.geocoders import Nominatim


def get_zip_code(lat, lon):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.reverse((lat, lon), exactly_one=True, addressdetails=True)

    if location and 'postcode' in location.raw['address']:
        return location.raw['address']['postcode']
    else:
        return None


# Example usage
latitude = 37.7750
longitude = -122.4195
zip_code = get_zip_code(latitude, longitude)
print(f"The ZIP code is: {zip_code}")
