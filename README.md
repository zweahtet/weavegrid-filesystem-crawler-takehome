# File System REST API

## Overview
A REST API to browse and manage files and directories within a specified root directory on your file system. All file operations are restricted to the given root directory to ensure security.

## Features

- **Browse directories**: list all files (including hidden ones) with metadata (name, owner, size, permissions)
- **Read file content**: retrieve the content of text files
- **Create files/directories**: create new files (with optional content) or directories 
- **Update files**: replace the content of existing files
- **Delete files and directories**: delete files or directories (directories are removed recursively)

## Assumptions
- All files are text files encoded in UTF-8.
- File system operations are strictly confined to the specified `ROOT_DIR`.
- A trailing slash in the URL indicates directory creation.

## Notes
- It took me exactly 4 hours to complete this project. I took some breaks in between.
- I run into some issues where the localhost:8000/docs page was not loading properly due to port mismatches in the Docker container, but I was able to resolve it by changing the container port to 8000.
- Some test cases were failing due to the normalization of the URL path. The fastapi web framework automatically normalizes the URL path, and one of the test cases where I tested for accessing outside the root was failing. `/../` was being normalized to `/`, so the endpoint receives an empty string as the path and returns a 200 response rather than raising an error. I was able to resolve this by asking ChatGPT for help, and replace the literal `/../` with the `/%2E%2E/` encoded string.

## Pre-requisites
- [Docker Compose](https://docs.docker.com/compose/install/) 

## Setup

### 1. Prepare the data directory (optional)
Create a directory called `data` in the project root. This directory will be mounted into the Docker container and serve as the root directory for all file operations. 
```bash
mkdir data
```
_(For convenience, I have already included a `data` directory in the project root with some sample files. You may add some files or directories into `data` if you want.)_

### 2. Configuration (optional)
The application requires the `ROOT_DIR` environment variable to be set, which specifies the root directory for file operations. 
_(For convenience, the `docker-compose.yml` file sets the `ROOT_DIR` to `/data` and mounts the host's `./data` directory into the container. You may change the `ROOT_DIR` to any directory of your choice.)_

### 3. Running the API using Docker Compose
Build and start the API server by running:
```bash
docker compose up -d --build
```
This will start the API server on port `8000`. You can verify the API is running by visiting: http://localhost:8000/docs

_(The `-d` flag runs the container in detached mode, so you can continue using the terminal. If you want to see the logs, you can omit the `-d` flag.)_

### 4. Testing the API 
#### Testing via the browser using Swagger UI
Once the API is running, you can interact with it using your web browser through the Swagger UI interface: http://localhost:8000/docs

#### Running Automated Tests with Docker Compose
When you start the API server using Docker Compose, the test suite is automatically run. You can view the test results by running:
```bash
docker compose logs test_runner
```
If you want to run the tests again inside the Docker container, execute the following command from the project root:
```bash
docker compose up -d test_runner
```

### 5. Stopping the API
Stop the API server by running:
```bash
docker compose down
```
