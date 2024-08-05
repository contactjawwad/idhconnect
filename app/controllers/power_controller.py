#jawwad@jumphost:~/InventoryDataHub/app/controllers/power_controller.py
from .main_controller import BaseController 
from flask import Flask, Blueprint, request, jsonify, flash, render_template, session, redirect, url_for,current_app
from ..services.shelf_power_service import ShelfPowerService
import re
power_blueprint=Blueprint('power_module',__name__)
#This power_module used in argument is used in HTML power_module. 

@power_blueprint.route('/power',methods=['GET'])
def power_module_render_route():
    print("power_module report_route called.")
    controller=PowerController()
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    return  controller.power_module_report(uploaded_files,temp_dir)

@power_blueprint.route('/power/data', methods=['GET'])
def power_module_report_route():
    controller = PowerController()
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    start = int(request.args.get('start', 0))
    chunk_size = int(request.args.get('length', 10000))
    print(f"Controller Requesting chunk: start={start}, length={chunk_size}")
    return controller.power_module_report_data(uploaded_files, temp_dir, start, chunk_size)

class PowerController(BaseController):
   def __init__(self):
      super().__init__('power_report.html', 'Power Modules Report')
      self.service=ShelfPowerService()
      print("Power Controller Initialized")
   def power_module_report(self,uploaded_files: list[str], temp_dir: str):
      #self.service.process_chassis_model_files( uploaded_files, temp_dir, 0, 10000)        
      print("In Power Controller:/power power_module_report()")
      return self.render()
   
   def power_module_report_data(self, uploaded_files: list[str], temp_dir: str, start: int, chunk_size: int):
      print("In Power Controller:  /power/data : power_module_report_data()")
      table_data,summary_data,all_data_fetched = self.service.process_files(uploaded_files, temp_dir, start, chunk_size)
      print(f"Controller Class Returning chunk to JS: {len(table_data)} rows, start={start}, length={chunk_size}")
      #return jsonify({'data': table_data,'all_data_fetched': all_data_fetched})
      return jsonify({'data': table_data, 'summary_data': summary_data, 'all_data_fetched': all_data_fetched})