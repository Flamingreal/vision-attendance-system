# Vision-Based Attendance System

## Overview
A real-time facial recognition attendance system with a **multi-role login interface**. Built using **PyQt5**, **FaceNet**, and **MTCNN**, this system allows **students**, **teachers**, **administrators**, and **developers** to interact with the attendance platform according to their roles.

## Key Features
- Real-time face detection using **MTCNN**
- Face recognition powered by **pretrained FaceNet**
- **SQLite** database for users, embeddings, and attendance
- **Multi-role login system** (Student, Teacher, Admin, Developer)
- Role-based UI via **PyQt5** modular design
- Role-specific features:
  - Student: View personal attendance logs
  - Teacher: Manage student records
  - Admin: Manage users and assign roles
  - Developer: Test features and view internal data

## Folder Structure
```
vision-attendance-system/
├── ui/                        # All UI components
│   ├── login_dialog.py
│   ├── dashboard_page.py
│   ├── student_page.py
│   ├── teacher_page.py
│   ├── admin_page.py
│   ├── developer_page.py
│   └── manage_face_dialog.py
├── face_models.py            # FaceNet embedding logic
├── match_faces.py            # Face comparison
├── camera.py                 # Camera feed handler
├── database.py               # Database operations (SQLite)
├── main_window.py            # Central controller (QMainWindow)
├── main.py                   # Application entry point
├── attendance_system.db      # SQLite3 database file
└── README.md
```

## Installation
```bash
git clone https://github.com/Flamingreal/vision-attendance-system.git
cd vision-attendance-system
pip install -r requirements.txt
```

## Usage
```bash
python main.py
```
The application launches with a dashboard. Click **Login** to access role-specific features.

## Default Users
| Username | Password | Role      |
|----------|----------|-----------|
| alice    | 1234     | student   |
| bob      | 5678     | teacher   |
| admin    | admin    | admin     |
| dev      | devmode  | developer |

> You can create or manage users using the **Admin** role.

## Notes
- Embeddings are generated via `facenet-pytorch`
- Attendance is logged automatically on successful face match
- Face and attendance data is stored in `attendance_system.db`

## To-Do
- [ ] UI beautification & responsive layout
- [ ] Export attendance records (CSV, Excel)
- [ ] Pagination / filtering for large logs
- [ ] Add face via webcam in all roles (not just Admin)
