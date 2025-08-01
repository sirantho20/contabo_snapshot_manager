#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Contabo Snapshot Manager

Author: Anthony Afetsrom <sirantho20@gmail.com>
License: GNU General Public License (GPL) v3.0

This script is designed to manage snapshots for Contabo compute instances.
It handles the creation, deletion, and management of snapshots for all instances returned by Contabo API.

Usage:
1. Install required dependencies.
2. Place your API credentials in a .env file in the same directory as the script.
3. Run the script to automatically manage snapshots for your Contabo compute instances.

This software is licensed under the GNU General Public License (GPL) v3.0. You may copy, modify, and distribute it under the same license.
"""
import logging
from logging.handlers import RotatingFileHandler
import requests
import json
import uuid
import re
import os
from dotenv import load_dotenv
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import pytz

class ContaboSnapshotManager:
    """
    ContaboSnapshotManager is a class to manage snapshots for Contabo compute instances. 
    It handles the creation, deletion, and management of snapshots across multiple instances.
    """

    def __init__(self):
        """
        Initializes the ContaboSnapshotManager instance and retrieves an access token.
        
        The credentials for accessing the Contabo API are loaded from environment variables.
        Docker environment variables take precedence over .env file variables.
        """
        # Load environment variables from .env file (as fallback)
        # load_dotenv(override=False)  # Don't override existing environment variables

        # Setup logging
        self.logger = self.setup_logger()

        # Set timezone from environment variable with fallback to Asia/Manila
        timezone_name = os.getenv('TZ', 'Asia/Manila')
        self.timezone = pytz.timezone(timezone_name)
        self.logger.info(f"Timezone set to: {self.timezone} ({timezone_name})")

        # Get environment variables (Docker env vars will take precedence)
        self.client_id = os.getenv("CLIENT_ID")
        self.api_user = os.getenv("API_USER")
        self.api_password = os.getenv("API_PASSWORD")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.instances_per_page = 20
        self.auth_url = "https://auth.contabo.com/auth/realms/contabo/protocol/openid-connect/token"
        self.list_instances_url = "https://api.contabo.com/v1/compute/instances?size={}".format(self.instances_per_page)
        self.list_snapshots_url = "https://api.contabo.com/v1/compute/instances/{instance_id}/snapshots"
        self.create_snapshot_url = "https://api.contabo.com/v1/compute/instances/{instance_id}/snapshots"
        self.snapshots = []
        self.access_token = self.get_access_token()
        self.logger.info("Initialized ContaboSnapshotManager.")
        
        # Initialize snapshot results tracking
        self.snapshot_results = []

    def get_current_time(self):
        """
        Gets the current time in the configured timezone (from TZ environment variable).
        
        Returns:
            datetime: Current time in the configured timezone.
        """
        return datetime.now(self.timezone)

    def setup_logger(self):
        """Sets up the logger with rotation.""" 
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(log_dir, "contabo_snapshot_manager.log")

        # Get log configuration from environment variables with defaults
        # Convert MB to bytes (1MB = 1024 * 1024 bytes)
        max_mb = int(os.getenv('LOG_MAX_MB', 200))  # Default 200MB
        max_bytes = max_mb * 1024 * 1024
        backup_count = int(os.getenv('LOG_BACKUP_COUNT', 5))  # Default 5 backup files

        # Create a rotating file handler for logs
        handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        handler.setLevel(logging.INFO)

        # Create a formatter and attach it to the handler
        # Include filename, line number, and function name in the log format
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d - %(funcName)s()] - %(message)s'
        )
        handler.setFormatter(formatter)

        # Get the root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Remove any existing handlers to avoid duplicate logs
        for existing_handler in logger.handlers[:]:
            logger.removeHandler(existing_handler)
            
        logger.addHandler(handler)

        # Log the current log configuration
        logger.info(f"Logging configured with max file size: {max_mb}MB and {backup_count} backup files")

        return logger

    def generate_request_id(self):
        """
        Generates a unique UUID to be used as a request identifier for API calls.

        Returns:
            str: A generated UUID to be used as the request identifier.
        """
        return str(uuid.uuid4())

    def get_access_token(self):
        """
        Authenticates with Contabo's OAuth 2.0 service to retrieve an access token.
        
        Returns:
            str: The access token used for API authentication.

        Raises:
            Exception: If the authentication request fails, raises an error with the message.
        """
        self.logger.info("Requesting access token using client credentials...")
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': self.api_user,
            'password': self.api_password,
            'grant_type': 'password'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(self.auth_url, data=data, headers=headers)

        if response.status_code == 200:
            response_json = response.json()
            access_token = response_json.get('access_token')
            if access_token:
                self.logger.info(f"Access token acquired successfully: {access_token[:10]}...")  # Log only part of the token
                return access_token
            else:
                self.logger.error(f"Failed to get access token. Error: {e}")
                return None
        else:
            self.logger.error(f"Error: Failed to get access token. Response: {response.text}")
            return None

    def list_instances(self):
        """List all instances, handling pagination to get all instances."""
        self.logger.info("Requesting list of instances...")

        # Initialize list to hold all instances
        all_instances = []

        # Get the first page of instances
        access_token = self.get_access_token()
        next_page_url = self.list_instances_url
        while next_page_url:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'X-Request-ID': str(uuid.uuid4())
            }
            
            try:
                response = requests.get(next_page_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Append the instances from the current page
                all_instances.extend(data.get('data', []))
                
                # Check if there is a next page
                if data['_links'].get('next'):
                    next_page_url = 'https://api.contabo.com'+data['_links'].get('next')
                else:
                    next_page_url = None
                    
                self.logger.info(f"Fetched {len(data.get('data', []))} instances. Next page URL: {next_page_url}")
            
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to list instances. Error: {e}")
                break
        
        self.logger.info(f"Successfully fetched {len(all_instances)} instances.")

        for instance in all_instances:
                    self.logger.info([instance["instanceId"], instance["displayName"]])
        return all_instances

    def fetch_snapshots(self, instance_id):
        """
        Fetches all snapshots for a specific instance.

        Parameters:
            instance_id (str): The unique identifier of the instance for which snapshots will be fetched.

        Returns:
            list: A list of snapshots for the given instance.
        """
        self.logger.info("Fetching snapshots for instance {}...".format(instance_id))

        request_id = self.generate_request_id()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Request-ID': request_id
        }
        url = self.list_snapshots_url.format(instance_id=instance_id)
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            snapshots = response.json().get('data', [])
            self.logger.info(f"Fetched {len(snapshots)} snapshots for instance {instance_id}.")
            return snapshots
        else:
            self.logger.error(f"Error: Failed to fetch snapshots for instance {instance_id}. Response: {response.text}")
            return []

    def find_oldest_snapshot(self, snapshots):
        """
        Finds the oldest snapshot based on the createdDate field.

        Parameters:
            snapshots (list): The list of snapshots to search through.

        Returns:
            dict: The oldest snapshot based on the 'createdDate' field.
        """
        oldest_snapshot = None
        self.logger.info("Getting oldest of snapshots for instance")
        for snapshot in snapshots:
            if 'createdDate' in snapshot:
                if oldest_snapshot is None or snapshot['createdDate'] < oldest_snapshot['createdDate']:
                    oldest_snapshot = snapshot
                    self.logger.info("Oldest snapshot is {}".format(oldest_snapshot))
        return oldest_snapshot

    def delete_snapshot(self, instance_id, snapshot_id):
        """
        Deletes a specific snapshot for an instance by its snapshot ID.

        Parameters:
            instance_id (str): The unique identifier of the instance.
            snapshot_id (str): The unique identifier of the snapshot to be deleted.

        Returns:
            None
        """
        request_id = self.generate_request_id()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Request-ID': request_id
        }
        url = self.list_snapshots_url.format(instance_id=instance_id)
        delete_body = {"request_id": request_id}
        self.logger.info("About to delete oldest snapshot {} for {}".format(snapshot_id, instance_id))
        response = requests.delete(f"{url}/{snapshot_id}", headers=headers, json=delete_body)

        if response.status_code == 204:
            self.logger.info(f"Snapshot {snapshot_id} deleted successfully.")
        else:
            self.logger.error(f"Error: Failed to delete snapshot {snapshot_id}. Response: {response.text}")

    def delete_snapshots(self, instance_id):
        """
        Deletes the oldest snapshot for a specific instance based on createdDate.
        
        This method retrieves all snapshots for the given instance and deletes the oldest one.

        Parameters:
            instance_id (str): The unique identifier of the instance for which snapshots will be deleted.

        Returns:
            None
        """
        snapshots = self.fetch_snapshots(instance_id)

        if snapshots:
            oldest_snapshot = self.find_oldest_snapshot(snapshots)
            if oldest_snapshot:
                snapshot_id = oldest_snapshot.get('snapshotId')
                self.logger.info(f"Oldest snapshot found with ID: {snapshot_id}, Created Date: {oldest_snapshot['createdDate']}")
                self.delete_snapshot(instance_id, snapshot_id)
            else:
                self.logger.info("No valid snapshot found to delete.")
        else:
            self.logger.info("No snapshots found to delete.")

    def send_summary_email(self):
        """
        Generates and sends a summary email of the snapshot operations.
        """
        try:
            # Load email template
            env = Environment(loader=FileSystemLoader('templates/email'))
            template = env.get_template('snapshot_summary.html')
            
            # Prepare email data
            successful_snapshots = sum(1 for result in self.snapshot_results if result.get('success', False))
            failed_snapshots = len(self.snapshot_results) - successful_snapshots
            
            email_data = {
                'timestamp': self.get_current_time().strftime('%Y-%m-%d %H:%M:%S'),
                'total_instances': len(self.snapshot_results),
                'successful_snapshots': successful_snapshots,
                'failed_snapshots': failed_snapshots,
                'instances': self.snapshot_results
            }
            
            # Render template
            html_content = template.render(**email_data)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Contabo Snapshot Summary - {self.get_current_time().strftime("%Y-%m-%d %H:%M")}'
            msg['From'] = os.getenv('EMAIL_FROM')
            msg['To'] = os.getenv('ADMIN_EMAIL')
            
            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))
            
            # Get SMTP settings from environment
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
                raise ValueError("Missing SMTP configuration. Please check your environment variables.", smtp_server, smtp_port, smtp_username, smtp_password)
            
            # Send email with proper connection handling
            self.logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}")
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.set_debuglevel(1)  # Enable debug output
                self.logger.info("Starting TLS connection")
                server.starttls()
                self.logger.info(f"Logging in as {smtp_username}")
                server.login(smtp_username, smtp_password)
                self.logger.info("Sending email message")
                server.send_message(msg)
                self.logger.info("Email sent successfully")
                
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error while sending summary email: {str(e)}")
        except ValueError as e:
            self.logger.error(f"Configuration error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error while sending summary email: {str(e)}")
            # Don't re-raise the exception to allow the script to continue

    def create_snapshot(self, instance_id):
        """
        Creates a new snapshot for a specific instance. If the snapshot limit is exceeded, 
        it deletes the oldest snapshot before retrying the creation of a new snapshot.

        Parameters:
            instance_id (str): The unique identifier of the instance for which the snapshot will be created.

        Returns:
            None
        """
        snapshot_name = f"snapshot-{self.get_current_time().strftime('%Y-%m-%d_%H-%M-%S')}"
        # Ensure snapshot name contains only allowed characters
        snapshot_name = re.sub(r'[^a-zA-Z0-9 -]', '', snapshot_name)  # Allow letters, numbers, spaces, and dashes
        self.logger.info(f"Creating new snapshot for instance {instance_id} with name: {snapshot_name}")

        request_id = self.generate_request_id()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Request-ID': request_id
        }

        data = {
            "name": snapshot_name,
            "description": f"Automated snapshot taken on {self.get_current_time().strftime('%Y-%m-%d_%H-%M-%S')}"
        }

        url = self.create_snapshot_url.format(instance_id=instance_id)
        
        try:
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 402 and "Total snapshots exceed the total max limit" in response.text:
                self.logger.info(f"Snapshot limit exceeded for instance {instance_id}. Deleting oldest snapshot...")
                self.delete_snapshots(instance_id)
                self.logger.info(f"Retrying snapshot creation for instance {instance_id}")
                response = requests.post(url, headers=headers, json=data)  # Retry creating snapshot

            if response.status_code == 201:
                try:
                    response_json = response.json()
                    # The API returns data in a nested structure
                    snapshot_data = response_json.get('data', [{}])[0] if isinstance(response_json.get('data'), list) else response_json.get('data', {})
                    
                    self.logger.info(f"Snapshot {snapshot_name} created successfully for instance {instance_id}!")
                    self.logger.debug(f"Snapshot response data: {snapshot_data}")
                    
                    # Track successful snapshot with more details
                    self.snapshot_results.append({
                        'id': instance_id,
                        'name': snapshot_data.get('name', 'Unknown'),
                        'success': True,
                        'snapshot_name': snapshot_name,
                        'snapshot_id': snapshot_data.get('snapshotId', 'Unknown'),
                        'timestamp': self.get_current_time().strftime('%Y-%m-%d %H:%M:%S'),
                        'status': 'success'
                    })
                except (KeyError, IndexError, TypeError) as e:
                    error_msg = f"Error parsing snapshot response: {str(e)}. Response: {response.text}"
                    self.logger.error(error_msg)
                    self.snapshot_results.append({
                        'id': instance_id,
                        'name': 'Unknown',
                        'success': False,
                        'snapshot_name': snapshot_name,
                        'timestamp': self.get_current_time().strftime('%Y-%m-%d %H:%M:%S'),
                        'error': error_msg,
                        'status': 'error'
                    })
            else:
                error_msg = f"Failed to create snapshot. Status code: {response.status_code}, Response: {response.text}"
                self.logger.error(error_msg)
                
                # Track failed snapshot with more details
                self.snapshot_results.append({
                    'id': instance_id,
                    'name': 'Unknown',
                    'success': False,
                    'snapshot_name': snapshot_name,
                    'timestamp': self.get_current_time().strftime('%Y-%m-%d %H:%M:%S'),
                    'error': error_msg,
                    'status': 'failed'
                })
                
        except Exception as e:
            error_msg = f"Exception while creating snapshot for instance {instance_id}: {str(e)}"
            self.logger.error(error_msg)
            
            # Track failed snapshot with exception details
            self.snapshot_results.append({
                'id': instance_id,
                'name': 'Unknown',
                'success': False,
                'snapshot_name': snapshot_name,
                'timestamp': self.get_current_time().strftime('%Y-%m-%d %H:%M:%S'),
                'error': error_msg,
                'status': 'error'
            })

    def manage_snapshots(self):
        """
        Loops through all instances and manages snapshots (creates and deletes) for each one.
        
        This method iterates over all the available instances and performs snapshot management (creation and deletion) 
        for each instance.

        Returns:
            None
        """
        instances = self.list_instances()
        if instances:
            for instance in instances:
                instance_id = instance.get('instanceId')
                if instance_id:
                    self.create_snapshot(instance_id)
            
            # Send summary email after all operations are complete
            self.send_summary_email()
        else:
            self.logger.info("No instances to manage.")
