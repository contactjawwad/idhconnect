#jawwad@jumphost:~/InventoryDataHub/app/controllers/card_controller.py
from .main_controller import BaseController
from flask import session,url_for,Blueprint,current_app,render_template,request,jsonify
from ..services.card_service import CardService
import re


card_blueprint = Blueprint('card', __name__)
#This card used in argument is used in HTML card. 
@card_blueprint.route('/card',methods=['GET'])
def card_render_route():
    print("sfp_report_route called.")
    controller=CardController()
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    return  controller.card_report(uploaded_files,temp_dir)

@card_blueprint.route('/card/data', methods=['GET'])
def card_report_data():
    
    controller = CardController()
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    start = int(request.args.get('start', 0))
    chunk_size = int(request.args.get('length', 10000))
    print(f"Controller Requesting chunk: start={start}, length={chunk_size}")
    return controller.card_report_data(uploaded_files, temp_dir, start, chunk_size)


class CardController(BaseController):
   def __init__(self):
      super().__init__('card_report.html', 'Card Report')
      
      self.service=CardService()
      print("Card Controller Initialized")
   
   def card_report(self,uploaded_files: list[str], temp_dir: str):
      #filtered_files,total_rows=self.service.fetch_filtered_file_details(uploaded_files,temp_dir)
      #print(f" files length{len(filtered_files)} and Total Rows Len {len(total_rows)}")
      #return self.render({'filtered_files': filtered_files, 'total_rows': total_rows})
      return self.render()
   
   def card_report_data(self, uploaded_files: list[str], temp_dir: str, start: int, chunk_size: int):
      
      table_data, summary_data, all_data_fetched = self.service.process_files(uploaded_files, temp_dir, start, chunk_size)
      print(f"Controller Class Returning chunk to JS: {len(table_data)} rows, start={start}, length={chunk_size}")
      return jsonify({'data': table_data, 'summary_data': summary_data, 'all_data_fetched': all_data_fetched})
  