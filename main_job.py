from dotenv import load_dotenv
load_dotenv()

from lib import ContaboSnapshotManager

def main():
    """
    Main function to initialize and manage snapshots for all instances using ContaboSnapshotManager.

    This function initializes the ContaboSnapshotManager class and manages snapshots for all available instances.
    """
    snapshot_manager = ContaboSnapshotManager()
    snapshot_manager.manage_snapshots()


if __name__ == "__main__":
    main()
