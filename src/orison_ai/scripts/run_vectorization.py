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

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the parent directory to the path to import orison_ai modules
sys.path.append(str(Path(__file__).parent.parent))

# Internal

from orison_ai.core.environment import get_env
from orison_ai.core.config import VectorConfig, LLMConfig, AppConfig
from orison_ai.database.secrets import OrisonSecrets
from orison_ai.core.client import LLMClient
from orison_ai.storage.vector_store import VectorStore
from orison_ai.storage.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


async def vectorize_pdfs():
    """Vectorize all PDF files from test_data directory"""

    # Get paths
    scripts_dir = Path(__file__).parent
    test_data_dir = scripts_dir.parent / "test_data"

    if not test_data_dir.exists():
        logger.error(f"Test data directory not found: {test_data_dir}")
        return

    # Find all PDF files
    pdf_files = list(test_data_dir.glob("*.pdf"))

    if not pdf_files:
        logger.warning(f"No PDF files found in {test_data_dir}")
        return

    logger.info(f"Found {len(pdf_files)} PDF files to vectorize")

    # Initialize configuration
    env = get_env()
    config = VectorConfig(
        collection_name="test_orison",
        url=env.qdrant_url,
        api_key=env.qdrant_api_key,
    )

    secrets = OrisonSecrets(
        openai_api_key=env.openai_api_key,
        qdrant_url=env.qdrant_url,
        qdrant_api_key=env.qdrant_api_key,
        collection_name=config.collection_name,
    )

    llm_config = LLMConfig()
    app_config = AppConfig()

    # Initialize components
    llm_client = LLMClient(secrets, llm_config, app_config)
    document_processor = DocumentProcessor(config, llm_client)
    vector_store = VectorStore(config, llm_client)

    # Process each PDF file
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing PDF: {pdf_file.name}")

            # Generate file ID from filename
            file_id = pdf_file.stem  # Remove .pdf extension

            # Load and process document
            documents = document_processor.load_document(str(pdf_file), file_id)
            texts, payloads = await document_processor.chunk_documents(
                documents, "research", file_id
            )

            if not texts:
                logger.warning(f"No text chunks generated for {pdf_file.name}")
                continue

            logger.info(f"Generated {len(texts)} chunks from {pdf_file.name}")

            # Store vectors
            await vector_store.store_vectors(texts, payloads, "research", file_id)
            logger.info(
                f"Successfully vectorized {pdf_file.name} - stored {len(texts)} vectors"
            )

        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {e}")
            continue

    logger.info("PDF vectorization completed!")


async def main():
    """Main function to run vectorization"""

    logger.info("Starting PDF vectorization script")

    # Vectorize PDFs
    await vectorize_pdfs()

    logger.info("Script completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
