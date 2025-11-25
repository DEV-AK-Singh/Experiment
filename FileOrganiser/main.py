import os
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_organizer.log'),
        logging.StreamHandler()
    ]
)

# Define file type categories
FILE_CATEGORIES = {
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
    'Videos': ['.mp4', '.mov', '.avi', '.mkv', '.flv'],
    'Audio': ['.mp3', '.wav', '.aac', '.flac'],
    'Archives': ['.zip', '.rar', '.7z', '.tar'],
    'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp'],
    'Executables': ['.exe', '.msi', '.dmg', '.pkg']
}

def organize_files(source_dir):
    """Organize files in source_dir into categorized folders"""
    source_path = Path(source_dir)
    
    # Check if source directory exists
    if not source_path.exists():
        logging.error(f"Source directory {source_dir} does not exist")
        return
    
    # Create category directories
    for category in FILE_CATEGORIES.keys():
        category_path = source_path / category
        category_path.mkdir(exist_ok=True)
    
    # Create 'Others' directory for unknown file types
    others_path = source_path / 'Others'
    others_path.mkdir(exist_ok=True)
    
    # Track statistics
    moved_files = 0
    errors = 0
    
    # Process each file in source directory
    for file_path in source_path.iterdir():
        if file_path.is_file():
            try:
                # Get file extension
                extension = file_path.suffix.lower()
                
                # Find appropriate category
                category = 'Others'
                for cat, extensions in FILE_CATEGORIES.items():
                    if extension in extensions:
                        category = cat
                        break
                
                # Determine destination path
                dest_dir = source_path / category
                dest_path = dest_dir / file_path.name
                
                # Handle file name conflicts
                counter = 1
                original_dest = dest_path
                while dest_path.exists():
                    stem = original_dest.stem
                    suffix = original_dest.suffix
                    dest_path = original_dest.parent / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                # Move file
                # shutil.move(str(file_path), str(dest_path))
                # Copy file
                shutil.copy(str(file_path), str(dest_path))
                moved_files += 1
                logging.info(f"Moved: {file_path.name} -> {category}/{dest_path.name}")
                
            except PermissionError as e:
                errors += 1
                logging.error(f"Permission denied: {file_path.name} - {e}")
            except OSError as e:
                errors += 1
                logging.error(f"OS error moving {file_path.name}: {e}")
            except Exception as e:
                errors += 1
                logging.error(f"Unexpected error with {file_path.name}: {e}")

    # Log summary
    logging.info(f"Organization complete. Moved {moved_files} files, {errors} errors")

def main():
    # Get source directory from user input
    source_dir = input("Enter the directory path to organize: ").strip()
    
    # Validate input
    if not source_dir:
        # source_dir = os.getcwd()  # Use current directory if no input
        logging.error("No source directory provided.")
        return
    
    print(f"Organizing files in: {source_dir}")
    organize_files(source_dir)

if __name__ == "__main__":
    main()