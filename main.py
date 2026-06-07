import math
from collections import defaultdict, Counter
from time import sleep
from geopy.geocoders import Nominatim
import csv


class User:
    def __init__(self, email, password, name, contacts=None, location=None, interests=None, zip_code=None):
        self.email = email
        self.name = name
        self.password = password
        self.contacts = contacts if contacts else set()
        self.location = location  # (latitude, longitude)
        self.zip_code = zip_code
        self.friends = set()
        self.interests = set(interests) if interests else set()


class SocialNetwork:
    def __init__(self):
        self.users = {}
        self.contact_map = defaultdict(set)

    def add_user(self, user: User):
        self.users[user.email] = user
        for contact in user.contacts:
            self.contact_map[contact].add(user.email)

    def add_friendship(self, email1, email2):
        self.users[email1].friends.add(email2)
        self.users[email2].friends.add(email1)

    def remove_friendship(self, email1, email2):
        self.users[email1].friends.remove(email2)
        self.users[email2].friends.remove(email1)

    def get_distance(self, loc1, loc2):
        # Haversine formula to calculate distance between two lat/lng points
        if not loc1 or not loc2:
            return float('inf')
        lat1, lon1 = loc1
        lat2, lon2 = loc2
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def load_users_from_csv(self, file_path):
        geolocator = Nominatim(user_agent="geoapi")

        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                email = row['email']
                password = row['password']
                name = row['full_name']
                contacts = set(row['contacts'].split(';')) if row['contacts'] else set()
                interests = set(row['interests'].split(';')) if row['interests'] else set()

                # Parse existing location fields
                lat = float(row['latitude']) if row['latitude'] else None
                lon = float(row['longitude']) if row['longitude'] else None
                zip_code = row['zip_code'] if row['zip_code'] else None
                location = (lat, lon) if lat is not None and lon is not None else None

                # Only geocode if either location or zip_code is missing
                if (not location or not zip_code) and location:
                    try:
                        loc = geolocator.reverse((lat, lon), exactly_one=True, addressdetails=True, timeout=10)
                        if loc and 'postcode' in loc.raw['address']:
                            zip_code = loc.raw['address']['postcode']
                        sleep(1)  # Respect rate limits
                    except Exception as e:
                        print(f"Error geocoding {email}: {e}")

                user = User(email, password, name, contacts, location, interests, zip_code)
                self.add_user(user)

    def save_users_to_csv(self, file_path):
        fieldnames = ['email', 'password', 'full_name', 'contacts', 'latitude', 'longitude', 'interests', 'zip_code']
        with open(file_path, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for user in self.users.values():
                writer.writerow({
                    'email': user.email,
                    'password': user.password,
                    'full_name': user.name,
                    'contacts': ';'.join(user.contacts),
                    'latitude': user.location[0] if user.location else '',
                    'longitude': user.location[1] if user.location else '',
                    'interests': ';'.join(user.interests),
                    'zip_code': user.zip_code or ''
                })


    def suggest_friends(self, email, share_location=True, max_distance_km=10):
        user = self.users[email]
        suggestions = Counter()
        # From contacts
        """for friendInApp in self.findFriendsBFS(email):
            suggestions[friendInApp] += 1"""
        for contact in user.contacts:
            for other_email in self.contact_map[contact]:
                if other_email != email and other_email not in user.friends:
                    suggestions[other_email] += 3  # higher weight for contact match
        # From location
        if share_location and user.location:
            for other_user in self.users.values():
                if other_user.email != email and other_user.email not in user.friends:
                    dist = self.get_distance(user.location, other_user.location)
                    if dist <= max_distance_km:
                        suggestions[other_user.email] += 2
        # From mutual friends
        for friend_id in user.friends:
            mutual_friend = self.users[friend_id]
            for friend_of_friend in mutual_friend.friends:
                if friend_of_friend != email and friend_of_friend not in user.friends:
                    suggestions[friend_of_friend] += 1
        # Gets suggestion points for user based on interests
        for other_user in self.users.values():
            if other_user.email != email and other_user.email not in user.friends:
                suggestions[other_user.email] += (len(other_user.interests.intersection(user.interests)))
        # Return suggestions sorted by priority
        return suggestions.most_common()

    # Searches for friends of friends in app
    """def findFriendsBFS(self, email):
        res = []
        queue = Queue()
        queue.enqueue((email, 0))
        visited = {email}
        while not queue.isEmpty():
            current, depth = queue.dequeue()
            print(current)
            if depth == 2:
                res.append(current)
            if depth < 2:
                for x in self.users[current].friends:
                    if x not in visited:
                        visited.add(x)
                        queue.enqueue((x, depth+1))
        return res"""

    # creates a new user that can be identified by userID
    def createNewUser(self, email, password, name, contacts, location, interests):
        if email not in network.users:
            network.add_user(User(email, password, name, contacts, location, interests))
        else:
            return 0

    # searches for users by email
    def search_by_email(self, email):
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    # searches for users by username
    def search_by_username(self, username):
        return self.users.get(username, None)


# Example usage:
network = SocialNetwork()
network.load_users_from_csv("user_dataset.csv")

# suggestions = network.suggest_friends("emily.harris@example.com")
# for email, score in suggestions:
#     print(f"Suggested: {email}, Score: {score}")
"""bob = User("bob", contacts={"emily.harris@example.com"}, location=(37.7750, -122.4195))
carol = User("carol", contacts={"dave@gmail.com"}, location=(37.7752, -122.4196))
eve = User("eve", contacts={"emily.harris@example.com"}, location=(40.7128, -74.0060))"""  # far away

# Add users to network
"""for user in [alice, bob, carol, eve]:
    network.add_user(user)"""

# Add friendships
"""network.add_friendship("alice", "bob")
network.add_friendship("bob", "carol")"""

# Get friend suggestions for Alice
"""print("Friend suggestions for Alice:")
suggestions = network.suggest_friends("alice")
for email, score in suggestions:
    print(f"{email} (score: {score})")
print(alice.friends)"""
network.createNewUser("bob@gmail.com", "a", "bob", contacts={"emily.harris@example.com"}, location=(37.7750, -122.4195),
                      interests=("sports", "music", "art"))
network.add_friendship("emily.harris@example.com", "bob@gmail.com")

print(network.users["emily.harris@example.com"].name, network.users["emily.harris@example.com"].email,
      network.users["emily.harris@example.com"].password, network.users["emily.harris@example.com"].location,
      network.users["emily.harris@example.com"].interests, network.users["emily.harris@example.com"].contacts,
      network.users["emily.harris@example.com"].zip_code, network.users["emily.harris@example.com"].friends if
      network.users["emily.harris@example.com"].contacts else "No Friends")

if "" in network.users:
    user = network.users["bob@gmail.com"]
    print(user.email, user.name, user.contacts, user.location, user.interests,
          user.friends if user.friends else "No Friends")
suggestions = network.suggest_friends("emily.harris@example.com")
network.save_users_to_csv("user_dataset_with_zip.csv")
