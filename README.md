# Contabo Snapshot Manager

## Author: Anthony Afetsrom <sirantho20@gmail.com>

### License: GNU General Public License (GPL) v3.0

This project allows you to manage snapshots for Contabo compute instances using their API. It handles the creation, deletion, and management of snapshots across multiple instances in your Contabo account. It also includes comprehensive tests to ensure the functionality works as expected.

## Features
- Create snapshots for multiple Contabo instances.
- Delete the oldest snapshot when the snapshot limit is exceeded.
- Securely authenticate using OAuth 2.0 credentials.

## Requirements

To run the script and the tests, make sure you have the following dependencies installed:

- **Python 3.6+**
- **pip** (Python's package installer)

### Required Python Libraries

- `requests`: For making HTTP requests to the Contabo API.
- `python-dotenv`: To load environment variables from a `.env` file securely.
- `unittest2`: To run unit tests for the code.

## Installation Instructions

1. **Clone the repository**:
   Clone the project to your local machine by running the following command:
   ```bash
   git clone https://github.com/yourusername/contabo-snapshot-manager.git
   cd contabo-snapshot-manager

2. **Install Dependencies**: \
    Install the necessary Python libraries specified in the requirements.txt file by running:
    ```bash
    pip install -r requirements.txt
    ```
    This command installs the required libraries: 
    - requests
    - python-dotenv
3. **Create the .env File**: \
    Create a `.env` file in the root directory of the project to store your sensitive credentials. The .env file should contain the following environment variables: 
    ```bash
    CLIENT_ID=your-client-id
    CLIENT_SECRET=your-client-secret
    USERNAME=your-email@example.com
    PASSWORD=your-password
    ````
    The `.env` file is used to securely load your Contabo credentials without hardcoding them into the script.

4. **Verify the .env File**: \
    Ensure that the `.env` file is correctly placed in the root of the project directory. The script will load the credentials from this file automatically.

5. **Run the Script**: \
    Now that everything is set up, you can run the snapshot management script (`job_script.py`).
    To start the process, simply run:
    ```bash
    python job_script.py
    ```
    This will execute the following tasks:
    - Fetch your access token using the credentials from the .env file.
    - List the available instances from your Contabo account.
    - Fetch the snapshots for the listed instances.
    - Create a new snapshot for the first instance.
    - If the snapshot limit is exceeded, it will delete the oldest snapshot.

    *Sample Output*:
    ```bash
    python job_script.py
    Fetching access token...
    Access Token: mock-access-token

    Listing instances...
    Instances:
    Instance ID: 123456789, Display Name: Mock Instance 1
    Instance ID: 987654321, Display Name: Mock Instance 2

    Fetching snapshots for instance 123456789...
    Snapshots:
    Snapshot ID: snap12345, Created Date: 2025-01-01T11:44:40.436Z

    Creating snapshot for instance 123456789 with name: snapshot-2025-01-01_21-21-38...
    Snapshot snapshot-2025-01-01_21-21-38 created successfully!

    Checking if snapshot limit is exceeded for instance 123456789...
    Oldest snapshot deleted successfully!
    ````
6. **Automating the Script (Optional)**: \
    You can automate the script to run periodically by using cron jobs (on Linux/macOS) or Task Scheduler (on Windows).
    xample: Automate with Cron (Linux/macOS)
    To schedule the script to run daily at 2 AM, you can add a cron job:

    1. Open the cron file:
    ```bash
    crontab -e
    ````
    2. Add the following line to schedule the script:
    ```bash
    0 2 * * * /usr/bin/yourenv/python /path/to/your/project/job_script.py
    ```
    This cron job will run the script every day at 2 AM.
    Example: Automate with Task Scheduler (Windows)
    1. Open Task Scheduler on Windows.
    2. Create a new task that triggers the script at the desired time.
    3. Set the program to run as python.exe and provide the full path to the `job_script.py` as the argument.