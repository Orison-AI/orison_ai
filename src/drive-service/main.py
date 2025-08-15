#!/usr/bin/env python3

# External Imports
import functions_framework
import requests
from flask import Request, jsonify, make_response
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from google.cloud import firestore
import time
import logging

# Internal Imports
import sys
import os
import pathlib
import re
import uuid
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.config import config
from shared.firestore_client import TokenManager, LoadedFilesManager

token_manager = TokenManager(config.firebase_project_id)
loaded_manager = LoadedFilesManager(config.firebase_project_id)


# Job tracking for progress persistence
class JobManager:
    def __init__(self, firestore_client):
        self.db = firestore_client

    def create_job(self, user_id: str, job_type: str, total_files: int) -> str:
        """Create a new job and return job_id"""
        job_id = str(uuid.uuid4())
        job_data = {
            "job_id": job_id,
            "user_id": user_id,
            "job_type": job_type,
            "status": "running",
            "total_files": total_files,
            "processed_files": 0,
            "successful_files": 0,
            "failed_files": 0,
            "created_at": time.time(),
            "updated_at": time.time(),
            "results": [],
            "error": None,
        }
        self.db.collection("jobs").document(job_id).set(job_data)
        return job_id

    def update_job_progress(self, job_id: str, processed: int, result: dict = None):
        """Update job progress"""
        try:
            # Start with simple updates to test basic functionality
            basic_updates = {"processed_files": processed, "updated_at": time.time()}

            logger.info(f"Updating job {job_id}: processed={processed}")

            # First, try basic update
            self.db.collection("jobs").document(job_id).update(basic_updates)
            logger.info(f"Basic update successful for job {job_id}")

            # Then try to add result if available
            if result:
                try:
                    # Add result to results array
                    self.db.collection("jobs").document(job_id).update(
                        {"results": firestore.ArrayUnion([result])}
                    )
                    logger.info(f"Added result to job {job_id}")

                    # Update counters
                    if result.get("downloaded"):
                        self.db.collection("jobs").document(job_id).update(
                            {"successful_files": firestore.Increment(1)}
                        )
                        logger.info(f"Incremented successful_files for job {job_id}")
                    else:
                        self.db.collection("jobs").document(job_id).update(
                            {"failed_files": firestore.Increment(1)}
                        )
                        logger.info(f"Incremented failed_files for job {job_id}")

                except Exception as e:
                    logger.error(
                        f"Failed to update result/counters for job {job_id}: {e}"
                    )
                    # Continue with basic progress tracking

            logger.info(f"Successfully updated job {job_id} progress")

        except Exception as e:
            logger.error(f"Failed to update job {job_id} progress: {e}")
            # Try to update without the complex operations
            try:
                simple_updates = {
                    "processed_files": processed,
                    "updated_at": time.time(),
                }
                self.db.collection("jobs").document(job_id).update(simple_updates)
                logger.info(f"Updated job {job_id} with simple updates")
            except Exception as e2:
                logger.error(f"Failed even simple update for job {job_id}: {e2}")

    def complete_job(self, job_id: str, status: str = "completed", error: str = None):
        """Mark job as completed"""
        updates = {
            "status": status,
            "updated_at": time.time(),
            "completed_at": time.time(),
        }
        if error:
            updates["error"] = error
        self.db.collection("jobs").document(job_id).update(updates)

    def cancel_job(self, job_id: str):
        """Cancel a running job"""
        updates = {
            "status": "cancelled",
            "updated_at": time.time(),
            "completed_at": time.time(),
            "error": "Job cancelled by user",
        }
        self.db.collection("jobs").document(job_id).update(updates)

    def is_job_cancelled(self, job_id: str) -> bool:
        """Check if job has been cancelled"""
        doc = self.db.collection("jobs").document(job_id).get()
        if doc.exists:
            return doc.to_dict().get("status") == "cancelled"
        return False

    def get_job_status(self, job_id: str) -> dict:
        """Get current job status"""
        doc = self.db.collection("jobs").document(job_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def get_user_jobs(self, user_id: str, limit: int = 10) -> list:
        """Get recent jobs for user"""
        try:
            # Simple query without complex ordering to avoid index requirements
            docs = (
                self.db.collection("jobs")
                .where("user_id", "==", user_id)
                .limit(limit)
                .stream()
            )
            jobs = [doc.to_dict() for doc in docs]
            # Sort in memory instead of in query
            jobs.sort(key=lambda x: x.get("created_at", 0), reverse=True)
            return jobs
        except Exception as e:
            logger.error(f"Failed to get user jobs: {e}")
            return []


job_manager = JobManager(firestore.Client())

DOWNLOAD_BASE = os.environ.get(
    "DOWNLOAD_DIR", os.path.join(os.path.dirname(__file__), "downloads")
)

# Ensure base dir exists
pathlib.Path(DOWNLOAD_BASE).mkdir(parents=True, exist_ok=True)


def _user_download_dir(user_id: str) -> str:
    user_dir = os.path.join(DOWNLOAD_BASE, user_id)
    pathlib.Path(user_dir).mkdir(parents=True, exist_ok=True)
    return user_dir


logger = logging.getLogger(__name__)


@functions_framework.http
def drive_handler(request: Request):
    """Handle Google Drive operations."""

    if request.method == "OPTIONS":
        resp = make_response("", 204)
        resp.headers["Access-Control-Allow-Origin"] = config.frontend_url
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST"
        resp.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-User-ID"
        )
        return resp

    def with_cors(response):
        response.headers["Access-Control-Allow-Origin"] = config.frontend_url
        if "Content-Type" not in response.headers:
            response.headers["Content-Type"] = "application/json"
        return response

    user_id = request.headers.get("X-User-ID")
    if not user_id:
        resp = jsonify({"error": "User ID required"})
        resp.status_code = 401
        return with_cors(resp)

    if request.method == "GET" and request.path.endswith("/files"):
        try:
            body = _list_files(user_id)
            return with_cors(body)
        except Exception as e:
            logger.exception("/files failed: %s", e)
            msg = str(e).lower()
            if "relink" in msg or "refresh_token" in msg or "access_token" in msg:
                resp = jsonify({"error": "relink_required", "message": str(e)})
                resp.status_code = 401
                return with_cors(resp)
            resp = jsonify({"error": str(e)})
            resp.status_code = 500
            return with_cors(resp)

    if request.method == "GET" and request.path.endswith("/loaded"):
        return with_cors(_get_loaded(user_id))

    if request.method == "GET" and request.path.endswith("/debug"):
        return with_cors(_debug_loaded_files(user_id))

    if request.method == "GET" and request.path.endswith("/test-firestore"):
        return with_cors(_test_firestore_operations(user_id))

    if request.method == "POST" and request.path.endswith("/manual-mark-loaded"):
        return with_cors(_manual_mark_loaded(request, user_id))

    if request.method == "GET" and request.path.endswith("/token"):
        try:
            token = _refresh_token_if_needed(user_id)
            return with_cors(jsonify({"access_token": token}))
        except Exception as e:
            logger.exception("/token failed: %s", e)
            msg = str(e).lower()
            if "relink" in msg or "refresh_token" in msg or "access_token" in msg:
                resp = jsonify({"error": "relink_required", "message": str(e)})
                resp.status_code = 401
                return with_cors(resp)
            resp = jsonify({"error": str(e)})
            resp.status_code = 500
            return with_cors(resp)

    if request.method == "POST" and request.path.endswith("/download"):
        return with_cors(_download_files(request, user_id))

    if request.method == "POST" and request.path.endswith("/load"):
        return with_cors(_load_files(request, user_id))

    if request.method == "POST" and request.path.endswith("/unload"):
        return with_cors(_unload_files(request, user_id))

    if request.method == "GET" and "/job/" in request.path:
        # Get job status: /job/{job_id}
        job_id = request.path.split("/job/")[-1]
        return with_cors(_get_job_status(job_id, user_id))

    if (
        request.method == "POST"
        and "/job/" in request.path
        and request.path.endswith("/cancel")
    ):
        # Cancel job: /job/{job_id}/cancel
        job_id = request.path.split("/job/")[-1].replace("/cancel", "")
        return with_cors(_cancel_job(job_id, user_id))

    if request.method == "GET" and request.path.endswith("/jobs"):
        # Get user's recent jobs
        return with_cors(_get_user_jobs(user_id))

    resp = jsonify({"error": "Not found"})
    resp.status_code = 404
    return with_cors(resp)


