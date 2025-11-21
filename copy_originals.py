import os
import glob
import shutil
from tqdm import tqdm

def main():
    # Directory paths
    test_dir = "./test"
    train_images_dir = "./train/images"
    
    # 1. Identify unique hashes from files in ./test
    # Pattern in test: {hash}.mask.{n}.raw.jpg or {hash}.mask.{n}.pred.png
    # We just need to look at one type to get all hashes, e.g., *.mask.0.raw.jpg
    # But to be safe and cover all, we can grab all files and extract the hash.
    
    print(f"Scanning {test_dir} for file hashes...")
    test_files = glob.glob(os.path.join(test_dir, "*"))
    
    hashes = set()
    for file_path in test_files:
        filename = os.path.basename(file_path)
        # The hash is the part before the first dot
        if "." in filename:
            file_hash = filename.split(".")[0]
            # Verify it looks like a hash (hexadecimal, 32 chars usually, but basic check is enough)
            if len(file_hash) > 0: 
                hashes.add(file_hash)
    
    print(f"Found {len(hashes)} unique hashes in {test_dir}.")
    
    # 2. Copy corresponding original images from ./train/images
    copied_count = 0
    missing_count = 0
    
    print(f"Copying original images from {train_images_dir} to {test_dir}...")
    
    for file_hash in tqdm(list(hashes)):
        source_filename = f"{file_hash}.jpg"
        source_path = os.path.join(train_images_dir, source_filename)
        
        # Check if source exists
        if os.path.exists(source_path):
            dest_path = os.path.join(test_dir, source_filename)
            
            # Copy if destination doesn't exist or to overwrite
            # shutil.copy2 preserves metadata
            try:
                if not os.path.exists(dest_path):
                    shutil.copy2(source_path, dest_path)
                    copied_count += 1
                else:
                    # If file already exists, we can skip or overwrite. 
                    # Let's assume skip if it exists to save time, or overwrite?
                    # User said "copy the original files", usually implies ensuring they are there.
                    # shutil.copy2 will overwrite.
                    shutil.copy2(source_path, dest_path)
                    copied_count += 1
            except Exception as e:
                print(f"Error copying {source_path}: {e}")
        else:
            # Try .png or .jpeg just in case? 
            # The listing showed .jpg, so we stick to that for now unless requested.
            missing_count += 1
            
    print(f"Finished.")
    print(f"Copied: {copied_count}")
    print(f"Missing/Not Found in source: {missing_count}")

if __name__ == "__main__":
    main()

