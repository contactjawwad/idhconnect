from ..models.chassis_fan_model import ChassisFanModel
import pandas as pd
import gc
class ShelfFanService:
    def __init__(self):
        self.model=ChassisFanModel()
        # Initialize a dictionary to keep track of quantities for Fan Part Numbers
        # Part description mapping
        self.part_description_mapping = {
            '3HE08152AA': 'FAN - 7210 SAS-R6 FAN TRAY',
            '3HE12375AB': 'FAN - 7750 SR-2s FAN MODULE',
            '3HE05106AA': 'FAN - 7750 SR-12 ENHANCED FAN TRAY',
            '3HE05107AA': 'FAN - 7450 ESS-12 ENHANCED FAN TRAY',
            '3HE05181AA': 'FAN - 7450 ESS-7 ENHANCED FAN TRAY',
        }


    def fetch_filtered_file_details(self, uploaded_files: list[str],temp_dir: str):
        filtered_files=self.model.filter_files(uploaded_files)
        total_rows=[]
        files_with_path=[]
        
        for file_name in filtered_files:
            file_path=f"{temp_dir}/{file_name}"
            print(f"In Fecth Service Class Filter File Pasth {file_path}")
            files_with_path.append(file_path)
            # Get the total number of rows in the file and add to the list
            print(f"In Fecth Service Class Filter File Pasth {self.model.get_total_rows(file_path)}")
            total_rows.append(self.model.get_total_rows(file_path))
        return files_with_path,total_rows
    def process_files(self, uploaded_files: list[str], temp_dir: str, start: int = 0, chunk_size: int = 10000):
        filtered_files = self.model.filter_files(uploaded_files)
        table_data = []
        summary_data = {}  # To accumulate summary data
        rows_processed = 0
        all_data_fetched = True  # Indicates if all data has been fetched

     
        print(f"Starting process_files with start={start}, chunk_size={chunk_size}")
        print(f"Filtered files: {filtered_files}")

        for file_name in filtered_files:
            file_path = f"{temp_dir}/{file_name}"
            total_rows = self.model.get_total_rows(file_path)
            print(f"Processing file: {file_name} with {total_rows} total rows")

            rows_to_skip = start  # Initialize rows_to_skip for each file iT WILL START WITH 0 FOR EACH FILE

            while rows_to_skip < total_rows:
                print(f"Reading data from file {file_name} starting at row {rows_to_skip}")
                data_chunk = self.model.read_filtered_data(file_path, chunk_size=chunk_size, start=rows_to_skip)
                #Data_chunk is basicaly a data fram return from read_Filtered_Data
                print(f"Data chunk length: {len(data_chunk)}")
                if data_chunk.empty:  #This is usually not happened in our case
                    print(f"Data chunk is empty. Breaking loop for file {file_name}")
                    break

                print(f"Read {len(data_chunk)} rows from {file_name}, starting at row {rows_to_skip}")
                table_data.extend(data_chunk.to_dict('records'))
                
                 # Update summary data
                for row in data_chunk.to_dict('records'):
                    part_number = row.get("Part Number")
                    shelf_type = row.get("Shelf Type")
                    fan_pn = row.get("Fan P/N")
                    fan_qty = row.get("Fan QTY")

                    # For shelf parts
                    if part_number:
                        if part_number not in summary_data:
                            summary_data[part_number] = {
                                'QTY': 0,
                                'description': shelf_type  # Assuming shelf_type is the description for shelf parts
                            }
                        summary_data[part_number]['QTY'] += 1

                    # For fan parts (excluding 'FanLess' and 'Internal Fan')
                    if fan_pn and fan_pn not in ['FanLess', 'Internal Fan']:
                        if fan_pn not in summary_data:
                            summary_data[fan_pn] = {
                                'QTY': 0,
                                'description': self.model.get_part_description(fan_pn)
                            }
                        summary_data[fan_pn]['QTY'] += fan_qty
                #previous_rows_to_skip = rows_to_skip
                rows_to_skip += chunk_size  # Increase by chunk_size, regardless of the actual number of rows read
                rows_processed += len(data_chunk)
                print(f"Updated rows_to_skip to {rows_to_skip}, total rows_processed: {rows_processed}")

                if len(data_chunk) < chunk_size:
                     print(f"Data chunk size {len(data_chunk)} is less <  than chunk_size {chunk_size}.")
                     all_data_fetched = False
                     #break ## tHIS IS THE CHANGE If you break it it will come out of loop

                 # Force garbage collection after processing each chunk
                del data_chunk
                gc.collect()
                
            print(f"Completed processing file {file_name}. Resetting rows_to_skip for next file to Zero")
            # rows_to_skip = 0  # Reset rows_to_skip for the next file tHIS IS THE CHANGE
        all_data_fetched = True
        print(f"Completed processing all files. Total rows processed: {rows_processed}")
        return table_data,summary_data, all_data_fetched