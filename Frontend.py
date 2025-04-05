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

    # Updated palette (harmonized)
    bg_color = "#C4DFDF"       # Now used as the main background
    text_color = "#65647C"     # Clean, dark-blue for all text
    button_bg = "#20948B"      # Subtle, elegant highlight

    welcome.config(bg=bg_color)

    images = [PhotoImage(file=f"photos/{img}.png") for img in ["url", "older", "delete", "download_all", "number_of_photos"]]
    texts = [
        "🢃 Here you insert the URL of the photo/video that the download will start from. 🢃",
        "🢃 Here you'll need to choose if you want to download older files from the URL you chose, or earlier. 🢃",
        "🢃 Here you need to decide if all the files that downloaded will be deleted from Google Photos or not. 🢃",
        "🢃 Here you can choose if you want to download all the files from the URL you chose, or a specific number of files. 🢃",
        "🢃 If you didn't choose to download all photos, you need to specify how many files you want to"
        " download starting from 🢃  \t\t\t\t the URL you chose."
    ]

    Label(welcome, text="Welcome to Google Photos Downloader",
          font=("Arial", 20, "bold"), bg=bg_color, fg="black").pack(pady=20)

    frame = Frame(welcome, bg=bg_color)
    frame.pack(pady=10)

    for i, (img, text) in enumerate(zip(images, texts)):
        Label(frame, text=text, font=("Arial", 14), bg=bg_color, fg=text_color,
              wraplength=1000, justify="left", padx=10, pady=5).grid(row=i * 2, column=0, pady=5)
        Label(frame, image=img, bg=bg_color).grid(row=i * 2 + 1, column=0, padx=10)


    Button(welcome, text="Next", command=lambda: switch_screen(welcome, run_ui),
           font=("Arial", 16, "bold"), bg=button_bg, fg="black", activebackground="#98D2C0").pack(pady=20)

    welcome.images = images  # Prevent garbage collection
    welcome.mainloop()


def run_ui():
    """Main UI for user inputs and validation."""
    window = Tk()
    window.update_idletasks()
    width, height = 700, 300
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.resizable(False, False)
    window.title("Google Photos Downloader")

    # Color scheme
    bg_color = "#C4DFDF"
    text_color = "black"
    button_bg = "#68A7AD"

    window.configure(bg=bg_color)

    url_var = StringVar()
    older_newer_var = StringVar(value="Newer photos")
    all_photos_var = StringVar(value="Yes")
    delete_photos_var = StringVar(value="No")
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
            number_of_photos_label.grid(row=4, column=1, sticky='w', padx=10, pady=5)
            number_of_photos_entry.grid(row=4, column=2, sticky='w', padx=10, pady=5)
        else:
            number_of_photos_label.grid_remove()
            number_of_photos_entry.grid_remove()

    # Frame setup
    frame = Frame(window, bg=bg_color)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    label_font = ("Arial", 13, "bold")

    # Form layout
    Label(frame, text="Insert the starting photo/video URL:", bg=bg_color, fg=text_color,
          font=label_font).grid(row=0, column=1, sticky='w', padx=10, pady=5)
    Entry(frame, textvariable=url_var, width=40).grid(row=0, column=2, sticky='w', padx=10, pady=5)

    Label(frame, text="Choose download option:", bg=bg_color, fg=text_color,
          font=label_font).grid(row=1, column=1, sticky='w', padx=10, pady=5)
    Combobox(frame, textvariable=older_newer_var, values=('Older photos', 'Newer photos'), width=15).grid(
        row=1, column=2, sticky='w', padx=10, pady=5)

    Label(frame, text="Delete downloaded photos from Google Photos:", bg=bg_color, fg=text_color,
          font=label_font).grid(row=2, column=1, sticky='w', padx=10, pady=5)
    Combobox(frame, textvariable=delete_photos_var, values=('Yes', 'No'), width=15).grid(
        row=2, column=2, sticky='w', padx=10, pady=5)

    Label(frame, text="Download all photos from starting URL:", bg=bg_color, fg=text_color,
          font=label_font).grid(row=3, column=1, sticky='w', padx=10, pady=5)
    download_all = Combobox(frame, textvariable=all_photos_var, values=('Yes', 'No'), width=15)
    download_all.grid(row=3, column=2, sticky='w', padx=10, pady=5)
    download_all.bind("<<ComboboxSelected>>", toggle_number_of_photos_entry)

    number_of_photos_label = Label(frame, text="Number of photos to download:",
                                   bg=bg_color, fg=text_color, font=label_font)
    number_of_photos_entry = Entry(frame, textvariable=number_of_photos_var, width=20)
    toggle_number_of_photos_entry()

    # Buttons Frame (centered container for both buttons)
    button_frame = Frame(frame, bg=bg_color)
    button_frame.grid(row=5, column=1, columnspan=2, pady=20)

    Button(button_frame, text="Back", width=12, bg=button_bg, fg="black",
           font=("Arial", 12, "bold"), command=lambda: switch_screen(window, welcome_screen)).pack(
        side=LEFT, padx=10)

    Button(button_frame, text="Submit", width=12, bg=button_bg, fg="black",
           font=("Arial", 12, "bold"), command=validate_and_submit).pack(
        side=LEFT, padx=10)

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
