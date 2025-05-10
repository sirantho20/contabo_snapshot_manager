# Contabo Snapshot Manager

## Author: Anthony Afetsrom <sirantho20@gmail.com>

### License: GNU General Public License (GPL) v3.0

This project allows you to manage snapshots for Contabo compute instances using their API. It handles the creation, deletion, and management of snapshots across multiple instances in your Contabo account.

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

## Installation Instructions

1. **Clone the repository**:
   Clone the project to your local machine by running the following command:
   ```bash
   git clone https://github.com/sirantho20/contabo_snapshot_manager.git
   cd contabo_snapshot_manager
   ```

2. **Install Dependencies**: \
    Install the necessary Python libraries specified in the requirements.txt file by running:
    ```bash
    pip install -r requirements.txt
    ```
    This command installs the required libraries: 
    - requests
    - python-dotenv

3. **Set Up the .env File**: \
    Rename the `.env.example` file to `.env` and update the values with your Contabo credentials. The `.env` file should contain the following environment variables:
    ```bash
    CLIENT_ID=your-client-id
    CLIENT_SECRET=your-client-secret
    API_USER=your-email@example.com
    API_PASSWORD=your-password
    ```
    This file will be used to securely load your Contabo credentials without hardcoding them into the script.

4. **Verify the .env File**: \
    Ensure that the `.env` file is correctly placed in the root of the project directory. The script will load the credentials from this file automatically.

5. **Run the Script**: \
    Now that everything is set up, you can run the snapshot management script (`main_job.py`).
    To start the process, simply run:
    ```bash
    python main_job.py
    ```
    This will execute the following tasks:
    - Fetch your access token using the credentials from the .env file.
    - List the available instances from your Contabo account.
    - Fetch the snapshots for the listed instances.
    - Create a new snapshot for **each** instance.
    - If the snapshot limit is exceeded, it will delete the oldest snapshot.

    *Sample Output*:
    ```bash
    python main_job.py
    Fetching access token...
    Access Token: eyJhbGciOi...

    Listing instances...
    Instances:
    Instance ID: 1, Display Name: Mock Instance 1

    Creating snapshot for instance 1 with name: snapshot-2025-01-01_12-34-56...
    Checking if snapshot limit is exceeded for instance 1...
    Fetching snapshots for instance 1...
    Snapshots:
    Snapshot ID: snap12345, Created Date: 2025-01-01T08:00:00.000Z
    Snapshot ID: snap23456, Created Date: 2025-01-01T11:44:40.436Z
    Oldest snapshot deleted successfully!
    Snapshot snapshot-2025-01-01_12-34-56 created successfully!
    ```

6. **Automating the Script (Optional)**: \
    You can automate the script to run periodically by using cron jobs (on Linux/macOS) or Task Scheduler (on Windows).
    Example: Automate with Cron (Linux/macOS)
    To schedule the script to run daily at 2 AM, you can add a cron job:

    1. Open the cron file:
    ```bash
    crontab -e
    ```
    2. Add the following line to schedule the script:
    ```bash
    0 2 * * * /usr/bin/yourenv/python /path/to/your/project/main_job.py
    ```
    This cron job will run the script every day at 2 AM.
    Example: Automate with Task Scheduler (Windows)
    1. Open Task Scheduler on Windows.
    2. Create a new task that triggers the script at the desired time.
    3. Set the program to run as python.exe and provide the full path to the `main_job.py` as the argument.
    
7. **Logging enabled for issue tracing**: \
    Native python logging added with log rotation whenever log file size reaches 1MB. Logs are located in the logs/ directory. For better traceability, some sensitive details are logged. ensure to protect your log files. I do not accept any damages, loses or breaching resulting from the use of this software or as a result of any sensitive information being exposed to the wrong audience. Special thanks to [Luis](http://www.pcexper.pt) for inspiring this release.

    [Support with a donation](https://www.paypal.com/ncp/payment/88A7B8W7888JL)