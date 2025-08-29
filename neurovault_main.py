#!/usr/bin/env python3
"""
NeuroVault - Secure Personal Vault with Face Recognition Authentication
Main application module that handles the GUI and coordinates all components.

Author: NeuroVault Team
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
from datetime import datetime
import cv2
from PIL import Image, ImageTk

from face_auth import FaceAuthenticator
from encryptor import VaultEncryptor


class NeuroVaultApp:
    """Main application class for NeuroVault"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NeuroVault - Secure Personal Vault")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Initialize components
        self.face_auth = FaceAuthenticator()
        self.encryptor = VaultEncryptor()
        
        # Application state
        self.is_authenticated = False
        self.vault_data = {"notes": "", "last_modified": ""}
        
        # GUI components
        self.setup_styles()
        self.create_login_interface()
        
        # Center window on screen
        self.center_window()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Configure custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', 
                       background='#2c3e50', 
                       foreground='#ecf0f1', 
                       font=('Arial', 18, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       background='#2c3e50', 
                       foreground='#bdc3c7', 
                       font=('Arial', 12))
        
        style.configure('Custom.TButton', 
                       background='#3498db', 
                       foreground='white', 
                       font=('Arial', 10, 'bold'))
        
        style.configure('Success.TButton', 
                       background='#27ae60', 
                       foreground='white', 
                       font=('Arial', 10, 'bold'))
        
        style.configure('Danger.TButton', 
                       background='#e74c3c', 
                       foreground='white', 
                       font=('Arial', 10, 'bold'))
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_login_interface(self):
        """Create the face recognition login interface"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔒 NeuroVault", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Secure Personal Vault with Face Recognition", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 30))
        
        # Camera feed frame
        self.camera_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        self.camera_frame.pack(pady=20)
        
        # Camera label
        self.camera_label = tk.Label(self.camera_frame, text="Camera Feed", 
                                    bg='#34495e', fg='white', font=('Arial', 14))
        self.camera_label.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Click 'Start Authentication' to begin", 
                                     style='Subtitle.TLabel')
        self.status_label.pack(pady=10)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(pady=20)
        
        # Authentication button
        self.auth_button = ttk.Button(button_frame, text="Start Authentication", 
                                     command=self.start_face_auth, style='Custom.TButton')
        self.auth_button.pack(side='left', padx=5)
        
        # Setup button (for first-time users)
        setup_button = ttk.Button(button_frame, text="Setup Face", 
                                 command=self.setup_face, style='Custom.TButton')
        setup_button.pack(side='left', padx=5)
        
        # Check if user face exists
        if not os.path.exists('user_face.jpg'):
            self.status_label.config(text="⚠️ Please setup your face first using 'Setup Face' button")
            self.auth_button.config(state='disabled')
    
    def setup_face(self):
        """Setup face recognition for first-time users"""
        def capture_face():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "Cannot access camera")
                return
            
            messagebox.showinfo("Setup", "Position your face in the camera and press SPACE to capture")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Draw rectangle for face positioning
                h, w = frame.shape[:2]
                cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (0, 255, 0), 2)
                cv2.putText(frame, "Position face in green rectangle - Press SPACE to capture", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('Face Setup', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord(' '):  # Space key to capture
                    # Save the captured frame
                    cv2.imwrite('user_face.jpg', frame)
                    messagebox.showinfo("Success", "Face captured successfully!")
                    break
                elif key == ord('q'):  # Q key to quit
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            # Enable authentication button
            self.auth_button.config(state='normal')
            self.status_label.config(text="Face setup complete! Click 'Start Authentication' to login")
        
        # Run capture in separate thread
        threading.Thread(target=capture_face, daemon=True).start()
    
    def start_face_auth(self):
        """Start face recognition authentication"""
        if not os.path.exists('user_face.jpg'):
            messagebox.showerror("Error", "Please setup your face first")
            return
        
        self.status_label.config(text="🔄 Authenticating... Look at the camera")
        self.auth_button.config(state='disabled')
        
        # Run authentication in separate thread
        threading.Thread(target=self.authenticate_face, daemon=True).start()
    
    def authenticate_face(self):
        """Perform face recognition authentication"""
        try:
            success, message = self.face_auth.authenticate()
            
            # Update UI in main thread
            self.root.after(0, self.handle_auth_result, success, message)
            
        except Exception as e:
            self.root.after(0, self.handle_auth_result, False, f"Authentication error: {str(e)}")
    
    def handle_auth_result(self, success, message):
        """Handle the result of face authentication"""
        if success:
            self.is_authenticated = True
            self.status_label.config(text="✅ Authentication successful!")
            self.load_vault_interface()
        else:
            self.status_label.config(text=f"❌ {message}")
            self.auth_button.config(state='normal')
            messagebox.showerror("Authentication Failed", message)
    
    def load_vault_interface(self):
        """Load the main vault interface after successful authentication"""
        # Clear login interface
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main vault interface
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Header frame
        header_frame = tk.Frame(main_frame, bg='#2c3e50')
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, text="🔓 NeuroVault - Secure Notes", 
                               style='Title.TLabel')
        title_label.pack(side='left')
        
        # Logout button
        logout_button = ttk.Button(header_frame, text="Logout", 
                                  command=self.logout, style='Danger.TButton')
        logout_button.pack(side='right')
        
        # Notes frame
        notes_frame = tk.LabelFrame(main_frame, text="Your Secure Notes", 
                                   bg='#34495e', fg='white', font=('Arial', 12, 'bold'))
        notes_frame.pack(expand=True, fill='both', pady=10)
        
        # Text area for notes
        self.notes_text = scrolledtext.ScrolledText(notes_frame, 
                                                   wrap=tk.WORD, 
                                                   font=('Arial', 11),
                                                   bg='#ecf0f1',
                                                   fg='#2c3e50',
                                                   insertbackground='#2c3e50')
        self.notes_text.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Save button
        save_button = ttk.Button(button_frame, text="💾 Save", 
                                command=self.save_vault_data, style='Success.TButton')
        save_button.pack(side='left', padx=(0, 10))
        
        # Clear button
        clear_button = ttk.Button(button_frame, text="🗑️ Clear", 
                                 command=self.clear_notes, style='Danger.TButton')
        clear_button.pack(side='left')
        
        # Status label
        self.vault_status_label = ttk.Label(button_frame, text="", style='Subtitle.TLabel')
        self.vault_status_label.pack(side='right')
        
        # Load existing data
        self.load_vault_data()
    
    def load_vault_data(self):
        """Load and decrypt vault data"""
        try:
            self.vault_data = self.encryptor.load_data()
            self.notes_text.delete(1.0, tk.END)
            self.notes_text.insert(1.0, self.vault_data.get('notes', ''))
            
            last_modified = self.vault_data.get('last_modified', 'Never')
            self.vault_status_label.config(text=f"Last modified: {last_modified}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load vault data: {str(e)}")
    
    def save_vault_data(self):
        """Save and encrypt vault data"""
        try:
            notes_content = self.notes_text.get(1.0, tk.END).strip()
            
            self.vault_data = {
                'notes': notes_content,
                'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.encryptor.save_data(self.vault_data)
            self.vault_status_label.config(text=f"✅ Saved at {self.vault_data['last_modified']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save vault data: {str(e)}")
    
    def clear_notes(self):
        """Clear all notes after confirmation"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all notes?"):
            self.notes_text.delete(1.0, tk.END)
    
    def logout(self):
        """Logout and return to login screen"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.is_authenticated = False
            self.create_login_interface()
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit NeuroVault?"):
            self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    print("🔒 Starting NeuroVault...")
    print("📋 Checking dependencies...")
    
    # Check if required files exist
    required_files = ['face_auth.py', 'encryptor.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Missing required file: {file}")
            return
    
    print("✅ All dependencies found")
    
    # Create and run the application
    app = NeuroVaultApp()
    app.run()


if __name__ == "__main__":
    main()
