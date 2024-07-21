import docker

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()

    def run_code(self, code, language):
        # Create a temporary file with the user's code
        with open('temp_code.py', 'w') as f:
            f.write(code)

        # Build the Docker image
        image, build_logs = self.client.images.build(path=".", dockerfile="Dockerfile")

        # Run the Docker container
        container = self.client.containers.run(image, "python temp_code.py", detach=True)
        logs = container.logs()
        container.remove()

        return logs.decode('utf-8')

docker_manager = DockerManager()
