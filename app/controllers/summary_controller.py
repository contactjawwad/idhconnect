#jawwad@jumphost:~/InventoryDataHub/app/controllers/summary_controller.py
from .main_controller import BaseController
from flask import session,url_for,Blueprint,current_app,render_template,request,jsonify
from ..services.summary_service import SummaryService
from ..services.shelf_power_service import ShelfPowerService

import re

class SummaryController(BaseController):
    def __init__(self):
        super().__init__('summary_report.html', 'Summary Reports')
        self.service=SummaryService()
        self.shelf_pw_service=ShelfPowerService()
        print("Card Controller Initialized")
    def summary_report(self):
      return self.render()
    def card_report_data(self, uploaded_files: list[str], temp_dir: str, start: int, chunk_size: int):
        summary_data, all_data_fetched = self.service.process_card_files(uploaded_files, temp_dir, start, chunk_size)
        print(f"Controller Class Returning chunk For Cards to JS:, start={start}, length={chunk_size}")
        return jsonify({'summary_data': summary_data, 'all_data_fetched': all_data_fetched})
    def shelf_fan_report_data(self, uploaded_files: list[str], temp_dir: str, start: int, chunk_size: int):
        summary_data, all_data_fetched = self.service.process_shelf_fan_files(uploaded_files, temp_dir, start, chunk_size)
        print(f"Controller Class Returning chunk For Shelf Fan to JS:, start={start}, length={chunk_size}")
        return jsonify({'summary_data': summary_data, 'all_data_fetched': all_data_fetched})
    def power_report_data(self, uploaded_files: list[str], temp_dir: str, start: int, chunk_size: int):
        print(f"Controller Requesting chunk: start={start}, length={chunk_size}")
        print(f"Uploaded files: {uploaded_files}")
        print(f"Temp dir: {temp_dir}")
        if not uploaded_files or not temp_dir:
            print("Error: Uploaded files or temp directory is missing.")
            return jsonify({'summary_data': [], 'all_data_fetched': True})

        summary_data, all_data_fetched = self.shelf_pw_service.process_power_summary(uploaded_files, temp_dir, start, chunk_size)
        print(f"Controller Class Returning chunk For Power Report Summary to JS:, start={start}, length={chunk_size}")
        return jsonify({'summary_data': summary_data, 'all_data_fetched': all_data_fetched})
    def sfp_report_data(self, uploaded_files: list[str], temp_dir: str, start: int, chunk_size: int):
        summary_data, all_data_fetched = self.service.process_sfp_files(uploaded_files, temp_dir, start, chunk_size)
        print(f"Controller Class Returning chunk For SFP to JS:, start={start}, length={chunk_size}")
        return jsonify({'summary_data': summary_data, 'all_data_fetched': all_data_fetched})
    def flash_memory_report_data(self, uploaded_files: list[str], temp_dir: str, start: int, chunk_size: int):
        summary_data, all_data_fetched = self.service.process_flash_memory_files(uploaded_files, temp_dir, start, chunk_size)
        print(f"Controller Class Returning chunk For CF Memeory to JS:, start={start}, length={chunk_size}")
        return jsonify({'summary_data': summary_data, 'all_data_fetched': all_data_fetched})
        
    
summary_blueprint = Blueprint('summary', __name__)
controller=SummaryController()

@summary_blueprint.route('/summary',methods=['GET'])
def summary_render_route():
    print("summary_render_route called.")
    return  controller.summary_report()

@summary_blueprint.route('/summary/card', methods=['GET'])
def card_report_data():
    print("Now card_report_data() called in Controller")
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    start = int(request.args.get('start', 0))
    chunk_size = int(request.args.get('length', 10000))
    print(f"Controller Requesting chunk: start={start}, length={chunk_size}")
    return controller.card_report_data(uploaded_files, temp_dir, start, chunk_size)    

@summary_blueprint.route('/summary/shelf_fan', methods=['GET'])
def shelf_fan_report_data():
    print("Now shelf_fan_report_data() called in Controller")
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    start = int(request.args.get('start', 0))
    chunk_size = int(request.args.get('length', 10000))
    print(f"Controller Requesting chunk: start={start}, length={chunk_size}")
    return controller.shelf_fan_report_data(uploaded_files, temp_dir, start, chunk_size)    

@summary_blueprint.route('/summary/power', methods=['GET'])
def power_report_data():
    print("Now power_report_data() called in Controller")
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    print(f"Session temp_files: {uploaded_files}")
    print(f"Config temp_dir: {temp_dir}")
    start = int(request.args.get('start', 0))
    chunk_size = int(request.args.get('length', 10000))
    print(f"Controller Requesting chunk: start={start}, length={chunk_size}")
    return controller.power_report_data(uploaded_files, temp_dir, start, chunk_size)    

@summary_blueprint.route('/summary/sfp', methods=['GET'])
def sfp_report_data():
    print("Now sfp_report_data() called in Controller")
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    print(f"Session temp_files: {uploaded_files}")
    print(f"Config temp_dir: {temp_dir}")
    start = int(request.args.get('start', 0))
    chunk_size = int(request.args.get('length', 10000))
    print(f"Controller Requesting chunk: start={start}, length={chunk_size}")
    return controller.sfp_report_data(uploaded_files, temp_dir, start, chunk_size)    


@summary_blueprint.route('/summary/flash_memory', methods=['GET'])
def flash_memory_report_data():
    print("Now flash_memory_report_data() called in Controller")
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    print(f"Session temp_files: {uploaded_files}")
    print(f"Config temp_dir: {temp_dir}")
    start = int(request.args.get('start', 0))
    chunk_size = int(request.args.get('length', 10000))
    print(f"Controller Requesting chunk: start={start}, length={chunk_size}")
    return controller.flash_memory_report_data(uploaded_files, temp_dir, start, chunk_size)