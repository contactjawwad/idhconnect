# /home/jawwad/InventoryDataHub/app/models/power_model.py
import re
import pandas as pd
class PowerModel:
    def __init__(self):
        #This regex pattern can be configured here to keep the model focused on data validation and parsing
        self.pattern=re.compile(r'^(power_supply_\d+_NFMP[12])\.(csv|xlsx?|xls)$')
        
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
            'Assigned Type': 'str',
            
        }
        usecols = ['Site Name', 'Assigned Type']
        skiprows = range(1, start + 1)

        if file_path.endswith(('.xlsx', '.xls')):
            data = pd.read_excel(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size)
        else:
            data = pd.read_csv(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size, low_memory=False)
        
        print(f"In Power Model Class read method, Read Data Length: {len(data)}, rows from file_path: {file_path}")
         # Rename column 'Serial Number (Manufacturer Details)' to 'Serial Number'
        
           # Replace None with 'Not Assigned'
        data['Assigned Type'] = data['Assigned Type'].fillna('Not Assigned')
      
        # Filter out rows with 'N/A', empty strings, and 'Default' values in 'Assigned Type' column
        data = data[data['Assigned Type'] != 'N/A']
        data = data[data['Assigned Type'].str.strip() != '']
        data = data[data['Assigned Type'] != 'Default']
        
        
        # Keep only the necessary columns
        filtered_data = data[['Site Name','Assigned Type']]
          # Group by 'Site Name' and take the first two rows per group
        filtered_data = filtered_data.groupby('Site Name').head(2).reset_index(drop=True)


        print(f"Returning from Power Model  to Service Class the Processed data length: {len(filtered_data)}\n")
        return filtered_data.where(pd.notnull(filtered_data), None)
   
    