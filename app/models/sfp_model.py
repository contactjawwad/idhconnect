# /home/jawwad/InventoryDataHub/app/models/sfp_model.py
import re
import pandas as pd
import logging
class SFPModel:
    def __init__(self):
        #This regex pattern can be configured here to keep the model focused on data validation and parsing
        # Compile a regex pattern to match specific filenames
        self.pattern=re.compile(r'^media_adaptor_\d+_NFMP[12]\.(csv|xlsx?|xls)$')
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)  
        self.part_number_description_mapping = {
            '3FE25772AA': '1000Base-BX10-U SFP 1310NM 10KM 11DB',
            '3FE25774AA': '1000Base-LX SFP SM 1310nm 10km 11dB',
            '3FE25776AA': '1000Base-ZX SFP SM 1550NM 80KM 24DB',
            '3FE62600AA': '10GBase-LR SFP+ 10km I-Temp',
            '3FE62600CA': 'SFP+ 10GE Optical',
            '3FE65831AA': '10GBase-ER SFP+ 40km I-Temp',
            '3FE65832AA': '10GBase-ZR SFP+ 80km I-Temp',
            '3HE00027CA': 'SFP - GIGE SX - LC ROHS 6/6 DDM -40/85C',
            '3HE00028CA': 'SFP - GIGE LX - LC ROHS 6/6 DDM -40/85C',
            '3HE00029CA': 'SFP - GIGE ZX - LC ROHS 6/6 DDM -40/85C',
            '3HE00062AA': 'SFP - GIGE TX SFP COPPER MOD - RJ45',
            '3HE00062CB': 'SFP - GIGE BASE-T RJ45 R6/6 DDM -40/85C',
            '3HE00867CA': 'SFP - GIGE EX - LC ROHS 6/6 DDM -40/85C',
            '3HE00868CA': 'SFP - GIGE BX10-U - LC R6/6 DDM -40/85C',
            '3HE01454CA': 'SFP - 100M EX - LC ROHS 6/6 DDM -40/85C',
            '3HE04324AA': 'SFP - GIGE BX-U 40KM SFP',
            '3HE04324AB': 'SFP - GIGE BX-D 40KM SFP',
            '3HE04823AA': 'SFP+  10GE LR - LC ROHS6/6 0/70C',
            '3HE04824AA': 'SFP+  10GE SR - LC ROHS6/6 0/70C',
            '3HE05036AA': 'SFP+  10GE ER - LC ROHS6/6 0/70C',
            '3HE05037AA': 'SFP+ 10GE BX10-U LC ROHS6/6 0/70C',
            '3HE05037AB': 'SFP+ 10GE BX10-D LC ROHS6/6 0/70C',
            '3HE05894AA': 'SFP+ 10GE ZR - LC ROHS6/6 0/70C',
            '3HE08217AA': 'CFP2 - 100G LR4 10KM LC ROHS6/6 0/70C',
            '3HE08313BA': 'cSFP - GIGE BX10-D - LC R6/6 DDM -40/85C',
            '3HE08314BA': 'cSFP - GIGE BX40-D - LC R6/6 DDM -40/85C',
            '3HE09255AA': 'CFP2 - OTU4 ER4 40KM LC ROHS6/6 0/70C',
            '3HE09326AA': 'SFP+10GE SR - LC ROHS6/6-40/85C',
            '3HE09327AA': 'SFP+10GE LR - LC ROHS6/6-40/85C',
            '3HE09328AA': 'SFP+10GE ER - LC ROHS6/6-40/85C',
            '3HE09329AA': 'SFP+10GE ZR - LC ROHS6/6 -40/85C',
            '3HE10452AA': 'SFP+ 10GE BX40-U LC ROHS6/6 -40/85C',
            '3HE10452AB': 'SFP+ 10GE BX40-D LC ROHS6/6 -40/85C',
            '3HE10550AA': 'QSFP28 - 100GBASE-LR4 ROHS6/6 0/70C',
            '3HE11239AA': 'QSFP28 - 100GBase-ER4Lite RoHS6/6 0/70C',
            '3HE11241AA': 'QSFP+ - 4x10GE LR SMF MPO ROHS6/6 0/70',
            '3HE12194AA': 'QSFP28 - 10x10G LR, MPO24, 0/70C',
            '3HE12229AA': 'QSFP28- 100G LR4 10KM ROHS6/6 -40/85C',
            '3HE14002AA': 'QSFP28-DD 2x100G LR4 10KM CS 0/70C',
            '3HE14835AA': 'SFP28 25GE LR - LC ROHS6/6 -40/85C',
            '3HE15272AA': 'QSFP56-DD - 400G FR4 2km 0/70C',
            '3HE16558AA': 'QSFP28 - 100GE ZR4 0/70C',
        }

        
        
    def filter_files(self,uploaded_files:list[str]) -> list[str]:
        filtered_files=[] #Initialize an empty list to store filtered files
        #Filter file names based on the specific SFP pattern.
        #Iteratre the Files which is received and add in filtered_files list
        for file_name in uploaded_files:
            if self.pattern.match(file_name):
                filtered_files.append(file_name) #Add the Matched Pattern in the list
        return filtered_files
    
    def get_total_rows(self, file_path: str) -> int:
        if file_path.endswith(('.xlsx', '.xls')):
            total_rows = pd.read_excel(file_path, usecols=[1]).shape[0]
            
        else:
            total_rows = pd.read_csv(file_path, usecols=[1]).shape[0]
            print(f"get_total_rows Method Called:Total rows in {file_path}: {total_rows}")
        return total_rows

    def read_filtered_data(self,file_path: str, chunk_size: int = 10000, start: int = 0) -> pd.DataFrame:
         # Define data types for columns if known
        dtype = {
            'Site Name': 'str',
            'Connector Type': 'str',
            'Model Number': 'str',
            'Vendor Serial Number': 'str',
           
        }
        # Specify the columns to be used
        usecols = ['Site Name', 'Connector Type', 'Model Number', 'Vendor Serial Number']

        skiprows = range(1, start + 1)  # Skip rows up to the start index
        #For the first request, start is 0, so skiprows is range(1, 1), which skips no rows.
        #For the second request, start is 10,000, so skiprows is range(1, 10001), which skips the first 10,000 rows.
        #For the third request, start is 20,000, so skiprows is range(1, 20001), which skips the first 20,000 rows.


        # Read the file in chunks based on its extension (CSV or Excel)
        if file_path.endswith(('.xlsx','.xls')):
            # If the file is an Excel file, read it using pandas' read_excel method
            #data = pd.read_excel(file_path, dtype=dtype, usecols=usecols)
            #This Below is not used
            data = pd.read_excel(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size)
            
        else:
            # If the file is a CSV file, read it using pandas' read_csv method
            #data = pd.read_csv(file_path, dtype=dtype, usecols=usecols, low_memory=False) 
            #This Below is not used currently
            data = pd.read_csv(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size, low_memory=False) 
                    
                
        #self.logger.info(f"In Model Class, Read Data Length: {len(data)}, rows from file_path: {file_path}")
        print(f"In Model Class read method, Read Data Length: {len(data)}, rows from file_path: {file_path}")
        #Apply filters to the data

                
        # Define the function to process the 'Model Number' column based on specified rules
        def process_model_number(model_number: str) -> str:
            model_number = model_number.strip().upper()

            # If the model number starts with "3HE", take the first 10 characters
            if model_number.startswith('3HE'):
                return model_number[:10]
            # If the model number starts with "Alcatel ", take the 10 characters after "Alcatel "
            elif model_number.startswith('ALCATEL '):
                return model_number[8:18]
            # If the model number starts with "fa", return "fa"
            else:
                #return model_number
                return None
        
        data = data[data['Model Number'].notna() & (data['Model Number'] != 'N/A') & (data['Model Number'].str.strip() != '')]
        data['Part Number'] = data['Model Number'].apply(process_model_number)
        data = data[data['Part Number'].notna()]
        data['Description'] = data['Part Number'].map(self.part_number_description_mapping)
        data = data.drop(columns=['Model Number'])
        
        print(f"Returning now to Service Class the Processed data length: {len(data)}")
        #self.logger.info(f"Processed data length: {len(data)}")
        #return data
        return data.where(pd.notnull(data), None)
    def read_summary_data(self,file_path: str, chunk_size: int = 10000, start: int = 0) -> pd.DataFrame:
        # Define data types for columns if known
        dtype = {
            'Model Number': 'str',
        }
        # Specify the columns to be used
        usecols = ['Model Number']

        skiprows = range(1, start + 1)  # Skip rows up to the start index
        #For the first request, start is 0, so skiprows is range(1, 1), which skips no rows.
        #For the second request, start is 10,000, so skiprows is range(1, 10001), which skips the first 10,000 rows.
        #For the third request, start is 20,000, so skiprows is range(1, 20001), which skips the first 20,000 rows.


        # Read the file in chunks based on its extension (CSV or Excel)
        if file_path.endswith(('.xlsx','.xls')):
            # If the file is an Excel file, read it using pandas' read_excel method
            #data = pd.read_excel(file_path, dtype=dtype, usecols=usecols)
            #This Below is not used
            data = pd.read_excel(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size)
            
        else:
            # If the file is a CSV file, read it using pandas' read_csv method
            #data = pd.read_csv(file_path, dtype=dtype, usecols=usecols, low_memory=False) 
            #This Below is not used currently
            data = pd.read_csv(file_path, dtype=dtype, usecols=usecols, skiprows=skiprows, nrows=chunk_size, low_memory=False) 
                    
                
        #self.logger.info(f"In Model Class, Read Data Length: {len(data)}, rows from file_path: {file_path}")
        print(f"In Model Class read method, Read Data Length: {len(data)}, rows from file_path: {file_path}")
        #Apply filters to the data

                
        # Define the function to process the 'Model Number' column based on specified rules
        def process_model_number(model_number: str) -> str:
            model_number = model_number.strip().upper()

            # If the model number starts with "3HE", take the first 10 characters
            if model_number.startswith('3HE'):
                return model_number[:10]
            # If the model number starts with "Alcatel ", take the 10 characters after "Alcatel "
            elif model_number.startswith('ALCATEL '):
                return model_number[8:18]
            # If the model number starts with "fa", return "fa"
            else:
                #return model_number
                return None
        
        data = data[data['Model Number'].notna() & (data['Model Number'] != 'N/A') & (data['Model Number'].str.strip() != '')]
        data['Part Number'] = data['Model Number'].apply(process_model_number)
        data = data[data['Part Number'].notna()]
       
        data['Description'] = data['Part Number'].map(self.part_number_description_mapping)
        data = data.drop(columns=['Model Number'])
        
        print(f"Returning now to Service Class the Processed data length: {len(data)}")
        #self.logger.info(f"Processed data length: {len(data)}")
        #return data
        return data.where(pd.notnull(data), None)
       