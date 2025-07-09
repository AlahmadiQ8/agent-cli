import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime


class TemporaryFileStorage:
    """A temporary file storage system for key-value pairs stored as JSON files"""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the temporary file storage
        
        Args:
            storage_dir: Optional directory path. If None, creates a 'storage' folder in current directory
        """
        if storage_dir is None:
            self.storage_dir = Path("storage")
        else:
            self.storage_dir = Path(storage_dir)
        
        # Create storage directory if it doesn't exist
        self.storage_dir.mkdir(exist_ok=True)
        
        # Create a metadata file to track stored items
        self.metadata_file = self.storage_dir / "metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """Load metadata about stored files"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {}
        except (json.JSONDecodeError, IOError):
            self.metadata = {}
    
    def _save_metadata(self):
        """Save metadata to file"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"Failed to save metadata: {e}")
    
    def _get_file_path(self, key: str) -> Path:
        """Generate file path for a given key"""
        # Sanitize key to make it filesystem-safe
        safe_key = "".join(c for c in key if c.isalnum() or c in "._-")
        if not safe_key:
            safe_key = str(uuid.uuid4())
        
        return self.storage_dir / f"{safe_key}.json"
    
    def store(self, key: str, value: Any) -> bool:
        """
        Store a key-value pair
        
        Args:
            key: The key to store the value under
            value: The value to store (must be JSON serializable)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = self._get_file_path(key)
            
            # Store the data
            data = {
                "key": key,
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "file_path": str(file_path)
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Update metadata
            self.metadata[key] = {
                "file_path": str(file_path),
                "timestamp": data["timestamp"],
                "type": type(value).__name__
            }
            
            self._save_metadata()
            return True
            
        except (json.JSONDecodeError, IOError, TypeError) as e:
            print(f"Error storing key '{key}': {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve a value by key
        
        Args:
            key: The key to retrieve
            
        Returns:
            The stored value or None if not found
        """
        try:
            if key not in self.metadata:
                return None
            
            file_path = Path(self.metadata[key]["file_path"])
            
            if not file_path.exists():
                # Clean up metadata for missing file
                del self.metadata[key]
                self._save_metadata()
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data["value"]
                
        except (json.JSONDecodeError, IOError, KeyError) as e:
            print(f"Error retrieving key '{key}': {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete a key-value pair
        
        Args:
            key: The key to delete
            
        Returns:
            bool: True if successful or key didn't exist, False on error
        """
        try:
            if key not in self.metadata:
                return True  # Key doesn't exist, consider it successful
            
            file_path = Path(self.metadata[key]["file_path"])
            
            # Remove the file if it exists
            if file_path.exists():
                file_path.unlink()
            
            # Remove from metadata
            del self.metadata[key]
            self._save_metadata()
            
            return True
            
        except (IOError, KeyError) as e:
            print(f"Error deleting key '{key}': {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists
        
        Args:
            key: The key to check
            
        Returns:
            bool: True if key exists, False otherwise
        """
        if key not in self.metadata:
            return False
        
        file_path = Path(self.metadata[key]["file_path"])
        return file_path.exists()
    
    def list_keys(self) -> List[str]:
        """
        Get a list of all stored keys
        
        Returns:
            List of all keys
        """
        # Verify files still exist and clean up metadata
        valid_keys = []
        keys_to_remove = []
        
        for key, info in self.metadata.items():
            file_path = Path(info["file_path"])
            if file_path.exists():
                valid_keys.append(key)
            else:
                keys_to_remove.append(key)
        
        # Clean up metadata for missing files
        if keys_to_remove:
            for key in keys_to_remove:
                del self.metadata[key]
            self._save_metadata()
        
        return valid_keys
    
    def get_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata information about a stored key
        
        Args:
            key: The key to get info for
            
        Returns:
            Dictionary with key information or None if not found
        """
        if key not in self.metadata:
            return None
        
        info = self.metadata[key].copy()
        info["key"] = key
        info["exists"] = self.exists(key)
        
        return info
    
    def clear_all(self) -> bool:
        """
        Clear all stored data
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Remove all data files
            for key in list(self.metadata.keys()):
                self.delete(key)
            
            # Clear metadata
            self.metadata = {}
            self._save_metadata()
            
            return True
            
        except Exception as e:
            print(f"Error clearing storage: {e}")
            return False
    
    def get_storage_size(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Dictionary with storage statistics
        """
        total_size = 0
        file_count = 0
        
        for key in self.list_keys():
            if key in self.metadata:
                file_path = Path(self.metadata[key]["file_path"])
                if file_path.exists():
                    total_size += file_path.stat().st_size
                    file_count += 1
        
        # Add metadata file size
        if self.metadata_file.exists():
            total_size += self.metadata_file.stat().st_size
        
        return {
            "total_size_bytes": total_size,
            "total_size_human": self._format_bytes(total_size),
            "file_count": file_count,
            "key_count": len(self.metadata),
            "storage_directory": str(self.storage_dir)
        }
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human readable string"""
        value = float(bytes_value)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if value < 1024.0:
                return f"{value:.1f} {unit}"
            value /= 1024.0
        return f"{value:.1f} TB"
    
    def __len__(self) -> int:
        """Return the number of stored keys"""
        return len(self.list_keys())
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator"""
        return self.exists(key)
    
    def __repr__(self) -> str:
        """String representation"""
        return f"TemporaryFileStorage(dir='{self.storage_dir}', keys={len(self)})"


# Example usage and testing
if __name__ == "__main__":
    # Create storage instance
    storage = TemporaryFileStorage()
    
    # Test basic operations
    print("Testing TemporaryFileStorage...")
    
    # Store some data
    storage.store("user_data", {"name": "John", "age": 30, "city": "New York"})
    storage.store("config", {"debug": True, "api_url": "https://api.example.com"})
    storage.store("numbers", [1, 2, 3, 4, 5])
    storage.store("message", "Hello, World!")
    
    # Retrieve data
    print("Retrieved user_data:", storage.retrieve("user_data"))
    print("Retrieved config:", storage.retrieve("config"))
    print("Retrieved numbers:", storage.retrieve("numbers"))
    print("Retrieved message:", storage.retrieve("message"))
    
    # List all keys
    print("All keys:", storage.list_keys())
    
    # Check existence
    print("'user_data' exists:", storage.exists("user_data"))
    print("'nonexistent' exists:", storage.exists("nonexistent"))
    
    # Get info
    print("Info for 'config':", storage.get_info("config"))
    
    # Storage statistics
    print("Storage stats:", storage.get_storage_size())
    
    # Delete a key
    print("Deleting 'numbers':", storage.delete("numbers"))
    print("Keys after deletion:", storage.list_keys())
    
    # Test container methods
    print("Length:", len(storage))
    print("'config' in storage:", "config" in storage)
    
    print("Storage representation:", repr(storage))
