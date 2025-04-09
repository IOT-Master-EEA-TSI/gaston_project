import time
import board
import adafruit_dht
import smbus2
import RPi.GPIO as GPIO
import spidev
import mysql.connector
from mysql.connector import Error

# --- Broches GPIO ---
DHT_PIN = 5
LIGHT_CH = 1      # Photoresistance sur canal A1 du MCP3008
SOIL_CH = 0       # Humidité du sol sur canal A0 du MCP3008
TRIG = 6
ECHO = 7
LED_PIN = 8
PUMP_PIN = 9
BUZZER_PIN = 10
CHAT_SENSOR_OUT = 11
ULTRASON_REPULSIF = 13

# --- Setup SPI (MCP3008) ---
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

# --- I2C pour capteur O₂ Atlas Scientific ---
O2_EZO_I2C_ADDRESS = 0x61
i2c_bus = smbus2.SMBus(20)  # Bus I2C habituel sur Raspberry Pi

# --- DHT11 capteur ---
dht_device = adafruit_dht.DHT11(board.D5)

# --- Setup GPIO ---
GPIO.setmode(GPIO.BCM)
GPIO.setup([TRIG, LED_PIN, PUMP_PIN, BUZZER_PIN, ULTRASON_REPULSIF], GPIO.OUT)
GPIO.setup([ECHO, CHAT_SENSOR_OUT], GPIO.IN)

# --- Lecture des capteurs analogiques via MCP3008 ---
def read_channel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# --- Lecture capteur O₂ (EZO DO via I²C) ---
def read_o2():
    try:
        i2c_bus.write_i2c_block_data(O2_EZO_I2C_ADDRESS, 0x00, list(map(ord, 'R')))
        time.sleep(1)
        data = i2c_bus.read_i2c_block_data(O2_EZO_I2C_ADDRESS, 0x00, 20)
        raw = ''.join(chr(x) for x in data if 32 <= x <= 126)
        return float(raw.strip()) if raw.strip() else -1
    except:
        return -1

# --- Lecture distance (ultrason) ---
def read_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.05)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Initialisation de pulse_start et pulse_end
    pulse_start = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    pulse_end = pulse_start  # Permet de s'assurer que pulse_end est défini
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    duration = pulse_end - pulse_start
    distance = duration * 17150
    return round(distance, 1)

# --- Gestion LED & buzzer ---
def alert_led_buzzer(state):
    GPIO.output(LED_PIN, state)
    GPIO.output(BUZZER_PIN, state)

# --- Arrosage automatique ---
def arrosage():
    print("[ACTION] Arrosage automatique lancé...")
    GPIO.output(PUMP_PIN, True)
    time.sleep(5)
    GPIO.output(PUMP_PIN, False)

# --- Insertion MySQL ---
def insert_to_db(temp, hum, light, soil, height, o2, cat, alerte):
    try:
        conn = mysql.connector.connect(
            #host='127.0.0.1',  # Base de données locale
            #user='root',      # Remplacez par votre utilisateur MySQL


            host='asaret.o2switch.net',  # Base de données en ligne
            user='gicu3476_userGaston',      # Remplacez par votre utilisateur MySQL


            password='PassGaston',   # Remplacez par votre mot de passe MySQL
            database='gicu3476_gaston'
        )
        cursor = conn.cursor()
        query = """
        INSERT INTO thym_monitoring
        (temperature, humidity_air, light, soil_moisture, height_thym, oxygen, cat_detected, alert)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (temp, hum, light, soil, height, o2, cat, alerte))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"[MySQL] Erreur : {e}")

# --- Boucle principale ---
try:
    while True:
        try:
            temp = dht_device.temperature
            hum = dht_device.humidity
        except:
            print("Erreur capteur DHT11")
            continue

        light_value = read_channel(LIGHT_CH)
        soil_value = read_channel(SOIL_CH)
        light_percent = light_value / 1023 * 100
        soil_percent = (1023 - soil_value) / 1023 * 100

        height = read_distance()
        o2_value = read_o2()
        chat_detecte = GPIO.input(CHAT_SENSOR_OUT)

        alerte = light_percent < 30 or temp > 30 or temp < 10 or soil_percent < 30 or (0 < o2_value < 5)
        alert_led_buzzer(alerte)

        if soil_percent < 30:
            arrosage()

        if chat_detecte:
            print("[ALERTE CHAT] Présence détectée ! Activation du répulsif...")
            GPIO.output(ULTRASON_REPULSIF, True)
            time.sleep(3)
            GPIO.output(ULTRASON_REPULSIF, False)

        print("----- ÉTAT DU THYM -----")
        print(f"🌡️  Température: {temp} °C")
        print(f"💧 Humidité air: {hum} %")
        print(f"☀️  Luminosité: {light_percent:.1f} %")
        print(f"🌱 Humidité sol: {soil_percent:.1f} %")
        print(f"📏 Hauteur du thym: {height} cm")
        print(f"🧪 Oxygène (O₂): {o2_value if o2_value >= 0 else 'Erreur'} mg/L")
        print("------------------------\n")

        insert_to_db(temp, hum, light_percent, soil_percent, height, o2_value, int(chat_detecte), int(alerte))

        time.sleep(2)

except KeyboardInterrupt:
    print("Arrêt du système.")
    GPIO.cleanup()