def _refresh_token_if_needed(user_id: str):
    """Return a valid access_token. Refresh if expired or missing access_token."""
    token_data = token_manager.get_token(user_id, "google_drive")
    if not token_data:
        raise Exception("No token found for user")

    now = time.time()
    expires_at = token_data.get("expires_at") or 0
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    needs_refresh = (expires_at <= now + 60) or (not access_token)

    if needs_refresh:
        if not refresh_token:
            # Cannot refresh without refresh_token
            raise Exception("Missing refresh_token; please relink")
        oauth_config = config.get_oauth_config()
        refresh_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": oauth_config["client_id"],
                "client_secret": oauth_config["client_secret"],
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if refresh_response.status_code != 200:
            raise Exception(f"Refresh failed: {refresh_response.text}")
        new_token_data = refresh_response.json()
        new_access_token = new_token_data.get("access_token")
        if not new_access_token:
            raise Exception("No access_token in refresh response")
        # Persist merged token
        new_token_data["refresh_token"] = refresh_token
        new_token_data["expires_at"] = now + new_token_data.get("expires_in", 3600)
        token_manager.save_token(user_id, "google_drive", new_token_data)
        return new_access_token

    # Use existing access token
    return access_token


def _get_files_data(user_id: str):
    """Get user's Google Drive files data without jsonify (for internal use)."""
    access_token = _refresh_token_if_needed(user_id)

    all_files = []
    page_token = None

    while True:
        params = {
            "pageSize": 1000,  # Maximum allowed by Google Drive API
            "fields": "nextPageToken,files(id,name,mimeType,modifiedTime,iconLink,owners(displayName))",
            "orderBy": "modifiedTime desc",
        }

        if page_token:
            params["pageToken"] = page_token

        response = requests.get(
            "https://www.googleapis.com/drive/v3/files",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
        )

        if response.status_code != 200:
            logger.error(f"Drive API error: {response.text}")
            raise Exception(f"Drive API error: {response.text}")

        data = response.json()
        files = data.get("files", [])
        all_files.extend(files)

        logger.info(
            f"Fetched page with {len(files)} files, total so far: {len(all_files)}"
        )

        # Check if there are more pages
        page_token = data.get("nextPageToken")
        if not page_token:
            break

    loaded_ids = set(loaded_manager.get_loaded_ids(user_id))

    logger.info(f"Found {len(all_files)} total files for user {user_id}")
    logger.info(f"Loaded IDs count: {len(loaded_ids)}")
    logger.info(f"First 10 loaded IDs: {list(loaded_ids)[:10]}")

    loaded_count = 0
    for f in all_files:
        is_loaded = f.get("id") in loaded_ids
        f["loaded"] = is_loaded
        if is_loaded:
            loaded_count += 1

    logger.info(f"Total files with loaded=True: {loaded_count}")

    return all_files


