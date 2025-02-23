import tkinter as tk


errors_dict = {
    'STATUS_SUCCESS': 'Success',
    'STATUS_ERROR': 'Error',
    'STATUS_NO_PHONE': 'Error : Phone folder not found',
    'STATUS_NO_DIR': 'Error : Directory not found'
}

global_info_box = None

class MyInfoBox:
    def __init__(self, text_box, debug_mode=False):
        self.text_box = text_box
        self.debug = debug_mode

    def clear(self):
        """
        Erase all content form the text box.
        """
        self.text_box.delete(1.0, tk.END)

    def append(self, text, color=None):
        if color:
            self.text_box.insert(tk.END, text, color)
        else:
            self.text_box.insert(tk.END, text)
        self.text_box.update_idletasks()
        self.text_box.see(tk.END)  # Scroll to the end to show the latest text    

    def set_text(self, text):
        """
        Replace text box content with new content
        """
        self.clear()
        self.text_box.insert(tk.END, text)
        self.text_box.update_idletasks()
        self.text_box.see(tk.END)  # Scroll to the end to show the latest text   


def print_message(msg, end='\n'):
    global global_info_box
    if global_info_box:
        global_info_box.append(msg + end)

def print_message_d(msg, end='\n'):
    global global_info_box
    if global_info_box and global_info_box.debug:
        global_info_box.append(msg + end, '#666666')        

def set_info_box(ib, dm):
    global global_info_box
    gib = MyInfoBox(ib, dm)
    global_info_box = gib

def display_status(status, msg=None):
    if status == 'STATUS_SUCCESS':
        color = '#00FF00'
    else:
        color = '#FF0000'
    if msg is None:
        msg = 'Action'
    if global_info_box:
        global_info_box.append(f'{msg}  ended with status: {errors_dict[status]} \n', color)

def clear_info_box():
    global global_info_box
    if global_info_box:
        global_info_box.clear()
