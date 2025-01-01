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

import requests
import json
import uuid
import re
import os
from dotenv import load_dotenv
from datetime import datetime

class ContaboSnapshotManager:
    """
    ContaboSnapshotManager is a class to manage snapshots for Contabo compute instances. 
    It handles the creation, deletion, and management of snapshots across multiple instances.
    """

    def __init__(self):
        """
        Initializes the ContaboSnapshotManager instance and retrieves an access token.
        
        The credentials for accessing the Contabo API are loaded from environment variables.
        """
        self.client_id = os.getenv("CLIENT_ID")
        self.api_user = os.getenv("API_USER")
        self.api_password = os.getenv("API_PASSWORD")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.auth_url = "https://auth.contabo.com/auth/realms/contabo/protocol/openid-connect/token"
        self.list_instances_url = "https://api.contabo.com/v1/compute/instances"
        self.list_snapshots_url = "https://api.contabo.com/v1/compute/instances/{instance_id}/snapshots"
        self.create_snapshot_url = "https://api.contabo.com/v1/compute/instances/{instance_id}/snapshots"
        self.snapshots = []
        self.access_token = self.get_access_token()

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
        print("Requesting access token using client credentials...")
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
                print("Access token acquired successfully.")
                return access_token
            else:
                print("Error: No access token found in the response.")
                return None
        else:
            print(f"Error: Failed to get access token. Response: {response.text}")
            return None

    def list_instances(self):
        """
        Fetches and returns a list of all compute instances available in the Contabo account.

        Returns:
            list: A list of instances, each containing metadata about the instance (e.g., ID, name, status).
        
        Raises:
            Exception: If the request to list instances fails, an error message will be printed.
        """
        request_id = self.generate_request_id()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Request-ID': request_id
        }
        response = requests.get(self.list_instances_url, headers=headers)

        if response.status_code == 200:
            instances = response.json().get('data', [])
            if instances:
                return instances
            else:
                print("No instances found.")
                return []
        else:
            print(f"Error: Failed to retrieve instances. Response: {response.text}")
            return []

    def fetch_snapshots(self, instance_id):
        """
        Fetches all snapshots for a specific instance.

        Parameters:
            instance_id (str): The unique identifier of the instance for which snapshots will be fetched.

        Returns:
            list: A list of snapshots for the given instance.
        """
        request_id = self.generate_request_id()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Request-ID': request_id
        }
        url = self.list_snapshots_url.format(instance_id=instance_id)
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            print(f"Error: Failed to fetch snapshots for instance {instance_id}. Response: {response.text}")
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
        for snapshot in snapshots:
            if 'createdDate' in snapshot:
                if oldest_snapshot is None or snapshot['createdDate'] < oldest_snapshot['createdDate']:
                    oldest_snapshot = snapshot
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
        response = requests.delete(f"{url}/{snapshot_id}", headers=headers, json=delete_body)

        if response.status_code == 204:
            print(f"Snapshot {snapshot_id} deleted successfully.")
        else:
            print(f"Error: Failed to delete snapshot {snapshot_id}. Response: {response.text}")

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
                print(f"Oldest snapshot found with ID: {snapshot_id}, Created Date: {oldest_snapshot['createdDate']}")
                self.delete_snapshot(instance_id, snapshot_id)
            else:
                print("No valid snapshot found to delete.")
        else:
            print("No snapshots found to delete.")

    def create_snapshot(self, instance_id):
        """
        Creates a new snapshot for a specific instance. If the snapshot limit is exceeded, 
        it deletes the oldest snapshot before retrying the creation of a new snapshot.

        Parameters:
            instance_id (str): The unique identifier of the instance for which the snapshot will be created.

        Returns:
            None
        """
        snapshot_name = f"snapshot-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        # Ensure snapshot name contains only allowed characters
        snapshot_name = re.sub(r'[^a-zA-Z0-9 -]', '', snapshot_name)  # Allow letters, numbers, spaces, and dashes
        print(f"Creating new snapshot for instance {instance_id} with name: {snapshot_name}")

        request_id = self.generate_request_id()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Request-ID': request_id
        }

        data = {
            "name": snapshot_name,
            "description": f"Automated snapshot taken on {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        }

        url = self.create_snapshot_url.format(instance_id=instance_id)
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 402 and "Total snapshots exceed the total max limit" in response.text:
            print(f"Snapshot limit exceeded for instance {instance_id}. Deleting oldest snapshot...")
            self.delete_snapshots(instance_id)
            response = requests.post(url, headers=headers, json=data)  # Retry creating snapshot

        if response.status_code == 201:
            response_json = response.json()
            print(f"Snapshot {snapshot_name} created successfully for instance {instance_id}!")
        else:
            print(f"Error: Failed to create snapshot for instance {instance_id}. Response: {response.text}")

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
        else:
            print("No instances to manage.")
