
import os
import cv2
import glob
import numpy as np
from collections import defaultdict

def analyze_directory(base_path, name):
    print(f"--- Analyzing {name} Dataset at {base_path} ---")
    if not os.path.exists(base_path):
        print(f"Path does not exist: {base_path}")
        return

    file_counts = defaultdict(int)
    image_sizes = defaultdict(int)
    corrupt_files = []
    total_files = 0
    
    # Walk through the directory
    for root, dirs, files in os.walk(base_path):
        # If we have subdirectories, we assume those are classes (if they contain images)
        # If we are in a leaf directory (no subdirs) and it has images, we count them.
        
        # Filter for image files
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        if image_files:
            # Current directory name is potential class name if we are deep enough
            # For ASL/Images/A.jpg, root is .../Images. 
            # If files are direct children of base_path, treat filenames as classes?
            
            rel_path = os.path.relpath(root, base_path)
            if rel_path == '.':
                rel_path = "root"
            
            print(f"Found {len(image_files)} images in '{rel_path}'")
            total_files += len(image_files)
            
            for img_file in image_files:
                img_path = os.path.join(root, img_file)
                
                # Check file size/validity
                try:
                    # Just check file size first to be fast
                    size = os.path.getsize(img_path)
                    if size == 0:
                        corrupt_files.append(img_path)
                        continue
                        
                    # Optional: Check if valid image (can be slow for many files)
                    # img = cv2.imread(img_path)
                    # if img is None:
                    #     corrupt_files.append(img_path)
                    # else:
                    #     image_sizes[img.shape[:2]] += 1
                        
                except Exception as e:
                    print(f"Error reading {img_file}: {e}")
                    corrupt_files.append(img_path)
                
                # If valid, count class
                # Heuristic: if many files in folder, folder is class.
                # If few files (like 1 per alphabet) in folder, filename is class.
                
                if len(image_files) > 1 and rel_path != "root":
                     file_counts[rel_path] += 1
                else:
                     # e.g. A.jpg -> Class A
                     class_name = os.path.splitext(img_file)[0]
                     file_counts[class_name] += 1

    print(f"Total Images: {total_files}")
    print(f"Total Classes Identified: {len(file_counts)}")
    
    if file_counts:
        avg = total_files / len(file_counts)
        print(f"Average Header images per class: {avg:.2f}")
        print(f"Max images: {max(file_counts.values())}")
        print(f"Min images: {min(file_counts.values())}")
    
    if corrupt_files:
        print(f"Found {len(corrupt_files)} potentially corrupt/empty files.")
        for f in corrupt_files[:5]:
             print(f" - {f}")

    print("\n")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(base_dir, 'dataset')
    
    # Analyze ASL
    analyze_directory(os.path.join(dataset_dir, 'ASL_IMAGES', 'Images'), "ASL")
    
    # Analyze ISL
    # Note: Structure seems to be dataset/isl_dataset/isl_dataset/
    analyze_directory(os.path.join(dataset_dir, 'isl_dataset', 'isl_dataset'), "ISL")
    
    # Analyze Tamil
    analyze_directory(os.path.join(dataset_dir, 'TAMIL_IMAGES', 'ReferenceImages'), "Tamil")

if __name__ == "__main__":
    main()