def _list_files(user_id: str):
    """List user's Google Drive files and mark which are loaded."""
    files = _get_files_data(user_id)
    return jsonify({"files": files})


def _sanitize_filename(name: str) -> str:
    # Remove path separators and limit length
    name = re.sub(r'[\\/\0-\x1f<>:"|?*]+', "_", name)
    return name[:150] if len(name) > 150 else name


def _download_to_disk(
    user_id: str, file_id: str, name: str, access_token: str, mime_type: str = None
) -> dict:
    """Download a file content to local disk. Returns metadata with path/size."""
    try:
        # Handle Google Workspace files that need export
        if mime_type and mime_type.startswith("application/vnd.google-apps."):
            return _export_google_file(user_id, file_id, name, access_token, mime_type)

        # Try direct media download for regular files
        r = requests.get(
            f"https://www.googleapis.com/drive/v3/files/{file_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"alt": "media"},
            stream=True,
            timeout=30,  # Add timeout
        )

        if r.status_code == 403 and "binary content" in r.text:
            # This is a Google Workspace file that needs export
            logger.info(f"File {name} needs export, attempting export...")
            return _export_google_file(user_id, file_id, name, access_token, mime_type)

        if r.status_code != 200:
            error_msg = f"HTTP {r.status_code}: {r.text[:200]}"
            logger.error(f"Failed to download {name} (ID: {file_id}): {error_msg}")
            return {
                "file_id": file_id,
                "downloaded": False,
                "reason": error_msg,
                "show_in_ui": True,
            }

        safe_name = _sanitize_filename(name)
        dest_dir = _user_download_dir(user_id)
        dest_path = os.path.join(dest_dir, f"{file_id}_{safe_name}")
        size = 0

        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    size += len(chunk)

        logger.info(
            f"Successfully downloaded {name} (ID: {file_id}) - Size: {size} bytes"
        )
        return {"file_id": file_id, "downloaded": True, "path": dest_path, "size": size}

    except requests.exceptions.Timeout:
        error_msg = "Download timeout (30s)"
        logger.error(f"Timeout downloading {name} (ID: {file_id})")
        return {
            "file_id": file_id,
            "downloaded": False,
            "reason": error_msg,
            "show_in_ui": True,
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(f"Request error downloading {name} (ID: {file_id}): {e}")
        return {
            "file_id": file_id,
            "downloaded": False,
            "reason": error_msg,
            "show_in_ui": True,
        }
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error downloading {name} (ID: {file_id}): {e}")
        return {
            "file_id": file_id,
            "downloaded": False,
            "reason": error_msg,
            "show_in_ui": True,
        }


def _export_google_file(
    user_id: str, file_id: str, name: str, access_token: str, mime_type: str
) -> dict:
    """Export Google Workspace files to downloadable formats."""
    try:
        # Map Google MIME types to export formats
        export_formats = {
            "application/vnd.google-apps.document": "application/pdf",  # Google Docs to PDF
            "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # Sheets to Excel
            "application/vnd.google-apps.presentation": "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # Slides to PowerPoint
        }

        export_mime_type = export_formats.get(mime_type)
        if not export_mime_type:
            logger.info(
                f"Skipping unsupported Google file type: {mime_type} for {name}"
            )
            return {
                "file_id": file_id,
                "downloaded": False,
                "reason": f"Unsupported Google file type: {mime_type}",
                "show_in_ui": False,  # Don't show this as an error in UI
            }

        # Export the file
        r = requests.get(
            f"https://www.googleapis.com/drive/v3/files/{file_id}/export",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"mimeType": export_mime_type},
            stream=True,
            timeout=30,
        )

        if r.status_code != 200:
            error_msg = f"Export failed HTTP {r.status_code}: {r.text[:200]}"
            logger.error(f"Failed to export {name} (ID: {file_id}): {error_msg}")
            return {
                "file_id": file_id,
                "downloaded": False,
                "reason": error_msg,
                "show_in_ui": False,  # Don't show export errors in UI
            }

        # Determine file extension based on export format
        extensions = {
            "application/pdf": ".pdf",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
        }

        extension = extensions.get(export_mime_type, ".exported")
        safe_name = _sanitize_filename(name) + extension
        dest_dir = _user_download_dir(user_id)
        dest_path = os.path.join(dest_dir, f"{file_id}_{safe_name}")
        size = 0

        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    size += len(chunk)

        logger.info(
            f"Successfully exported {name} (ID: {file_id}) as {export_mime_type} - Size: {size} bytes"
        )
        return {"file_id": file_id, "downloaded": True, "path": dest_path, "size": size}

    except Exception as e:
        error_msg = f"Export error: {str(e)}"
        logger.error(f"Export error for {name} (ID: {file_id}): {e}")
        return {
            "file_id": file_id,
            "downloaded": False,
            "reason": error_msg,
            "show_in_ui": False,  # Don't show export errors in UI
        }


