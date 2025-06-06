#!/usr/bin/env python3
from lib import ContaboSnapshotManager
import logging

def main():
    """
    Main function to initialize and manage snapshots for all instances using ContaboSnapshotManager.

    This function initializes the ContaboSnapshotManager class and manages snapshots for all available instances.
    """
    try:
        manager = ContaboSnapshotManager()
        manager.manage_snapshots()
    except Exception as e:
        logging.error(f"Error in main job: {str(e)}")

if __name__ == "__main__":
    main()
