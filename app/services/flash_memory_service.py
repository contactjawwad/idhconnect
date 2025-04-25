# /home/jawwad/InventoryDataHub/app/services/flash_memory_service.py
from ..models.flash_memory_model import FlashMemoryModel
from ..models.chassis_model import ChassisModel
import pandas as pd
import gc
import numpy as np
class FlashMemoryService:
    def __init__(self):
        self.flash_memory_model = FlashMemoryModel()
        self.chassis_model = ChassisModel()
        self.flash_data = pd.DataFrame()  # To store the flash memory data
        self.chassis_data = pd.DataFrame()  # To store the chassis da
        self.data_processed = False  # Flag to ensure data is processed only once
        # Initialize a dictionary to keep track of quantities for  Part Numbers
        # Part description mapping
         # Part description mapping of the CF Part Numbers
        self.cf_desc_mapping = {
            "3HE01619AA": "2GB Compact Flash",
            "3HE04707AA": "4GB Compact Flash",
            "3HE04708AA": "8GB Compact Flash",
            "3HE01052AA": "16GB Compact Flash",
            "3HE06083AA": "32GB Compact Flash",
            "3HE06735AA": "64GB Compact Flash"
        }

        

    def fetch_filtered_file_details(self, uploaded_files: list[str],temp_dir: str):
        filtered_files=self.flash_memory_model.filter_files(uploaded_files)
        total_rows=[]
        files_with_path=[]
        
        for file_name in filtered_files:
            file_path=f"{temp_dir}/{file_name}"
            print(f"In Fecth Service Class Filter File Pasth {file_path}")
            files_with_path.append(file_path)
            # Get the total number of rows in the file and add to the list
            print(f"In Fecth Service Class Filter File Pasth {self.model.get_total_rows(file_path)}")
            total_rows.append(self.flash_memory_model.get_total_rows(file_path))
        return files_with_path,total_rows
    
    def process_flash_memory_files(self, uploaded_files: list[str], temp_dir: str, start: int = 0, chunk_size: int = 10000):
        filtered_files = self.flash_memory_model.filter_files(uploaded_files)
        self.flash_data = pd.DataFrame()  # Reset the dataframe
        
        for file_name in filtered_files:
            file_path = f"{temp_dir}/{file_name}"
            total_rows = self.flash_memory_model.get_total_rows(file_path)
            rows_to_skip = start
            
            while rows_to_skip < total_rows:
                data_chunk = self.flash_memory_model.read_filtered_data(file_path, chunk_size=chunk_size, start=rows_to_skip)
                if data_chunk.empty:
                    break
                self.flash_data = pd.concat([self.flash_data, data_chunk], ignore_index=True)
                rows_to_skip += chunk_size
                 # Force garbage collection after processing each chunk
                del data_chunk
                gc.collect()
        
        return True

    def process_chassis_model_files(self, uploaded_files: list[str], temp_dir: str, start: int = 0, chunk_size: int = 10000):
        filtered_files = self.chassis_model.filter_files(uploaded_files)
        self.chassis_data = pd.DataFrame()  # Reset the dataframe
        
        for file_name in filtered_files:
            file_path = f"{temp_dir}/{file_name}"
            total_rows = self.chassis_model.get_total_rows(file_path)
            rows_to_skip = start
            
            while rows_to_skip < total_rows:
                data_chunk = self.chassis_model.read_filtered_data_without_part_number_first_site_name(file_path, chunk_size=chunk_size, start=rows_to_skip)
                                              
                if data_chunk.empty:
                    break
                self.chassis_data = pd.concat([self.chassis_data, data_chunk], ignore_index=True)
                rows_to_skip += chunk_size
                 # Force garbage collection after processing each chunk
                del data_chunk
                gc.collect()
   
        return True

    def merge_and_transform_data(self):
        if self.flash_data.empty or self.chassis_data.empty:
            print("No data to process")
            return pd.DataFrame()

        merged_data = pd.merge(self.flash_data, self.chassis_data, on='Site Name', how='left')
      # Clean NaN and ensure it's JSON-safe
        merged_data.replace({np.nan: None}, inplace=True)
        #merged_data.drop(columns=['Site Name'], inplace=True)
        return merged_data[['Site Name','Slot', 'CF No', 'Capacity (GB)', 'CF Part Number', 'Shelf Type']]
    
    def generate_summary_data(self, merged_data):
        # Filter out rows where CF Part Number is None
        filtered_data = merged_data[merged_data['CF Part Number'].notna()]

        # Count occurrences of each part number
        part_number_counts = filtered_data['CF Part Number'].value_counts().to_dict()

        # Create the summary data
        summary_data = []
        for part_number, count in part_number_counts.items():
            if part_number in self.cf_desc_mapping:
                summary_data.append({
                    "CF Part Number": part_number,
                    "QTY": count,
                    "Description": self.cf_desc_mapping[part_number]
                })

        return summary_data

    def process_files(self, uploaded_files: list[str], temp_dir: str, start: int = 0, chunk_size: int = 10000):
        if self.data_processed:
            return []

        self.process_flash_memory_files(uploaded_files, temp_dir, start, chunk_size)
        self.process_chassis_model_files(uploaded_files, temp_dir, start, chunk_size)
        
        self.data_processed = True  # Mark data as processed

        table_data = self.merge_and_transform_data()
        summary_data = self.generate_summary_data(table_data)
        num_rows_table_data = len(table_data)
        print(f"Number of rows in table_data (list of dictionaries): {num_rows_table_data}")

        return table_data.to_dict(orient='records'),summary_data, self.data_processed
    