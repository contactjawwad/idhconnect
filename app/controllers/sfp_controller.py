#jawwad@jumphost:~/InventoryDataHub/app/controllers/sfp_controller.py

from flask import Blueprint,session,render_template,current_app,request,jsonify,send_file,Response
from .main_controller import BaseController
from ..services.sfp_service import SFPService  
import re
import tempfile
import pandas as pd
from io import BytesIO


sfp_blueprint=Blueprint('sfp',__name__)
#This sfp used in argument is used in HTML sfp.

@sfp_blueprint.route('/sfp',methods=['GET'])
def sfp_report_route():
    print("sfp_report_route called.")
    controller=SFPController()
    uploaded_files = session.get('temp_files', [])  # Get data from session
    temp_dir = current_app.config['temp_dir']
    return controller.sfp_report(uploaded_files,temp_dir)  # Pass the data to the controller method
    # THE ABOVE CODE IS NOT REQUIRED AS NOW IT WILL BE COVERED IN THE sfp_report_data 


@sfp_blueprint.route('/sfp/data', methods=['GET'])
def sfp_report_data():    
    controller = SFPController()
    uploaded_files = session.get('temp_files', [])
    temp_dir = current_app.config['temp_dir']
    start = int(request.args.get('start', 0))
    chunk_size = int(request.args.get('length', 10000))
    print(f"Controller Requesting chunk: start={start}, length={chunk_size}")
    return controller.sfp_report_data(uploaded_files, temp_dir, start, chunk_size)

@sfp_blueprint.route('/sfp/export', methods=['GET'])
def sfp_export_route():
    controller = SFPController()
    return controller.export_sfp_report()


class SFPController(BaseController):

    def __init__(self):
        #Pass Template Name and Title Name , which can be used in rendering
        super().__init__('sfp_report.html', 'SFP Report')
        self.service=SFPService()
        print("SFP Controller Initialized")

    def sfp_report(self,uploaded_files:list[str],temp_dir:str):
        
        #table_data, summary_data = self.service.process_files(uploaded_files, temp_dir) 
        #return self.render({'sfp_files': table_data, 'summary_data': summary_data})
        return self.render()
    
    def sfp_report_data(self, uploaded_files: list[str], temp_dir: str, start: int, chunk_size: int):
        table_data, summary_data, all_data_fetched = self.service.process_files(uploaded_files, temp_dir, start, chunk_size)
        print(f"Controller Class Returning chunk to JS: {len(table_data)} rows, start={start}, length={chunk_size}")
        
        return jsonify({'data': table_data, 'summary_data': summary_data, 'all_data_fetched': all_data_fetched})
        
    def export_sfp_report(self):
        try:
            current_app.logger.info('EXPORT START')
            uploaded_files = session.get('temp_files', [])
            temp_dir = current_app.config['temp_dir']

            # Fetch all data
            table_data, summary_data, _ = self.service.process_files(
                uploaded_files, temp_dir, start=0, chunk_size=10**9
            )
            current_app.logger.info(f'DONE PROCESSING {len(table_data)} rows')

            # Convert to DataFrames
            df_main = pd.DataFrame(table_data)
            df_summary = pd.DataFrame([{'Part Number': pn, 'QTY': info['QTY'], 'Description': info['Description']}
                                    for pn, info in summary_data.items()])

            # Write to Excel using XlsxWriter (constant_memory for streaming)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter', options={'constant_memory': True}) as writer:
                # Main sheet
                df_main.to_excel(writer, sheet_name='Main Report', index=False, header=False, startrow=1)
                workbook  = writer.book
                worksheet = writer.sheets['Main Report']
                # Header formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#000080',
                    'font_color': '#FFFFFF',
                    'align': 'center',
                    'border': 1
                })
                # Write header row manually
                main_headers = ['Site Name','Connector Type','Part Number','Vendor Serial Number','Description','Shelf Type']
                for col_num, header in enumerate(main_headers):
                    worksheet.write(0, col_num, header, header_format)
                # Auto column widths
                for i, width in enumerate([20,18,15,22,30,18]):
                    worksheet.set_column(i, i, width)

                # Summary sheet
                df_summary.to_excel(writer, sheet_name='Summary Report', index=False, header=False, startrow=1)
                worksheet2 = writer.sheets['Summary Report']
                summary_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#000080',
                    'font_color': '#FFFFFF',
                    'align': 'center',
                    'border': 1
                })
                summary_headers = ['Part Number','QTY','Description']
                for col_num, header in enumerate(summary_headers):
                    worksheet2.write(0, col_num, header, summary_format)
                for i, width in enumerate([15,8,30]):
                    worksheet2.set_column(i, i, width)

            output.seek(0)
            current_app.logger.info('EXCEL READY, SENDING')

            return send_file(
                output,
                as_attachment=True,
                download_name='SFP_Model_Report.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except Exception:
            current_app.logger.exception('Failed to export SFP report')
            return jsonify({'error': 'Export failed on server'}), 500
