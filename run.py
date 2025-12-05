import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any


def load_env() -> dict[str, str]:
    """Load environment variables from .env file"""
    env_path: Path = Path(".env")
    if not env_path.exists():
        raise FileNotFoundError("Error: .env file not found")

    env_vars: dict[str, str] = {}
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()

    return env_vars


def calculate_file_hash(file_path: Path | str) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash: hashlib._Hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def find_arclight_jar() -> Path:
    """Find the most recent arclight jar in server-core folder"""
    server_core_path: Path = Path("server-core")
    if not server_core_path.exists():
        print("Error: server-core folder not found")
        sys.exit(1)

    arclight_jars: list[Path] = list(server_core_path.glob("arclight-*.jar"))

    if not arclight_jars:
        print("Error: No arclight-*.jar file found in server-core folder")
        sys.exit(1)

    if len(arclight_jars) > 1:
        # Sort by modification time, most recent first
        arclight_jars.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        print(
            f"Found {len(arclight_jars)} arclight jars, using most recent: {arclight_jars[0].name}"
        )

    return arclight_jars[0]


def deploy() -> None:
    """Deploy server configurations to MCSManager"""
    # Load environment variables
    try:
        env_vars: dict[str, str] = load_env()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Get MCSMANAGER_DEMON_PATH
    mcs_path: str | None = env_vars.get("MCSMANAGER_DEMON_PATH")
    if not mcs_path:
        print("Error: MCSMANAGER_DEMON_PATH not found in .env file")
        sys.exit(1)

    # Validate the path exists
    if not os.path.exists(mcs_path):
        print(f"Error: MCSMANAGER_DEMON_PATH '{mcs_path}' does not exist")
        sys.exit(1)

    # Find InstanceConfig folder
    instance_config_path: Path = Path(mcs_path) / "InstanceConfig"
    if not instance_config_path.exists():
        print(f"Error: InstanceConfig folder not found at '{instance_config_path}'")
        sys.exit(1)

    # Find InstanceData folder
    instance_data_path: Path = Path(mcs_path) / "InstanceData"
    if not instance_data_path.exists():
        print(f"Error: InstanceData folder not found at '{instance_data_path}'")
        sys.exit(1)

    # Find the arclight jar to deploy
    arclight_jar: Path = find_arclight_jar()
    arclight_jar_name: str = arclight_jar.name
    arclight_jar_hash: str = calculate_file_hash(arclight_jar)
    print(f"Using arclight jar: {arclight_jar_name}")

    # Load global.json
    global_json_path: Path = Path("global.json")
    if not global_json_path.exists():
        print("Error: global.json not found")
        sys.exit(1)

    with open(global_json_path, "r") as f:
        global_config: dict[str, Any] = json.load(f)

    # Update each instance configuration
    updated_count: int = 0
    copied_count: int = 0
    skipped_copy_count: int = 0

    for server_name, server_config in global_config.items():
        instance_id: str | None = server_config.get("id")
        startup_command: str | None = server_config.get("startup_command")

        if not instance_id or not startup_command:
            print(f"Warning: Skipping {server_name} - missing id or startup_command")
            continue

        print(f"\n--- Processing {server_name} ---")

        # Find the instance JSON file
        instance_file: Path = instance_config_path / f"{instance_id}.json"
        if not instance_file.exists():
            print(
                f"Warning: Instance file not found for {server_name} ({instance_id}.json)"
            )
            continue

        # Find the instance data folder
        instance_folder: Path = instance_data_path / instance_id
        if not instance_folder.exists():
            print(
                f"Warning: Instance data folder not found for {server_name} ({instance_id})"
            )
            continue

        # Remove old arclight jars from instance folder
        old_arclight_jars: list[Path] = list(instance_folder.glob("arclight-*.jar"))
        for old_jar in old_arclight_jars:
            old_jar.unlink()
            print(f"Removed old jar: {old_jar.name}")

        # Copy the new arclight jar if needed
        target_jar_path: Path = instance_folder / arclight_jar_name
        should_copy: bool = True

        if target_jar_path.exists():
            target_jar_hash: str = calculate_file_hash(target_jar_path)
            if target_jar_hash == arclight_jar_hash:
                print(f"Jar already up-to-date, skipping copy")
                should_copy = False
                skipped_copy_count += 1

        if should_copy:
            shutil.copy2(arclight_jar, target_jar_path)
            print(f"Copied {arclight_jar_name} to instance folder")
            copied_count += 1

        # Update the startup command with the correct jar name
        updated_startup_command: str = startup_command.replace(
            "arclight.jar", arclight_jar_name
        )

        # Read and update instance config
        try:
            with open(instance_file, "r") as f:
                instance_data: dict[str, Any] = json.load(f)

            current_start_command: str = instance_data.get("startCommand", "")

            # Only save if modified
            if current_start_command != updated_startup_command:
                instance_data["startCommand"] = updated_startup_command

                with open(instance_file, "w") as f:
                    json.dump(instance_data, f, indent=2)

                print(f"Updated startCommand in config")
                updated_count += 1
            else:
                print(f"startCommand already up-to-date, skipping save")

        except Exception as e:
            print(f"Error updating {server_name}: {e}")

    print(f"\n=== Deployment Summary ===")
    print(f"Config updates: {updated_count}")
    print(f"Jars copied: {copied_count}")
    print(f"Jars skipped (already up-to-date): {skipped_copy_count}")
    print(f"Deployment complete.")


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Minecraft server management script"
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Deploy server configurations to MCSManager",
    )

    args: argparse.Namespace = parser.parse_args()

    if args.deploy:
        deploy()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
