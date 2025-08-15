#!/usr/bin/env python3

# External Imports
import functions_framework
import requests
from flask import Request, jsonify, make_response
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
import time
import os
import logging

# Internal Imports
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.config import config
from shared.firestore_client import TokenManager

token_manager = TokenManager(config.firebase_project_id)
logger = logging.getLogger(__name__)


@functions_framework.http
def auth_handler(request: Request):
    """Handle OAuth authentication flow."""

    if request.method == "OPTIONS":
        resp = make_response("", 204)
        resp.headers["Access-Control-Allow-Origin"] = config.frontend_url
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE"
        resp.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-User-ID"
        )
        return resp

    def with_cors(response):
        response.headers["Access-Control-Allow-Origin"] = config.frontend_url
        if "Content-Type" not in response.headers:
            response.headers["Content-Type"] = "application/json"
        return response

    if request.method == "GET":
        try:
            if request.path.endswith("/status"):
                return with_cors(_check_status(request))
            return with_cors(_get_auth_url())
        except Exception as e:
            logger.exception("GET failed: %s", e)
            resp = jsonify({"error": str(e)})
            resp.status_code = 500
            return with_cors(resp)

    if request.method == "POST":
        try:
            return with_cors(_exchange_code(request))
        except Exception as e:
            logger.exception("POST failed: %s", e)
            resp = jsonify({"error": str(e)})
            resp.status_code = 500
            return with_cors(resp)

    if request.method == "DELETE":
        try:
            if request.path.endswith("/unlink"):
                return with_cors(_unlink_account(request))
            return with_cors(_exchange_code(request))
        except Exception as e:
            logger.exception("DELETE failed: %s", e)
            resp = jsonify({"error": str(e)})
            resp.status_code = 500
            return with_cors(resp)

    resp = jsonify({"error": "Not found"})
    resp.status_code = 404
    return with_cors(resp)


def _get_auth_url():
    """Generate OAuth authorization URL."""
    oauth_config = config.get_oauth_config()
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={oauth_config['client_id']}&"
        f"redirect_uri={oauth_config['redirect_uri']}&"
        f"scope={'+'.join(oauth_config['scopes'])}&"
        f"response_type=code&"
        f"access_type=offline&"
        f"prompt=consent&"
        f"include_granted_scopes=true"
    )
    return jsonify({"auth_url": auth_url})


def _check_status(request: Request):
    """Check if user has linked their Google Drive."""
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        resp = jsonify({"error": "User ID required"})
        resp.status_code = 400
        return resp

    try:
        token = token_manager.get_token(user_id, "google_drive")
        if not token:
            return jsonify({"linked": False})
        expired = _is_token_expired(token)
        has_access = bool(token.get("access_token")) and not expired
        has_refresh = bool(token.get("refresh_token"))
        is_linked = has_access or has_refresh
        return jsonify({"linked": is_linked})
    except Exception as e:
        return jsonify({"linked": False, "error": str(e)})


def _unlink_account(request: Request):
    """Unlink user's Google Drive account and revoke Google grant."""
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        resp = jsonify({"error": "User ID required"})
        resp.status_code = 400
        return resp

    try:
        token = token_manager.get_token(user_id, "google_drive")
        # Best-effort revoke at Google so next consent returns a refresh_token
        if token:
            revoke_token = token.get("refresh_token") or token.get("access_token")
            if revoke_token:
                try:
                    requests.post(
                        "https://oauth2.googleapis.com/revoke",
                        data={"token": revoke_token},
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                    )
                except Exception:
                    pass
        token_manager.delete_token(user_id, "google_drive")
        return jsonify({"success": True})
    except Exception as e:
        resp = jsonify({"error": str(e)})
        resp.status_code = 500
        return resp


def _is_token_expired(token_data):
    """Check if token is expired."""
    if not token_data or "expires_at" not in token_data:
        return True
    return time.time() >= token_data["expires_at"]


def _exchange_code(request: Request):
    """Exchange authorization code for tokens and persist, preserving refresh_token if not returned."""
    data = request.get_json(silent=True) or {}
    code = data.get("code")
    user_id = data.get("user_id")
    if not code or not user_id:
        resp = jsonify({"error": "code and user_id are required"})
        resp.status_code = 400
        return resp

    oauth_config = config.get_oauth_config()

    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": oauth_config["client_id"],
            "client_secret": oauth_config["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": oauth_config["redirect_uri"],
        },
    )

    if token_response.status_code != 200:
        logger.error("Token exchange failed: %s", token_response.text)
        resp = jsonify(
            {"error": "token_exchange_failed", "details": token_response.text}
        )
        resp.status_code = 502
        return resp

    token_data = token_response.json()

    # Ensure we have an access_token
    access_token = token_data.get("access_token")
    if not access_token:
        logger.error("No access_token in token response: %s", token_data)
        resp = jsonify({"error": "no_access_token"})
        resp.status_code = 502
        return resp

    # Compute absolute expiry
    token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600)

    # Preserve existing refresh_token if Google didn't resend it
    if not token_data.get("refresh_token"):
        existing = token_manager.get_token(user_id, "google_drive")
        if existing and existing.get("refresh_token"):
            token_data["refresh_token"] = existing["refresh_token"]

    token_manager.save_token(user_id, "google_drive", token_data)

    return jsonify(
        {"success": True, "has_refresh_token": bool(token_data.get("refresh_token"))}
    )


# For local development
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Starting auth service in development mode...")

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
    app = functions_framework.create_app(auth_handler)
    port = int(os.environ.get("PORT", 5001))
    logger.info(f"🚀 Auth service running on http://localhost:{port}")
    app.run(port=port, host="0.0.0.0", debug=True)
