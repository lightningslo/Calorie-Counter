import requests
import json
from bs4 import BeautifulSoup
import sqlite3


# Function to extract data from the HTML content
def extract_data(html_content):
    # Parse HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract name
    h2_tag = soup.find('h2')  # Find first tag <h2>
    if h2_tag:
        name = h2_tag.contents[0]
    else:
        name = 'Not Found'

    # Extract portion size
    portion_size_elem = soup.find('dl', id='nutritionalFactsHead').find('dd')
    portion_size = portion_size_elem.text.strip() if portion_size_elem else "0"

    # Extract calories
    calories_elem = soup.find('dl', id='nutritionalFactsTop')
    if calories_elem:
        calories = calories_elem.find('dd').text.strip()
    else:
        calories = "0"

    # Extract total fat
    total_fat_elem = soup.find('td', class_='name', string='Total Fat')
    total_fat_value = total_fat_elem.find_next_sibling('td').text.strip() if total_fat_elem else "0"
    total_fat_unit = total_fat_elem.find_next_sibling('td', class_='unit').text.strip() if total_fat_elem else ""
    total_fat = f"{total_fat_value} {total_fat_unit}" if total_fat_elem else "0"

    # Extract total carbohydrates
    total_carbohydrates_elem = soup.find('td', class_='name', string='Total Carbohydrates')
    total_carbohydrates_value = total_carbohydrates_elem.find_next_sibling(
        'td').text.strip() if total_carbohydrates_elem else "0"
    total_carbohydrates_unit = total_carbohydrates_elem.find_next_sibling('td',
                                                                          class_='unit').text.strip() if total_carbohydrates_elem else ""
    total_carbohydrates = f"{total_carbohydrates_value} {total_carbohydrates_unit}" if total_carbohydrates_elem else "0"

    # Extract protein data
    protein_elem = soup.find('td', class_='name', string='Protein')
    protein_value = protein_elem.find_next_sibling('td').text.strip() if protein_elem else "0"
    protein_unit = protein_elem.find_next_sibling('td', class_='unit').text.strip() if protein_elem else ""
    protein = f"{protein_value} {protein_unit}" if protein_elem else "0"

    # Extract Cholesterol
    cholesterol_elem = soup.find('td', class_='name', string='Cholesterol')
    cholesterol_value = cholesterol_elem.find_next_sibling('td').text.strip() if cholesterol_elem else "0"
    cholesterol_unit = cholesterol_elem.find_next_sibling('td', class_='unit').text.strip() if cholesterol_elem else ""
    cholesterol = f"{cholesterol_value} {cholesterol_unit}" if cholesterol_elem else "0"

    # Extract Sodium
    sodium_elem = soup.find('td', class_='name', string='Sodium')
    sodium_value = sodium_elem.find_next_sibling('td').text.strip() if sodium_elem else "0"
    sodium_unit = sodium_elem.find_next_sibling('td', class_='unit').text.strip() if sodium_elem else ""
    sodium = f"{sodium_value} {sodium_unit}" if sodium_elem else "0"

    # Extract Ingredients
    ingredients_elem = soup.find('p', class_='ingredients')
    ingredients = ingredients_elem.text.strip() if ingredients_elem else "0"

    return name, portion_size, calories, total_fat, total_carbohydrates, protein, cholesterol, sodium, ingredients

# Function to generate SQL statements
def generate_sql(name, portion_size, calories, total_fat, total_carbohydrates, protein, cholesterol, sodium, ingredients):
    # Generate SQL statements
    sql_statements = []

    # Create table for menu items if not exists
    sql_statements.append(
        "CREATE TABLE IF NOT EXISTS menu_items (Name TEXT, Portion_Size TEXT, Calories TEXT, Total_Fat TEXT, Total_Carbohydrates TEXT, Protein TEXT, Cholesterol TEXT, Sodium TEXT, Ingredients TEXT);")

    # Insert menu item data into the table
    sql_statements.append(f'INSERT INTO menu_items VALUES ("{name}", "{portion_size}", "{calories}", "{total_fat}", "{total_carbohydrates}", "{protein}","{cholesterol}", "{sodium}", "{ingredients}");')

    return sql_statements


# Connect to the SQLite database
conn = sqlite3.connect('menu23-24.db')
cursor = conn.cursor()

# Retrieve URLs from the 'items' table
cursor.execute("SELECT url FROM items")
urls = cursor.fetchall()

# Close the cursor and connection
cursor.close()
conn.close()

# Iterate over each URL
for url in urls:
    url = "https://gustavus.edu" + url[0] + "?barebones"  # Prepend and append necessary parts
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract data from HTML content
        name, portion_size, calories, total_fat, total_carbohydrates, protein, cholesterol, sodium, ingredients = extract_data(
            response.text)

        # Generate SQL statements
        sql_statements = generate_sql(name, portion_size, calories, total_fat, total_carbohydrates, protein,
                                      cholesterol, sodium, ingredients)

        # Write SQL statements to a file
        with open("nutrient_info23-24.sql", "a") as sql_file:  # Append mode
            sql_file.write("\n".join(sql_statements))
            sql_file.write("\n")  # Add a newline between each item's SQL statements

    else:
        print(f"Failed to retrieve the page {url}. Status code:", response.status_code)

print("SQL statements generated and saved to nutrient_info23-24.sql")
