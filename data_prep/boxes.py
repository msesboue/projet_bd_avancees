import json

with open("pistes_cyclables.json", "r") as read_file:
    data = json.load(read_file)
    
data[0]['geometry']['coordinates'][0]