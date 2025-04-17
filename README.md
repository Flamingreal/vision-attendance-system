# Vision-Based Attendance System

A PyQt5-based desktop application that utilizes face recognition (FaceNet) to automate and manage attendance in a university classroom setting.

## Features

- Real-time face recognition using webcam
- Embedding generation with FaceNet
- SQLite database for face storage and attendance records
- Admin Mode to manage face entries and view attendance
- Recording Mode for automatic attendance logging
- Modern UI layout with toolbar-based navigation
- Filtering and deleting of attendance records

## Folder Structure

```
vision-attendance-system/
├── ui/                        # All UI components
│   ├── main_window.py
│   ├── dashboard_page.py
│   ├── admin_page.py
│   ├── manage_face_dialog.py
│   ├── capture_face_dialog.py
│   ├── custom_selection_dialog.py
│   └── utils.py
├── face_models.py            # FaceNet embedding logic
├── match_faces.py            # Face comparison
├── camera.py                 # Camera feed handler
├── database.py               # Database operations (SQLite)
├── main.py                   # Application entry point
├── attendance_system.db      # SQLite3 database file
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- Required libraries listed in `requirements.txt`

### Run

```bash
python main.py
```

The application launches with the main window. Use the top toolbar to switch between Recording Mode and Admin Mode.

## To-Do

- [x] Basic FaceNet integration
- [x] Add / Update / Delete face
- [x] Record attendance
- [x] Admin Mode with record filtering
- [x] UI beautification
- [x] Export and delete attendance by ID
- [ ] Unit tests and error handling improvements

## Author

Zhiyuan Xu - Undergraduate Final Year Project (University of Reading)
