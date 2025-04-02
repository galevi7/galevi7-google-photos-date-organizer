from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import Combobox
import multiprocessing
import photos_downloader  # Uncomment when using the downloader


def welcome_screen():
    welcome = Tk()
    welcome.geometry("400x200")
    welcome.title("Welcome")

    Label(welcome, text="Welcome to Google Photos Downloader", font=("Arial", 14)).pack(pady=20)
    Button(welcome, text="Next", command=welcome.quit).pack()

    welcome.mainloop()
    welcome.destroy()


def info_screen():
    info = Tk()
    info.geometry("400x200")
    info.title("Information")

    Label(info, text="This tool downloads photos from Google Photos.", font=("Arial", 12)).pack(pady=20)
    Button(info, text="Continue", command=info.quit).pack()

    info.mainloop()
    info.destroy()


def run_ui():
    window = Tk()
    window.geometry("850x300")
    window.title("Google Photos Downloader")

    # Variables
    url_var = StringVar()
    older_newer_var = StringVar()
    all_photos_var = StringVar()
    delete_photos_var = StringVar()
    number_of_photos_var = StringVar()
    pd_params = None  # Will hold validated values

    # Functions
    def is_photo_url_valid():
        url = url_var.get()
        if not url.startswith('https://photos.google.com/'):
            return "Please enter a valid Google Photos URL."
        return None

    def is_number_of_photos_valid():
        if all_photos_var.get() == "No":
            num_photos_input = number_of_photos_var.get().strip()
            if not num_photos_input.isdigit() or int(num_photos_input) <= 0:
                return "Please enter a valid positive integer for the number of photos."
        return None

    def validate_and_submit():
        nonlocal pd_params
        errors = []

        url_error = is_photo_url_valid()
        if url_error:
            errors.append(url_error)

        number_of_photos_error = is_number_of_photos_valid()
        if number_of_photos_error:
            errors.append(number_of_photos_error)

        if errors:
            messagebox.showerror("Validation Errors", "\n".join(errors))
            return

        url = url_var.get()
        directory_path = filedialog.askdirectory(title="Select Download Directory")
        if not directory_path:
            messagebox.showerror("Error", "No directory selected.")
            return

        older_photos = older_newer_var.get() == "Older photos"
        download_all_photos = all_photos_var.get() == "Yes"
        number_of_photos = int(number_of_photos_var.get()) if not download_all_photos else None
        delete = delete_photos_var.get() == "Yes"

        pd_params = (url, directory_path, older_photos, download_all_photos, number_of_photos, delete)

        messagebox.showinfo("Success", "All inputs are valid and have been saved.")
        window.quit()
        window.destroy()

    def toggle_number_of_photos_entry(*args):
        if all_photos_var.get() == "No":
            number_of_photos_label.grid(row=5, column=0, sticky='e', padx=10, pady=5)
            number_of_photos_entry.grid(row=5, column=1, columnspan=2, sticky='w', padx=10, pady=5)
        else:
            number_of_photos_label.grid_remove()
            number_of_photos_entry.grid_remove()

    # Labels
    url_label = Label(window, text='Insert the starting photo/video URL:')
    older_newer_label = Label(window, text='Choose download option:')
    delete_photos_label = Label(window, text='Delete downloaded photos from Google Photos:')
    download_all_label = Label(window, text='Download all photos from starting URL:')
    number_of_photos_label = Label(window, text='Number of photos you want to download:')

    # Components
    url_entry = Entry(window, width=85, textvariable=url_var)
    older_newer_chosen = Combobox(window, width=17, textvariable=older_newer_var,
                                  values=('Older photos', 'Newer photos'))
    older_newer_chosen.current(0)
    delete_photos_chosen = Combobox(window, width=17, textvariable=delete_photos_var, values=('Yes', 'No'))
    delete_photos_chosen.current(1)
    download_all = Combobox(window, width=17, textvariable=all_photos_var, values=('Yes', 'No'))
    download_all.current(0)
    download_all.bind("<<ComboboxSelected>>", toggle_number_of_photos_entry)
    number_of_photos_entry = Entry(window, width=50, textvariable=number_of_photos_var)

    # Optional: Add option to select a picture
    # Label(window, text='Select a picture to associate with download:').grid(row=6, column=0, sticky='e', padx=10, pady=5)
    # Button(window, text="Browse", command=lambda: filedialog.askopenfilename(title="Select Picture"))

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
    toggle_number_of_photos_entry()
    submit_button.grid(row=6, column=1, columnspan=2, pady=20)

    window.mainloop()
    return pd_params


def start_downloader(pd_params):
    if pd_params:
        url, directory_path, older_photos, download_all_photos, number_of_photos, delete = pd_params
        pd = photos_downloader.PhotosDownloader(url, directory_path, older_photos, download_all_photos,
                                                number_of_photos, delete)
        pd.start()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    welcome_screen()
    info_screen()
    pd_params = run_ui()
    if pd_params:
        process = multiprocessing.Process(target=start_downloader, args=(pd_params,))
        process.start()
        process.join()
