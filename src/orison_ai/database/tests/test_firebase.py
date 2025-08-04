#! /usr/bin/env python3.11

# ==========================================================================
#  Copyright (c) Orison AI, 2025.
#
#  All rights reserved. All hardware and software names used are registered
#  trade names and/or registered trademarks of the respective manufacturers.
#
#  The user of this computer program acknowledges that the above copyright
#  notice, which constitutes the Universal Copyright Convention, will be
#  attached at the position in the function of the computer program which the
#  author has deemed to sufficiently express the reservation of copyright.
#  It is prohibited for customers, users and/or third parties to remove,
#  modify or move this copyright notice.
# ==========================================================================

# External

import pytest
import os
import asyncio
import tempfile
import hashlib
import logging
from datetime import datetime, timezone

# Internal

from database.firebase_storage import FirebaseStorage

logger = logging.getLogger(__name__)


class TestFirebaseStorage:
    """Test Firebase Storage upload/download/delete operations"""

    # Test constants
    TEST_ATTORNEY_ID = "test_attorney_storage"
    TEST_APPLICANT_ID = "test_applicant_storage"
    TEST_TAG = "test_documents"

    @pytest.fixture(scope="class")
    def event_loop(self):
        """Create event loop for async tests"""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()

    def create_test_file(self, filename: str, content: str) -> str:
        """Create a test file with given content"""
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return file_path

    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of a file for integrity verification"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def build_remote_path(self, filename: str) -> str:
        """Build remote file path following the application's convention"""
        return os.path.join(
            "documents",
            "attorneys",
            self.TEST_ATTORNEY_ID,
            "applicants",
            self.TEST_APPLICANT_ID,
            self.TEST_TAG,
            filename,
        ).replace(
            "\\", "/"
        )  # Ensure forward slashes for cloud storage

    @pytest.mark.asyncio
    async def test_text_file_upload_download(self):
        """Test uploading and downloading a text file"""
        try:
            # Create test file
            test_content = f"""Test Document
            
This is a test document created on {datetime.now(timezone.utc).isoformat()}.

It contains multiple lines and unicode characters: 
- Bullet point 1 ✓
- Bullet point 2 ✓  
- Special chars: åäö, 中文, العربية

This file is used to test Firebase Storage operations.
"""

            filename = "test_document.txt"
            local_file = self.create_test_file(filename, test_content)
            remote_path = self.build_remote_path(filename)

            logger.info(
                f"Created test file: {local_file} -> Remote path: {remote_path}"
            )

            # Calculate original hash
            original_hash = self.calculate_file_hash(local_file)

            # Upload file
            await FirebaseStorage.upload_file(local_file, remote_path)
            logger.info("Text file uploaded successfully")

            # Download file to different location
            download_path = self.create_test_file("downloaded_" + filename, "")
            await FirebaseStorage.download_file(remote_path, download_path)
            logger.info("Text file downloaded successfully")

            # Verify integrity
            downloaded_hash = self.calculate_file_hash(download_path)
            assert original_hash == downloaded_hash, "File integrity check failed"

            # Verify content
            with open(download_path, "r", encoding="utf-8") as f:
                downloaded_content = f.read()

            assert downloaded_content == test_content, "File content mismatch"

            logger.info(
                f"Text file upload/download test passed - "
                f"Hash verification: {original_hash == downloaded_hash} "
                f"(Original: {original_hash[:8]}..., Downloaded: {downloaded_hash[:8]}...), "
                f"Size: {len(test_content)} chars"
            )

            # Test delete operation
            await FirebaseStorage.delete_file(remote_path)
            logger.info("Text file deleted from Firebase Storage successfully")

            # Verify deletion using file_exists method
            file_still_exists = await FirebaseStorage.file_exists(remote_path)
            if file_still_exists:
                pytest.fail("File was not properly deleted from Firebase Storage")
            else:
                logger.info(
                    "Confirmed: File successfully deleted from Firebase Storage"
                )

            # Cleanup local files
            os.remove(local_file)
            os.remove(download_path)

        except Exception as e:
            pytest.fail(f"Text file upload/download test failed: {e}")

    @pytest.mark.asyncio
    async def test_binary_file_upload_download(self):
        """Test uploading and downloading a binary file"""
        try:
            # Create test binary file (simple PDF-like structure)
            binary_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
