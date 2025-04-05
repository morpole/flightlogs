import requests
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("AVIATIONSTACK_API_KEY")
if not api_key:
    print("Error: AVIATIONSTACK_API_KEY not found in .env file")
    exit(1)

# API endpoint for flights
url = "http://api.aviationstack.com/v1/flights"

# Parameters: flights arriving at DUB
params = {
    "access_key": api_key,
    "arr_iata": "DUB",  # Arrivals at Dublin Airport
    "limit": 10  # Limit to 10 results
}

# Make the request
response = requests.get(url, params=params)
data = response.json()

# Check if the request was successful
if response.status_code == 200:
    print("Success! Here's the flight data:")
    for flight in data.get("data", []):
        print(f"Flight {flight['flight']['iata']} from {flight['departure']['iata']}: "
              f"Scheduled Arrival: {flight['arrival']['scheduled']}")
else:
    print(f"Error: {response.status_code}, {data.get('error', 'Unknown error')}")

# Convert to DataFrame for analysis
flights = data.get("data", [])
df = pd.DataFrame(flights)

# Extract relevant columns
df = df[["flight", "departure", "arrival"]]
df["flight_number"] = df["flight"].apply(lambda x: x["iata"])
df["departure_airport"] = df["departure"].apply(lambda x: x["iata"])
df["arrival_time"] = df["arrival"].apply(lambda x: x["scheduled"])

# Group by departure airport
departure_counts = df.groupby("departure_airport").size().reset_index(name="flight_count")
print(departure_counts)

# Create a new DataFrame with only SQLite-compatible columns
df_for_db = df[["flight_number", "departure_airport", "arrival_time"]]

# Save to SQLite database
conn = sqlite3.connect("flight_data.db")
df_for_db.to_sql("flights", conn, if_exists="replace", index=False)

# Query with SQL
query = "SELECT departure_airport, COUNT(*) as flight_count FROM flights GROUP BY departure_airport"
result = pd.read_sql(query, conn)
print("SQL Query Result:")
print(result)

# Plot
departure_counts.plot(kind="bar", x="departure_airport", y="flight_count", title="Flights Arriving at DUB by Departure Airport", color="skyblue", edgecolor="black")
plt.xlabel("Departure Airport")
plt.ylabel("Number of Flights")
plt.xticks(rotation=45, ha="right")  # Rotate labels for readability
plt.tight_layout()  # Adjust layout to fit labels
plt.savefig("flight_chart.png")  # Save the plot
print("Plot saved to flight_chart.png")
plt.show()

# Close the connection
conn.close()