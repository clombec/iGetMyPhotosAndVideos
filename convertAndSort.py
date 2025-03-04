"""
From https://github.com/dragonGR/PyHEIC2JPG
"""

import os
import shutil
import exifread
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener
from infoBoxMgmt import print_message, print_message_d

fail_list = []

"""
    This file converts HEIC to JPG from input folder,
    then renames and sorts all photos by Year in output folder
"""

def is_directory_empty(directory):
    """
    Check if a directory is empty.

    Args:
    directory (str): Path to the directory.

    Returns:
    bool: True if the directory is empty, False otherwise.
    """
    return not os.listdir(directory)

def delete_empty_directories(root_directory):
    """
    Delete all empty directories within the specified root directory.

    Args:
    root_directory (str): Path to the root directory.
    """
    for root, dirs, _ in os.walk(root_directory, topdown=False):
        try:
            for directory in dirs:
                full_path = os.path.join(root, directory)
                if is_directory_empty(full_path):
                    print_message_d(f"Deleting empty directory: {full_path}")
                    os.rmdir(full_path)
        except Exception as e:
            print_message(f"Error deleting directory {full_path}: {e}")
            return 'STATUS_ERROR'
    return 'STATUS_SUCCESS'


def move_file_with_unique_name(file_path, destination_directory):
    """
    Move a file to a destination directory with a unique name.

    Args:
    file_path (str): Path of the file to be moved.
    destination_directory (str): Destination directory.
    """
    base_name, extension = os.path.splitext(os.path.basename(file_path))
    new_file_path = os.path.join(destination_directory, base_name + extension)

    # Check if the file already exists in the destination directory
    counter = 1
    while os.path.exists(new_file_path):
        new_file_path = os.path.join(destination_directory, f"{base_name}_{counter}{extension}")
        counter += 1

    # Move the file to the new unique path
    shutil.move(file_path, new_file_path)

def move_files_and_delete_empty_dirs(main_directory):
    """
    Move all files to the main directory and delete empty directories.

    Args:
    main_directory (str): Main directory.
    """
    for root, dirs, files in os.walk(main_directory, topdown=False):
        # Skip the main directory itself
        if root != main_directory:
            for name in files:
                # Construct the full file path
                file_path = os.path.join(root, name)
                # Move the file to the main directory
                move_file_with_unique_name(file_path, main_directory)

        for name in dirs:
            # Construct the full directory path
            dir_path = os.path.join(root, name)
            # Delete the directory if it is empty
            try:
                os.rmdir(dir_path)
            except OSError as e:
                print_message(f"Error deleting directory {dir_path}: {e}")

def get_exif_date(image_path):
    """
    Retrieve the capture date from the EXIF metadata of an image.

    Args:
    image_path (str): Path to the image.

    Returns:
    str: Capture date in the format 'YYYY:MM:DD HH:MM:SS'.
    """
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)
        date_taken = tags.get('EXIF DateTimeOriginal')
        if date_taken:
            return date_taken.values
    return None

def process_photos(source_folder, destination_folder):
    """
    Process photos by moving and renaming them based on the capture date.

    Args:
    source_folder (str): Source folder containing the photos.
    destination_folder (str): Destination folder for the processed photos.
    """
    try:
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
    except Exception as e:
        print_message(f"Error creating directory {destination_folder}: {e}")
        return 'STATUS_ERROR'

    num_moved = 0
    for root, _, files in os.walk(source_folder):
        # Get all image files in the specified directory
        jpg_files = [file for file in files if os.path.splitext(file)[1].lower() in ['.jpg', '.jpeg', '.png']]
        total_files = len(jpg_files)
        print_message_d(f'Number of image files in {root}: {total_files}')
        if total_files > 0:
            for filename in files:
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in ['.jpg', '.jpeg', '.png']:
                    current_path = os.path.join(root, filename)
                    try:
                        date_taken = get_exif_date(current_path)
                        if date_taken:
                            year = date_taken[:4]
                            new_filename = f"{date_taken.replace(':', '-').replace(' ', '_')}{file_ext}"

                            year_folder = os.path.join(destination_folder, year)
                            if not os.path.exists(year_folder):
                                os.makedirs(year_folder)

                            new_path = os.path.join(year_folder, new_filename)
                            base_name, extension = os.path.splitext(os.path.basename(new_path))
                            # Check if the file already exists in the destination directory
                            counter = 1
                            while os.path.exists(new_path):
                                new_path = os.path.join(year_folder, f"{base_name}_{counter}{file_ext}")
                                counter += 1
                            os.rename(current_path, new_path)
                            # Display progress
                            num_moved += 1
                            # progress = int((num_moved / total_files) * 100)
                            # print_message_d(f"Rename and move progress: {progress}%", end="\r")
                    except Exception as e:
                        print_message(f"Error processing {current_path}: {e}")
                        return 'STATUS_ERROR'
    
    print_message(f"\nRename and move completed successfully. {num_moved} files.")
    return 'STATUS_SUCCESS'

