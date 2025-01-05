# Blog App

This repository contains a web application built using Flask. The application allows users to register, log in, create posts, follow other users, and more. The project follows the recommended structure for a Python Flask project and adheres to Python style guidelines as outlined in [PEP 8](https://peps.python.org/pep-0008/).

## Features

- User Registration and Authentication
- Create, Edit, and Delete Posts
- Follow and Unfollow Users
- Create and Join Spaces
- Create and Manage Channels
- Upload Images and Videos
- Like and Comment on Posts
- Upvote and Downvote Posts
- User Profile Management

## Installation

To run this application locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/Kamande14918/blog-app.git
    cd blog-app
    ```

2. Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Configure the database:
    Update the `SQLALCHEMY_DATABASE_URI` in `app.py` to match your database configuration.

5. Create the database tables:
    ```bash
    flask db upgrade
    ```

6. Run the application:
    ```bash
    flask run
    ```

## Running Tests

To run the tests, ensure you have the dependencies from `dev-requirements.txt` installed in your environment. Use the following command to run the tests:
```bash
pytest