def _load_files(request: Request, user_id: str):
    data = request.get_json(silent=True) or {}
    all_flag = data.get("all")
    file_ids = data.get("file_ids", [])

    access_token = _refresh_token_if_needed(user_id)

    if all_flag:
        # Get current list and filter to PDFs only
        all_files = _get_files_data(user_id)

        # Apply PDF filter on backend too
        pdf_mime_types = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "application/vnd.google-apps.document",
        }
        pdf_files = [f for f in all_files if f.get("mimeType") in pdf_mime_types]

        # RESUME LOADING: Filter out already loaded files to avoid duplicates
        already_loaded_ids = set(loaded_manager.get_loaded_ids(user_id))
        unloaded_files = [f for f in pdf_files if f["id"] not in already_loaded_ids]
        ids_to_load = [f["id"] for f in unloaded_files]

        logger.info(
            f"Resume loading: Total PDF files: {len(pdf_files)}, Already loaded: {len(already_loaded_ids)}, To load: {len(ids_to_load)}"
        )
    else:
        ids_to_load = file_ids

    total_files = len(ids_to_load)
    if total_files == 0:
        return jsonify(
            {"success": True, "job_id": None, "message": "No PDF files found to load"}
        )

    # Create job in Firestore for progress tracking
    job_id = job_manager.create_job(user_id, "load_files", total_files)

    # Start background processing
    thread = threading.Thread(
        target=_process_files_async, args=(job_id, user_id, ids_to_load, access_token)
    )
    thread.daemon = True
    thread.start()

    return jsonify(
        {
            "success": True,
            "job_id": job_id,
            "total_files": total_files,
            "message": f"Started loading {total_files} files. Use job_id to check progress.",
        }
    )


