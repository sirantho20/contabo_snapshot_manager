# Contabo Snapshot Manager

A Python-based tool for managing snapshots of Contabo compute instances. This tool automatically creates and manages snapshots for all your Contabo VPS instances, with email notifications and log rotation.

## Features

- **Automated Snapshot Management**
  - Creates snapshots for all Contabo compute instances
  - Automatically deletes oldest snapshots when limit is reached
  - Runs every 12 hours via cron job

- **Email Notifications**
  - Sends detailed summary reports after each run
  - Beautiful HTML email template with statistics
  - Includes success/failure status for each instance
  - Shows snapshot names and timestamps

- **Logging System**
  - Rotating log files with configurable size
  - Configurable number of backup files
  - Detailed logging of all operations
  - Log rotation to prevent disk space issues

- **Docker Support**
  - Containerized application
  - Easy deployment
  - Environment variable configuration
  - Persistent log storage

## Prerequisites

- Python 3.9 or higher
- Docker (for containerized deployment)
- Contabo API credentials
- SMTP server access for email notifications

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Contabo API Credentials
CLIENT_ID=your_client_id
API_USER=your_api_user
API_PASSWORD=your_api_password
CLIENT_SECRET=your_client_secret

# Email Configuration
EMAIL_FROM=your-email@example.com
ADMIN_EMAIL=admin@example.com
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password

# Logging Configuration
LOG_MAX_MB=200          # Maximum log file size in MB
LOG_BACKUP_COUNT=5      # Number of backup files to keep
```

## Installation

### Using Docker (Recommended)

1. Build the Docker image:
```bash
docker build -t contabo-snapshot-manager .
```

2. Run the container:
```bash
docker run -d \
  --name contabo-snapshot \
  -v $(pwd)/logs:/app/logs \
  contabo-snapshot-manager
```

### Manual Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the script:
```bash
python main_job.py
```

## Testing

The project includes a comprehensive test suite that covers all functionality. The tests use Python's unittest framework and mock external dependencies to ensure reliable testing.

### Running Tests

To run the test suite:
```bash
python test.py
```

### Test Coverage

The test suite includes:

1. **Logger Tests**
   - Logger creation and configuration
   - Log file creation and rotation
   - Environment variable handling

2. **API Tests**
   - Access token retrieval
   - Instance listing
   - Snapshot operations (create, delete, fetch)
   - Error handling

3. **Email Tests**
   - Email summary generation
   - SMTP connection handling
   - Email content verification

4. **Integration Tests**
   - Complete snapshot management workflow
   - End-to-end process verification

### Test Environment

The tests:
- Run in isolation
- Mock all external API calls
- Mock SMTP server
- Clean up after themselves
- Use a separate test configuration

### Writing New Tests

To add new tests:
1. Add test methods to the `TestContaboSnapshotManager` class
2. Use the `@patch` decorator to mock external dependencies
3. Follow the existing test patterns
4. Ensure proper cleanup in `tearDown`

## Log Files

Logs are stored in the `logs` directory:
- Main log file: `logs/contabo_snapshot_manager.log`
- Backup files: `logs/contabo_snapshot_manager.log.1`, `.2`, etc.
- Cron job logs: `logs/cron.log`

## Email Reports

The system sends email reports after each run, including:
- Total number of instances
- Number of successful/failed snapshots
- Detailed information for each instance
- Timestamps and error messages (if any)

## Docker Volume

The Docker container uses a volume for logs:
- Mounted at `/app/logs`
- Persists between container restarts
- Accessible from the host machine

## Updating Configuration

### With Docker

1. Update the `.env` file
2. Rebuild and restart the container:
```bash
docker stop contabo-snapshot
docker rm contabo-snapshot
docker build -t contabo-snapshot-manager .
docker run -d --name contabo-snapshot -v $(pwd)/logs:/app/logs contabo-snapshot-manager
```

### Manual Update

1. Update the `.env` file
2. Restart the script

## License

This project is licensed under the GNU General Public License (GPL) v3.0.

## Author

Anthony Afetsrom <sirantho20@gmail.com>