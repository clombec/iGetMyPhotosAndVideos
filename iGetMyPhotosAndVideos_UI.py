import os
import tkinter as tk
from tkinter import filedialog, Scrollbar, messagebox
from tkinter import simpledialog
from PIL import Image, ImageTk
import iPhoneImport
import convertAndSort
import mov_to_mp4
from infoBoxMgmt import set_info_box, print_message, print_message_d, display_status, clear_info_box, set_debug_mode
from threading import Thread


"""
ENVIRONMENT VARIABLES
"""

__TEST__ = False
__DEBUG__ = False
if os.getenv('__TEST__') == 'True':
    __TEST__ = True
if os.getenv('__DEBUG__') == 'True':
    __DEBUG__ = True

"""
GLOBAL VARIABLES
"""
# Global variables to track the state of each option
import_active = False
convert1_active = False
convert2_active = False
sort_active = False

action_running = False
default_bg = None

"""
FUNCTIONS
"""

def perform_actions(root, iPhoneFolder, filesFolder, mp4quality):
    global action_running
    def run_action():
        global action_running

        #While True loop, to exit the loop with a break, instead of a return so that the action_running variable is reset
        while True:
            if not (import_active or convert1_active or convert2_active or sort_active):
                print_message("No actions selected. Please select an action to perform.")
                break
            if filesFolder == "":
                print_message("Please select an output folder.")
                break   
            # Default import in filesFolder\.import --> Then conversion starts in this .import folder and sort in filesFolder
            import_folder = filesFolder + '\\.import'
            if import_active:
                print_message("Performing actions: Import")
                status = iPhoneImport.iPhoneImportFiles(iPhoneFolder, import_folder)
                display_status(status, "Import")
                if status != 'STATUS_SUCCESS':
                    break
            if convert1_active: 
                print_message("Performing actions: convert heic to jpg")
                status, fail_list = convertAndSort.convert_heic_to_jpg_subfolders(import_folder)
                if status == 'STATUS_SUCCESS':
                    if len(fail_list) > 0:
                        print_message(f"Failed to convert {" ".join(map(str, fail_list))} files. Check the debug log for details.")
                    status = convertAndSort.process_photos(import_folder,filesFolder)
                if status == 'STATUS_SUCCESS':
                    status = convertAndSort.delete_empty_directories(import_folder)
                display_status(status, "HEIC to JPG conversion")
                if status != 'STATUS_SUCCESS':
                    break
            if convert2_active:
                print_message("Performing actions: convert mov to mp4")
                status = mov_to_mp4.convert_all_mov_to_mp4(import_folder, filesFolder, mp4quality)
                display_status(status, "MOV to MP4 conversion")
                if status != 'STATUS_SUCCESS':
                    break
            if sort_active:
                print_message("Performing actions: sort other files")
                status = convertAndSort.sort_all_other_files(import_folder,filesFolder + '\\OtherFiles')
                if status == 'STATUS_SUCCESS':
                    print_message('Delete empty directories')
                    status = convertAndSort.delete_empty_directories(filesFolder)
                display_status(status, "Sort other files")
                if status != 'STATUS_SUCCESS':
                    break
            break

        action_running = False
        root.configure(bg=default_bg)

    if action_running == True:
        print_message("Action already running. Please wait.")
        return
    else:
        action_running = True
        root.configure(bg="#987d7d")
        conversion_thread = Thread(target=run_action)
        conversion_thread.start()
        
def browse_folder(entry_widget):
    folder_selected = filedialog.askdirectory().replace("/", "\\")
    if folder_selected:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder_selected)

def toggle_image(image_button, color_image, gray_image, state_variable):
    global import_active, convert1_active, convert2_active, sort_active
    if state_variable == "import_active":
        import_active = not import_active
        image_button.config(image=color_image if import_active else gray_image)
    elif state_variable == "convert1_active":
        convert1_active = not convert1_active
        image_button.config(image=color_image if convert1_active else gray_image)
    elif state_variable == "convert2_active":
        convert2_active = not convert2_active
        image_button.config(image=color_image if convert2_active else gray_image)
    elif state_variable == "sort_active":
        sort_active = not sort_active
        image_button.config(image=color_image if sort_active else gray_image)

