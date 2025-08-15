#!/usr/bin/env python3

# External Imports
import os
from typing import Dict, Any

# Internal Imports


class Config:
    """Centralized configuration management."""

    def __init__(self):
        self.google_client_id = os.environ["GOOGLE_CLIENT_ID"]
        self.google_client_secret = os.environ["GOOGLE_CLIENT_SECRET"]
        self.firebase_project_id = os.environ["FIREBASE_PROJECT_ID"]
        self.frontend_url = os.environ["FRONTEND_URL"]

    def get_oauth_config(self) -> Dict[str, Any]:
        """Get OAuth configuration for Google Drive."""
        return {
            "client_id": self.google_client_id,
            "client_secret": self.google_client_secret,
            "scopes": ["https://www.googleapis.com/auth/drive.readonly"],
            "redirect_uri": f"{self.frontend_url}/oauth/callback",
        }


config = Config()
