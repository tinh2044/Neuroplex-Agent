import os
import json
import time
from pathlib import Path
import traceback

from ai_engine import agent_config
from ai_engine.utils import logger
from ai_engine.core.kb_db_manager import kb_db_manager

def json2sqlite():
    """Migrate knowledge base data from JSON to SQLite"""
    # Original JSON file path
    json_path = os.path.join(agent_config.workspace, "data", "database.json")

    if not os.path.exists(json_path):
        logger.info(f"Original JSON file not found: {json_path}, no need to migrate")
        return False

    try:
        # Read JSON file
        with open(json_path, "r", encoding='utf-8') as f:
            data = json.load(f)

        if not data or "databases" not in data or not data["databases"]:
            logger.info("JSON file does not contain database information, no need to migrate")
            return False

        # Start migration
        logger.info(f"Start migrating knowledge base data, total {len(data['databases'])} databases")

        # Iterate over all databases
        for db_info in data["databases"]:
            db_id = db_info["db_id"]
            name = db_info["name"]
            description = db_info["description"]
            embed_model = db_info.get("embed_model")
            dimension = db_info.get("dimension")
            metadata = db_info.get("metadata", {})

            logger.info(f"Processing database: {name} (ID: {db_id}), metadata type: {type(metadata)}")

            # Check if database already exists
            existing_db = kb_db_manager.get_database_by_id(db_id)
            if existing_db:
                logger.info(f"Database {name} (ID: {db_id}) already exists, skipping creation")
                continue

            # Create database
            db = kb_db_manager.create_database(
                db_id=db_id,
                name=name,
                description=description,
                embed_model=embed_model,
                dimension=dimension,
                metadata=metadata  # This will be stored as meta_info in kb_db_manager
            )

            # Process files
            files = db_info.get("files", {})
            if isinstance(files, list):
                files = {f["file_id"]: f for f in files}

            for file_id, file_info in files.items():
                # Add file
                kb_db_manager.add_file(
                    db_id=db_id,
                    file_id=file_id,
                    filename=file_info["filename"],
                    path=file_info["path"],
                    file_type=file_info["type"],
                    status=file_info["status"]
                )

                # Process nodes
                nodes = file_info.get("nodes", [])
                for node in nodes:
                    node_metadata = node.get("metadata", {})
                    if node_metadata is None:
                        node_metadata = {}
                    logger.debug(f"Node metadata type: {type(node_metadata)}")

                    kb_db_manager.add_node(
                        file_id=file_id,
                        text=node["text"],
                        hash_value=node.get("hash"),
                        start_char_idx=node.get("start_char_idx"),
                        end_char_idx=node.get("end_char_idx"),
                        metadata=node_metadata  # This will be stored as meta_info in kb_db_manager
                    )

            logger.info(f"Database {name} (ID: {db_id}) migration completed, total {len(files)} files")

        # Backup original JSON file
        backup_path = json_path + f".bak.{int(time.time())}"
        os.rename(json_path, backup_path)
        logger.info(f"Migration completed, original JSON file backed up to: {backup_path}")

        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    json2sqlite()