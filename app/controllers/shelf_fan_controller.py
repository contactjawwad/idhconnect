#jawwad@jumphost:~/InventoryDataHub/app/controllers/shelf_fan_controller.py
from .main_controller import BaseController 
from flask import Flask, Blueprint, request, jsonify, flash, render_template, session, redirect, url_for,current_app
from ..services.shelf_fan_service import ShelfFanService
import re
shelf_fan_blueprint=Blueprint('shelf_fan',__name__)

@shelf_fan_blueprint.route('/shelf_fan',methods=['GET'])
def shelf_fan_render_route():
    print("Shelf_Fan report_route called.")
    controller=ShelfFanController()
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    return  controller.shelf_fan_report(uploaded_files,temp_dir)

@shelf_fan_blueprint.route('/shelf_fan/data', methods=['GET'])
def shelf_fan_report_route():
    controller = ShelfFanController()
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    start = int(request.args.get('start', 0))
    chunk_size = int(request.args.get('length', 10000))
    print(f"Controller Requesting chunk: start={start}, length={chunk_size}")
    return controller.shelf_fan_report_data(uploaded_files, temp_dir, start, chunk_size)

class ShelfFanController(BaseController):
   def __init__(self):
      super().__init__('shelf_fan_report.html', 'Shelf & Fan Reports')
      self.service=ShelfFanService()
      print("Shelf Fan Controller Initialized")
   def shelf_fan_report(self,uploaded_files: list[str], temp_dir: str):
      filtered_files,total_rows=self.service.fetch_filtered_file_details(uploaded_files,temp_dir)
      print(f" files length{len(filtered_files)} and Total Rows Len {len(total_rows)}")
      return self.render({'filtered_files': filtered_files, 'total_rows': total_rows})
   
   def shelf_fan_report_data(self, uploaded_files: list[str], temp_dir: str, start: int, chunk_size: int):
      table_data, summary_data,  all_data_fetched = self.service.process_files(uploaded_files, temp_dir, start, chunk_size)
      print(f"Controller Class Returning chunk to JS: {len(table_data)} rows, start={start}, length={chunk_size}")
      return jsonify({'data': table_data, 'summary_data': summary_data, 'all_data_fetched': all_data_fetched})