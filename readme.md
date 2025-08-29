NeuroVault
Secure Personal Vault with Face Recognition Authentication
Easily protect notes and information using your face for login.

Features
Secure notes protected by face recognition (no passwords to remember).

Encryption of your vault data with military-grade security.

Simple, modern desktop app you can run on Windows, Mac, or Linux.

Prerequisites
Python 3.7 or newer installed on your computer.

A working webcam, for face authentication.

All project files in the same folder:

neurovault_main.py

neurovault_face_auth.py

neurovault_encryptor.py

neurovault_setup.py

neurovault_requirements.txt

Step 1: Prepare the Files
Download all the listed files above and place them in one folder on your computer.

Step 2: Install Python (If Needed)
If you don’t have Python:

Visit python.org/downloads.

Download and install Python 3.7 or higher.

Check installation by running:

text
python --version
Step 3: Run Setup Script
Open your Terminal (Mac/Linux) or Command Prompt (Windows).

Change directory to where you saved the files:

text
cd path/to/your/project
Run the NeuroVault setup:

text
python neurovault_setup.py
This checks your Python version, installs needed system tools, Python dependencies, and prepares the folders.

If prompted for a password, enter your computer password (needed for installing system packages).

Step 4: Launch NeuroVault
Start the main application by running:

text
python neurovault_main.py
If you run for the first time, click Setup Face in the app and follow the instructions to register your face with your webcam.

Step 5: Secure Your Notes
After face authentication, you’ll see a secure notes area.

Write your notes. Click the Save button to encrypt and store them securely.

Only you can unlock your notes—using your registered face!

FAQ & Troubleshooting
Issue	Solution
Python error/old version	Install Python 3.7+ from python.org
Missing dependencies	Re-run python neurovault_setup.py
Camera not detected	Ensure webcam is plugged in/not used by other apps
Face setup not working	Use 'Setup Face' in app, follow instructions
App window doesn’t open	Run python neurovault_main.py
Notes not saving	Make sure face authentication is successful
Development & Next Steps
To backup your vault: Built-in features allow backup and restore.

For advanced usage, view the source code or explore encryption and face authentication modules.

Run tests:

text
python -m pytest
Format code:

text
black .
Lint code:

text
flake8 .
Support
File and module errors? Double-check all the filenames are exact and kept together in the same folder.

Questions or help: See comments in the code, or refer to the printed instructions during setup and app launch.

Learn more: Review the README and neurovault_requirements.txt for dependency info.

