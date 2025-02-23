import tkinter as tk


errors_dict = {
    'STATUS_SUCCESS': 'Success',
    'STATUS_ERROR': 'Error',
    'STATUS_NO_PHONE': 'Error : Phone folder not found',
    'STATUS_NO_DIR': 'Error : Directory not found'
}

global_info_box = None

class MyInfoBox:
    def __init__(self, text_box):
        self.text_box = text_box

    def clear(self):
        """
        Erase all content form the text box.
        """
        self.text_box.delete(1.0, tk.END)

    def append(self, text):
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

def set_info_box(ib):
    global global_info_box
    gib = MyInfoBox(ib)
    global_info_box = gib

def display_status(status, msg=None):
    if msg is None:
        msg = 'Action'
    print_message(msg + ' ended with status: ' + errors_dict[status])

def clear_info_box():
    global global_info_box
    if global_info_box:
        global_info_box.clear()