# /home/jawwad/InventoryDataHub/app/models/chassis_model.py
import re
import pandas as pd
class ChassisModel:
    def __init__(self):
        #This regex pattern can be configured here to keep the model focused on data validation and parsing
        self.pattern=re.compile(r'^(shelf_\d+_NFMP[12])\.(csv|xlsx?|xls)$')
        self.shelf_type_mapping = {
            '3HE08151AA':'CHAS - 7210 SAS-R6 CHASSIS SPARE',
            '3HE14798AA':'SYS - 7210 SAS-Dxp 2SFP+ 4F 6T ETR AC ETR',
            '3HE09426AA':'SYS - SYS - 7210 SAS-K 2F2T1C ETR',
            '3HE11597AA':'SYS - 7210 SAS-Sx 64SFP+ 4QSFP28',
            '3HE12340AA':'CHAS - 7750 SR-2s CHASSIS LVDC',
            '3HE14782AA':'SYS - 7250 IXR-e 24SFP+ 8SFP28 2QSFP28',
            '3HE10768AA':'CHAS - 7750 SR-12-B CHASSIS SPARE RoHS6',
            '3HE02036AA':'CHAS - 7450 ESS-12 CHASSIS - FLT',
            '3HE00245AA':'CHAS - 7450 ESS-7 AC/DC CHASSIS SPARE',
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
            'Part Number': 'str',
            'Shelf Type': 'str',
        }
        usecols = ['Site Name', 'Part Number', 'Shelf Type']
        skiprows = range(1, start + 1)

        if file_path.endswith(('.xlsx', '.xls')):
            data = pd.read_excel(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size)
        else:
            data = pd.read_csv(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size, low_memory=False)
        
        print(f"\n In \"ChassisModel\" Class read method, Read Data Length: {len(data)}, rows from file_path: {file_path}")
         # Rename column 'Serial Number (Manufacturer Details)' to 'Serial Number'
      
         # Filter out rows with empty or 'N/A' values in Part Number column
        data = data[data['Part Number'].notna()]  # Remove rows with NaN values
        data = data[data['Part Number'] != 'N/A']  # Remove rows with 'N/A' values
        data = data[data['Part Number'].str.strip() != '']  # Remove rows with empty strings
        data['Part Number'] = data['Part Number'].str[:10]
        
        # Map Shelf Type and fill missing values
        data['Shelf Type'] = data['Part Number'].map(self.shelf_type_mapping).fillna(data['Shelf Type'])

        # Keep only the necessary columns
        filtered_data = data[['Site Name', 'Part Number','Shelf Type']]

        print(f"\n In Chassis Model Returning now to Service Class the Processed data length: {len(filtered_data)}")
        return filtered_data.where(pd.notnull(filtered_data), None)
   
    def read_filtered_data_without_part_number_first_site_name(self, file_path: str, chunk_size: int = 10000, start: int = 0) -> pd.DataFrame:
        dtype = {
            'Site Name': 'str',
            'Part Number': 'str',
            'Shelf Type': 'str',
        }
        usecols = ['Site Name', 'Part Number', 'Shelf Type']
        skiprows = range(1, start + 1)

        if file_path.endswith(('.xlsx', '.xls')):
            data = pd.read_excel(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size)
        else:
            data = pd.read_csv(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size, low_memory=False)
        
        print(f"\nIn \"ChassisModel\" Class read method, Read Data Length: {len(data)}, rows from file_path: {file_path}")
        
        data = data[data['Part Number'].notna()]  # Remove rows with NaN values
        data = data[data['Part Number'] != 'N/A']  # Remove rows with 'N/A' values
        data = data[data['Part Number'].str.strip() != '']  # Remove rows with empty strings
        data['Part Number'] = data['Part Number'].str[:10]
        
        data['Shelf Type'] = data['Part Number'].map(self.shelf_type_mapping).fillna(data['Shelf Type'])
        
        # Keep only the necessary columns
        filtered_data = data[['Site Name', 'Shelf Type']].drop_duplicates(subset=['Site Name'], keep='first')

        print(f"\nIn Chassis Model Returning now to Service Class the Processed data length: {len(filtered_data)}")
        return filtered_data.where(pd.notnull(filtered_data), None)