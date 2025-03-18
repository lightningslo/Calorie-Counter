import requests
import json
from datetime import datetime, timedelta

# Function to generate URL for a specific date
def generate_menu_url(date):
    return f"https://gustavus.edu/diningservices/menu/{date}?json"

# Function to retrieve menu data for a specific date
def retrieve_menu_data(date):
    url = generate_menu_url(date)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data for {date}")
        return None

# Function to generate SQL statements for menu data
def generate_sql_statements(menu_data, existing_items):
    sql_statements = []

    # Create table for 'date'
    sql_statements.append("CREATE TABLE IF NOT EXISTS date (date TEXT, timezone_type INTEGER, timezone TEXT);")
    date_data = menu_data['date']
    date_values = f"('{date_data['date']}', {date_data['timezone_type']}, '{date_data['timezone']}')"
    sql_statements.append(f"INSERT INTO date VALUES {date_values};")

    # Create table for 'stations'
    sql_statements.append("CREATE TABLE IF NOT EXISTS stations (name TEXT);")
    for station in menu_data['stations']:
        station_name = station['name']
        sql_statements.append(f"INSERT INTO stations VALUES ('{station_name}');")

    # Create table for 'items'
    sql_statements.append("CREATE TABLE IF NOT EXISTS items (station_name TEXT, item_name TEXT, permanent INTEGER, url TEXT, meal TEXT, price REAL);")
    for station in menu_data['stations']:
        station_name = station['name']
        for item in station['items']:
            item_name = item['name']
            # Check if item exists in the set of existing items
            if (station_name, item_name) not in existing_items:
                permanent = 1 if item.get('permanent', False) else 0
                url = item['url']
                meal = item['meal']
                price = float(item['price'])
                sql_statements.append(f'INSERT INTO items VALUES ("{station_name}", "{item_name}", {permanent}, "{url}", "{meal}", {price});')
                # Add item to the set of existing items
                existing_items.add((station_name, item_name))

    return sql_statements

# Function to save SQL statements to file
def save_sql_statements(sql_statements, filename):
    with open("menu23-24.sql", "a") as sql_file:
        sql_file.write("\n".join(sql_statements) + "\n\n")

# Define starting and ending dates
start_date = datetime.strptime("2023-09-01", "%Y-%m-%d").date()
end_date = datetime.strptime("2024-05-25", "%Y-%m-%d").date()  # Adjust end date as needed

# Set to store existing items
existing_items = set()

# Loop through dates and scrape data
current_date = start_date
while current_date <= end_date:
    print(f"Scraping data for {current_date}...")
    menu_data = retrieve_menu_data(current_date)
    if menu_data:
        sql_statements = generate_sql_statements(menu_data, existing_items)
        save_sql_statements(sql_statements, "menu23-24.sql")
        print("SQL statements generated and saved.")
    else:
        print("Failed to retrieve menu data.")
    current_date += timedelta(days=1)

print("Scraping and SQL generation complete.")
