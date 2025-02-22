import subprocess
import re
import os
import logging
from infoBoxMgmt import print_message

# def convert_mov_to_mp4(mov_file_path):

# # Example usage
# if __name__ == "__main__":
#     mov_file_path = 'D:\\Projects\\iGetMyPhotos\\TestFolder\\FilesIn\\202405__\\IMG_7153.MOV'  # Specify the path to your .MOV file
#     convert_mov_to_mp4(mov_file_path)

def convert_one_file(mov_file_path, output_quality, mp4_path):
    command = f"ffmpeg -i {mov_file_path} -vcodec libx264 -crf {output_quality} -acodec aac -n {mp4_path}"
    print_message(f'Convert file {mov_file_path}, with quality {output_quality}, to {mp4_path}')
    try:
        subprocess.run(command, 
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True)
    except subprocess.CalledProcessError as e:
        print_message(f"Error executing command : {e}")

def get_creation_time(file_path):
    try:
        # Exécuter la commande ffmpeg pour obtenir les informations du fichier
        result = subprocess.run(
            ['ffmpeg', '-i', file_path],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )

        creation_time_match = re.search(r'creationdate\s*: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', result.stderr)

        if not creation_time_match:
            creation_time_match = re.search(r'creation_time\s*: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', result.stderr)

        if creation_time_match:
            creation_time = creation_time_match.group(1)
            print_message(f"Creation Time: {creation_time}")
            return creation_time[:19].split('T')
        else:
            print_message("Creation time not found in the output.")
            return None

    except Exception as e:
        print_message(f"Erreur lors de la récupération des informations du fichier : {e}")

def convert_mov_to_mp4(mov_file_path, destination_folder, output_quality ):
    video_info = get_creation_time(mov_file_path)
    print_message(video_info[0] + video_info[1])
    # output_path = video_info[0] + '_' + video_info[1].replace(':', '-') + '.mp4'

    year = video_info[0][:4]
    new_filename = f"{video_info[0]}_{video_info[1].replace(':', '-')}.mp4"

    year_folder = os.path.join(destination_folder, year)
    if not os.path.exists(year_folder):
        os.makedirs(year_folder)

    mp4_path = os.path.join(year_folder, new_filename)
    base_name, extension = os.path.splitext(os.path.basename(mp4_path))
    # Check if the file already exists in the destination directory
    counter = 1
    while os.path.exists(mp4_path):
        mp4_path = os.path.join(year_folder, f"{base_name}_{counter}{extension}")
        counter += 1

    try:
        convert_one_file(mov_file_path, output_quality, mp4_path)
        os.remove(mov_file_path)
    except Exception as e:  
        print_message(f"Error while converting file : {e}")



def convert_folder_mov_to_mp4(input_folder, destination_folder, output_quality=28):
    
    if not os.path.isdir(input_folder):
        logging.error("Directory '%s' does not exist.", input_folder)
        return 0

    mov_files = [file for file in os.listdir(input_folder) if file.lower().endswith(".mov")]
    total_files = len(mov_files)

    if total_files == 0:
        logging.info("No MOV files found in the directory.")
        return 0
    else:
        print_message(f"Number of files to convert: {total_files}")

    # Convert files
    num_converted = 0
    for mov_file in mov_files:
        convert_mov_to_mp4(os.path.join(input_folder, mov_file), destination_folder, output_quality)
        num_converted += 1

    print_message(f"Conversion completed successfully. {num_converted} files converted from {input_folder}")
    return num_converted

def convert_all_mov_to_mp4(in_folder, out_folder):
    num_converted = 0
    for root, _, _ in os.walk(in_folder):
        # TODO not .metadata or other .xxxx folder
        num_converted += convert_folder_mov_to_mp4(root, out_folder)
    print_message(f'Operation comlpeted. {num_converted} files converted')