from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
from tkinter import filedialog
import photos_downloader

window = Tk()
window.geometry("850x400")
window.title("Google Photos Downloader")

# functions
def is_photo_url_valid():
    url = url_var.get()
    if not url.startswith('https://photos.google.com/'):
        return "Please enter a valid Google Photos URL."
    return None


def is_number_of_photos_valid():
    if all_photos_var.get() == "No":
        num_photos_input = number_of_photos_var.get().strip()
        if not num_photos_input:
            return "Please enter a number for the number of photos."
        if not num_photos_input.isdigit():
            return "Please enter a valid positive integer for the number of photos."
        num_photos = int(num_photos_input)
        if num_photos <= 0:
            return "Please enter a number greater than zero."
    return None


def validate_and_submit():
    errors = []

    url_error = is_photo_url_valid()
    if url_error:
        errors.append(url_error)

    number_of_photos_error = is_number_of_photos_valid()
    if number_of_photos_error:
        errors.append(number_of_photos_error)

    if errors:
        messagebox.showerror("Validation Errors", "\n".join(errors))
    else:
        global url, directory_path, older_photos, download_all_photos, number_of_photos, delete

        url = url_var.get()
        directory_path = filedialog.askdirectory(title="Select Download Directory")
        older_photos = older_newer_var.get() == "Older photos"
        download_all_photos = all_photos_var.get() == "Yes"
        number_of_photos = int(number_of_photos_var.get()) if not download_all_photos else None
        delete = delete_photos_var.get() == "Yes"

        messagebox.showinfo("Success", "All inputs are valid and have been saved.")
        window.destroy()

        pd = photos_downloader.PhotosDownloader(url, directory_path, older_photos, download_all_photos,
                                                number_of_photos, delete)
        try:
            pd.start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            messagebox.showinfo("Finished", "The program has finished running.")
            window.quit()


def toggle_number_of_photos_entry(*args):
    if all_photos_var.get() == "No":
        number_of_photos_label.grid(row=5, column=0, sticky='e', padx=10, pady=5)
        number_of_photos_entry.grid(row=5, column=1, columnspan=2, sticky='w', padx=10, pady=5)
    else:
        number_of_photos_label.grid_remove()
        number_of_photos_entry.grid_remove()


# variables
url_var = StringVar()
older_newer_var = StringVar()
all_photos_var = StringVar()
delete_photos_var = StringVar()
number_of_photos_var = StringVar()

# labels
url_label = Label(window, text='Insert the starting photo/video URL:')
older_newer_label = Label(window, text='Choose download option:')
delete_photos_label = Label(window, text='Delete downloaded photos from Google Photos:')
download_all_label = Label(window, text='Download all photos from starting URL:')
number_of_photos_label = Label(window, text='Number of photos you want to download:')

# components
width_of_entries = 50
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

# Position elements in grid
url_label.grid(row=0, column=0, sticky='e', padx=10, pady=5)
url_entry.grid(row=0, column=1, columnspan=2, sticky='w', padx=10, pady=5)
older_newer_label.grid(row=1, column=0, sticky='e', padx=10, pady=5)
older_newer_chosen.grid(row=1, column=1, columnspan=2, sticky='w', padx=10, pady=5)
delete_photos_label.grid(row=2, column=0, sticky='e', padx=10, pady=5)
delete_photos_chosen.grid(row=2, column=1, columnspan=2, sticky='w', padx=10, pady=5)
download_all_label.grid(row=3, column=0, sticky='e', padx=10, pady=5)
download_all.grid(row=3, column=1, columnspan=2, sticky='w', padx=10, pady=5)

# Initial check for "Download all" selection
toggle_number_of_photos_entry()

# Add submit button
submit_button.grid(row=6, column=1, columnspan=2, pady=20)

# display window
window.mainloop()