def _process_files_async(job_id: str, user_id: str, file_ids: list, access_token: str):
    """Background file processing with Firestore progress tracking"""
    successful_downloads = []

    logger.info(f"Starting async processing for job {job_id}: {len(file_ids)} files")

    try:
        for i, fid in enumerate(file_ids):
            logger.info(f"Processing file {i+1}/{len(file_ids)} (ID: {fid})")

            # Check if job has been cancelled
            if job_manager.is_job_cancelled(job_id):
                logger.info(f"Job {job_id} was cancelled, stopping processing")
                job_manager.complete_job(job_id, "cancelled", "Job cancelled by user")
                return

            try:
                # Get file metadata
                meta_response = requests.get(
                    f"https://www.googleapis.com/drive/v3/files/{fid}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"fields": "id,name,mimeType,size"},
                )

                if meta_response.status_code == 200:
                    meta = meta_response.json()
                    file_name = meta.get("name", fid)
                    file_size = meta.get("size", "Unknown")
                    file_mime_type = meta.get("mimeType")

                    logger.info(
                        f"Downloading file: {file_name} (ID: {fid}) - MIME: {file_mime_type}"
                    )

                    # Download the file
                    result = _download_to_disk(
                        user_id, fid, file_name, access_token, file_mime_type
                    )
                    result["progress"] = f"{i+1}/{len(file_ids)}"
                    result["file_name"] = file_name
                    result["file_size"] = file_size

                    if result.get("downloaded"):
                        successful_downloads.append(fid)
                        logger.info(f"Successfully downloaded: {file_name}")

                        # Mark file as loaded immediately after successful download
                        try:
                            loaded_manager.add_loaded(user_id, [fid])
                            logger.info(f"Marked file {fid} as loaded immediately")
                        except Exception as e:
                            logger.error(f"Failed to mark file {fid} as loaded: {e}")
                    else:
                        logger.warning(
                            f"Failed to download: {file_name} - {result.get('reason')}"
                        )

                    # Update progress in Firestore
                    logger.info(f"Updating progress for file {i+1}/{len(file_ids)}")
                    job_manager.update_job_progress(job_id, i + 1, result)

                else:
                    # Failed to get metadata
                    failed_result = {
                        "file_id": fid,
                        "downloaded": False,
                        "reason": f"metadata fetch failed: {meta_response.status_code}",
                        "progress": f"{i+1}/{len(file_ids)}",
                    }
                    logger.warning(
                        f"Metadata fetch failed for file ID {fid}: {meta_response.status_code}"
                    )
                    job_manager.update_job_progress(job_id, i + 1, failed_result)

            except Exception as e:
                # Individual file error
                error_result = {
                    "file_id": fid,
                    "downloaded": False,
                    "reason": f"error: {str(e)}",
                    "progress": f"{i+1}/{len(file_ids)}",
                }
                logger.error(f"Error processing file ID {fid}: {e}")
                job_manager.update_job_progress(job_id, i + 1, error_result)

        # Files are now marked as loaded individually during download
        # Just log the final summary
        if successful_downloads:
            logger.info(
                f"Job completed: {len(successful_downloads)} files were downloaded and marked as loaded"
            )
            current_loaded = loaded_manager.get_loaded_ids(user_id)
            logger.info(f"User now has {len(current_loaded)} total loaded files")
        else:
            logger.info("Job completed: No files were successfully downloaded")

        # Complete the job (only if not cancelled)
        if not job_manager.is_job_cancelled(job_id):
            logger.info(f"Completing job {job_id} successfully")
            job_manager.complete_job(job_id, "completed")

    except Exception as e:
        # Job-level error
        logger.error(f"Job-level error in {job_id}: {e}")
        job_manager.complete_job(job_id, "failed", str(e))


