# EDC Data Analysis Application

A Flask-based web application for scraping and visualizing EDC (Electricity Data Collection) data from the OKTE website. The application allows users to select a date range, scrape the data, store it in a SQLite database, and visualize it through interactive graphs.

## Features

- Date range selection for data scraping
- Automatic data scraping from OKTE website
- SQLite database storage
- Interactive data visualization using Plotly
- Clean and responsive user interface

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd EDC_data
```

2. Create and activate a virtual environment (optional but recommended):
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python run.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Using the application:
   - On the home page, select a date range using the date pickers
   - Click "Scrape Data" to fetch and store the data
   - Navigate to the "Graph" page to view the data visualization
   - The graph shows three metrics:
     - Positive flexibility
     - Negative flexibility
     - Shared electricity

## Project Structure

```
EDC_data/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── models.py            # Database models
│   ├── routes.py            # Application routes
│   ├── scraper.py           # Data scraping logic
│   └── static/
│       └── css/
│           └── style.css    # Application styles
├── templates/
│   ├── base.html            # Base template
│   ├── index.html           # Home page template
│   └── graph.html           # Graph visualization template
├── instance/
│   └── database.db          # SQLite database (created automatically)
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── README.md               # This file
```

## Data Model

The application uses a SQLite database with the following schema:

```python
class EDCData:
    id: Integer (Primary Key)
    date: Date
    time_period: String
    positive_flexibility: Float
    negative_flexibility: Float
    shared_electricity: Float
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data source: [OKTE website](https://okte.sk/sk/edc/zverejnovanie-udajov/aktivovana-agregovana-flexibilita-a-zdielanie-elektriny/)
- Built with Flask, SQLAlchemy, and Plotly 