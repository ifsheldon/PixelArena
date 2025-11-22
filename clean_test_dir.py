"""
This script cleans the results directory by removing files of which IDs are not in the eval_images_dir directory.
"""

import os

EVAL_IMAGES_DIR = "./eval-set/images-150"
RESULTS_DIR = "./processed-results/gemini-150"


def clean_result_dir():
    # Get valid IDs from eval-set/images
    if not os.path.exists(EVAL_IMAGES_DIR):
        print(f"Error: Directory {EVAL_IMAGES_DIR} does not exist.")
        return

    valid_ids = set()
    for filename in os.listdir(EVAL_IMAGES_DIR):
        if filename.startswith("."):
            continue
        # ID is the part before the first dot
        file_id = filename.split(".")[0]
        valid_ids.add(file_id)

    print(f"Found {len(valid_ids)} valid IDs in {EVAL_IMAGES_DIR}")

    # Check and remove files in test directory
    if not os.path.exists(RESULTS_DIR):
        print(f"Error: Directory {RESULTS_DIR} does not exist.")
        return

    deleted_count = 0
    test_files = os.listdir(RESULTS_DIR)

    print(f"Checking {len(test_files)} files in {RESULTS_DIR}...")

    for filename in test_files:
        if filename.startswith("."):
            continue

        file_id = filename.split(".")[0]

        if file_id not in valid_ids:
            file_path = os.path.join(RESULTS_DIR, filename)
            try:
                os.remove(file_path)
                print(f"Deleted: {filename} (ID: {file_id})")
                deleted_count += 1
            except Exception as e:
                print(f"Failed to delete {filename}: {e}")

    print(f"Cleanup complete. Deleted {deleted_count} files.")


if __name__ == "__main__":
    clean_result_dir()
