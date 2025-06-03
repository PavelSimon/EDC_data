from flask import Blueprint, render_template, request, jsonify, flash
from app.models import EDCData
from app import db
from app.scraper import scrape_edc_data
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd
import logging

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
            EDCData.date >= start_date,
            EDCData.date <= end_date
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
        # Get data from database
        data = EDCData.query.all()
        
        if not data:
            return render_template('graph.html', 
                                plot=None, 
                                message="No data available. Please scrape some data first.")
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'date': d.date,
            'time_period': d.time_period,
            'positive_flexibility': d.positive_flexibility,
            'negative_flexibility': d.negative_flexibility,
            'shared_electricity': d.shared_electricity
        } for d in data])
        
        # Create graph
        fig = px.line(df, 
                     x='time_period', 
                     y=['positive_flexibility', 'negative_flexibility', 'shared_electricity'],
                     title='EDC Data Visualization',
                     labels={
                         'time_period': 'Time Period',
                         'value': 'Value (MWh)',
                         'variable': 'Metric'
                     })
        
        return render_template('graph.html', plot=fig.to_html(), message=None)
    except Exception as e:
        logging.error(f"Error creating graph: {str(e)}")
        return render_template('graph.html', 
                             plot=None, 
                             message=f"Error creating graph: {str(e)}") 