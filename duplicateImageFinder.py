import os
import hashlib
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import cv2


def hash_image(path):
    try:
        with Image.open(path) as img:
            img = img.resize((100, 100)).convert('L')
            return hashlib.md5(img.tobytes()).hexdigest()
    except:
        return None


def hash_video(path):
    try:
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            return None

        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_hashes = []

        for i in [0, length // 2, length - 1]:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (100, 100))
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_hashes.append(hashlib.md5(gray.tobytes()).hexdigest())

        cap.release()
        return hashlib.md5("".join(frame_hashes).encode()).hexdigest()
    except Exception as e:
        print(f"Video hash error for {path}: {e}")
        return None


def find_duplicates(folder):
    hashes = {}
    duplicates = {}

    for root, _, files in os.walk(folder):
        for name in files:
            ext = name.lower()
            path = os.path.join(root, name)
            h = None

            if ext.endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif")):
                h = hash_image(path)
            elif ext.endswith((".mp4", ".avi", ".mov", ".mkv")):
                h = hash_video(path)

            if not h:
                continue

            if h in hashes:
                duplicates.setdefault(h, [hashes[h]]).append(path)
            else:
                hashes[h] = path

    return duplicates


def find_json_files(folder):
    json_files = []
    for root, _, files in os.walk(folder):
        for name in files:
            if name.lower().endswith(".json"):
                json_files.append(os.path.join(root, name))
    return json_files


class DuplicateMediaApp:
    def __init__(self, master, duplicates, json_files):
        self.master = master
        self.master.title("Duplicate Media Cleaner")
        self.check_vars = []

        canvas = tk.Canvas(master)
        scrollbar = ttk.Scrollbar(master, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for dup_list in duplicates.values():
            if len(dup_list) < 2:
                continue

            group_frame = ttk.Frame(scrollable_frame, padding=10, relief="groove")
            group_frame.pack(fill="x", pady=5)

            original = dup_list[0]
            self.display_media(group_frame, original, is_original=True)

            for path in dup_list[1:]:
                self.display_media(group_frame, path, is_original=False)

        if json_files:
            json_label = ttk.Label(scrollable_frame, text="JSON Files Found", foreground="red")
            json_label.pack(pady=(20, 5))

            for path in json_files:
                frame = ttk.Frame(scrollable_frame)
                frame.pack(anchor="w", padx=10)

                var = tk.BooleanVar()
                var.set(True)
                cb = ttk.Checkbutton(frame, text=path, variable=var)
                cb.pack(anchor="w")
                self.check_vars.append((var, path))

        delete_btn = ttk.Button(master, text="Delete Selected", command=self.delete_selected)
        delete_btn.pack(pady=10)

    def display_media(self, frame, path, is_original=False):
        ext = path.lower()
        label_text = "Original\n" if is_original else ""

        if ext.endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif",".heic")):
            try:
                img = Image.open(path)
                img.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(img)

                wrapper = ttk.Frame(frame)
                wrapper.pack(side="left", padx=10)

                label = ttk.Label(wrapper, image=photo,
                                  text=label_text + os.path.basename(path),
                                  compound="top", foreground="green" if is_original else "black")
                label.image = photo
                label.pack()

                if not is_original:
                    var = tk.BooleanVar()
                    var.set(True)
                    cb = ttk.Checkbutton(wrapper, variable=var)
                    cb.pack()
                    self.check_vars.append((var, path))

            except Exception as e:
                print(f"Error loading image {path}: {e}")

        elif ext.endswith((".mp4", ".avi", ".mov", ".mkv")):
            wrapper = ttk.Frame(frame)
            wrapper.pack(side="left", padx=10)

            label = ttk.Label(wrapper,
                              text=label_text + os.path.basename(path),
                              foreground="green" if is_original else "black")
            label.pack()

            video_label = ttk.Label(wrapper, text="[VIDEO FILE]", foreground="blue")
            video_label.pack()

            if not is_original:
                var = tk.BooleanVar()
                var.set(True)
                cb = ttk.Checkbutton(wrapper, variable=var)
                cb.pack()
                self.check_vars.append((var, path))

    def delete_selected(self):
        to_delete = [path for var, path in self.check_vars if var.get()]
        if not to_delete:
            messagebox.showinfo("No selection", "No files selected for deletion.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Delete {len(to_delete)} file(s)?")
        if confirm:
            deleted = 0
            for path in to_delete:
                try:
                    os.remove(path)
                    deleted += 1
                except Exception as e:
                    print(f"Failed to delete {path}: {e}")
            messagebox.showinfo("Deleted", f"Deleted {deleted} file(s).")
            self.master.destroy()


def main():
    folder = filedialog.askdirectory(title="Select Folder to Scan for Duplicate Images & Videos")
    if not folder:
        return

    duplicates = find_duplicates(folder)
    json_files = find_json_files(folder)

    if not duplicates and not json_files:
        messagebox.showinfo("Nothing Found", "No duplicate media or JSON files found.")
        return

    root = tk.Tk()
    app = DuplicateMediaApp(root, duplicates, json_files)
    root.mainloop()


if __name__ == "__main__":
    main()