def convert_single_file(heic_path, jpg_path, output_quality):
    """
    Convert a single HEIC file to JPG format.

    Args:
    heic_path (str): Path to the HEIC file.
    jpg_path (str): Path to save the converted JPG file.
    output_quality (int): Quality of the output JPG image.

    Returns:
    tuple: Path to the HEIC file and conversion status.
    """
    try:
        with Image.open(heic_path) as image:
            # Automatically handle and preserve EXIF metadata
            exif_data = image.info.get("exif")
            image.save(jpg_path, "JPEG", quality=output_quality, exif=exif_data)
            # Preserve the original access and modification timestamps
            heic_stat = os.stat(heic_path)
            os.utime(jpg_path, (heic_stat.st_atime, heic_stat.st_mtime))
            os.remove(heic_path)
            return heic_path, True  # Successful conversion
    except (UnidentifiedImageError, FileNotFoundError, OSError) as e:
        logging.error("Error converting '%s': %s", heic_path, e)
        return heic_path, False  # Failed conversion

def convert_heic_to_jpg(heic_dir, output_quality=50, max_workers=4):
    """
    Convert HEIC images in a directory to JPG format using parallel processing.

    Args:
    heic_dir (str): Path to the directory containing HEIC files.
    output_quality (int): Quality of the output JPG images (1-100).
    max_workers (int): Number of parallel threads.
    """
    # Register the HEIF file format with Pillow
    register_heif_opener()

    if not os.path.isdir(heic_dir):
        print_message("Directory '%s' does not exist.", heic_dir)
        return 'STATUS_NO_DIR'

    # Create a directory to store the converted JPG files
    jpg_dir = os.path.join(heic_dir, ".ConvertedFiles")
    try:
        if os.path.exists(jpg_dir):
            shutil.rmtree(jpg_dir)
        os.makedirs(jpg_dir, exist_ok=True)
    except Exception as e:
        print_message(f"Error creating or deleting directory {jpg_dir}: {e}")
        return 'STATUS_ERROR'

    # Get all HEIC files in the specified directory and sub directories
    heic_files = [file for file in os.listdir(heic_dir) if file.lower().endswith(".heic")]
    total_files = len(heic_files)

    if total_files == 0:
        print_message_d("No HEIC files found in the directory.")
        return 'STATUS_SUCCESS'
    else:
        print_message_d(f"Number of files to convert: {total_files}")

    # Prepare file paths for conversion
    tasks = [(os.path.join(heic_dir, file_name), os.path.join(jpg_dir, os.path.splitext(file_name)[0] + ".jpg"))
             for file_name in heic_files if not os.path.exists(os.path.join(jpg_dir, os.path.splitext(file_name)[0] + ".jpg"))]

    # Convert HEIC files to JPG in parallel using ThreadPoolExecutor
    num_converted = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(convert_single_file, heic_path, jpg_path, output_quality): heic_path
                          for heic_path, jpg_path in tasks}

        # Process the completed futures
        for future in as_completed(future_to_file):
            heic_file = future_to_file[future]
            try:
                _, success = future.result()
                if success:
                    num_converted += 1
                # Display progress
                # progress = int((num_converted / total_files) * 100)
                # print_message_d(f"Conversion progress: {progress}%", end="\r")
            except Exception as e:
                print_message("Error occurred during conversion of '%s'", heic_file)
                fail_list.append(heic_file)

    print_message(f"Conversion completed successfully. {num_converted} files converted from {heic_dir}")
    return 'STATUS_SUCCESS'

def convert_heic_to_jpg_subfolders(pathin):
    for root, _, _ in os.walk(pathin):
        if not os.path.basename(root).startswith('.') or root == pathin:
            # TODO: count total number of converted files
            status = convert_heic_to_jpg(root)
            if status != 'STATUS_SUCCESS':
                return status
    return 'STATUS_SUCCESS', fail_list


def sort_other_files(root, motherland):
    for filename in os.listdir(root):
        if not os.path.isdir(os.path.join(root, filename)):
            try:
                print_message_d(f"Found file: {filename}")
                if not os.path.exists(motherland):
                    os.makedirs(motherland)
                    print_message_d(f"Created directory: {motherland}")
                shutil.move(os.path.join(root, filename), os.path.join(motherland, filename))
            except Exception as e:
                print_message(f"Error moving file {filename}: {e}")
                return 'STATUS_ERROR'
    return 'STATUS_SUCCESS'


def sort_all_other_files(pathin, pathout):
    for root, _, _ in os.walk(pathin):
        if os.path.basename(root) != '.metadata':
            status = sort_other_files(root, pathout)
            if status != 'STATUS_SUCCESS':
                return status
    return 'STATUS_SUCCESS'

