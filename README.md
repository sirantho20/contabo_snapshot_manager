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