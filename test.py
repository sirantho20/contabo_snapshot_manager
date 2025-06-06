#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock
import os
import json
from datetime import datetime
from lib import ContaboSnapshotManager
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class TestContaboSnapshotManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'CLIENT_ID': 'test_client_id',
            'API_USER': 'test_user',
            'API_PASSWORD': 'test_password',
            'CLIENT_SECRET': 'test_secret',
            'EMAIL_FROM': 'test@example.com',
            'ADMIN_EMAIL': 'admin@example.com',
            'SMTP_SERVER': 'smtp.test.com',
            'SMTP_PORT': '587',
            'SMTP_USERNAME': 'test@example.com',
            'SMTP_PASSWORD': 'test_password',
            'LOG_MAX_MB': '200',
            'LOG_BACKUP_COUNT': '5'
        })
        self.env_patcher.start()

        # Create test instance
        self.manager = ContaboSnapshotManager()

    def tearDown(self):
        """Clean up after each test."""
        self.env_patcher.stop()
        # Clean up any created log files
        if os.path.exists('logs'):
            for file in os.listdir('logs'):
                os.remove(os.path.join('logs', file))
            os.rmdir('logs')

    def test_setup_logger(self):
        """Test logger setup and configuration."""
        # Verify logger is created
        self.assertIsInstance(self.manager.logger, logging.Logger)
        
        # Verify log directory is created
        self.assertTrue(os.path.exists('logs'))
        
        # Verify log file is created
        log_file = os.path.join('logs', 'contabo_snapshot_manager.log')
        self.assertTrue(os.path.exists(log_file))

    @patch('requests.post')
    def test_get_access_token(self, mock_post):
        """Test access token retrieval."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'test_token'}
        mock_post.return_value = mock_response

        token = self.manager.get_access_token()
        self.assertEqual(token, 'test_token')

        # Test failed API response
        mock_response.status_code = 401
        token = self.manager.get_access_token()
        self.assertIsNone(token)

    @patch('requests.get')
    def test_list_instances(self, mock_get):
        """Test instance listing functionality."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {'instanceId': '1', 'displayName': 'Test Instance 1'},
                {'instanceId': '2', 'displayName': 'Test Instance 2'}
            ],
            '_links': {'next': None}
        }
        mock_get.return_value = mock_response

        instances = self.manager.list_instances()
        self.assertEqual(len(instances), 2)
        self.assertEqual(instances[0]['instanceId'], '1')

    @patch('requests.get')
    def test_fetch_snapshots(self, mock_get):
        """Test snapshot fetching functionality."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {'snapshotId': '1', 'createdDate': '2024-01-01T00:00:00Z'},
                {'snapshotId': '2', 'createdDate': '2024-01-02T00:00:00Z'}
            ]
        }
        mock_get.return_value = mock_response

        snapshots = self.manager.fetch_snapshots('test_instance_id')
        self.assertEqual(len(snapshots), 2)
        self.assertEqual(snapshots[0]['snapshotId'], '1')

    def test_find_oldest_snapshot(self):
        """Test finding oldest snapshot."""
        snapshots = [
            {'snapshotId': '1', 'createdDate': '2024-01-02T00:00:00Z'},
            {'snapshotId': '2', 'createdDate': '2024-01-01T00:00:00Z'},
            {'snapshotId': '3', 'createdDate': '2024-01-03T00:00:00Z'}
        ]
        
        oldest = self.manager.find_oldest_snapshot(snapshots)
        self.assertEqual(oldest['snapshotId'], '2')

    @patch('requests.delete')
    def test_delete_snapshot(self, mock_delete):
        """Test snapshot deletion."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        self.manager.delete_snapshot('test_instance_id', 'test_snapshot_id')
        mock_delete.assert_called_once()

    @patch('requests.post')
    def test_create_snapshot(self, mock_post):
        """Test snapshot creation."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'data': {
                'name': 'Test Instance',
                'snapshotId': 'test_snapshot_id'
            }
        }
        mock_post.return_value = mock_response

        self.manager.create_snapshot('test_instance_id')
        
        # Verify snapshot was tracked
        self.assertEqual(len(self.manager.snapshot_results), 1)
        self.assertTrue(self.manager.snapshot_results[0]['success'])

        # Test failed API response
        mock_response.status_code = 400
        mock_response.text = "Error message"
        self.manager.create_snapshot('test_instance_id')
        
        # Verify failed snapshot was tracked
        self.assertEqual(len(self.manager.snapshot_results), 2)
        self.assertFalse(self.manager.snapshot_results[1]['success'])
        self.assertEqual(self.manager.snapshot_results[1]['error'], "Failed to create snapshot. Status code: 400, Response: Error message")

        # Test exception handling
        mock_post.side_effect = Exception("Test exception")
        self.manager.create_snapshot('test_instance_id')
        
        # Verify exception was tracked
        self.assertEqual(len(self.manager.snapshot_results), 3)
        self.assertFalse(self.manager.snapshot_results[2]['success'])
        self.assertEqual(self.manager.snapshot_results[2]['error'], "Exception while creating snapshot for instance test_instance_id: Test exception")

    @patch('smtplib.SMTP')
    def test_send_summary_email(self, mock_smtp):
        """Test email summary sending."""
        # Add some test snapshot results
        self.manager.snapshot_results = [
            {
                'id': '1',
                'name': 'Test Instance 1',
                'success': True,
                'snapshot_name': 'test-snapshot-1',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'id': '2',
                'name': 'Test Instance 2',
                'success': False,
                'snapshot_name': 'test-snapshot-2',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': 'Test error'
            }
        ]

        # Mock SMTP server
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        # Test successful email sending
        self.manager.send_summary_email()
        mock_smtp_instance.send_message.assert_called_once()

        # Test SMTP connection error
        mock_smtp.side_effect = Exception("SMTP connection error")
        self.manager.send_summary_email()  # Should not raise exception

    @patch('requests.get')
    @patch('requests.post')
    def test_manage_snapshots(self, mock_post, mock_get):
        """Test complete snapshot management process."""
        # Mock instance listing
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            'data': [
                {'instanceId': '1', 'displayName': 'Test Instance 1'},
                {'instanceId': '2', 'displayName': 'Test Instance 2'}
            ],
            '_links': {'next': None}
        }
        mock_get.return_value = mock_get_response

        # Mock snapshot creation
        mock_post_response = MagicMock()
        mock_post_response.status_code = 201
        mock_post_response.json.return_value = {
            'data': {
                'displayName': 'Test Instance',
                'snapshotId': 'test_snapshot_id'
            }
        }
        mock_post.return_value = mock_post_response

        self.manager.manage_snapshots()

        # Verify snapshots were created for all instances
        self.assertEqual(len(self.manager.snapshot_results), 2)

if __name__ == '__main__':
    unittest.main() 