from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
from tkinter import filedialog
import photos_downloader

window = Tk()
window.geometry("850x400")
window.title("Google Photos Downloader")


# functions
def is_username_and_password_valid():
    username = username_var.get()
    password = password_var.get()
    if (len(username) > 0 and len(password) == 0) or (len(username) == 0 and len(password) > 0):
        return "Both username and password must be provided together."
    return None


def is_photo_url_valid():
    url = url_var.get()
    if not url.startswith('https://photos.google.com/'):
        return "Please enter a valid Google Photos URL."
    return None


def is_number_of_photos_valid():
    if all_photos_var.get() == "No":
        num_photos_input = number_of_photos_var.get().strip()  # Get the input and remove any whitespace
        if not num_photos_input:  # Check for empty input
            return "Please enter a number for the number of photos."
        if not num_photos_input.isdigit():  # Check if the input is a valid integer
            return "Please enter a valid positive integer for the number of photos."
        num_photos = int(num_photos_input)
        if num_photos <= 0:
            return "Please enter a number greater than zero."
    return None


def validate_and_submit():
    # Collect all error messages
    errors = []

    # Run each validation and collect errors
    username_password_error = is_username_and_password_valid()
    if username_password_error:
        errors.append(username_password_error)

    url_error = is_photo_url_valid()
    if url_error:
        errors.append(url_error)

    number_of_photos_error = is_number_of_photos_valid()
    if number_of_photos_error:
        errors.append(number_of_photos_error)

    # If there are errors, show them in a single messagebox
    if errors:
        messagebox.showerror("Validation Errors", "\n".join(errors))
    else:
        # Save inputs to variables if all validations pass
        global url, directory_path, older_photos, download_all_photos, number_of_photos, delete, username, password

        url = url_var.get()
        directory_path = filedialog.askdirectory(title="Select Download Directory")
        older_photos = older_newer_var.get() == "Older photos"
        download_all_photos = all_photos_var.get() == "Yes"
        number_of_photos = int(number_of_photos_var.get()) if not download_all_photos else None
        delete = delete_photos_var.get() == "Yes"
        username = username_var.get() if username_var.get().strip() else None
        password = password_var.get() if password_var.get().strip() else None

        # Show success message and close the window
        messagebox.showinfo("Success", "All inputs are valid and have been saved.")
        window.destroy()  # Close the Tkinter window

        # Run the photos_downloader function with the saved parameters
        photos_downloader.crawler(url, directory_path, older_photos, download_all_photos, number_of_photos, delete,
                                  username, password)


def show_password_toggle():
    if show_password_var.get() == 1:
        password_entry.config(show='')
        show_password_checkbutton.config(text='Hide Password')
    else:
        password_entry.config(show='*')
        show_password_checkbutton.config(text='Show Password')


def toggle_number_of_photos_entry(*args):
    if all_photos_var.get() == "No":
        number_of_photos_label.grid(row=6, column=0, sticky='e', padx=10, pady=5)
        number_of_photos_entry.grid(row=6, column=1, columnspan=2, sticky='w', padx=10, pady=5)
    else:
        number_of_photos_label.grid_remove()
        number_of_photos_entry.grid_remove()


# variables
username_var = StringVar()
password_var = StringVar()
show_password_var = IntVar()
url_var = StringVar()
older_newer_var = StringVar()
all_photos_var = StringVar()
delete_photos_var = StringVar()
number_of_photos_var = StringVar()  # changed to StringVar for validation

# labels
username_label = Label(window, text='Username: (optional)')
password_label = Label(window, text='Password: (optional)')
url_label = Label(window, text='Insert the starting photo/video URL:')
older_newer_label = Label(window, text='Choose download option:')
delete_photos_label = Label(window, text='Delete downloaded photos from Google Photos:')
download_all_label = Label(window, text='Download all photos from starting URL:')
number_of_photos_label = Label(window, text='Number of photos you want to download:')

# components
width_of_entries = 50
username_entry = Entry(window, width=width_of_entries, textvariable=username_var)
password_entry = Entry(window, width=width_of_entries - 10, textvariable=password_var, show='*')
show_password_checkbutton = Checkbutton(window, text='Show Password', variable=show_password_var,
                                        onvalue=1, offvalue=0, command=show_password_toggle)
url_entry = Entry(window, width=85, textvariable=url_var)
older_newer_chosen = Combobox(window, width=17, textvariable=older_newer_var)
older_newer_chosen['values'] = ('Older photos', 'Newer photos')
older_newer_chosen.current(0)
delete_photos_chosen = Combobox(window, width=17, textvariable=delete_photos_var)
delete_photos_chosen['values'] = ('Yes', 'No')
delete_photos_chosen.current(1)
download_all = Combobox(window, width=17, textvariable=all_photos_var)
download_all['values'] = ('Yes', 'No')
download_all.current(0)
download_all.bind("<<ComboboxSelected>>", toggle_number_of_photos_entry)
number_of_photos_entry = Entry(window, width=width_of_entries, textvariable=number_of_photos_var)

# Submit button
submit_button = Button(window, text="Submit", command=validate_and_submit)

# Position elements in grid with padding and alignment for better layout
username_label.grid(row=0, column=0, sticky='e', padx=10, pady=5)
username_entry.grid(row=0, column=1, columnspan=2, sticky='w', padx=10, pady=5)
password_label.grid(row=1, column=0, sticky='e', padx=10, pady=5)
password_entry.grid(row=1, column=1, sticky='w', padx=(10, 0), pady=5)
show_password_checkbutton.grid(row=1, column=2, sticky='w', padx=5, pady=5)
url_label.grid(row=2, column=0, sticky='e', padx=10, pady=5)
url_entry.grid(row=2, column=1, columnspan=2, sticky='w', padx=10, pady=5)
older_newer_label.grid(row=3, column=0, sticky='e', padx=10, pady=5)
older_newer_chosen.grid(row=3, column=1, columnspan=2, sticky='w', padx=10, pady=5)
delete_photos_label.grid(row=4, column=0, sticky='e', padx=10, pady=5)
delete_photos_chosen.grid(row=4, column=1, columnspan=2, sticky='w', padx=10, pady=5)
download_all_label.grid(row=5, column=0, sticky='e', padx=10, pady=5)
download_all.grid(row=5, column=1, columnspan=2, sticky='w', padx=10, pady=5)

# Initial check for "Download all" selection
toggle_number_of_photos_entry()

# Add submit button
submit_button.grid(row=7, column=1, columnspan=2, pady=20)

# display window
window.mainloop()
