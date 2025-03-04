import subprocess
import re
import os
import logging
from infoBoxMgmt import print_message, print_message_d

# def convert_mov_to_mp4(mov_file_path):

# # Example usage
# if __name__ == "__main__":
#     mov_file_path = 'D:\\Projects\\iGetMyPhotos\\TestFolder\\FilesIn\\202405__\\IMG_7153.MOV'  # Specify the path to your .MOV file
#     convert_mov_to_mp4(mov_file_path)

def convert_one_file(mov_file_path, output_quality, mp4_path):
    command = f"ffmpeg -i {mov_file_path} -c:v mpeg4 -q:v {output_quality} -c:a aac -n {mp4_path}"
    # command = f"ffmpeg -i {mov_file_path} -vcodec libx264 -crf {output_quality} -acodec aac -n {mp4_path}"
    print_message_d(f'Convert file {mov_file_path}, with quality {output_quality}, to {mp4_path}')
    try:
        e = subprocess.run(command, 
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True)
    except subprocess.CalledProcessError as e:
        print_message(f"Error executing command : {e}")

    print_message_d('stderr: ' + e.stderr)
    print_message_d('stdout: ' + e.stdout)

def get_creation_time(file_path):
    try:
        # Exécuter la commande ffmpeg pour obtenir les informations du fichier
        result = subprocess.run(
            ['ffmpeg', '-i', file_path],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )

        print_message_d('stderr: ' + result.stderr)
        print_message_d('stdout: ' + result.stdout)
        
        creation_time_match = re.search(r'creationdate\s*: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', result.stderr)

        if not creation_time_match:
            creation_time_match = re.search(r'creation_time\s*: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', result.stderr)

        if creation_time_match:
            creation_time = creation_time_match.group(1)
            print_message_d(f"Creation Time: {creation_time}")
            return creation_time[:19].split('T')
        else:
            print_message_d("Creation time not found in the output.")
            return None

    except Exception as e:
        print_message(f"Erreur lors de la récupération des informations du fichier : {e}")

def convert_mov_to_mp4(mov_file_path, destination_folder, output_quality ):
    try:
        video_info = get_creation_time(mov_file_path)
    except Exception as e:
        print_message(f"Error while getting video info : {e}")
        return 'STATUS_ERROR'
    
    print_message_d(video_info[0] + video_info[1])
    # output_path = video_info[0] + '_' + video_info[1].replace(':', '-') + '.mp4'

    year = video_info[0][:4]
    new_filename = f"{video_info[0]}_{video_info[1].replace(':', '-')}.mp4"

    year_folder = os.path.join(destination_folder, year)
    try:
        if not os.path.exists(year_folder):
            os.makedirs(year_folder)
    except Exception as e:
        print_message(f"Error while creating directory : {e}")
        return 'STATUS_ERROR'

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
        return 'STATUS_ERROR'
    return 'STATUS_SUCCESS'



def convert_folder_mov_to_mp4(input_folder, destination_folder, output_quality=10):
    
    if not os.path.isdir(input_folder):
        print_message("Directory '%s' does not exist.", input_folder)
        return 0, 'STATUS_NO_DIR'

    mov_files = [file for file in os.listdir(input_folder) if file.lower().endswith(".mov")]
    total_files = len(mov_files)

    if total_files == 0:
        print_message("No MOV files found in the directory.")
        return 0, 'STATUS_SUCCESS'
    else:
        print_message_d(f"Number of files to convert: {total_files}")

    # Convert files
    num_converted = 0
    for mov_file in mov_files:
        if convert_mov_to_mp4(os.path.join(input_folder, mov_file), destination_folder, output_quality) != 'STATUS_SUCCESS':
            print_message(f"Error converting file {mov_file}")
            return num_converted, 'STATUS_ERROR' 
        num_converted += 1

    print_message(f"Conversion completed successfully. {num_converted} files converted from {input_folder}")
    return num_converted, 'STATUS_SUCCESS'

def convert_all_mov_to_mp4(in_folder, out_folder, mp4quality):
    total_num_converted = 0
    for root, _, _ in os.walk(in_folder):
        if not os.path.basename(root).startswith('.') or root == in_folder:
            num_converted, status = convert_folder_mov_to_mp4(root, out_folder, mp4quality)
            total_num_converted += num_converted
            if status != 'STATUS_SUCCESS':
                print_message(f"Error converting files in {root}. {total_num_converted} files converted")
                return status
    print_message(f'Operation completed. {total_num_converted} files converted')
    return 'STATUS_SUCCESS'