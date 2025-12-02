"""
This script checks the results by checking if the expected files are present in the target directory.
"""

import os

SOURCE_DIR = "./eval-set/celeb/images-150"
TARGET_DIR = "./results/celeb/uni-moe-2-image-150"
ATTEMPTS = 1


def find_missing_ids():
    # Check if directories exist
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory {SOURCE_DIR} does not exist.")
        return
    if not os.path.exists(TARGET_DIR):
        print(f"Error: Target directory {TARGET_DIR} does not exist.")
        return

    # Get IDs from source directory
    source_ids = set()
    for filename in os.listdir(SOURCE_DIR):
        if filename.startswith("."):
            continue
        # ID is the part before the first dot
        file_id = filename.split(".")[0]
        source_ids.add(file_id)

    print(f"Found {len(source_ids)} IDs in {SOURCE_DIR}")

    # Get IDs from target directory
    target_ids = set()
    for filename in os.listdir(TARGET_DIR):
        if filename.startswith("."):
            continue
        # ID is the part before the first dot
        file_id = filename.split(".")[0]
        target_ids.add(file_id)

    print(f"Found {len(target_ids)} IDs in {TARGET_DIR}")

    # Find missing IDs
    missing_ids = source_ids - target_ids

    print(f"\nFound {len(missing_ids)} IDs in source but missing from target:")
    for file_id in sorted(missing_ids):
        print(file_id)


def check_missing_files():
    # Check if directories exist
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory {SOURCE_DIR} does not exist.")
        return
    if not os.path.exists(TARGET_DIR):
        print(f"Error: Target directory {TARGET_DIR} does not exist.")
        return

    # Get expected IDs from source directory
    expected_ids = set()
    for filename in os.listdir(SOURCE_DIR):
        if filename.startswith("."):
            continue
        # ID is the part before the first dot
        file_id = filename.split(".")[0]
        expected_ids.add(file_id)

    print(f"Checking {len(expected_ids)} IDs for required files...")

    missing_files = []

    for file_id in expected_ids:
        # Check for 3 raw mask predictions and 3 processed masks
        for i in range(ATTEMPTS):
            # Check raw mask
            raw_mask_jpg = f"{file_id}.mask.{i}.raw.jpg"
            raw_mask_png = f"{file_id}.mask.{i}.raw.png"
            raw_mask = f"{file_id}.mask.{i}.raw.{{jpg, png}}"

            if not os.path.exists(
                os.path.join(TARGET_DIR, raw_mask_png)
            ) and not os.path.exists(os.path.join(TARGET_DIR, raw_mask_jpg)):
                missing_files.append(raw_mask)

            # Check processed mask
            pred_mask = f"{file_id}.mask.{i}.pred.png"
            if not os.path.exists(os.path.join(TARGET_DIR, pred_mask)):
                missing_files.append(pred_mask)

    if missing_files:
        for filename in sorted(missing_files):
            print(filename)
        print(f"\nFound {len(missing_files)} missing files:")
    else:
        print("\nAll expected files are present.")


if __name__ == "__main__":
    check_missing_files()
    print("--------------------------------")
    find_missing_ids()
