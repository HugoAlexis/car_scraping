# Web Scraping Project with Custom ORM and PostgreSQL

## Overview

This project extracts data daily from multiple websites using custom scrapers, then stores the structured data in a PostgreSQL database.  
A simple custom ORM is implemented to interact with the database using Python objects. The project includes automated scheduling and testing.

## Project Structure

- `scraping/` - General scraping utilities and helpers.  
- `webpage_models/` - Site-specific scrapers to extract data from each target website.  
- `orm/` - Custom ORM implementation and database connection management using a singleton pattern.  
- `scheduler/` - Automation module to run scraping tasks periodically.  
- `tests/` - Unit and integration tests for scrapers, ORM, and data pipeline.  
- `db/` - SQL scripts and initialization scripts for PostgreSQL setup.

## Getting Started

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   
2. Set up environment variables in a .env file 
   
    DB_NAME = ''       # Database bane

    DB_USER = ''       # Database username

    DB_PASSWORD = ''   # Database password

    DB_HOST = ''       # Database host

    DB_PORT = ''       # Database port


3. Initialize the database by running
    
    ```bash
    python db/init_db.py

4. Run the scraper manually

    ```bash
   python main.py
   

## Notes

* The ORM manages a single database connection using a singleton pattern for efficiency
* Scheduler automates daily scraping runs

## License

MIT License