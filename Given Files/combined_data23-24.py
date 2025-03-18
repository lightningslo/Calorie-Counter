import sqlite3

# Connect to the SQLite databases
menu_conn = sqlite3.connect('menu23-24.db')
nutrient_conn = sqlite3.connect('nutrient_info23-24.db')

menu_cursor = menu_conn.cursor()
nutrient_cursor = nutrient_conn.cursor()

# Retrieve data from the 'items' table in 'menu23-24.db'
menu_cursor.execute("SELECT station_name, item_name, permanent, meal, price FROM items")
menu_data = menu_cursor.fetchall()

# Retrieve data from the 'menu_items' table in 'nutrient_info23-24.db'
nutrient_cursor.execute("SELECT Name, Portion_Size, Calories, Total_Fat, Total_Carbohydrates, Protein, Cholesterol, Sodium, Ingredients FROM menu_items")
nutrient_data = nutrient_cursor.fetchall()

# Close the cursors and connections
menu_cursor.close()
menu_conn.close()
nutrient_cursor.close()
nutrient_conn.close()

# Write combined data to a new SQL file
with open("combined_data23-24.sql", "w", encoding="utf-8") as sql_file:
    # Write SQL header
    sql_file.write("CREATE TABLE IF NOT EXISTS combined_data (station_name TEXT, item_name TEXT, permanent INTEGER, meal TEXT, portion_size TEXT, calories TEXT, total_fat TEXT, total_carbohydrates TEXT, protein TEXT, cholesterol TEXT, sodium TEXT, ingredients TEXT, price REAL);\n\n")

    # Write combined data rows
    for menu_item, nutrient_item in zip(menu_data, nutrient_data):
        station_name, item_name, permanent, meal, price = menu_item
        name, portion_size, calories, total_fat, total_carbohydrates, protein, cholesterol, sodium, ingredients = nutrient_item
        sql_row = f'INSERT INTO combined_data VALUES ("{station_name}", "{item_name}", {permanent}, "{meal}", "{portion_size}", "{calories}", "{total_fat}", "{total_carbohydrates}", "{protein}", "{cholesterol}", "{sodium}", "{ingredients}", {price});\n'
        sql_file.write(sql_row)

print("Combined data SQL file generated: combined_data.sql")