# Custom dialog box for options
class OptionDialogBox(simpledialog.Dialog):
    def __init__(self, parent, title=None, initial_value=False, initial_entry_value=10):
        self.checkbox_var = tk.BooleanVar(value=initial_value)
        self.entry_var = tk.IntVar(value=initial_entry_value)
        super().__init__(parent, title)

    def body(self, master):
        # Add the checkbox
        self.checkbox = tk.Checkbutton(master, text="Debug", variable=self.checkbox_var, anchor="w")
        self.checkbox.pack(padx=10, pady=15, anchor="w")

        # Add the entry for an integer value
        self.qlabel = tk.Label(master, text="MP4 Quality [1-31] (1 is higher quality):")
        self.qlabel.pack(padx=10, pady=0)
        self.entry = tk.Entry(master, textvariable=self.entry_var)
        self.entry.pack(padx=10, pady=0)
        
        # Return the Checkbutton widget for the initial focus
        return self.checkbox

    def apply(self):
        self.result = (self.checkbox_var.get(), self.entry_var.get())

def show_help():
    # Paths to the images
    image_paths = [
        "",
        "Images/Gooo.jpg",
        "Images/imageImport.jpg",
        "Images/HeicToJpg.jpg",
        "Images/MovToMp4.jpg",
        "Images/SortPhotos.jpg",
        "Images/DeleteHistory.jpg"
    ]   

    # Corresponding descriptions
    descriptions = [
        """iGetMyPhotosAndVideos is an import and Conversion Manager application for iPhone photos.""",
        """     The usage is: select functions with described below buttons. Colored button = active function.
                Click on Gooo to launch the functions.
                The functions are:""",
        """
        Imports files from iPhone, located in \"This PC\\Apple iPhone\\Internal Storage\".
        This is the default path for iPhone photos. It can be changed manually: the 
        open folder dialog box on Windows doesn't allow to navigate through these files.
        This folder can be changed to any other folder, not necessarily iPhone.
        This funciton will import all files from the folder and its subfolders to the 
        output folder, in a .import subfolder.
        In this .import subfolder, a new folder named .metadata will be created, containing
        a list of all imported files, so the next time the import is run, only new files
        will be imported.""",
"""     Converts files from HEIC to JPG format. It will convert all files in the .import
                folder and its subfolders. The converted files will be placed in the output folder,
                in subfolders with the name of the photo's year""",
        """     Converts files from MOV to MP4 format. It will convert all files in the .import
                folder and its subfolders. The converted files will be placed in the output folder,
                in subfolders with the name of the video's year""",
        """     Sorts all files which have not been already converted and sorted. If photos, they 
                will be placed in the output folder, in subfolders with the name of the photo's year.
                Otherwise they will be moved to a subfolder named OtherFiles.""",
        """     Delete History: clear the info box."""
    ]    

    # Create a help window
    help_window = tk.Toplevel()
    help_window.title("Application Help")

    # Create a frame for images and descriptions
    frame = tk.Frame(help_window)
    frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Add images and descriptions
    for i, (path, desc) in enumerate(zip(image_paths, descriptions)):
        try:
            # Create a frame for each image-description pair
            row_frame = tk.Frame(frame)
            row_frame.pack(anchor='w', pady=5, fill=tk.X, expand=True)

            # Load and resize the image if path is not empty
            if path != "":
                image = Image.open(path)
                if i == len(image_paths) - 1:  # Last row
                    image.thumbnail((50, 50))  # Smaller size for the last image
                elif i == 1:
                    image.thumbnail((200, 100))
                else:
                    image.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(image)

                if i == len(image_paths) - 1 or i == 1:  # Last row
                    # Add the description first
                    description_label = tk.Label(row_frame, text=desc, justify=tk.LEFT,)
                    description_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
                    # Add the image to the right
                    image_label = tk.Label(row_frame, image=photo)
                    image_label.image = photo  # Keep a reference
                    image_label.pack(side=tk.RIGHT)
                else:
                    # Add the image
                    image_label = tk.Label(row_frame, image=photo)
                    image_label.image = photo  # Keep a reference
                    image_label.pack(side=tk.LEFT)
                    # Add the description
                    description_label = tk.Label(row_frame, text=desc, justify=tk.LEFT)
                    description_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
            else:
                # Add the description only
                description_label = tk.Label(row_frame, text=desc, justify=tk.LEFT, height=1)
                description_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        except Exception as e:
            print(f"Unable to load image: {path}\nError: {e}")


