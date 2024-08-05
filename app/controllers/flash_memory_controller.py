#jawwad@jumphost:~/InventoryDataHub/app/controllers/flash_memory_controller.py
from .main_controller import BaseController 
from flask import Flask, Blueprint, request, jsonify, flash, render_template, session, redirect, url_for,current_app
from ..services.flash_memory_service import FlashMemoryService
import re

flash_memory_blueprint=Blueprint('flash_memory',__name__)
#This flash_memory used in argument is used in HTML flash_memory. 

@flash_memory_blueprint.route('/flash',methods=['GET'])
def flash_memory_render_route():
    print("Flash Memory report_route called.")
    controller=FlashMemoryController()
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    return  controller.flash_memory_report(uploaded_files,temp_dir)

@flash_memory_blueprint.route('/flash/data', methods=['GET'])
def flash_memory_report_route():
    controller = FlashMemoryController()
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    start = int(request.args.get('start', 0))
    chunk_size = int(request.args.get('length', 10000))
    print(f"Flash Memory Controller Requesting chunk: start={start}, length={chunk_size}")
    return controller.flash_memory_report_data(uploaded_files, temp_dir, start, chunk_size)

class FlashMemoryController(BaseController):
   def __init__(self):
      super().__init__('flash_memory_report.html', 'Compact Flash Memory Reports')
      self.service=FlashMemoryService()
      print("Flash Memory Controller Initialized")
   def flash_memory_report(self,uploaded_files: list[str], temp_dir: str):
      #self.service.process_chassis_model_files( uploaded_files, temp_dir, 0, 10000)        
      print("In Flash Controller:/flash flash_memory_report()")
      return self.render()
   
   def flash_memory_report_data(self, uploaded_files: list[str], temp_dir: str, start: int, chunk_size: int):
      print("In Flash Memory Controller:  /flash/data :flash_report_data()")
      table_data,summary_data,all_data_fetched = self.service.process_files(uploaded_files, temp_dir, start, chunk_size)
      print(f"Flash Memory Controller Class Returning chunk to JS: {len(table_data)} rows, start={start}, length={chunk_size}")
      return jsonify({'data': table_data, 'summary_data': summary_data, 'all_data_fetched': all_data_fetched})
      