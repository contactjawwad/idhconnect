#jawwad@jumphost:~/InventoryDataHub/app/controllers/sfp_controller.py

from flask import Blueprint,session,render_template,current_app,request,jsonify,send_file,Response
from .main_controller import BaseController
from ..services.sfp_service import SFPService  
import re
import tempfile
import pandas as pd
from io import BytesIO

from openpyxl import Workbook
from openpyxl.writer.write_only import WriteOnlyCell
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

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
                uploaded_files,
                temp_dir,
                start=0,
                chunk_size=10**9
            )
            current_app.logger.info(f'DONE PROCESSING {len(table_data)} rows')

            # Create write-only workbook
            wb = Workbook(write_only=True)

            # Styles
            header_fill = PatternFill(fill_type='solid', fgColor='FF000080')
            data_fill   = PatternFill(fill_type='solid', fgColor='FFDCE6F1')
            header_font = Font(bold=True, color='FFFFFFFF')
            thin_border = Border(
                left=Side(style='thin'), right=Side(style='thin'),
                top=Side(style='thin'), bottom=Side(style='thin')
            )
            align_center = Alignment(horizontal='center', vertical='center')

            # --- Main Report ---
            ws_main = wb.create_sheet('Main Report')
            main_headers = ['Site Name','Connector Type','Part Number','Vendor Serial Number','Description','Shelf Type']
            # Header row
            header_row = []
            for h in main_headers:
                cell = WriteOnlyCell(ws_main, value=h)
                cell.fill      = header_fill
                cell.font      = header_font
                cell.border    = thin_border
                cell.alignment = align_center
                header_row.append(cell)
            ws_main.append(header_row)
            # Data rows
            for r in table_data:
                row = []
                for col in main_headers:
                    cell = WriteOnlyCell(ws_main, value=r.get(col, ''))
                    cell.fill      = data_fill
                    cell.border    = thin_border
                    cell.alignment = align_center
                    row.append(cell)
                ws_main.append(row)

            # --- Summary Report ---
            ws_sum = wb.create_sheet('Summary Report')
            sum_headers = ['Part Number','QTY','Description']
            header_row2 = []
            for h in sum_headers:
                cell = WriteOnlyCell(ws_sum, value=h)
                cell.fill      = header_fill
                cell.font      = header_font
                cell.border    = thin_border
                cell.alignment = align_center
                header_row2.append(cell)
            ws_sum.append(header_row2)
            for pn, info in summary_data.items():
                row = []
                vals = [pn, info['QTY'], info['Description']]
                for v in vals:
                    cell = WriteOnlyCell(ws_sum, value=v)
                    cell.fill      = data_fill
                    cell.border    = thin_border
                    cell.alignment = align_center
                    row.append(cell)
                ws_sum.append(row)

            current_app.logger.info('ABOUT TO STREAM EXCEL')
            # Stream to BytesIO
            output = BytesIO()
            wb.save(output)
            output.seek(0)
            current_app.logger.info('EXCEL READY, SENDING')

            # Send file response
            return send_file(
                output,
                as_attachment=True,
                download_name='SFP_Model_Report.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        except Exception:
            current_app.logger.exception('Failed to export SFP report')
            return jsonify({'error': 'Export failed on server'}), 500
