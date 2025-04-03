from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import Combobox
import multiprocessing
import photos_downloader  # Ensure this module exists


def switch_screen(current, next_screen):
    """Destroy the current screen and open the next one."""
    current.destroy()
    next_screen()


def welcome_screen():
    """Welcome screen with feature highlights."""
    welcome = Tk()
    welcome.state('zoomed')
    welcome.title("Welcome")

    # Set the background color to green for the entire window
    welcome.config(bg="green")

    images = [PhotoImage(file=f"photos/{img}.png") for img in ["url", "older", "delete", "download_all",
                                                               "number_of_photos"]]
    texts = ["Here you insert the url of the photo/video that the download will start from.",
             "Here you'll need to choose if you want to download older files from the url you chose, or earlier",
             "Here you need to decide if all the files that downloaded will be deletes from google photos or not.",
             "Here you can choose if you want to download all the files from the url you chose, or a specific number of files.",
             "Here you can choose how many files you want to download starting from the url you chose."]

    Label(welcome, text="Welcome to Google Photos Downloader", font=("Arial", 18, "bold"), bg="green").pack(pady=10)

    frame = Frame(welcome, bg="green")  # Set the background color for the frame
    frame.pack(pady=20)

    for i, (img, text) in enumerate(zip(images, texts)):
        Label(frame, image=img, bg="green").grid(row=i * 2, column=0, padx=10)
        Label(frame, text=text, font=("Arial", 16, "bold"), bg="green").grid(row=i * 2 + 1, column=0)

    Button(welcome, text="Next", command=lambda: switch_screen(welcome, info_screen), bg="green").pack(pady=10)

    welcome.images = images  # Prevent garbage collection
    welcome.mainloop()


def info_screen():
    """Information screen explaining the tool."""
    info = Tk()
    info.state('zoomed')
    info.title("Information")

    Label(info, text="This tool downloads photos from Google Photos.", font=("Arial", 14)).pack(pady=10)

    Button(info, text="Back", command=lambda: switch_screen(info, welcome_screen)).pack(side="left", padx=20, pady=20)
    Button(info, text="Continue", command=lambda: switch_screen(info, run_ui)).pack(side="right", padx=20, pady=20)

    info.mainloop()


def run_ui():
    """Main UI for user inputs and validation."""
    window = Tk()
    window.state('zoomed')
    window.title("Google Photos Downloader")

    url_var, older_newer_var = StringVar(), StringVar(value="Newer photos")
    all_photos_var, delete_photos_var = StringVar(value="Yes"), StringVar(value="No")
    number_of_photos_var = StringVar(value="0")

    def validate_and_submit():
        url = url_var.get().strip()
        if not url.startswith('https://photos.google.com/'):
            messagebox.showerror("Error", "Please enter a valid Google Photos URL.")
            return

        download_all_photos = all_photos_var.get() == "Yes"
        num_photos = number_of_photos_var.get().strip()

        if not download_all_photos and (not num_photos.isdigit() or int(num_photos) <= 0):
            messagebox.showerror("Error", "Please enter a valid positive integer for the number of photos.")
            return

        directory_path = filedialog.askdirectory(title="Select Download Directory")
        if not directory_path:
            messagebox.showerror("Error", "No directory selected.")
            return

        pd_params.update({
            "url": url,
            "directory_path": directory_path,
            "older_photos": older_newer_var.get() == "Older photos",
            "download_all_photos": download_all_photos,
            "number_of_photos": int(num_photos) if num_photos else None,
            "delete": delete_photos_var.get() == "Yes"
        })

        messagebox.showinfo("Success", "Inputs validated successfully!")
        window.quit()
        window.destroy()

    def toggle_number_of_photos_entry(*args):
        if all_photos_var.get() == "No":
            number_of_photos_label.grid(row=5, column=0, sticky='e', padx=10, pady=5)
            number_of_photos_entry.grid(row=5, column=1, columnspan=2, sticky='w', padx=10, pady=5)
        else:
            number_of_photos_label.grid_remove()
            number_of_photos_entry.grid_remove()

    Label(window, text="Insert the starting photo/video URL:").grid(row=0, column=0, sticky='e', padx=10, pady=5)
    Entry(window, width=85, textvariable=url_var).grid(row=0, column=1, columnspan=2, sticky='w', padx=10, pady=5)

    Label(window, text="Choose download option:").grid(row=1, column=0, sticky='e', padx=10, pady=5)
    Combobox(window, width=17, textvariable=older_newer_var, values=('Older photos', 'Newer photos')).grid(
        row=1, column=1, columnspan=2, sticky='w', padx=10, pady=5)

    Label(window, text="Delete downloaded photos from Google Photos:").grid(row=2, column=0, sticky='e', padx=10,
                                                                            pady=5)
    Combobox(window, width=17, textvariable=delete_photos_var, values=('Yes', 'No')).grid(
        row=2, column=1, columnspan=2, sticky='w', padx=10, pady=5)

    Label(window, text="Download all photos from starting URL:").grid(row=3, column=0, sticky='e', padx=10, pady=5)
    download_all = Combobox(window, width=17, textvariable=all_photos_var, values=('Yes', 'No'))
    download_all.grid(row=3, column=1, columnspan=2, sticky='w', padx=10, pady=5)
    download_all.bind("<<ComboboxSelected>>", toggle_number_of_photos_entry)

    number_of_photos_label = Label(window, text="Number of photos to download:")
    number_of_photos_entry = Entry(window, width=50, textvariable=number_of_photos_var)
    toggle_number_of_photos_entry()

    Button(window, text="Submit", command=validate_and_submit).grid(row=6, column=1, columnspan=2, pady=20)
    window.mainloop()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    pd_params = {}  # Store parameters globally

    welcome_screen()

    if pd_params:
        try:
            pd = photos_downloader.PhotosDownloader(
                pd_params["url"],
                pd_params["directory_path"],
                pd_params["older_photos"],
                pd_params["download_all_photos"],
                pd_params["number_of_photos"],
                pd_params["delete"]
            )
            pd.start()
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            print("Ended session")