#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced File Organizer Script

This script organizes files in a target directory based on file extension,
placing them into category subfolders (e.g., Images, Documents).

Features:
- Command-line arguments for directory path, concurrency, and dry-run mode
- Logging for visibility
- Concurrency with ThreadPoolExecutor for faster file moves
- Dry-run mode to preview actions without making changes

Author: Your Name
"""

import argparse
import logging
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    # Add more as needed...
}


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments using argparse.
    
    Returns:
        argparse.Namespace: The parsed command-line arguments.
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
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker threads to use for concurrency (default: 4)."
    )
    args = parser.parse_args()
    return args


def categorize_file(file_path: Path) -> str:
    """
    Determine the category name for a file based on its extension.
    
    Args:
        file_path (Path): The path to the file being categorized.
    
    Returns:
        str: The folder/category name the file should be moved into.
    """
    extension = file_path.suffix.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category
    return "Other"


def organize_file(file_path: Path, target_dir: Path, dry_run: bool = False) -> None:
    """
    Move a single file to the appropriate category folder within target_dir.
    
    Args:
        file_path (Path): Path to the file that needs to be organized.
        target_dir (Path): The root directory where organized subfolders are created.
        dry_run (bool): If True, simulate the move but don't actually move the file.
    """
    category = categorize_file(file_path)
    category_folder = target_dir / category

    if not category_folder.exists():
        if not dry_run:
            category_folder.mkdir(parents=True, exist_ok=True)
        logging.info("Created folder: %s", category_folder)

    if not dry_run:
        destination = category_folder / file_path.name
        try:
            shutil.move(str(file_path), str(destination))
            logging.info("Moved: %s -> %s", file_path.name, category)
        except shutil.Error as e:
            logging.error("Failed to move %s: %s", file_path.name, e)
    else:
        logging.info("[DRY RUN] Would move: %s -> %s", file_path.name, category)


def organize_directory(target_dir: Path, dry_run: bool, workers: int = 4) -> None:
    """
    Organize all files within the target directory into categorized subfolders.
    
    Args:
        target_dir (Path): The directory containing files to organize.
        dry_run (bool): If True, only simulate the moves.
        workers (int): Number of threads for concurrent file moves.
    """
    if not target_dir.is_dir():
        logging.error("Target path '%s' is not a valid directory.", target_dir)
        sys.exit(1)

    # Gather all files (non-recursively) in the target directory
    files_to_organize = [f for f in target_dir.iterdir() if f.is_file()]

    if not files_to_organize:
        logging.info("No files found in '%s'. Nothing to organize.", target_dir)
        return

    logging.info(
        "Starting organization of %d files in '%s' (Dry run: %s, Workers: %d).",
        len(files_to_organize), target_dir, dry_run, workers
    )

    # Use threading to speed up organizing many files
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_file = {
            executor.submit(organize_file, f, target_dir, dry_run): f
            for f in files_to_organize
        }

        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                future.result()  # If an exception is raised, it will appear here
            except Exception as exc:
                logging.error("Error organizing %s: %s", file_path.name, exc)

    logging.info("Completed organizing files in '%s'.", target_dir)


def main() -> None:
    """
    Main entry point. Parses arguments, then organizes files in the specified directory.
    """
    args = parse_arguments()
    target_dir = Path(args.target_directory).resolve()

    logging.info("File Organizer Script Starting")
    logging.info("Target directory: %s", target_dir)
    logging.info("Dry run mode: %s", args.dry_run)
    logging.info("Worker threads: %d", args.workers)

    organize_directory(target_dir, args.dry_run, workers=args.workers)

    logging.info("File Organizer Script Finished")


if __name__ == "__main__":
    main()