xref
0 5
0000000000 65535 f 
0000000010 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
398
%%EOF"""

            filename = "test_document.pdf"
            temp_dir = tempfile.gettempdir()
            local_file = os.path.join(temp_dir, filename)

            # Write binary content
            with open(local_file, "wb") as f:
                f.write(binary_content)

            remote_path = self.build_remote_path(filename)

            logger.info(
                f"Created binary test file: {local_file} ({len(binary_content)} bytes)"
            )

            # Calculate original hash
            original_hash = self.calculate_file_hash(local_file)

            # Upload file
            await FirebaseStorage.upload_file(local_file, remote_path)
            logger.info("Binary file uploaded successfully")

            # Download file
            download_path = os.path.join(temp_dir, "downloaded_" + filename)
            await FirebaseStorage.download_file(remote_path, download_path)
            logger.info("Binary file downloaded successfully")

            # Verify integrity
            downloaded_hash = self.calculate_file_hash(download_path)
            assert (
                original_hash == downloaded_hash
            ), "Binary file integrity check failed"

            # Verify binary content
            with open(download_path, "rb") as f:
                downloaded_content = f.read()

            assert downloaded_content == binary_content, "Binary file content mismatch"

            logger.info(
                f"Binary file upload/download test passed - "
                f"Hash verification: {original_hash == downloaded_hash} "
                f"(Original: {original_hash[:8]}..., Downloaded: {downloaded_hash[:8]}...), "
                f"Size: {len(binary_content)} bytes"
            )

            # Test delete operation
            await FirebaseStorage.delete_file(remote_path)
            logger.info("Binary file deleted from Firebase Storage successfully")

            # Verify deletion using file_exists method
            file_still_exists = await FirebaseStorage.file_exists(remote_path)
            if file_still_exists:
                pytest.fail(
                    "Binary file was not properly deleted from Firebase Storage"
                )
            else:
                logger.info(
                    "Confirmed: Binary file successfully deleted from Firebase Storage"
                )

            # Cleanup local files
            os.remove(local_file)
            os.remove(download_path)

        except Exception as e:
            pytest.fail(f"Binary file upload/download test failed: {e}")

    @pytest.mark.asyncio
    async def test_multiple_file_operations(self):
        """Test uploading, downloading and managing multiple files"""
        try:
            files_to_test = [
                (
                    "resume.txt",
                    "John Doe Resume\nEducation: PhD Computer Science\nExperience: 5 years at Google",
                ),
                (
                    "cover_letter.txt",
                    "Dear Hiring Manager,\nI am writing to apply for the position...",
                ),
                (
                    "transcripts.txt",
                    "University Transcripts\nGPA: 3.9/4.0\nCourses: AI, ML, Algorithms",
                ),
                (
                    "references.txt",
                    "Professional References:\n1. Dr. Jane Smith\n2. Prof. Bob Johnson",
                ),
            ]

            upload_results = []

            # Upload all files
            for filename, content in files_to_test:
                local_file = self.create_test_file(filename, content)
                remote_path = self.build_remote_path(filename)

                await FirebaseStorage.upload_file(local_file, remote_path)

                original_hash = self.calculate_file_hash(local_file)
                upload_results.append(
                    {
                        "filename": filename,
                        "local_file": local_file,
                        "remote_path": remote_path,
                        "original_hash": original_hash,
                        "content_length": len(content),
                    }
                )

                os.remove(local_file)  # Remove original after upload

            logger.info(
                f"Multiple file upload phase completed - {len(upload_results)} files uploaded successfully"
            )

            # Download and verify all files
            verification_results = []

            for result in upload_results:
                download_path = self.create_test_file(
                    f"downloaded_{result['filename']}", ""
                )

                await FirebaseStorage.download_file(
                    result["remote_path"], download_path
                )

                downloaded_hash = self.calculate_file_hash(download_path)
                integrity_check = downloaded_hash == result["original_hash"]

                verification_results.append(
                    {
                        "filename": result["filename"],
                        "integrity_check": integrity_check,
                        "original_hash": result["original_hash"],
                        "downloaded_hash": downloaded_hash,
                    }
                )

                os.remove(download_path)  # Cleanup

            # Verify all files passed integrity check
            all_passed = all(
                result["integrity_check"] for result in verification_results
            )
            assert all_passed, "Not all files passed integrity check"

            # Prepare summary
            passed_files = [
                r["filename"] for r in verification_results if r["integrity_check"]
            ]
            failed_files = [
                r["filename"] for r in verification_results if not r["integrity_check"]
            ]

            logger.info(
                f"Multiple file operations test passed - "
                f"Files tested: {len(files_to_test)}, "
                f"Passed: {len(passed_files)}, Failed: {len(failed_files)} "
                f"(All files: {', '.join([f['filename'] for f in verification_results])})"
            )

            # Test delete operations for all uploaded files
            deletion_results = []
            for result in upload_results:
                try:
                    await FirebaseStorage.delete_file(result["remote_path"])
                    deletion_results.append(
                        {"filename": result["filename"], "deleted": True}
                    )
                    logger.info(
                        f"Successfully deleted {result['filename']} from Firebase Storage"
                    )
                except Exception as e:
                    deletion_results.append(
                        {
                            "filename": result["filename"],
                            "deleted": False,
                            "error": str(e),
                        }
                    )
                    logger.error(f"Failed to delete {result['filename']}: {e}")

            # Verify all files were deleted
            all_deleted = all(dr["deleted"] for dr in deletion_results)
            assert (
                all_deleted
            ), f"Not all files were deleted: {[dr for dr in deletion_results if not dr['deleted']]}"

            # Verify deletion using file_exists method for one of the files
            test_remote_path = upload_results[0]["remote_path"]
            file_still_exists = await FirebaseStorage.file_exists(test_remote_path)
            if file_still_exists:
                pytest.fail("Files were not properly deleted from Firebase Storage")
            else:
                logger.info(
                    "Confirmed: All files successfully deleted from Firebase Storage"
                )

            logger.info(
                f"Multiple file deletion test passed - {len(deletion_results)} files deleted successfully"
            )

        except Exception as e:
            pytest.fail(f"Multiple file operations test failed: {e}")
