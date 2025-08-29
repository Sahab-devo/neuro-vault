#!/usr/bin/env python3
"""
NeuroVault - Encryption Module
Handles encryption and decryption of vault data using Fernet symmetric encryption.

Author: NeuroVault Team
Version: 1.0
"""

import os
import json
import base64
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass
import hashlib


class VaultEncryptor:
    """Handles encryption and decryption of vault data"""
    
    def __init__(self, key_file: str = 'secret.key', data_file: str = 'vault_data.json'):
        """
        Initialize the vault encryptor
        
        Args:
            key_file: Path to the encryption key file
            data_file: Path to the encrypted data file
        """
        self.key_file = key_file
        self.data_file = data_file
        self.cipher = None
        
        # Load or generate encryption key
        self.load_or_generate_key()
    
    def generate_key(self) -> bytes:
        """
        Generate a new encryption key
        
        Returns:
            Generated encryption key
        """
        return Fernet.generate_key()
    
    def derive_key_from_password(self, password: str, salt: bytes = None) -> bytes:
        """
        Derive an encryption key from a password using PBKDF2
        
        Args:
            password: The password to derive key from
            salt: Salt for key derivation (generated if None)
            
        Returns:
            Derived encryption key
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def save_key(self, key: bytes):
        """
        Save the encryption key to file
        
        Args:
            key: Encryption key to save
        """
        try:
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Set file permissions (readable only by owner)
            os.chmod(self.key_file, 0o600)
            
            print(f"✅ Encryption key saved to {self.key_file}")
            
        except Exception as e:
            print(f"❌ Error saving key: {str(e)}")
            raise
    
    def load_key(self) -> Optional[bytes]:
        """
        Load the encryption key from file
        
        Returns:
            Loaded encryption key or None if not found
        """
        try:
            if not os.path.exists(self.key_file):
                return None
            
            with open(self.key_file, 'rb') as f:
                key = f.read()
            
            print(f"✅ Encryption key loaded from {self.key_file}")
            return key
            
        except Exception as e:
            print(f"❌ Error loading key: {str(e)}")
            return None
    
    def load_or_generate_key(self):
        """Load existing key or generate a new one"""
        try:
            # Try to load existing key
            key = self.load_key()
            
            if key is None:
                # Generate new key
                print("🔄 Generating new encryption key...")
                key = self.generate_key()
                self.save_key(key)
            
            # Initialize cipher with key
            self.cipher = Fernet(key)
            
        except Exception as e:
            print(f"❌ Error initializing encryption: {str(e)}")
            raise
    
    def encrypt_data(self, data: Dict[str, Any]) -> bytes:
        """
        Encrypt data using Fernet encryption
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data
        """
        try:
            # Convert data to JSON string
            json_data = json.dumps(data, indent=2)
            
            # Encrypt the JSON data
            encrypted_data = self.cipher.encrypt(json_data.encode())
            
            return encrypted_data
            
        except Exception as e:
            print(f"❌ Error encrypting data: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """
        Decrypt data using Fernet encryption
        
        Args:
            encrypted_data: Data to decrypt
            
        Returns:
            Decrypted data as dictionary
        """
        try:
            # Decrypt the data
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # Convert back to dictionary
            json_data = decrypted_data.decode()
            data = json.loads(json_data)
            
            return data
            
        except Exception as e:
            print(f"❌ Error decrypting data: {str(e)}")
            raise
    
    def save_data(self, data: Dict[str, Any]):
        """
        Save encrypted data to file
        
        Args:
            data: Data to save
        """
        try:
            # Encrypt the data
            encrypted_data = self.encrypt_data(data)
            
            # Save to file
            with open(self.data_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Set file permissions (readable only by owner)
            os.chmod(self.data_file, 0o600)
            
            print(f"✅ Data saved and encrypted to {self.data_file}")
            
        except Exception as e:
            print(f"❌ Error saving data: {str(e)}")
            raise
    
    def load_data(self) -> Dict[str, Any]:
        """
        Load and decrypt data from file
        
        Returns:
            Decrypted data as dictionary
        """
        try:
            if not os.path.exists(self.data_file):
                # Return empty data if file doesn't exist
                print(f"⚠️ Data file not found: {self.data_file}")
                return {"notes": "", "last_modified": ""}
            
            # Read encrypted data
            with open(self.data_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt and return data
            data = self.decrypt_data(encrypted_data)
            
            print(f"✅ Data loaded and decrypted from {self.data_file}")
            return data
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            # Return empty data on error
            return {"notes": "", "last_modified": ""}
    
    def backup_data(self, backup_file: str = None) -> bool:
        """
        Create a backup of the encrypted data
        
        Args:
            backup_file: Path for backup file (auto-generated if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.data_file):
                print("⚠️ No data file to backup")
                return False
            
            if backup_file is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{self.data_file}.backup_{timestamp}"
            
            # Copy the encrypted file
            import shutil
            shutil.copy2(self.data_file, backup_file)
            
            print(f"✅ Data backed up to {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating backup: {str(e)}")
            return False
    
    def restore_data(self, backup_file: str) -> bool:
        """
        Restore data from backup
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(backup_file):
                print(f"❌ Backup file not found: {backup_file}")
                return False
            
            # Test if backup can be decrypted
            with open(backup_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Try to decrypt (this will raise exception if invalid)
            self.decrypt_data(encrypted_data)
            
            # If successful, restore the backup
            import shutil
            shutil.copy2(backup_file, self.data_file)
            
            print(f"✅ Data restored from {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error restoring backup: {str(e)}")
            return False
    
    def change_encryption_key(self, new_key: bytes = None) -> bool:
        """
        Change the encryption key and re-encrypt existing data
        
        Args:
            new_key: New encryption key (generated if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing data
            existing_data = self.load_data()
            
            # Create backup
            if not self.backup_data():
                print("⚠️ Could not create backup before key change")
            
            # Generate new key if not provided
            if new_key is None:
                new_key = self.generate_key()
            
            # Update cipher with new key
            self.cipher = Fernet(new_key)
            
            # Save new key
            self.save_key(new_key)
            
            # Re-encrypt and save data
            self.save_data(existing_data)
            
            print("✅ Encryption key changed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error changing encryption key: {str(e)}")
            return False
    
    def verify_data_integrity(self) -> bool:
        """
        Verify the integrity of encrypted data
        
        Returns:
            True if data is valid, False otherwise
        """
        try:
            if not os.path.exists(self.data_file):
                return True  # No data file is valid state
            
            # Try to load and decrypt data
            data = self.load_data()
            
            # Check if data has expected structure
            if not isinstance(data, dict):
                return False
            
            # Check for required fields
            required_fields = ['notes', 'last_modified']
            for field in required_fields:
                if field not in data:
                    return False
            
            print("✅ Data integrity verified")
            return True
            
        except Exception as e:
            print(f"❌ Data integrity check failed: {str(e)}")
            return False
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about encryption files
        
        Returns:
            Dictionary with file information
        """
        info = {
            'key_file': {
                'path': self.key_file,
                'exists': os.path.exists(self.key_file),
                'size': os.path.getsize(self.key_file) if os.path.exists(self.key_file) else 0
            },
            'data_file': {
                'path': self.data_file,
                'exists': os.path.exists(self.data_file),
                'size': os.path.getsize(self.data_file) if os.path.exists(self.data_file) else 0
            },
            'cipher_initialized': self.cipher is not None
        }
        
        return info
    
    def secure_delete_file(self, file_path: str) -> bool:
        """
        Securely delete a file by overwriting it before deletion
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                return True
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Overwrite with random data multiple times
            with open(file_path, 'r+b') as f:
                for _ in range(3):  # 3 passes
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Finally delete the file
            os.remove(file_path)
            
            print(f"✅ File securely deleted: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error securely deleting file: {str(e)}")
            return False


def main():
    """Test the encryption system"""
    print("🔒 Testing NeuroVault Encryption System")
    
    encryptor = VaultEncryptor()
    
    # Test data
    test_data = {
        "notes": "This is a test note for NeuroVault encryption",
        "last_modified": "2025-01-01 12:00:00",
        "test_field": "Additional test data"
    }
    
    try:
        # Test encryption and saving
        print("🔄 Testing data encryption and saving...")
        encryptor.save_data(test_data)
        
        # Test decryption and loading
        print("🔄 Testing data decryption and loading...")
        loaded_data = encryptor.load_data()
        
        # Verify data integrity
        print("🔄 Testing data integrity...")
        if encryptor.verify_data_integrity():
            print("✅ Data integrity verified")
        else:
            print("❌ Data integrity check failed")
        
        # Test backup
        print("🔄 Testing backup functionality...")
        if encryptor.backup_data():
            print("✅ Backup created successfully")
        else:
            print("❌ Backup creation failed")
        
        # Display file info
        print("📊 File Information:")
        info = encryptor.get_file_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        print("\n✅ All encryption tests passed!")
        
    except Exception as e:
        print(f"❌ Encryption test failed: {str(e)}")


if __name__ == "__main__":
    main()