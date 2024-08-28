import argparse
import hashlib
import logging
import os
import shutil
import time

# Set values.
chunk_size = 4096

def calculate_md5(file_path):
    """Calculate the MD5 checksum of a given file."""
    md5 = hashlib.md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            md5.update(chunk)
    return md5.hexdigest()

def folder_synch(source, replica, logger):
    """Synchronize the replica folder to match the source folder."""

    # Adding missing files and updating existing ones.
    for root, dirs, files in os.walk(source):
        relpath = os.path.relpath(root, source)
        replica_dir = os.path.normpath(os.path.join(replica, relpath))

        # If the replica directory doesn't exist a new one is created.
        if not os.path.exists(replica_dir):
            os.makedirs(replica_dir)
            logger.info(f"Created directory: {replica_dir}")
            print(f"Created directory: {replica_dir}")

        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_dir, file)

            # If the files doesn't exist or is different we copy the file.
            if not os.path.exists(replica_file) or calculate_md5(source_file) != calculate_md5(replica_file):
                shutil.copy2(source_file, replica_file)
                logger.info(f"Copied file: {source_file} to {replica_file}") # os.path.abspath()
                print(f"Copied file: {source_file} to {replica_file}") # os.path.abspath()

    # Deleting files and directories from replica that don't exist in source, we check the files first then the directories.
    for root, dirs, files in os.walk(replica, topdown=False):
        relpath = os.path.relpath(root, replica)
        source_dir = os.path.join(source, relpath)

        for file in files:
            replica_file = os.path.normpath(os.path.join(root, file))
            source_file = os.path.join(source_dir, file)

            # If the file doesn't exist on the source we delete it from the replica.
            if not os.path.exists(source_file):
                os.remove(replica_file)
                logger.info(f"Removed file: {replica_file}") # os.path.abspath()
                print(f"Removed file: {replica_file}") # os.path.abspath()

        for dir in dirs:
            replica_sub_dir = os.path.join(root, dir)
            source_sub_dir = os.path.join(source_dir, dir)

            # If the directory doesn't exist on the source we delete it from the replica.
            if not os.path.exists(source_sub_dir):
                shutil.rmtree(replica_sub_dir)
                logger.info(f"Removed directory: {replica_sub_dir}")
                print(f"Removed directory: {replica_sub_dir}")

def main():
    # Using argparse for clarity for the user.
    parser = argparse.ArgumentParser(description="Synchronize replica folder with source folder.")
    parser.add_argument("source", type=str, help="Source folder.")
    parser.add_argument("replica", type=str, help="Replica folder.")
    parser.add_argument("interval", type=int, help="Time interval between synchronization in seconds.")
    parser.add_argument("logfile", type=str, help="Log file.")

    args = parser.parse_args()

    if not os.path.exists(args.source):
        print(f"Error: The source directory '{args.source}' doesn't exist.")
        return

    logging.basicConfig(filename=args.logfile, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    logger.info("Starting foler synchronization.")
    print("Starting folder synchronization.")

    # Adding a try block to stop the program gracefully without showing an error traceback.
    try:
        while True:
            folder_synch(args.source, args.replica, logger)
            print(f"Next synchronization in {args.interval} seconds.")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopping execution...")
        logger.info("Program  stopped by the user.")

# Helps in case this file is imported into another file so it doesn't run when not needed.  
if __name__ == "__main__":
    main()