# ==========================================================================
#  Copyright (c) Orison AI, 2024.
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

from private_gpt.server.ingest.ingest_service import IngestService
from pathlib import Path
import logging
from pydantic import BaseModel
from private_gpt.server.chunks.chunks_service import Chunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Source(BaseModel):
    file: str
    page: str
    text: str

    class Config:
        frozen = True

    @staticmethod
    def curate_sources(sources: list[Chunk]) -> list["Source"]:
        curated_sources = []

        for chunk in sources:
            doc_metadata = chunk.document.doc_metadata

            file_name = doc_metadata.get("file_name", "-") if doc_metadata else "-"
            page_label = doc_metadata.get("page_label", "-") if doc_metadata else "-"
            aggregate_chunk = (
                "".join(chunk.previous_texts)
                + ". "
                + chunk.text
                + ". ".join(chunk.next_texts)
            )
            source = Source(
                file=file_name,
                page=page_label,
                text=aggregate_chunk,
            )
            curated_sources.append(source)
            curated_sources = list(
                dict.fromkeys(curated_sources).keys()
            )  # Unique sources only

        return curated_sources


def find_all_files_in_folder(
    root_path: Path, ignored: list[str], files_under_root_folder: list[str]
) -> None:
    """Search all files under the root folder recursively.

    Count them at the same time
    """
    for file_path in root_path.iterdir():
        if file_path.is_file() and file_path.name not in ignored:
            files_under_root_folder.append(file_path)
        elif file_path.is_dir() and file_path.name not in ignored:
            find_all_files_in_folder(file_path, ignored, files_under_root_folder)


def ingest_folder(
    folder_path: Path, ignored: list[str], ingest_service: IngestService
) -> None:
    files_under_root_folder = []
    # Count total documents before ingestion
    find_all_files_in_folder(folder_path, ignored, files_under_root_folder)
    file_list = "\n".join([path.name for path in files_under_root_folder])
    logger.info(
        f"Number of files located: {len(files_under_root_folder)} and paths: \n{file_list}"
    )
    ingest_all(files_under_root_folder, ingest_service)


def ingest_all(files_to_ingest: list[Path], ingest_service: IngestService) -> None:
    logger.info("Ingesting files=%s", [f.name for f in files_to_ingest])
    ingest_service.bulk_ingest([(str(p.name), p) for p in files_to_ingest])
