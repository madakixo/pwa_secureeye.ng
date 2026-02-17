import docker
import os
import logging

logger = logging.getLogger(__name__)

try:
    client = docker.from_env()
except Exception as e:
    logger.error(f"Failed to connect to Docker: {e}")
    client = None

def start_user_camera(user_id: int, camera_url: str):
    if client is None:
        print(f"MOCK: Starting camera for user {user_id} with URL {camera_url}")
        return

    image = "secureeye-detector:latest"
    container_name = f"detector_{user_id}"

    try:
        # Stop and remove existing container for this user if it exists
        try:
            old_container = client.containers.get(container_name)
            old_container.stop()
            old_container.remove()
        except docker.errors.NotFound:
            pass

        client.containers.run(
            image,
            detach=True,
            name=container_name,
            environment={
                "CAMERA_URL": camera_url,
                "WHATSAPP_TO": os.getenv("WHATSAPP_TO"),
                "CALLMEBOT_KEY": os.getenv("CALLMEBOT_KEY")
            },
            network="secureeye-network",
            restart_policy={"Name": "always"}
        )
        print(f"Started detector container {container_name}")
    except Exception as e:
        print(f"Error starting detector: {e}")
