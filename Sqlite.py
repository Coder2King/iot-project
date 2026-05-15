import time
import board
import adafruit_dht
import sqlite3
import sys
import select

# --- Configuration ---
DB_NAME = "sensor_data.db"
DHT_PIN = board.D4

def init_db():
    """Initializes the SQLite database and table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
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

def get_summary_stats():
    """Compute summary statistics from database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = '''
        SELECT 
            COUNT(*), 
            AVG(temperature), 
            MIN(temperature), 
            MAX(temperature), 
            AVG(humidity) 
        FROM readings
    '''
    cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    
    if not row or row[0] == 0:
        return None

    return {
        'count': row[0],
        'avg_temp': round(row[1], 1),
        'min_temp': row[2],
        'max_temp': row[3],
        'avg_humidity': round(row[4], 1)
    }

def check_for_quit():
    """Non-blocking check for keyboard input 'q'."""
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return sys.stdin.read(1).lower() == 'q'
    return False

# --- Main Execution ---
init_db()
dhtDevice = adafruit_dht.DHT11(DHT_PIN, use_pulseio=False)

print(f"Starting DHT11 sensor loop...")
print(">>> Press 'q' then 'Enter' at any time to stop and see summary. <<<\n")

try:
    while True:
        try:
            # Check if user wants to quit
            if check_for_quit():
                break

            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            
            if temperature_c is not None and humidity is not None:
                print(f"Logged -> Temp: {temperature_c:.1f} C | Humidity: {humidity}%")
                
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO readings (temperature, humidity) VALUES (?, ?)",
                    (temperature_c, humidity)
                )
                conn.commit()
                conn.close()

        except RuntimeError as error:
            # DHT sensors often fail to read; just log and wait
            print(f"Sensor error: {error.args[0]}")
        
        time.sleep(2.0)

except KeyboardInterrupt:
    print("\nManual stop detected.")

finally:
    # Cleanup and Summary
    dhtDevice.exit()
    print("\n" + "="*30)
    print("FINAL SUMMARY REPORT")
    print("="*30)
    stats = get_summary_stats()
    
    if stats:
        print(f"Total readings: {stats['count']}")
        print(f"Temperature:    {stats['avg_temp']}°C (Range: {stats['min_temp']}°C to {stats['max_temp']}°C)")
        print(f"Avg Humidity:   {stats['avg_humidity']}%")
    else:
        print("No data was recorded.")
    print("="*30)