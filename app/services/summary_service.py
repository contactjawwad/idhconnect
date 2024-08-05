# /home/jawwad/InventoryDataHub/app/services/summary_service.py
from ..models.card_model import CardModel
from ..models.chassis_fan_model import ChassisFanModel
from ..models.sfp_model import SFPModel
from ..models.flash_memory_model import FlashMemoryModel
import pandas as pd
import gc

class SummaryService:
    def __init__(self) -> None:
        self.card_model=CardModel()
        self.chassis_fan_model=ChassisFanModel()
        self.sfp_model=SFPModel()
        self.flash_memory_model=FlashMemoryModel()
        self.cf_desc_mapping = {
            "3HE01619AA": "2GB Compact Flash",
            "3HE04707AA": "4GB Compact Flash",
            "3HE04708AA": "8GB Compact Flash",
            "3HE01052AA": "16GB Compact Flash",
            "3HE06083AA": "32GB Compact Flash",
            "3HE06735AA": "64GB Compact Flash"
        }
    def process_card_files(self, uploaded_files: list[str], temp_dir: str, start: int = 0, chunk_size: int = 10000):
        filtered_files = self.card_model.filter_files(uploaded_files)
        summary_data = {}  # To accumulate summary data
        rows_processed = 0
        all_data_fetched = True  # Indicates if all data has been fetched

        print(f"Starting process_files with start={start}, chunk_size={chunk_size}")
        print(f"Filtered files: {filtered_files}")

        for file_name in filtered_files:
            file_path = f"{temp_dir}/{file_name}"
            total_rows = self.card_model.get_total_rows(file_path)
            print(f"Processing file: {file_name} with {total_rows} total rows")

            rows_to_skip = start  # Initialize rows_to_skip for each file iT WILL START WITH 0 FOR EACH FILE

            while rows_to_skip < total_rows:
                print(f"Reading data from file {file_name} starting at row {rows_to_skip}")
                data_chunk = self.card_model.read_summary_data(file_path, chunk_size=chunk_size, start=rows_to_skip)
                #Data_chunk is basicaly a data fram return from read_Filtered_Data
                print(f"Data chunk length: {len(data_chunk)}")

                if data_chunk.empty:  #This is usually not happened in our case
                    print(f"Data chunk is empty. Breaking loop for file {file_name}")
                    break

                print(f"Read {len(data_chunk)} rows from {file_name}, starting at row {rows_to_skip}")
        
                 # Update summary data
                for row in data_chunk.to_dict('records'):
                    part_number = row.get("Part Number")
                    description = row.get("Description")
                    if part_number in summary_data:
                        summary_data[part_number]['QTY'] += 1
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
                del data_chunk
                gc.collect()
        
            print(f"Completed processing file {file_name}. Resetting rows_to_skip for next file to Zero")
            # rows_to_skip = 0  # Reset rows_to_skip for the next file tHIS IS THE CHANGE
        all_data_fetched = True
        print(f"Completed processing all files. Total rows processed: {rows_processed}")
        return summary_data, all_data_fetched
    

    def process_shelf_fan_files(self, uploaded_files: list[str], temp_dir: str, start: int = 0, chunk_size: int = 10000):
        filtered_files = self.chassis_fan_model.filter_files(uploaded_files)
        summary_data = {}  # To accumulate summary data
        rows_processed = 0
        all_data_fetched = True  # Indicates if all data has been fetched

        print(f"Starting process_files with start={start}, chunk_size={chunk_size}")
        print(f"Filtered files: {filtered_files}")

        for file_name in filtered_files:
            file_path = f"{temp_dir}/{file_name}"
            total_rows = self.chassis_fan_model.get_total_rows(file_path)
            print(f"Processing file: {file_name} with {total_rows} total rows")

            rows_to_skip = start  # Initialize rows_to_skip for each file iT WILL START WITH 0 FOR EACH FILE

            while rows_to_skip < total_rows:
                print(f"Reading data from file {file_name} starting at row {rows_to_skip}")
                data_chunk = self.chassis_fan_model.read_summary_data(file_path, chunk_size=chunk_size, start=rows_to_skip)
                # Data_chunk is basically a dataframe returned from read_Filtered_Data
                print(f"Data chunk length: {len(data_chunk)}")
                if data_chunk.empty:  # This usually does not happen in our case
                    print(f"Data chunk is empty. Breaking loop for file {file_name}")
                    break

                print(f"Read {len(data_chunk)} rows from {file_name}, starting at row {rows_to_skip}")

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
                                'Description': shelf_type  # Assuming shelf_type is the description for shelf parts
                            }
                        summary_data[part_number]['QTY'] += 1

                    # For fan parts (excluding 'FanLess' and 'Internal Fan')
                    if fan_pn and fan_pn not in ['FanLess', 'Internal Fan']:
                        if fan_pn not in summary_data:
                            summary_data[fan_pn] = {
                                'QTY': 0,
                                'Description': self.chassis_fan_model.get_part_description(fan_pn)
                            }
                        summary_data[fan_pn]['QTY'] += fan_qty

                rows_to_skip += chunk_size  # Increase by chunk_size, regardless of the actual number of rows read
                rows_processed += len(data_chunk)
                print(f"Updated rows_to_skip to {rows_to_skip}, total rows_processed: {rows_processed}")

                if len(data_chunk) < chunk_size:
                    print(f"Data chunk size {len(data_chunk)} is less than chunk_size {chunk_size}.")
                    all_data_fetched = False
                del data_chunk
                gc.collect()
        

            print(f"Completed processing file {file_name}. Resetting rows_to_skip for next file to Zero")
        all_data_fetched = True
        print(f"Completed processing all files. Total rows processed: {rows_processed}")
        return summary_data, all_data_fetched
    


    def process_sfp_files(self, uploaded_files: list[str], temp_dir: str, start: int = 0, chunk_size: int = 10000):
        filtered_files = self.sfp_model.filter_files(uploaded_files)
        summary_data = {}  # To accumulate summary data
        rows_processed = 0
        all_data_fetched = True  # Indicates if all data has been fetched

        print(f"Starting process_files with start={start}, chunk_size={chunk_size}")
        print(f"Filtered files: {filtered_files}")

        for file_name in filtered_files:
            file_path = f"{temp_dir}/{file_name}"
            total_rows = self.sfp_model.get_total_rows(file_path)
            print(f"Processing file: {file_name} with {total_rows} total rows")

            rows_to_skip = start  # Initialize rows_to_skip for each file iT WILL START WITH 0 FOR EACH FILE

            while rows_to_skip < total_rows:
                print(f"Reading data from file {file_name} starting at row {rows_to_skip}")
                data_chunk = self.sfp_model.read_summary_data(file_path, chunk_size=chunk_size, start=rows_to_skip)
                #Data_chunk is basicaly a data fram return from read_Filtered_Data
                print(f"Data chunk length: {len(data_chunk)}")

                if data_chunk.empty:  #This is usually not happened in our case
                    print(f"Data chunk is empty. Breaking loop for file {file_name}")
                    break

                print(f"Read {len(data_chunk)} rows from {file_name}, starting at row {rows_to_skip}")
        
                 # Update summary data
                for row in data_chunk.to_dict('records'):
                    part_number = row.get("Part Number")
                    description = row.get("Description")
                    if part_number in summary_data:
                        summary_data[part_number]['QTY'] += 1
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
                del data_chunk
                gc.collect()
        
            print(f"Completed processing file {file_name}. Resetting rows_to_skip for next file to Zero")
            # rows_to_skip = 0  # Reset rows_to_skip for the next file tHIS IS THE CHANGE
        all_data_fetched = True
        print(f"Completed processing all files. Total rows processed: {rows_processed}")
        return summary_data, all_data_fetched
    
    def process_flash_memory_files(self, uploaded_files: list[str], temp_dir: str, start: int = 0, chunk_size: int = 10000):
        filtered_files = self.flash_memory_model.filter_files(uploaded_files)
        summary_data = {}  # To accumulate summary data
        rows_processed = 0
        all_data_fetched = True  # Indicates if all data has been fetched

        print(f"Starting process_files with start={start}, chunk_size={chunk_size}")
        print(f"Filtered files: {filtered_files}")

        for file_name in filtered_files:
            file_path = f"{temp_dir}/{file_name}"
            total_rows = self.flash_memory_model.get_total_rows(file_path)
            print(f"Processing file: {file_name} with {total_rows} total rows")

            rows_to_skip = start  # Initialize rows_to_skip for each file iT WILL START WITH 0 FOR EACH FILE

            while rows_to_skip < total_rows:
                print(f"Reading data from file {file_name} starting at row {rows_to_skip}")
                data_chunk = self.flash_memory_model.read_summary_data(file_path, chunk_size=chunk_size, start=rows_to_skip)
                #Data_chunk is basicaly a data fram return from read_Filtered_Data
                print(f"Data chunk length: {len(data_chunk)}")

                if data_chunk.empty:  #This is usually not happened in our case
                    print(f"Data chunk is empty. Breaking loop for file {file_name}")
                    break

                print(f"Read {len(data_chunk)} rows from {file_name}, starting at row {rows_to_skip}")
        
                 # Update summary data
                for row in data_chunk.to_dict('records'):
                    part_number = row.get("Part Number")
                    description = row.get("Description")
                    if part_number in summary_data:
                        summary_data[part_number]['QTY'] += 1
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
                del data_chunk
                gc.collect()
        
            print(f"Completed processing file {file_name}. Resetting rows_to_skip for next file to Zero")
            # rows_to_skip = 0  # Reset rows_to_skip for the next file tHIS IS THE CHANGE
        all_data_fetched = True
        print(f"Completed processing all files. Total rows processed: {rows_processed}")
        return summary_data, all_data_fetched