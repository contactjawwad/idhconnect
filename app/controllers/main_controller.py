from flask import Flask, Blueprint, request, jsonify, flash, render_template, session, redirect, url_for, current_app
import tempfile
import os
import re
import logging
from datetime import datetime
from ..utils.app_logger import AppLogger

# Define a Blueprint for the main routes
main_blueprint = Blueprint('main', __name__)
logger = AppLogger('main_controller').get_logger()

class BaseController:
    def __init__(self, template_name, title):
        self.template_name = template_name
        self.title = title

    def render(self, context=None):
        if context is None:
            context = {}
        context['title'] = self.title
        return render_template(self.template_name, **context)

class MainController(BaseController):
    def __init__(self):
        super().__init__('welcome.html', 'Welcome - Inventory Data Hub')
        logger.info("In Main Controller Init Function")
        self.temp_dir = current_app.config['temp_dir']

    # Validate files for two NFMP mode
    def validate_files_two_nfmp(self, files):
        logger.info("Validating files for NFMP1 & 2")
        # Use the validation pattern for two NFMP mode
        return self._validate(files, r'^(cards|fans|flash_memory|media_adaptor|power_supply|shelf|network_element|port|port_connector)_(\d{2})(\d{2})(\d{4})_NFMP[12]\.(csv|xlsx?|xls)$', True)

    # Validate files for one NFMP mode
    def validate_files_one_nfmp(self, files):
        logger.info("Validating files for NFMP1")
        # Use the validation pattern for one NFMP mode
        return self._validate(files, r'^(cards|fans|flash_memory|media_adaptor|power_supply|shelf|network_element|port|port_connector)_(\d{2})(\d{2})(\d{4})_NFMP1\.(csv|xlsx?|xls)$', False)
        
    # General validation function
    def _validate(self, files, pattern, is_two_nfmp):
        
        valid_pattern = re.compile(pattern, re.I | re.IGNORECASE)
        temp_files = []
        valid = True
        error_message = ""

        # Define mandatory and optional files
        mandatory_files = {'cards_', 'flash_memory_', 'media_adaptor_', 'power_supply_', 'shelf_'}
        optional_files = {'fans_', 'network_element_', 'port_', 'port_connector_'}
        
        received_files = set()
        date_format = "%d%m%Y"
        
        # Validate each file against the pattern and date format
        for file in files:
            match = valid_pattern.match(file.filename)
            if not match:
                valid = False
                error_message = f"File validation failed for: {file.filename}"
                logger.error(error_message)
                break

            # Check date validity
            day, month, year = match.groups()[1:4]
            try:
                datetime.strptime(f"{day}{month}{year}", date_format)
            except ValueError:
                valid = False
                error_message = f"Invalid date in file: {file.filename}"
                logger.error(error_message)
                break

            received_files.add(match.group(1).lower() + '_')  # Convert to lowercase
            temp_file = os.path.join(self.temp_dir, file.filename)
            try:
                file.save(temp_file)
                temp_files.append(temp_file)
            except Exception as e:
                error_message = f"Failed to save file {temp_file}: {e}"
                logging.error(error_message)
                valid = False
                break

        # Check if all mandatory files are present and no invalid files are uploaded
        if not valid or not mandatory_files.issubset(received_files) or not all(f.lower().startswith(tuple(mandatory_files | optional_files)) for f in received_files):
            for temp_file_path in temp_files:
                os.remove(temp_file_path)
            logger.info("Cleanup completed for invalid files")
            if not valid:
                error_message = error_message or "Mandatory files missing."
            valid = False
        else:
            logger.info("All files have been successfully uploaded")

        return valid, temp_files, error_message

@main_blueprint.route('/', methods=['GET'])
def welcome():
    print("Serving welcome page")
    links_enabled = session.get('files_uploaded', False)
    return MainController().render({'links_enabled': links_enabled})

@main_blueprint.route('/validate', methods=['POST'])
def upload_and_validate():
    logger.info("In upload_and_validate function")
    print("\n In route upload_and_validate function")
    nfmp_mode = request.headers.get('NFMP-Mode', 'one_nfmp')
    files = request.files.getlist('inventory_files')
    main_controller = MainController()

    # Validate files based on the NFMP mode
    if nfmp_mode == 'one_nfmp':
        logger.info("You selected the one NFMP")
        valid, temp_files, error_message = main_controller.validate_files_one_nfmp(files)
    elif nfmp_mode == 'two_nfmp':
        logger.info("You selected two NFMP")
        valid, temp_files, error_message = main_controller.validate_files_two_nfmp(files)
    else:
        logger.info("Else Not working")
        error_message = "You selected the wrong  files Or Files are not in a supported format."
        session['error_message'] = error_message
        print(f"\n In else Redirecting to error page: {error_message}")
        #return redirect(url_for('main.error_page')), 400
        return jsonify({'success': False, 'message': session['error_message']}), 400

    # Handle validation result
    if not valid:
        logger.error(f"Validation failed: {error_message}")
        session['error_message'] = f"You selected the Wrong files Or Files are not in a supported format<br>{error_message}"
        print(f"\n if not valid Redirecting to error page: {session['error_message']}")
        #return redirect(url_for('main.error_page')), 400
        return jsonify({'success': False, 'message': error_message}), 400
    else:
        logger.info("All files have been successfully uploaded")
        print("\n All files have been successfully uploaded")
        session['temp_files'] = [os.path.basename(temp_file) for temp_file in temp_files]
        session['files_uploaded'] = True
        available_routes = [
            '/reports/sfp',
            '/reports/card',
            '/reports/shelf_fan',
            '/reports/power',
            '/reports/flash',
            '/reports/summary'
        ]
        return jsonify({
            'success': True,
            'message': 'All files have been successfully uploaded.',
            'temp_files': [os.path.basename(file) for file in temp_files],
            'available_routes': available_routes
        })

@main_blueprint.route('/error', methods=['GET'])
def error_page():
    #error_message = session.pop('error_message', 'An unexpected error occurred. Please make sure you upload correct files.')
    
    error_message = session.get('error_message', '"You selected the Wrong files Or Files are not in a supported format."')
    print(f"In Error Message Route: {error_message}")
    return render_template('error.html', title='Error - Invalid Files', error_message=error_message)
@main_blueprint.route('/get_links_status', methods=['GET'])
def get_links_status():
    links_enabled = session.get('files_uploaded', False)
    available_routes = [
        '/reports/sfp',
        '/reports/card',
        '/reports/shelf_fan',
        '/reports/power',
        '/reports/flash',
        '/reports/summary'
    ]
    return jsonify({'links_enabled': links_enabled, 'available_routes': available_routes})
