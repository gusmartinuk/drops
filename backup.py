import os
import subprocess
import datetime
from settings import *

def backup_database():
    # Set the name of the database and the backup directory
    database_name = DATABASE_NAME
    backup_directory = 'dbbackup'

    # Set the username and password for the MySQL server
    username = DATABASE_USERNAME
    password = DATABASE_PASSWORD

    # Set the host for the MySQL server
    host = DATABASE_HOST

    # Set the options for the mysqldump command
    options = [
        f"--user={username}",
        f"--password={password}",
        f"--host={host}",
        f"--routines",
        f"--triggers",
        f"--events",
        # f"--single-transaction",
        # f"--no-data",
        database_name
    ]

    # Create the backup directory if it doesn't exist
    os.makedirs(backup_directory, exist_ok=True)

    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Construct the backup file name
    backup_file = os.path.join(backup_directory, f"{database_name}_{timestamp}.sql")

    # Run the mysqldump command to create the backup file
    with open(backup_file, 'w') as f:
        subprocess.run(["C:\\Program Files\\MySQL\\MySQL Workbench 8.0 CE\\mysqldump"] + options, stdout=f)

    return(f"Database backup created in {backup_directory}")