def _get_job_status(job_id: str, user_id: str):
    """Get current status of a job"""
    job_data = job_manager.get_job_status(job_id)
    if not job_data:
        resp = jsonify({"error": "Job not found"})
        resp.status_code = 404
        return resp

    # Verify job belongs to user
    if job_data.get("user_id") != user_id:
        resp = jsonify({"error": "Unauthorized"})
        resp.status_code = 403
        return resp

    return jsonify(job_data)


def _get_user_jobs(user_id: str):
    """Get recent jobs for user"""
    jobs = job_manager.get_user_jobs(user_id)
    return jsonify({"jobs": jobs})


def _cancel_job(job_id: str, user_id: str):
    """Cancel a running job"""
    job_data = job_manager.get_job_status(job_id)
    if not job_data:
        resp = jsonify({"error": "Job not found"})
        resp.status_code = 404
        return resp

    # Verify job belongs to user
    if job_data.get("user_id") != user_id:
        resp = jsonify({"error": "Unauthorized"})
        resp.status_code = 403
        return resp

    # Only allow cancelling running jobs
    if job_data.get("status") != "running":
        resp = jsonify({"error": "Job is not running"})
        resp.status_code = 400
        return resp

    # Cancel the job
    job_manager.cancel_job(job_id)
    return jsonify({"success": True, "message": "Job cancelled successfully"})


