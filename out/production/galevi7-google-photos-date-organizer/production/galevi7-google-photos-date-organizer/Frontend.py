from tkinter import *
window = Tk()
# width x height
window.geometry("400x370")
# label
title = Label(window, text="google photos downloader")


# functions
def is_username_and_password_valid():
    username = username_var.get()
    password = password_var.get()
    if (len(username) > 0 and len(password) == 0) or (len(username) == 0 and len(password) > 0):
        return False
    return True


def show_password_toggle():
    if show_password_var.get() == 1:
        password_entry.config(show='')
        show_password_checkbutton.config(text='Hide Password')
    else:
        password_entry.config(show='*')
        show_password_checkbutton.config(text='Show Password')


def is_photo_url_valid():
    if url_var[:26] != 'https://photos.google.com/':
        return False
    return True


# variables
username_var = StringVar()
password_var = StringVar()
show_password_var = IntVar()
url_var = StringVar()

# labels
username_label = Label(window, text='Username')
password_label = Label(window, text='Password')
url_label = Label(window, text='Insert a valid google photo url (not video!!!)')

# components
username_entry = Entry(window, textvariable=username_var)
password_entry = Entry(window, textvariable=password_var, show='*')
show_password_checkbutton = Checkbutton(window, text='Show Password', variable=show_password_var,
                                        onvalue=1, offvalue=0, command=show_password_toggle)
url_entry = Entry(window, textvariable=url_var)


# position by grid
username_label.grid(row=0, column=0)
password_label.grid(row=1, column=0)
username_entry.grid(row=0, column=1)
password_entry.grid(row=1, column=1)
show_password_checkbutton.grid(row=1, column=2)










# display window
window.mainloop()
