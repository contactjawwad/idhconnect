# /home/jawwad/InventoryDataHub/app/models/flash_memory_model.py
import re
import pandas as pd

class FlashMemoryModel:
    def __init__(self):
        #This regex pattern can be configured here to keep the model focused on data validation and parsing
        self.pattern=re.compile(r'^(flash_memory_\d+_NFMP[12])\.(csv|xlsx?|xls)$')
        self.cf_desc_mapping = {
            "3HE01619AA": "2GB Compact Flash",
            "3HE04707AA": "4GB Compact Flash",
            "3HE04708AA": "8GB Compact Flash",
            "3HE01052AA": "16GB Compact Flash",
            "3HE06083AA": "32GB Compact Flash",
            "3HE06735AA": "64GB Compact Flash"
        }

        
    def filter_files(self,uploaded_files: list[str]) -> list[str]:
        filtered_files=[]
        for file_name in uploaded_files:
            if (self.pattern.match(file_name)):
                filtered_files.append(file_name)
        return filtered_files
    def get_total_rows(self, file_path: str) -> int:
        if file_path.endswith(('.xlsx', '.xls')):
            total_rows=pd.read_excel(file_path,usecols=[2]).shape[0]
        else:
            total_rows=pd.read_csv(file_path,usecols=[2]).shape[0]
        return total_rows
    def read_filtered_data(self, file_path: str, chunk_size: int = 10000, start: int = 0) -> pd.DataFrame:
        dtype = {
            'Site Name': 'str',
            'Slot': 'str',
            'Flash ID': 'int',
            'Capacity (KB)' : 'int'           
        }
        usecols = ['Site Name', 'Slot','Flash ID','Capacity (KB)']
        skiprows = range(1, start + 1)

        if file_path.endswith(('.xlsx', '.xls')):
            data = pd.read_excel(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size)
        else:
            data = pd.read_csv(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size, low_memory=False)
        
        print(f"In Flash Memory Model Class read method, Read Data Length: {len(data)}, rows from file_path: {file_path}")
        
          # Strip any extra spaces in column names
        data.columns = data.columns.str.strip()
        # Filter out rows with 'N/A', empty strings, and 'Default' values in 'Assigned Type' column
        data = data[data['Capacity (KB)'] != 'N/A']
        #data = data[data['Capacity (KB)'].str.strip() != '']
        data = data[data['Capacity (KB)'] != 0]

        # Rename column 'Serial Number (Manufacturer Details)' to 'Serial Number'
        data.rename(columns={'Flash ID': 'CF No'}, inplace=True)    
         # Map Capacity (KB) to Capacity (GB) and CF Part Number
        data['Capacity (GB)'] = data['Capacity (KB)'].apply(self.map_capacity)
        data['CF Part Number'] = data['Capacity (KB)'].apply(self.map_part_number)

        # Drop the 'Capacity (KB)' column
        data.drop(columns=['Capacity (KB)'], inplace=True)

        # Transform the 'Slot' column
        data['Slot'] = data['Slot'].apply(self.transform_slot)


        # Keep only the necessary columns
        filtered_data = data[['Site Name', 'Slot', 'CF No', 'Capacity (GB)', 'CF Part Number']]

        
        print(f"Returning from Flash Memory Model  to Service Class the Processed data length: {len(filtered_data)}\n")
        return filtered_data.where(pd.notnull(filtered_data), None)
   
    @staticmethod
    def map_capacity(value):
        if 1800000 <= value <= 2200000:
            return '2GB'
        elif 3800000 <= value <= 4100000:
            return '4GB'
        elif 5300000 <= value <= 8100000:
            return '8GB'
        elif 15000000 <= value <= 16100000:
            return '16GB'
        elif 29000000 <= value <= 32100000:
            return '32GB'
        else:
            return None

    @staticmethod
    def map_part_number(value):
        if 1800000 <= value <= 2200000:
            return '3HE01619AA'
        elif 3800000 <= value <= 4100000:
            return '3HE04707AA'
        elif 5300000 <= value <= 8100000:
            return '3HE04708AA'
        elif 15000000 <= value <= 16100000:
            return '3HE01052AA'
        elif 29000000 <= value <= 32100000:
            return '3HE06083AA'
        elif 58000000 <= value <= 65000000:
            return '3HE06735AA'
        else:
            return None
    
    @staticmethod
    def transform_slot(slot):
        if slot == 'Card Slot - A':
            return 'Card - A'
        elif slot == 'Card Slot - B':
            return 'Card - B'
        else:
            return slot
    
    def get_description(self, part_number):
        return self.cf_desc_mapping.get(part_number, "Unknown Description")
    def read_summary_data(self, file_path: str, chunk_size: int = 10000, start: int = 0) -> pd.DataFrame:
        dtype = {
            
            'Capacity (KB)' : 'int'           
        }
        usecols = ['Capacity (KB)']
        skiprows = range(1, start + 1)

        if file_path.endswith(('.xlsx', '.xls')):
            data = pd.read_excel(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size)
        else:
            data = pd.read_csv(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size, low_memory=False)
        
        print(f"In Flash Memory Model Class read method, Read Data Length: {len(data)}, rows from file_path: {file_path}")
        
          # Strip any extra spaces in column names
        data.columns = data.columns.str.strip()
        # Filter out rows with 'N/A', empty strings, and 'Default' values in 'Assigned Type' column
        data = data[data['Capacity (KB)'] != 'N/A']
        #data = data[data['Capacity (KB)'].str.strip() != '']
        data = data[data['Capacity (KB)'] != 0]

        data['Part Number'] = data['Capacity (KB)'].apply(self.map_part_number)
        data['Description'] = data['Part Number'].apply(self.get_description)

        # Drop the 'Capacity (KB)' column
        data.drop(columns=['Capacity (KB)'], inplace=True)


       # Keep only the necessary columns
        filtered_data = data[['Part Number', 'Description']]

        
        print(f"Returning from Flash Memory Model  to Service Class the Processed data length: {len(filtered_data)}\n")
        return filtered_data.where(pd.notnull(filtered_data), None)