def _unload_files(request: Request, user_id: str):
    data = request.get_json(silent=True) or {}
    all_flag = data.get("all")
    file_ids = data.get("file_ids", [])

    if all_flag:
        ids_to_remove = loaded_manager.get_loaded_ids(user_id)
    else:
        ids_to_remove = file_ids

    # Remove files from disk
    user_dir = _user_download_dir(user_id)
    removed = []
    for fid in ids_to_remove:
        # Remove any file starting with fid_
        for p in pathlib.Path(user_dir).glob(f"{fid}_*"):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass
        removed.append(fid)

    loaded_manager.remove_loaded(user_id, ids_to_remove)
    return jsonify({"success": True, "removed_count": len(ids_to_remove)})


def _download_files(request: Request, user_id: str):
    """Keep existing endpoint that returns file contents for selected files."""
    access_token = _refresh_token_if_needed(user_id)
    data = request.get_json()
    file_ids = data.get("file_ids", [])

    downloaded_files = []

    for file_id in file_ids:
        file_response = requests.get(
            f"https://www.googleapis.com/drive/v3/files/{file_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"alt": "media"},
        )

        if file_response.status_code == 200:
            downloaded_files.append(
                {
                    "file_id": file_id,
                    "content": file_response.content.decode("utf-8", errors="ignore"),
                    "size": len(file_response.content),
                }
            )

    return jsonify(
        {
            "success": True,
            "files_processed": len(downloaded_files),
            "files": downloaded_files,
        }
    )


def _get_loaded(user_id: str):
    return jsonify({"file_ids": loaded_manager.get_loaded_ids(user_id)})


def _debug_loaded_files(user_id: str):
    """Debug endpoint to check loaded files status"""
    try:
        loaded_ids = loaded_manager.get_loaded_ids(user_id)
        logger.info(f"Debug: User {user_id} has {len(loaded_ids)} loaded files")

        return jsonify(
            {
                "user_id": user_id,
                "loaded_count": len(loaded_ids),
                "loaded_ids": loaded_ids[:20],  # First 20 IDs
                "sample_loaded_ids": loaded_ids[:5] if loaded_ids else [],
            }
        )
    except Exception as e:
        logger.error(f"Debug endpoint failed: {e}")
        return jsonify({"error": str(e), "user_id": user_id})


