# Documentation

## Version

This project is currently at version 1.0.0. It is the initial stable release, and all core features are implemented and functional. Future updates may include additional features, optimizations, and bug fixes.

## Installation and Setup

To install and set up this project, follow these steps:

1. **Clone the Repository**:
   Clone the project repository to your local machine using the following command:

   ```bash
   git clone <repository-url>
   ```

2. **Navigate to the Project Directory**:
   Change into the project directory:

   ```bash
   cd <project-directory>
   ```

3. **Install Dependencies**:
   Ensure you have Python 3.8 or higher installed. Follow these steps to create a virtual environment and install the required dependencies:

   1. **Create a Virtual Environment**:
      Create a virtual environment in the project directory:

      ```bash
      python -m venv venv
      ```

   2. **Activate the Virtual Environment**:
      Activate the virtual environment:

      - On Windows:
        ```bash
        venv\Scripts\activate
        ```
      - On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

   3. **Install Dependencies**:
      Install the required dependencies using pip:

      ```bash
      pip install -r requirements.txt
      ```

   4. **Make Migrations**:
      Apply database migrations to set up the database schema:

      ```bash
      python manage.py makemigrations
      python manage.py migrate
      ```

   5. **Run the Project**:
      Start the development server:
      ```bash
      python manage.py runserver
      ```
