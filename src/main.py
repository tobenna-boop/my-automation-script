#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Award-Winning File Organizer Script

Organizes files in a specified directory into categorized subfolders based on their file extensions.

Usage:
    python main.py /path/to/target --dry-run
    python main.py /path/to/target

Author: Your Name
"""
import argparse
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# Map file extensions to folder names
FILE_CATEGORIES: Dict[str, List[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".xls", ".xlsx", ".ppt", ".pptx"],
    "Audio": [".mp3", ".wav", ".ogg", ".aac", ".flac"],
    "Video": [".mp4", ".mov", ".avi", ".mkv", ".wmv"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "Code": [".py", ".js", ".html", ".css", ".c", ".cpp", ".java", ".php", ".rb", ".go"],
    # Add more categories or extensions as needed...
}


def categorize_file(file_path: Path) -> str:
    """Determine which category (subfolder) a file belongs to based on extension.

    Args:
        file_path (Path): The path to the file being categorized.

    Returns:
        str: The category (subfolder) name, or 'Other' if it doesn't match any known extension.
    """
    extension = file_path.suffix.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category
    return "Other"


def organize_directory(
    target_dir: Path, dry_run: bool = False
) -> None:
    """Organize files in the target directory into subfolders by type.

    Args:
        target_dir (Path): The directory containing files to organize.
        dry_run (bool): If True, simulate actions without actually moving files.
    """
    if not target_dir.is_dir():
        logging.error("Target path '%s' is not a valid directory.", target_dir)
        sys.exit(1)

    # List all files (non-recursive) in the target directory
    files = [f for f in target_dir.iterdir() if f.is_file()]

    if not files:
        logging.info("No files found in '%s'. Nothing to organize.", target_dir)
        return

    for file_path in files:
        category = categorize_file(file_path)
        destination_folder = target_dir / category
        if not destination_folder.exists():
            if not dry_run:
                destination_folder.mkdir(parents=True, exist_ok=True)
            logging.info("Created folder: %s", destination_folder)

        logging.info("Organizing file: %s -> %s", file_path.name, category)
        if not dry_run:
            new_location = destination_folder / file_path.name
            try:
                shutil.move(str(file_path), str(new_location))
            except shutil.Error as e:
                logging.error("Error moving file '%s': %s", file_path, e)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments containing directory path and dry_run flag.
    """
    parser = argparse.ArgumentParser(
        description="Organize files in a given directory into categorized subfolders."
    )
    parser.add_argument(
        "target_directory",
        type=str,
        help="The path of the directory to organize."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the organization process without moving any files."
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the file organizer script."""
    args = parse_arguments()
    target_dir = Path(args.target_directory)

    logging.info("Starting File Organizer. Dry run: %s", args.dry_run)
    organize_directory(target_dir, dry_run=args.dry_run)
    logging.info("File Organizer completed.")


if __name__ == "__main__":
    main()

