# Script to configure the InfluxDB database

from influxdb import InfluxDBClient

client = InfluxDBClient(username="admin", password="123")
print(client.ping())
print(client.get_list_database())

client.create_user("admin", "123", admin=True)
client.create_user("kuring", "456")
client.create_database("kuringdb")
