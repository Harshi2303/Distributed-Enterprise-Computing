from flask import Flask, request, jsonify, render_template
import pymongo
from bson import ObjectId

app = Flask(__name__)

# Replace <username> and <password> with your MongoDB Atlas credentials
client = pymongo.MongoClient("mongodb+srv://22pw18:Pinkpanther@cluster007.kw3ms.mongodb.net/?retryWrites=true&w=majority&appName=Cluster007")
db = client["stage_events_db"]

# Collections
events_collection = db["events"]
shows_collection = db["shows"]

# Create Event
def create_event(event_name, event_date, event_location, event_description):
    event = {
        "event_name": event_name,
        "event_date": event_date,
        "event_location": event_location,
        "event_description": event_description
    }
    result = events_collection.insert_one(event)
    return str(result.inserted_id)

# Create Show with start_time, end_time, show_date, and show_id
def create_show(event_id, start_time, end_time, show_date, total_tickets):
    show = {
        "event_id": ObjectId(event_id),
        "start_time": start_time,
        "end_time": end_time,
        "show_date": show_date,
        "total_tickets": total_tickets,
        "booked_tickets": 0
    }
    result = shows_collection.insert_one(show)
    return str(result.inserted_id)

# Serve HTML file
@app.route('/')
def index():
    return render_template('index.html')

# Get Events
@app.route('/events', methods=['GET'])
def get_events():
    events = events_collection.find()
    result = []
    for event in events:
        result.append({
            'event_id': str(event['_id']),
            'event_name': event['event_name'],
            'event_date': event['event_date'],
            'event_location': event['event_location'],
            'event_description': event['event_description']
        })
    return jsonify(result), 200

# Get Shows for an Event
@app.route('/events/<event_id>/shows', methods=['GET'])
def get_shows(event_id):
    shows = shows_collection.find({"event_id": ObjectId(event_id)})
    result = []
    for show in shows:
        result.append({
            'show_id': str(show['_id']),
            'event_id': str(show['event_id']),
            'start_time': show['start_time'],
            'end_time': show['end_time'],
            'show_date': show['show_date'],
            'total_tickets': show['total_tickets'],
            'booked_tickets': show['booked_tickets']
        })
    return jsonify(result), 200

# Book Ticket
@app.route('/shows/<show_id>/book', methods=['POST'])
def book_ticket(show_id):
    show = shows_collection.find_one({"_id": ObjectId(show_id)})
    if show and show["booked_tickets"] < show["total_tickets"]:
        shows_collection.update_one(
            {"_id": ObjectId(show_id)},
            {"$inc": {"booked_tickets": 1}}
        )
        return jsonify(show), 200
    else:
        return jsonify({"error": "No more tickets available"}), 400

# New endpoint to fetch all shows
@app.route('/shows', methods=['GET'])
def get_all_shows():
    shows = shows_collection.find()
    result = []
    for show in shows:
        result.append({
            'show_id': str(show['_id']),
            'event_id': str(show['event_id']),
            'start_time': show['start_time'],
            'end_time': show['end_time'],
            'show_date': show['show_date'],
            'total_tickets': show['total_tickets'],
            'booked_tickets': show['booked_tickets']
        })
    return jsonify(result), 200

# Example Usage
if __name__ == "__main__":
    event_1_id = create_event("Rock Concert", "2025-01-10", "Concert Hall", "A thrilling rock concert with amazing performances.")
    event_2_id = create_event("Jazz Night", "2025-02-14", "Music Lounge", "An enchanting evening filled with smooth jazz tunes.")
    event_3_id = create_event("Comedy Show", "2025-03-21", "Comedy Club", "A hilarious night featuring top stand-up comedians.")
    event_4_id = create_event("Theater Play", "2025-04-18", "Grand Theater", "A captivating play performed by talented actors.")

    show_1_id = create_show(event_1_id, "18:00", "20:00", "2025-01-10", 100)
    show_2_id = create_show(event_2_id, "19:00", "21:00", "2025-02-14", 80)
    show_3_id = create_show(event_3_id, "20:00", "22:00", "2025-03-21", 120)
    show_4_id = create_show(event_4_id, "17:00", "19:00", "2025-04-18", 150)

    print(f"Created Event ID 1: {event_1_id}")
    print(f"Created Event ID 2: {event_2_id}")
    print(f"Created Event ID 3: {event_3_id}")
    print(f"Created Event ID 4: {event_4_id}")

    print(f"Created Show ID 1: {show_1_id}")
    print(f"Created Show ID 2: {show_2_id}")
    print(f"Created Show ID 3: {show_3_id}")
    print(f"Created Show ID 4: {show_4_id}")

    app.run(debug=True, port=5001)  # Specify a different port here
