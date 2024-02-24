# HTTP file storage system

Design and implement an HTTP file storage system to manage various file types including documents, photos, and data.

## Overview

This project involves creating an HTTP service to handle file storage operations. The service starts by default at `http://127.0.0.1:8080` but can be configured to use different addresses.

## Features

- **Service Status Check**: Endpoint to check the status of connected services like databases, caches, and mounted disks.

- **User Management**: Endpoints for user registration and authentication, enabling account creation and secure access.

- **File Handling**: Endpoints to upload, download, and retrieve information about stored files. These operations require user authentication.

- **Optional Features**: Additional functionalities include compressed file downloads, disk space usage information, and file search capabilities.

## Endpoints Summary

- `GET /ping`: Check the connectivity status of all services.
- `POST /auth`: Authenticate a user and provide an authorization token.
- `GET /files/`: Fetch information about uploaded files for authenticated users.
- `POST /files/upload`: Upload a file to the server.
- `GET /files/download`: Download a previously uploaded file.

## Additional (Optional) Endpoints

- Enhanced file download with compression options.
- User disk space usage status.
- File search functionality based on various parameters.

This README outlines the core functionalities required for the sprint, focusing on essential details for quick comprehension and implementation.


## Server Installation

1. **Clone the Repository**
   ```
   git clone git@github.com:dmshirochenko/async-python-sprint-5.git
   ```
2. **.ENV file creation**
    ```
    Create .env file using .env.example
    ```
2. **To Start the Server**
    ```
    make start
    ```
3. **To Stop the Server**
    ```
    make stop
    ```
4. **Open API documentation**
    ```
    For a server running on localhost, access it via:
    Auth service:
    http://localhost:8000/docs
    File storage service:
    http://localhost:8080/docs
    Nginx is working with both services:
    htttp://localhost + endpoint path(auth service/file storage service)
    ```
