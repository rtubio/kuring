# Script to configure the InfluxDB database

import time
import sys

from influxdb import InfluxDBClient

dbname = sys.argv[1]
usrname = sys.argv[2]
usrpass = sys.argv[3]
admname = sys.argv[4]
admpass = sys.argv[5]

print(f"> admname={admname}, admpass={admpass}, usrname={usrname}, usrpass={usrpass}")

RETRYTIME = 50              # 50 seconds in between connection attempts
connection_retries = 5      # maximum number of connection attempts

client = InfluxDBClient(username=admname, password=admpass)

while True:
    try:
        print("Checking connection status with local InfluxDB server...")
        client.ping()
        print("Connection established!")
        break
    except Exception as ex:
        print(f"Exception occurred while attempting connection, ex = {ex}")
        if connection_retries == 0:
            raise Exception()
        connection_retries = connection_retries - 1
        print(f"Could not connect to local influxdb server, retrying in {RETRYTIME} seconds")
        time.sleep(RETRYTIME)
        continue

# NOTE # This operation is not necessary anymore since it is carried out by the docker configuration step
# client.create_user("admin", "123", admin=True)

client.create_user(usrname, usrpass)
client.create_database(dbname)

print(f"> List of registered users: {client.get_list_users()}")
print(f"> List of registered databases: {client.get_list_database()}")