def _test_firestore_operations(user_id: str):
    """Comprehensive test of all Firestore operations"""
    results = {
        "user_id": user_id,
        "firebase_project_id": config.firebase_project_id,
        "tests": {},
    }

    try:
        # Test 1: Basic connectivity
        logger.info(f"Testing Firestore for user {user_id}")
        results["tests"]["connectivity"] = "success"

        # Test 2: Read current loaded files
        try:
            initial_loaded = loaded_manager.get_loaded_ids(user_id)
            results["tests"]["read_loaded"] = {
                "status": "success",
                "count": len(initial_loaded),
                "sample": initial_loaded[:3] if initial_loaded else [],
            }
            logger.info(f"Initial loaded files: {len(initial_loaded)}")
        except Exception as e:
            results["tests"]["read_loaded"] = {"status": "failed", "error": str(e)}
            logger.error(f"Read test failed: {e}")

        # Test 3: Add test files
        test_file_ids = ["test_file_1", "test_file_2", "test_file_3"]
        try:
            loaded_manager.add_loaded(user_id, test_file_ids)
            results["tests"]["add_files"] = {
                "status": "success",
                "added_ids": test_file_ids,
            }
            logger.info(f"Added test files: {test_file_ids}")
        except Exception as e:
            results["tests"]["add_files"] = {"status": "failed", "error": str(e)}
            logger.error(f"Add test failed: {e}")

        # Test 4: Verify files were added
        try:
            after_add = loaded_manager.get_loaded_ids(user_id)
            found_test_files = [fid for fid in test_file_ids if fid in after_add]
            results["tests"]["verify_add"] = {
                "status": "success",
                "total_after_add": len(after_add),
                "test_files_found": found_test_files,
                "all_test_files_present": len(found_test_files) == len(test_file_ids),
            }
            logger.info(
                f"After add: {len(after_add)} files, test files found: {found_test_files}"
            )
        except Exception as e:
            results["tests"]["verify_add"] = {"status": "failed", "error": str(e)}
            logger.error(f"Verify add failed: {e}")

        # Test 5: Remove test files
        try:
            loaded_manager.remove_loaded(user_id, test_file_ids)
            results["tests"]["remove_files"] = {
                "status": "success",
                "removed_ids": test_file_ids,
            }
            logger.info(f"Removed test files: {test_file_ids}")
        except Exception as e:
            results["tests"]["remove_files"] = {"status": "failed", "error": str(e)}
            logger.error(f"Remove test failed: {e}")

        # Test 6: Verify files were removed
        try:
            after_remove = loaded_manager.get_loaded_ids(user_id)
            remaining_test_files = [fid for fid in test_file_ids if fid in after_remove]
            results["tests"]["verify_remove"] = {
                "status": "success",
                "total_after_remove": len(after_remove),
                "test_files_remaining": remaining_test_files,
                "all_test_files_removed": len(remaining_test_files) == 0,
            }
            logger.info(
                f"After remove: {len(after_remove)} files, test files remaining: {remaining_test_files}"
            )
        except Exception as e:
            results["tests"]["verify_remove"] = {"status": "failed", "error": str(e)}
            logger.error(f"Verify remove failed: {e}")

        # Test 7: Direct Firestore access
        try:
            db = firestore.Client(project=config.firebase_project_id)
            doc_ref = db.collection("user_loaded_files").document(user_id)
            doc = doc_ref.get()

            results["tests"]["direct_firestore"] = {
                "status": "success",
                "document_exists": doc.exists,
                "document_data": doc.to_dict() if doc.exists else None,
            }
            logger.info(f"Direct Firestore access: exists={doc.exists}")
        except Exception as e:
            results["tests"]["direct_firestore"] = {"status": "failed", "error": str(e)}
            logger.error(f"Direct Firestore test failed: {e}")

        return jsonify(results)

    except Exception as e:
        logger.error(f"Firestore test failed: {e}")
        results["tests"]["overall"] = {"status": "failed", "error": str(e)}
        return jsonify(results)


def _manual_mark_loaded(request: Request, user_id: str):
    """Manual endpoint to mark files as loaded for testing"""
    try:
        data = request.get_json(silent=True) or {}
        file_ids = data.get("file_ids", [])

        if not file_ids:
            return jsonify({"error": "No file_ids provided"})

        loaded_manager.add_loaded(user_id, file_ids)

        # Verify they were added
        current_loaded = loaded_manager.get_loaded_ids(user_id)
        found_files = [fid for fid in file_ids if fid in current_loaded]

        return jsonify(
            {
                "success": True,
                "requested_files": len(file_ids),
                "files_marked": len(found_files),
                "total_loaded_now": len(current_loaded),
                "marked_files": found_files[:5],  # First 5 for verification
            }
        )

    except Exception as e:
        logger.error(f"Manual mark loaded failed: {e}")
        return jsonify({"error": str(e)})


# For local development
if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Starting drive service in development mode...")

    # Check if required environment variables are set
    if not os.environ.get("GOOGLE_CLIENT_ID") or os.environ.get(
        "GOOGLE_CLIENT_ID"
    ).startswith("your_"):
        logger.warning("⚠️  GOOGLE_CLIENT_ID not properly set!")
        logger.info(
            "Please set your real Google OAuth Client ID from Google Cloud Console"
        )
    else:
        logger.info(
            f"✅ Using Google Client ID: {os.environ.get('GOOGLE_CLIENT_ID')[:20]}..."
        )

    # Use functions-framework to run locally
    app = functions_framework.create_app(drive_handler)
    port = int(os.environ.get("PORT", 5002))
    logger.info(f"🚀 Drive service running on http://localhost:{port}")
    app.run(port=port, host="0.0.0.0", debug=True)
