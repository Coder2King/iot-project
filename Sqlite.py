import time
import board
import adafruit_dht
import sqlite3

# --- Database Setup ---
DB_NAME = "sensor_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database table
init_db()

# Set up for DHT11 on GPIO 4
dhtDevice = adafruit_dht.DHT11(board.D4, use_pulseio=False)

print(f"Starting DHT11 sensor loop... Logging to {DB_NAME}")

while True:
    try:
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        
        if temperature_c is not None and humidity is not None:
            print(f"Temp: {temperature_c:.1f} C    Humidity: {humidity}%")
            
            # --- Write to SQLite ---
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO readings (temperature, humidity) VALUES (?, ?)",
                (temperature_c, humidity)
            )
            conn.commit()
            conn.close()

    except RuntimeError as error:
        # Errors happen frequently with DHT11, just keep trying
        print(f"Reading failed: {error.args[0]}")
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2.0)