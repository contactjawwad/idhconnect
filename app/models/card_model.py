# /home/jawwad/InventoryDataHub/app/models/card_model.py
import re
import pandas as pd
class CardModel:
    def __init__(self):
        #This regex pattern can be configured here to keep the model focused on data validation and parsing
        self.pattern=re.compile(r'^(cards_\d+_NFMP[12])\.(csv|xlsx?|xls)$')
        self.card_type_mapping = {
            '3HE03618AA': 'SF/CPM - 7450 ESS SFM3-12',
            '3HE05950AA': 'SFM - 7450 ESS SFM4-12',
            '3HE06428AA': 'IMM - 7X50 48-PT GE SFP - L3HQ',
            '3HE07305CA': 'IMM - 7x50 20-PT 10GE SFP+ - L2HQ',
            '3HE14034AA': 'CPM - 7750 SR-2s CPM-2s',
            '3HE12379AA': 'XCM - 7750 SR-s XCM-2s',
            '3HE12392BA': 'XMA - SR-s 4.8T 36pt QSFP-DD ER to 12T',
            '3HE10717CA': 'IOM - 7750 SR IOM4-e-B L2HQ',
            '3HE09649AA': 'MDA-e - 7750 SR 10-port 10GE SFP+ MDA-e',
            '3HE09881AA': 'MDA-e - 7750 SR 1-port 100GE CFP2 MDA-e',
            '3HE08432AA': 'CPM - 7450 ESS CPM5',
            '3HE08430AA': 'SFM - 7450 ESS SFM5-12',
            '3HE12510CA': 'IOM-s - SR-s IOM-s 1.6T - HE',
            '3HE12515AA': 'MDA-s - SR-s 4pt QSFP-DD + 4pt QSFP28',
            '3HE04743AA': 'IMM - 7x50 12-PT 10GE SFP+ - L3HQ',
            '3HE06326CA': 'IMM - 7x50 48-PT GE MultiCore SFP - L2HQ',
            '3HE08154AB': 'SF/CPM - 7210 SAS-R6',
            '3HE09154AA': 'IMM - 7210 SAS-R-b 4SFP+',
            '3HE09155AA': 'IMM - 7210 SAS-R-b 11SFP/22cSFP',
            '3HE08431AA': 'SFM - 7450 ESS SFM5-7',
            '3HE03624AA': 'IMM - 7750 SR 48-PT GE - SFP',
            '3HE09193CA': 'IMM - 7x50 ISA2 + 10-pt 10GE SFP+ L2HQ',
            '3HE10642AA': 'MDA-e - 7750 SR 40cSFP/20SFP GE MDA-e',
            '3HE14782AA': 'SYS - 7250 IXR-e 24SFP+ 8SFP28 2QSFP28',
            '3HE09426AA': 'SYS - 7210 SAS-K 2F2T1C ETR',
            '3HE14798AA': 'SYS - 7210 SAS-Dxp 2SFP+ 4F 6T ETR AC'
        }
    def filter_files(self,uploaded_files: list[str]) -> list[str]:
        filtered_files=[]
        for file_name in uploaded_files:
            if (self.pattern.match(file_name)):
                filtered_files.append(file_name)
        return filtered_files   
    def get_total_rows(self,file_path: str) -> int:
        if file_path.endswith(('.xlsx', '.xls')):
            total_rows=pd.read_excel(file_path,usecols=[1]).shape[0]
        else:
            total_rows=pd.read_csv(file_path,usecols=[1]).shape[0]
        return total_rows
    def read_filtered_data(self, file_path: str, chunk_size: int = 10000, start: int = 0) -> pd.DataFrame:
        dtype = {
            'Site Name': 'str',
            'Part Number': 'str',
            'Serial Number': 'str',
            'Shelf Type': 'str',
        }
        usecols = ['Site Name', 'Part Number', 'Serial Number', 'Shelf Type']
        skiprows = range(1, start + 1)

        if file_path.endswith(('.xlsx', '.xls')):
            data = pd.read_excel(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size)
        else:
            data = pd.read_csv(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size, low_memory=False)
        
        print(f"In Model Class read method, Read Data Length: {len(data)}, rows from file_path: {file_path}")

        # Remove duplicates by Serial Number
        data = data.drop_duplicates(subset=['Serial Number'], keep='first')
        # Filter out rows with empty or 'N/A' values in Part Number column
        data = data[data['Part Number'].notna()]  # Remove rows with NaN values
        data = data[data['Part Number'] != 'N/A']  # Remove rows with 'N/A' values
        data = data[data['Part Number'].str.strip() != '']  # Remove rows with empty strings
        data['Part Number'] = data['Part Number'].str[:10]
        # Map Part Number to Card Description
        data['Card Description'] = data['Part Number'].map(self.card_type_mapping).fillna('Unknown Card Type')
        # Keep only the necessary columns
        filtered_data = data[['Site Name', 'Part Number', 'Serial Number', 'Shelf Type', 'Card Description']]
        print(f"Returning now to Service Class the Processed data length: {len(filtered_data)}")
        return filtered_data.where(pd.notnull(filtered_data), None)
    def read_summary_data(self, file_path: str, chunk_size: int = 10000, start: int = 0) -> pd.DataFrame:
        dtype = {
            'Part Number': 'str',
            'Serial Number': 'str',
        }
        usecols = [ 'Part Number', 'Serial Number',]
        skiprows = range(1, start + 1)

        if file_path.endswith(('.xlsx', '.xls')):
            data = pd.read_excel(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size)
        else:
            data = pd.read_csv(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size, low_memory=False)
        
        print(f"In Card Model Class read method, Read Data Length: {len(data)}, rows from file_path: {file_path}")

        # Remove duplicates by Serial Number
        data = data.drop_duplicates(subset=['Serial Number'], keep='first')
        # Filter out rows with empty or 'N/A' values in Part Number column
        data = data[data['Part Number'].notna()]  # Remove rows with NaN values
        data = data[data['Part Number'] != 'N/A']  # Remove rows with 'N/A' values
        data = data[data['Part Number'].str.strip() != '']  # Remove rows with empty strings
        data['Part Number'] = data['Part Number'].str[:10]
        # Map Part Number to Card Description
        data['Description'] = data['Part Number'].map(self.card_type_mapping).fillna('Unknown Card Type')
        # Keep only the necessary columns
        filtered_data = data[[ 'Part Number','Description']]
        #Print the Return Values
        print(f"Returning now to Service Class the Processed data length: {len(filtered_data)}")
        return filtered_data.where(pd.notnull(filtered_data), None)

