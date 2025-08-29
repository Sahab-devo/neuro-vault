#!/usr/bin/env python3
"""
NeuroVault - Face Recognition Authentication Module
Handles face detection, encoding, and authentication using OpenCV and face_recognition.

Author: NeuroVault Team
Version: 1.0
"""

import cv2
import face_recognition
import numpy as np
import os
import pickle
from typing import Tuple, Optional
import time


class FaceAuthenticator:
    """Handles face recognition authentication for NeuroVault"""
    
    def __init__(self, reference_image_path: str = 'user_face.jpg', 
                 encodings_path: str = 'face_encodings.pkl'):
        """
        Initialize the face authenticator
        
        Args:
            reference_image_path: Path to the reference face image
            encodings_path: Path to save/load face encodings
        """
        self.reference_image_path = reference_image_path
        self.encodings_path = encodings_path
        self.known_face_encodings = []
        self.tolerance = 0.6  # Face recognition tolerance (lower = more strict)
        self.max_attempts = 3  # Maximum authentication attempts
        self.timeout_seconds = 10  # Timeout for authentication
        
        # Load or create face encodings
        self.load_or_create_encodings()
    
    def load_or_create_encodings(self):
        """Load existing face encodings or create new ones from reference image"""
        try:
            # Try to load existing encodings
            if os.path.exists(self.encodings_path):
                with open(self.encodings_path, 'rb') as f:
                    self.known_face_encodings = pickle.load(f)
                print(f"✅ Loaded face encodings from {self.encodings_path}")
                return
            
            # Create new encodings if reference image exists
            if os.path.exists(self.reference_image_path):
                self.create_face_encodings()
            else:
                print(f"⚠️ Reference image not found: {self.reference_image_path}")
                print("Please run face setup first")
                
        except Exception as e:
            print(f"❌ Error loading face encodings: {str(e)}")
            self.known_face_encodings = []
    
    def create_face_encodings(self):
        """Create face encodings from the reference image"""
        try:
            print(f"🔄 Creating face encodings from {self.reference_image_path}")
            
            # Load the reference image
            reference_image = face_recognition.load_image_file(self.reference_image_path)
            
            # Find face locations in the reference image
            face_locations = face_recognition.face_locations(reference_image)
            
            if not face_locations:
                raise Exception("No face found in reference image")
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(reference_image, face_locations)
            
            if not face_encodings:
                raise Exception("Could not encode face from reference image")
            
            # Store the encodings
            self.known_face_encodings = face_encodings
            
            # Save encodings to file
            with open(self.encodings_path, 'wb') as f:
                pickle.dump(self.known_face_encodings, f)
            
            print(f"✅ Face encodings created and saved to {self.encodings_path}")
            
        except Exception as e:
            print(f"❌ Error creating face encodings: {str(e)}")
            raise
    
    def detect_and_encode_face(self, frame: np.ndarray) -> Tuple[bool, Optional[list]]:
        """
        Detect and encode faces in a frame
        
        Args:
            frame: Input frame from camera
            
        Returns:
            Tuple of (success, face_encodings)
        """
        try:
            # Convert BGR to RGB (OpenCV uses BGR, face_recognition uses RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find face locations
            face_locations = face_recognition.face_locations(rgb_frame)
            
            if not face_locations:
                return False, None
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            if not face_encodings:
                return False, None
            
            return True, face_encodings
            
        except Exception as e:
            print(f"❌ Error detecting face: {str(e)}")
            return False, None
    
    def verify_face(self, face_encodings: list) -> bool:
        """
        Verify if the detected face matches the known face
        
        Args:
            face_encodings: List of face encodings from current frame
            
        Returns:
            True if face matches, False otherwise
        """
        try:
            if not self.known_face_encodings or not face_encodings:
                return False
            
            # Compare each detected face with known faces
            for face_encoding in face_encodings:
                # Calculate face distance
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, face_encoding
                )
                
                # Check if any distance is within tolerance
                matches = face_distances <= self.tolerance
                
                if any(matches):
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error verifying face: {str(e)}")
            return False
    
    def authenticate(self) -> Tuple[bool, str]:
        """
        Perform face authentication using webcam
        
        Returns:
            Tuple of (success, message)
        """
        if not self.known_face_encodings:
            return False, "No reference face found. Please setup face first."
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return False, "Cannot access camera"
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("🔄 Starting face authentication...")
        print("📷 Look at the camera for authentication")
        
        start_time = time.time()
        attempts = 0
        consecutive_matches = 0
        required_matches = 3  # Require 3 consecutive matches for security
        
        try:
            while attempts < self.max_attempts:
                # Check timeout
                if time.time() - start_time > self.timeout_seconds:
                    break
                
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect and encode face
                success, face_encodings = self.detect_and_encode_face(frame)
                
                if success:
                    # Verify face
                    if self.verify_face(face_encodings):
                        consecutive_matches += 1
                        print(f"✅ Face match {consecutive_matches}/{required_matches}")
                        
                        if consecutive_matches >= required_matches:
                            cap.release()
                            return True, "Authentication successful"
                    else:
                        consecutive_matches = 0
                        attempts += 1
                        print(f"❌ Face mismatch (attempt {attempts}/{self.max_attempts})")
                else:
                    consecutive_matches = 0
                
                # Add small delay to prevent excessive CPU usage
                time.sleep(0.1)
            
            cap.release()
            
            if attempts >= self.max_attempts:
                return False, "Authentication failed: Maximum attempts exceeded"
            else:
                return False, "Authentication failed: Timeout"
                
        except Exception as e:
            cap.release()
            return False, f"Authentication error: {str(e)}"
    
    def update_reference_face(self, new_image_path: str) -> bool:
        """
        Update the reference face image and recreate encodings
        
        Args:
            new_image_path: Path to the new reference image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Backup current reference if it exists
            if os.path.exists(self.reference_image_path):
                backup_path = f"{self.reference_image_path}.backup"
                os.rename(self.reference_image_path, backup_path)
            
            # Copy new image
            import shutil
            shutil.copy2(new_image_path, self.reference_image_path)
            
            # Recreate encodings
            self.create_face_encodings()
            
            print("✅ Reference face updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error updating reference face: {str(e)}")
            return False
    
    def test_camera(self) -> bool:
        """
        Test if camera is accessible and working
        
        Returns:
            True if camera is working, False otherwise
        """
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                return False
            
            ret, frame = cap.read()
            cap.release()
            
            return ret
            
        except Exception:
            return False
    
    def get_face_info(self) -> dict:
        """
        Get information about the stored face encodings
        
        Returns:
            Dictionary with face information
        """
        info = {
            'encodings_count': len(self.known_face_encodings),
            'reference_image_exists': os.path.exists(self.reference_image_path),
            'encodings_file_exists': os.path.exists(self.encodings_path),
            'tolerance': self.tolerance,
            'max_attempts': self.max_attempts,
            'timeout_seconds': self.timeout_seconds
        }
        
        return info


def main():
    """Test the face authentication system"""
    print("🔒 Testing NeuroVault Face Authentication")
    
    authenticator = FaceAuthenticator()
    
    # Test camera
    if not authenticator.test_camera():
        print("❌ Camera not accessible")
        return
    
    print("✅ Camera accessible")
    
    # Show face info
    info = authenticator.get_face_info()
    print(f"📊 Face Info: {info}")
    
    # Test authentication
    if info['reference_image_exists']:
        print("🔄 Starting authentication test...")
        success, message = authenticator.authenticate()
        print(f"Result: {'✅' if success else '❌'} {message}")
    else:
        print("⚠️ No reference face found. Please setup face first.")


if __name__ == "__main__":
    main()