def create_gui():
    def open_option_dialog():
        dialog = OptionDialogBox(root, "Options", debug_state.get(), quality_state.get())
        if dialog.result is not None:
            debug_state.set(dialog.result[0])
            quality_state.set(dialog.result[1])
            set_debug_mode(dialog.result[0])

    global import_active, convert1_active, convert2_active, sort_active, info_box, default_bg
    # Set the default folder path for the iPhone
    iphone_default_path = "This PC\\Apple iPhone\\Internal Storage"

    # Create the main window
    root = tk.Tk()
    root.title("Conversion Manager")

    debug_state = tk.BooleanVar()
    quality_state = tk.IntVar(value=8)

    # Set a fixed window size
    root.geometry("520x520")
    root.resizable(True, True)
    if __DEBUG__:
        root.minsize(width=1000, height=520)  # Set width and height
    else:
        root.minsize(width=520, height=350)  # Set width and height

    # Create a menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # Create an file menu with optionand quit
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Options", command=open_option_dialog)
    file_menu.add_command(label="Exit", command=root.quit)

    # Create a Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="Help", command=show_help)
    menubar.add_cascade(label="About", menu=help_menu)

    # Configure grid weights for resizing
    root.grid_columnconfigure(0, weight=1, minsize=100)
    root.grid_columnconfigure(1, weight=1, minsize=100)
    root.grid_columnconfigure(2, weight=1, minsize=100)
    root.grid_columnconfigure(3, weight=1, minsize=100)
    root.grid_rowconfigure(4, weight=1)
    root.grid_columnconfigure(4, weight=1)

    # Create labels and entry fields for folder paths
    tk.Label(root, text="Input path:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry1 = tk.Entry(root, width=30)
    entry1.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
    entry1.insert(0, iphone_default_path)
    if __TEST__:
        entry1.insert(len(iphone_default_path), "\\202402__")
    tk.Button(root, text="Browse", command=lambda: browse_folder(entry1)).grid(row=0, column=3, padx=10, pady=5, sticky="e")

    tk.Label(root, text="Output path:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    entry2 = tk.Entry(root, width=30)
    entry2.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
    if __TEST__:
        entry2.insert(0, "D:\\Projects\\iGetMyPhotos\\TestFolder\\TestUI")
    tk.Button(root, text="Browse", command=lambda: browse_folder(entry2)).grid(row=1, column=3, padx=10, pady=5, sticky="e")

    # Load the images for the buttons
    image_paths = ["Images/imageImport.jpg", "Images/HeicToJpg.jpg", "Images/MovToMp4.jpg", "Images/SortPhotos.jpg", "Images/Gooo.jpg", "Images/DeleteHistory.jpg"]
    images = [Image.open(path).resize((100, 100), Image.LANCZOS) for path in image_paths]
    gray_images = [Image.open(path).convert("L").resize((100, 100), Image.LANCZOS) for path in image_paths]

    photo_images = [ImageTk.PhotoImage(img) for img in images]
    gray_photo_images = [ImageTk.PhotoImage(img) for img in gray_images]

    go_image = ImageTk.PhotoImage(Image.open(image_paths[4]).resize((220, 100), Image.LANCZOS))
    delete_image = ImageTk.PhotoImage(Image.open(image_paths[5]).resize((50, 50), Image.LANCZOS))

    # Create buttons with images and ensure uniform spacing
    import_button = tk.Button(root, image=gray_photo_images[0], command=lambda: toggle_image(import_button, photo_images[0], gray_photo_images[0], "import_active"))
    import_button.grid(row=2, column=0, padx=10, pady=10)

    convert1_button = tk.Button(root, image=gray_photo_images[1], command=lambda: toggle_image(convert1_button, photo_images[1], gray_photo_images[1], "convert1_active"))
    convert1_button.grid(row=2, column=1, padx=10, pady=10)

    convert2_button = tk.Button(root, image=gray_photo_images[2], command=lambda: toggle_image(convert2_button, photo_images[2], gray_photo_images[2], "convert2_active"))
    convert2_button.grid(row=2, column=2, padx=10, pady=10) 

    sort_button = tk.Button(root, image=gray_photo_images[3], command=lambda: toggle_image(sort_button, photo_images[3], gray_photo_images[3], "sort_active"))
    sort_button.grid(row=2, column=3, padx=10, pady=10)

    # Create a "go" button to perform actions based on image states
    tk.Button(root, image=go_image, command=lambda: perform_actions(root, entry1.get(), entry2.get(), quality_state.get())).grid(row=3, column=0, columnspan=3, pady=10)

    # Create a "clear" button to clear the info box
    tk.Button(root, image=delete_image, command=lambda: clear_info_box()).grid(row=3, column=3, pady=10, sticky="se")

    # Create a Text box with a scrollbar
    info_box = tk.Text(root, height=1, width=70)
    info_box.grid(row=4, column=0, columnspan=5, pady=10, sticky="nsew")

    if __DEBUG__:
        debug_state.set(True)
    else:
        debug_state.set(False)

    set_info_box(info_box, debug_state.get())

    scrollbar = Scrollbar(root, command=info_box.yview)
    scrollbar.grid(row=4, column=5, sticky="ns")
    info_box['yscrollcommand'] = scrollbar.set

    default_bg = root.cget("bg")

    # Run the main application loop
    root.mainloop()

# Call the function to create the graphical user interface
create_gui()
