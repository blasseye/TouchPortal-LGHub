import sqlite3
import os
import sys
import json

if sys.platform.startswith('win'): # Windows
    DEFAULT_FOLDER_LG_GHUB_SETTINGS = os.path.expandvars('%LOCALAPPDATA%/LGHUB/') # Must end with /
elif sys.platform.startswith('darwin'): # MacOS
    DEFAULT_FOLDER_LG_GHUB_SETTINGS = os.path.expandvars('$HOME/Library/Application Support/lghub/') # Must end with /
else: 
    error_message = "ERROR: Unsupported platform {platform}"
    print(error_message.format(platform=sys.platform))
    exit(1)

DEFAULT_FILENAME_SETTINGS_DB = 'settings.db'
DEFAULT_FILENAME_SETTINGS_JSON = 'settings.json'
CURRENT_PATH = os.getcwd() + '/'
DEFAULT_PATH_SETTINGS_DB = DEFAULT_FOLDER_LG_GHUB_SETTINGS + DEFAULT_FILENAME_SETTINGS_DB

def get_latest_id(file_path):
    sqlite_connection = 0
    try:
        sqlite_connection = sqlite3.connect(file_path)
        cursor = sqlite_connection.cursor()

        sql_get_latest_id = 'select MAX(_id) from DATA'
        cursor.execute(sql_get_latest_id)
        record = cursor.fetchall()
        latest_id = record[0][0]

        return latest_id
    except sqlite3.Error as error:
        error_message = """
ERROR: Failed to read latest id from the table inside settings.db file:
{file_path}
This program will quit.
Error:
{exception_message}
        """
        print(error_message.format(file_path=file_path, exception_message=error))
    finally:
        if sqlite_connection:
            sqlite_connection.close()

def write_to_file(data, file_path):
    # Convert binary data to proper format and write it on Hard Disk
    try:
        with open(file_path, 'wb') as file:
            file.write(data)
        print("Stored blob data into: ", file_path, "\n")
    except Exception as error:
        error_message = """
ERROR: Failed to write the following file:
{file_path}
Error:
{exception_message}
        """
        print(error_message.format(file_path=file_path, exception_message=error))

def read_blob_data(data_id, file_path):
    sqlite_connection = 0
    try:
        sqlite_connection = sqlite3.connect(file_path)
        cursor = sqlite_connection.cursor()

        sql_fetch_blob_query = """SELECT _id, FILE from DATA where _id = ?"""
        cursor.execute(sql_fetch_blob_query, (data_id,))
        record = cursor.fetchall()
        settings_file_path = CURRENT_PATH + DEFAULT_FILENAME_SETTINGS_JSON
        for row in record:
            print("Id = ", row[0])
            settings_data = row[1]
            write_to_file(settings_data, settings_file_path)
        cursor.close()

        return settings_file_path
    except sqlite3.Error as error:
        print("Failed to read blob data from sqlite table", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()

def get_battery():
    with open('settings.json') as f:
        data = json.load(f)
    for key, value in data.items():
        if key.startswith("battery/") and key.endswith("/warning"):
            # Extraire ce qu'il y a la place de *
            _, device, _ = key.split("/")
            print("Device: ", device)
            print("Percentage: ", value["percentage"])
            print("Level: ", value["level"])

def get_device_know():
    with open('settings.json') as f:
        data = json.load(f)
    known_list = data["devices/known"]["knownList"]
    for device in known_list:
        print("Device: ", device["modelId"])
        print("Type: ", device["type"])
    

def main():
    # Extraction des informations de la base de données
    latest_id = get_latest_id(DEFAULT_PATH_SETTINGS_DB)
    file_written = read_blob_data(latest_id, DEFAULT_PATH_SETTINGS_DB)
    # Attente d'une seconde avant la prochaine mise à jour
    print("List device:")
    get_device_know()
    print("Batery pourcent:") 
    get_battery()


if __name__ == "__main__":
    main()