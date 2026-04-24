import time
import board
import adafruit_dht

# Set up for DHT11 on GPIO 4
dhtDevice = adafruit_dht.DHT11(board.D4, use_pulseio=False)

print("Starting DHT11 sensor loop...")

while True:
    try:
        # DHT11 is slow; it needs a moment between attempts
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        print(f"Temp: {temperature_c:.1f} C    Humidity: {humidity}%")

    except RuntimeError as error:
        # Errors happen frequently with DHT11, just keep trying
        print(f"Reading failed: {error.args[0]}")
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2.0)