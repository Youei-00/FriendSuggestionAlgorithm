import streamlit as st
from math import radians, sin, cos, sqrt, atan2
from collections import Counter

# Sample user data
users = {
    "alice": {
        "contacts": {"bob@gmail.com", "eve@gmail.com"},
        "location": (37.7749, -122.4194),
        "friends": {"bob"}
    },
    "bob": {
        "contacts": {"alice@gmail.com"},
        "location": (37.7750, -122.4195),
        "friends": {"alice", "carol"}
    },
    "carol": {
        "contacts": {"dave@gmail.com"},
        "location": (37.7752, -122.4196),
        "friends": {"bob"}
    },
    "eve": {
        "contacts": {"alice@gmail.com"},
        "location": (40.7128, -74.0060),
        "friends": set()
    }
}


def haversine(loc1, loc2):
    if not loc1 or not loc2:
        return float("inf")
    lat1, lon1 = loc1
    lat2, lon2 = loc2
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def suggest_friends(user_id, share_location=True, max_distance_km=10):
    user = users[user_id]
    suggestions = Counter()

    # Contact matches
    for other_id, other in users.items():
        if other_id == user_id or other_id in user["friends"]:
            continue

        score = 0
        if user["contacts"] & other["contacts"]:
            score += 3

        if share_location:
            if haversine(user["location"], other["location"]) <= max_distance_km:
                score += 2

        mutuals = user["friends"] & other["friends"]
        score += len(mutuals)

        if score > 0:
            suggestions[other_id] = score

    return suggestions.most_common()


# Streamlit UI
st.title("🔗 Friend Suggestion System")

user_id = st.selectbox("Select a user", list(users.keys()))
share_location = st.checkbox("Share location", value=True)

if st.button("Suggest Friends"):
    suggestions = suggest_friends(user_id, share_location)

    if suggestions:
        st.subheader("Suggested Friends:")
        for uid, score in suggestions:
            st.write(f"**{uid}** (score: {score})")
    else:
        st.info("No suggestions found.")
