# /home/jawwad/InventoryDataHub/app/services/sfp_service.py
from ..models.sfp_model import SFPModel
from ..models.chassis_model import ChassisModel
import pandas as pd
from typing import List
import logging
import gc

class SFPService:
    def __init__(self):
        self.model = SFPModel()
        self.chassis_model = ChassisModel() 
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)  
    
    #def process_files(self,uploaded_files:List[str],temp_dir:str):
    def process_files(self, uploaded_files: List[str], temp_dir: str, start: int = 0, chunk_size: int = 10000):
        
        """
        Reads SFP data in paginated chunks, enriches each row with Shelf Type from chassis data,
        and builds summary counts per Part Number.
        Returns: (table_data, summary_data, all_data_fetched)
        """
        # 1) Build a mapping of Site Name -> Shelf Type from all chassis files
        shelf_map = {}
        chassis_files = self.chassis_model.filter_files(uploaded_files)
        for ch_file in chassis_files:
            ch_path = f"{temp_dir}/{ch_file}"
            total_ch_rows = self.chassis_model.get_total_rows(ch_path)
            df_ch = self.chassis_model.read_filtered_data(
                ch_path,
                start=0,
                chunk_size=total_ch_rows
            )
            # map each site to its shelf type
            shelf_map.update(zip(df_ch['Site Name'], df_ch['Shelf Type']))

        
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
                memory_usage = data_chunk.memory_usage(deep=True).sum()
                #print(f"Estimated memory usage for one chunk: {memory_usage / 1024**2} MB")
                print(f"Read {len(data_chunk)} rows from {file_name}, starting at row {rows_to_skip}")
                # Enrich with Shelf Type
                data_chunk['Shelf Type'] = data_chunk['Site Name'].map(shelf_map)
                     # Append to output list
                table_data.extend(data_chunk.to_dict(orient='records'))
                
                
                # Update summary data
                for row in data_chunk.to_dict('records'):
                    part_number = row.get("Part Number")
                    description = row.get("Description")
                    if part_number in summary_data: #Check if the model number already exists as a key in the summary_data dictionary
                        summary_data[part_number]['QTY'] += 1 ## Increment the count for this model number by 1
                    else:
                        summary_data[part_number] = {
                           'QTY': 1,
                           'Description': description
                        }

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
        
        return table_data, summary_data, all_data_fetched 
    
    