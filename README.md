# 🧹 Duplicate Media Cleaner

A Python GUI tool to **find and delete duplicate images, videos, and `.json` metadata files** from a selected folder.

## 🔍 Features

- ✅ Detects **duplicate images** using perceptual hashing
- ✅ Detects **duplicate videos** by comparing sample frames
- ✅ Finds and lists all `.json` files (commonly from labeling tools)
- ✅ Auto-marks duplicates and `.json` files for deletion
- ✅ Shows **side-by-side previews** of original and duplicate images
- ✅ Simple and clean **Tkinter GUI** for manual review
- ✅ One-click deletion with confirmation

## 🖼️ Supported File Types

- Images: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`
- Videos: `.mp4`, `.avi`, `.mov`, `.mkv`
- JSON: `.json` files in all subfolders

## 📦 Requirements

- Python 3.6+
- [Pillow](https://pypi.org/project/Pillow/)
- [OpenCV](https://pypi.org/project/opencv-python/)

Install dependencies:

```bash
pip install pillow opencv-python
