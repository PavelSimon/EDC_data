from flask import Blueprint, render_template, request, jsonify, flash
from app.models import EDCData
from app import db
from app.scraper import scrape_edc_data
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd
import logging
import sqlite3

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/scrape', methods=['POST'])
def scrape():
    try:
        # Get and validate dates
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        
        # Validate date range
        if end_date < start_date:
            return jsonify({'message': 'End date must be after start date'}), 400
        
        if end_date > datetime.now():
            return jsonify({'message': 'Cannot scrape data for future dates'}), 400
        
        # Check if data already exists for this date range
        existing_data = EDCData.query.filter(
            EDCData.date >= start_date.date(),
            EDCData.date <= end_date.date()
        ).first()
        
        if existing_data:
            return jsonify({'message': 'Data for this date range already exists in the database'}), 409
        
        # Scrape data
        logging.info(f"Starting scrape for date range: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
        data = scrape_edc_data(start_date, end_date)
        
        if not data:
            logging.warning("No data was returned from the scraper")
            return jsonify({
                'message': 'No data found for the selected date range. Please check the date range and try again.'
            }), 404
        
        # Save to database
        try:
            for item in data:
                edc_data = EDCData(**item)
                db.session.add(edc_data)
            
            db.session.commit()
            logging.info(f"Successfully saved {len(data)} records to database")
            
            return jsonify({
                'message': f'Successfully scraped and stored {len(data)} records for the period {start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}'
            })
        except Exception as e:
            db.session.rollback()
            logging.error(f"Database error: {str(e)}")
            return jsonify({'message': f'Error saving data to database: {str(e)}'}), 500
            
    except ValueError as e:
        logging.error(f"Invalid date format: {str(e)}")
        return jsonify({'message': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        logging.error(f"Unexpected error during scraping: {str(e)}")
        return jsonify({'message': f'Error during scraping: {str(e)}'}), 500

@main.route('/graph')
def graph():
    try:
        # First try direct SQL query to verify data exists
        conn = sqlite3.connect('okte_data.db')
        cursor = conn.cursor()
        
        # Get count
        cursor.execute("SELECT COUNT(*) FROM okte_data")
        count = cursor.fetchone()[0]
        logging.info(f"Direct SQL count: {count}")
        print(f"Direct SQL count: {count}")
        
        # Get sample data
        cursor.execute("SELECT * FROM okte_data LIMIT 5")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        print(f"Direct SQL sample data rows: {rows}")
        logging.info(f"Direct SQL sample data columns: {columns}")
        logging.info(f"Direct SQL sample data rows: {rows}")
        
        # Now try SQLAlchemy query with detailed debugging
        logging.info("\nAttempting SQLAlchemy query...")
        
        # Debug session state
        logging.info(f"Session is active: {db.session.is_active}")
        logging.info(f"Session is modified: {db.session.is_modified()}")
        
        # Try different query approaches
        query1 = EDCData.query
        query2 = db.session.query(EDCData)
        
        logging.info(f"Query1 SQL: {query1.statement}")
        logging.info(f"Query2 SQL: {query2.statement}")
        
        # Try to get first record with both queries
        first_record1 = query1.first()
        first_record2 = query2.first()
        
        logging.info(f"Query1 first record: {first_record1}")
        logging.info(f"Query2 first record: {first_record2}")
        
        # Try to get all records
        data1 = query1.all()
        data2 = query2.all()
        
        logging.info(f"Query1 retrieved {len(data1)} records")
        logging.info(f"Query2 retrieved {len(data2)} records")
        
        # Try to get data with raw SQL through SQLAlchemy
        result = db.session.execute('SELECT * FROM okte_data LIMIT 5').fetchall()
        logging.info(f"Raw SQL through SQLAlchemy: {result}")
        
        # Use the data that works
        data = data1 if data1 else data2 if data2 else []
        
        if not data:
            logging.warning("No data found in database")
            return render_template('graph.html', data=None)
        
        # Convert data to list of dictionaries for JSON serialization
        data_list = []
        for record in data:
            data_list.append({
                'datum': record.datum,
                'zuctovacia_perioda': record.zuctovacia_perioda,
                'aktivovana_agregovana_flexibilita_kladna': record.aktivovana_agregovana_flexibilita_kladna,
                'aktivovana_agregovana_flexibilita_zaporna': record.aktivovana_agregovana_flexibilita_zaporna,
                'zdielana_elektrina': record.zdielana_elektrina
            })
        
        return render_template('graph.html', data=data_list)
    except Exception as e:
        logging.error(f"Error in graph route: {str(e)}")
        return render_template('graph.html', data=None)

@main.route('/debug')
def debug():
    try:
        # Direct SQLite connection
        conn = sqlite3.connect('okte_data.db')
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        result = []
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            result.append({
                'table': table_name,
                'count': count,
                'columns': columns,
                'sample_data': [dict(zip(columns, row)) for row in rows]
            })
        
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/test_db')
def test_db():
    try:
        # Test database connection
        result = {
            'sqlalchemy_uri': str(db.engine.url),
            'direct_sql': {},
            'sqlalchemy_query': {}
        }
        
        # Test direct SQL
        conn = sqlite3.connect('okte_data.db')
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        result['direct_sql']['tables'] = [table[0] for table in tables]
        
        # Get okte_data count
        cursor.execute("SELECT COUNT(*) FROM okte_data")
        count = cursor.fetchone()[0]
        result['direct_sql']['okte_data_count'] = count
        
        # Get sample data
        cursor.execute("SELECT * FROM okte_data LIMIT 1")
        row = cursor.fetchone()
        if row:
            result['direct_sql']['sample_row'] = dict(zip([col[0] for col in cursor.description], row))
        
        conn.close()
        
        # Test SQLAlchemy
        with db.engine.connect() as conn:
            result['sqlalchemy_query']['connection'] = "Success"
            
            # Try to get count
            count = db.session.query(EDCData).count()
            result['sqlalchemy_query']['count'] = count
            
            # Try to get first record
            first = db.session.query(EDCData).first()
            if first:
                result['sqlalchemy_query']['first_record'] = {
                    'id': first.id,
                    'datum': first.datum,
                    'zuctovacia_perioda': first.zuctovacia_perioda
                }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 