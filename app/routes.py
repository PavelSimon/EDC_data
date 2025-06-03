from flask import Blueprint, render_template, request, jsonify, flash
from app.models import EDCData
from app import db
from app.scraper import scrape_edc_data
from datetime import datetime
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
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        
        # Validate date range
        if end_date < start_date:
            return jsonify({'message': 'End date must be after start date'}), 400
        
        # Check if data already exists for this date range
        existing_data = EDCData.query.filter(
            EDCData.date >= start_date,
            EDCData.date <= end_date
        ).first()
        
        if existing_data:
            return jsonify({'message': 'Data for this date range already exists in the database'}), 409
        
        # Scrape data
        data = scrape_edc_data(start_date, end_date)
        
        if not data:
            return jsonify({
                'message': 'No data found for the selected date range. Please check the date range and try again.'
            }), 404
        
        # Save to database
        for item in data:
            edc_data = EDCData(**item)
            db.session.add(edc_data)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully scraped and stored {len(data)} records'
        })
    except ValueError as e:
        return jsonify({'message': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error during scraping: {str(e)}")
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