###
# A simple GUI for choosing a file to process with the process_log logic
###

import tkinter
from tkinter import filedialog
import os

from process_log import process_file

from easysettings import EasySettings


settings = EasySettings("process_log.conf")

top = tkinter.Tk()
top.title ("Process a log file")
file_names = []

###
# Load a file and save the path for future use (to open the dialog in the same place next time)
###
def saveCallback():
    global file_names

    # use stored initial path if set 
    if settings.has_option('initialdir') and settings.get("initialdir") is not None:
        initialdir = settings.get("initialdir")
    else:
        initialdir = "/"

    # get the filename from a file picking dialog
    file_name =  filedialog.askopenfilenames(initialdir = initialdir, title = "Select file")
    

    if file_name is not None and len(file_name) > 0:
        file_names = list(top.tk.splitlist(file_name))
        
        file_name_label.set("\n".join(file_names))

    for name in file_names:
        # save the path for next time
        path = os.path.realpath(name)
        if path is not None:
            settings.set("initialdir", path)
            settings.save()


###
# Process the file and save it out 
###
def procCallback():
    global file_names
    if file_names is not None and len(file_names) > 0:
        for name in list(file_names):
            process_file (name)
            file_names.remove(name)
            file_name_label.set("\n".join(file_names))




# file field label
file_name_label = tkinter.StringVar()
file_label = tkinter.Label(top, textvariable=file_name_label, width=50, justify="left", relief="groove")

# buttons
b1 = tkinter.Button(top, text ="Choose files", command = saveCallback)
b2 = tkinter.Button(top, text ="Process", command = procCallback)

# instructions
instruction_label = tkinter.Label(top, justify="left", text="1) Select a file \n2) Click 'Process' to save the processed file as a CSV in the same location/same name as the original (but with a .csv extension)")

# pack UI elements
instruction_label.pack(side=tkinter.TOP, pady=5, padx=3)
file_label.pack(side=tkinter.LEFT, pady=3, padx=3)
b2.pack(side=tkinter.RIGHT, pady=3, padx=3)
b1.pack(side=tkinter.RIGHT, pady=3, padx=3)

# run with mainloop
top.mainloop()
