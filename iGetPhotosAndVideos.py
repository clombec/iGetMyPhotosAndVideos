from iPhoneImport import iPhoneImportFiles
from convertAndSort import convert_heic_to_jpg_subfolders
from convertAndSort import process_photos
from convertAndSort import delete_empty_directories
from mov_to_mp4 import convert_all_mov_to_mp4

iPhoneFolder = "This PC\\Apple iPhone\\Internal Storage"
filesFolder = "D:\\Projects\\iGetMyPhotos\\TestFolder\\FilesIn"
jpgFolder = "D:\\Projects\\iGetMyPhotos\\TestFolder\\JpgOut"
metadataFolder = "D:\\Projects\\iGetMyPhotos\\TestFolder\\MetadataFolder"

# iPhoneImportFiles(iPhoneFolder, filesFolder)
# convert_heic_to_jpg_subfolders(filesFolder)
# process_photos(filesFolder,jpgFolder)
# delete_empty_directories(filesFolder)

# movfilepath = 'D:\\Projects\\iGetMyPhotos\\TestFolder\\FilesIn\\202405__\\Testmov'
# convert_all_mov_to_mp4(movfilepath, jpgFolder)