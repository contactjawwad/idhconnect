# /home/jawwad/InventoryDataHub/app/services/sheld_power_service.py
from ..models.chassis_model import ChassisModel
from ..models.power_model import PowerModel
import pandas as pd
import gc

class ShelfPowerService:
    def __init__(self):
        self.power_model = PowerModel()  # Initialize PowerModel
        self.chassis_model = ChassisModel()  # Initialize ChassisModel
        self.power_data = pd.DataFrame()  # To store the power model data
        self.chassis_data = pd.DataFrame()  # To store the chassis model data
        self.data_processed = False  # Flag to ensure data is processed only once
        self.pw_desc_mapping = {
            "3HE08153AA": "PEM - 7210 SAS-R6 -48V",
            "3HE10964AA": "PS - 7210 SAS-K 2F4T6C ETR AC",
            "3HE10965AA": "PS - 7210 SAS-K 2F4T6C ETR -48V DC",
            "3HE10029AA": "PS - 7210 SAS-K ETR AC power supply",
            "3HE10030AA": "PS - 7210 SAS-K ETR -48V DC power supply",
            "3HE10837AA": "PS - DC -48V 210 WBX and 7210 Sx 100G",
            "3HE11185AA": "PSU - LVDC 6kw Power Supply",
            "3HE14785AA": "PS - 7250 IXR-e DC",
            "3HE03666AA": "PEM - 7450 ESS-12 175A DC PEM-3",
            "3HE03665AA": "PEM - 7450 ESS-7 100A DC PEM-3 SLOT 1",
            "3HE03664AA": "PEM - 7450 ESS-7 100A DC PEM-3 SLOT 2",
        }

    
    def fetch_filtered_file_details(self, uploaded_files: list[str],temp_dir: str):
        filtered_files=self.power_model.filter_files(uploaded_files)
        total_rows=[]
        files_with_path=[]
        
        for file_name in filtered_files:
            file_path=f"{temp_dir}/{file_name}"
            print(f"In Fecth Service Class Filter File Pasth {file_path}")
            files_with_path.append(file_path)
            # Get the total number of rows in the file and add to the list
            print(f"In Fecth Service Class Filter File Pasth {self.power_model.get_total_rows(file_path)} ")
            total_rows.append(self.power_model.get_total_rows(file_path))
        return files_with_path,total_rows

    def process_power_model_files(self, uploaded_files: list[str], temp_dir: str, start: int = 0, chunk_size: int = 10000):
        """
        Process power model files in chunks and store the data in self.power_data.
        """
        # Step 1: Filter the uploaded files to get only power model files
        filtered_files = self.power_model.filter_files(uploaded_files)
        self.power_data = pd.DataFrame()  # Reset the dataframe
        underline_start = "\033[4m"
        underline_end = "\033[0m"
        
        # Step 2: Iterate over each filtered file
        for file_name in filtered_files:
            file_path = f"{temp_dir}/{file_name}"  # Construct the full file path
            total_rows = self.power_model.get_total_rows(file_path)  # Get the total number of rows in the file
            rows_to_skip = start  # Initialize the number of rows to skip for chunking

            # Step 3: Read the file in chunks
            while rows_to_skip < total_rows:
                # Read a chunk of data from the file
                
                data_chunk = self.power_model.read_filtered_data(file_path, chunk_size=chunk_size, start=rows_to_skip)
                print(f"In Start While loop, Total Rows in Power Model {total_rows} & Chunk: {len(data_chunk)}")
                # If the chunk is empty, break the loop
                if data_chunk.empty:
                    break

                # Step 4:  # Concatenate the new data chunk to the existing self.power_data DataFrame
                # ignore_index=True ensures that the index is reset after concatenation
                self.power_data = pd.concat([self.power_data, data_chunk], ignore_index=True)
                
                
                # Update the number of rows to skip for the next chunk
                rows_to_skip += chunk_size
                print(f"In While loop, Total Rows to skio in Power Model {rows_to_skip}")
                 # Force garbage collection after processing each chunk
                del data_chunk
                gc.collect()       
                # If the chunk size is less than the specified chunk_size, all data has been fetched
                """  if len(data_chunk) < chunk_size:
                    print(f"If Power Service Len len(data_chunk) < chunk_size: {len(data_chunk)} < {chunk_size}")
                    break """
        print (f"\n{underline_start}Finished the exexuting the Power Function:- Process_power_model_files(){underline_end}")

        # Combine rows for the same Site Name into single rows with Assigned Type-1 and Assigned Type-2
        self.power_data = self.power_data.groupby('Site Name').agg(lambda x: list(x)[:2]).reset_index()
        self.power_data[['Assigned Type-1', 'Assigned Type-2']] = pd.DataFrame(self.power_data['Assigned Type'].tolist(), index=self.power_data.index)
        self.power_data.drop(columns=['Assigned Type'], inplace=True)

        return True
    def process_chassis_model_files(self, uploaded_files: list[str], temp_dir: str, start: int = 0, chunk_size: int = 10000):
        """
        Process chassis model files in chunks and apply transformations.
        """
        # Step 1: Filter the uploaded files to get only chassis model files
        filtered_files = self.chassis_model.filter_files(uploaded_files)
        self.chassis_data = pd.DataFrame()  # Reset the dataframe
        underline_start = "\033[4m"
        underline_end = "\033[0m"
        
        # Step 2: Iterate over each filtered file
        for file_name in filtered_files:
            file_path = f"{temp_dir}/{file_name}"  # Construct the full file path
            total_rows = self.chassis_model.get_total_rows(file_path)  # Get the total number of rows in the file
            rows_to_skip = start  # Initialize the number of rows to skip for chunking

            # Step 3: Read the file in chunks
            while rows_to_skip < total_rows:
                # Read a chunk of data from the file
                data_chunk = self.chassis_model.read_filtered_data(file_path, chunk_size=chunk_size, start=rows_to_skip)
                # If the chunk is empty, break the loop
                if data_chunk.empty:
                    break  
                # Concatenate the new data chunk to the existing self.chassis_data DataFrame
                self.chassis_data = pd.concat([self.chassis_data, data_chunk], ignore_index=True)
                # Update the number of rows to skip for the next chunk
                rows_to_skip += chunk_size
                # If the chunk size is less than the specified chunk_size, all data has not been fetched
                # Force garbage collection after processing each chunk
                del data_chunk
                gc.collect()
        
        print (f"\n{underline_start}Finished the exexuting the Chassis Function:- Process_chassis_model_files(){underline_end}")
        return True  # Indicate that processing for all files has been attempted

    def merge_and_transform_data(self):
        if self.power_data.empty or self.chassis_data.empty:
            print("No data to process")
            return pd.DataFrame()

        merged_data = pd.merge(self.chassis_data, self.power_data, on='Site Name', how='left')
        merged_data = self.map_ps_and_power_source(merged_data)
          # Drop 'Assigned Type-1' and 'Assigned Type-2' after mapping
        merged_data.drop(columns=['Assigned Type-1', 'Assigned Type-2'], inplace=True)
        return merged_data[['Site Name', 'Shelf Type', 'PS-1 PN', 'PS-2 PN', 'Power Source']]

    """ 
    def merge_and_transform_data(self):
        if self.flash_data.empty or self.chassis_data.empty:
            print("No data to process")
            return pd.DataFrame()

        merged_data = pd.merge(self.flash_data, self.chassis_data, on='Site Name', how='left')
        merged_data.drop(columns=['Site Name'], inplace=True)
        return merged_data[['Slot', 'CF No', 'Capacity (GB)', 'CF Part Number', 'Shelf Type']]
    """
    
    def map_ps_and_power_source(self, merged_data):
        """
        Map 'PS-1 PN', 'PS-2 PN', and 'Power Source' based on chassis data and power data.
        """
        # Define mappings for part numbers
        ps_mapping = {
            "3HE08151AA": ("3HE08153AA", "3HE08153AA", "DC"),
            "3HE11597AA": ("3HE10837AA", "3HE10837AA", "DC"),
            "3HE12340AA": ("3HE11185AA", "3HE11185AA", "DC"),
            "3HE14782AA": ("3HE14785AA", "3HE14785AA", "DC"),
            "3HE10768AA": ("3HE03666AA", "3HE03666AA", "DC"),
            "3HE02036AA": ("3HE03666AA", "3HE03666AA", "DC"),
            "3HE00245AA": ("3HE03665AA", "3HE03664AA", "DC"),
        }

        # Apply initial mapping for known part numbers
        merged_data['PS-1 PN'] = merged_data['Part Number'].map(lambda x: ps_mapping[x][0] if x in ps_mapping else None)
        merged_data['PS-2 PN'] = merged_data['Part Number'].map(lambda x: ps_mapping[x][1] if x in ps_mapping else None)
        merged_data['Power Source'] = merged_data['Part Number'].map(lambda x: ps_mapping[x][2] if x in ps_mapping else None)
        
        # Create lookup dictionaries for special cases

        special_cases_1 = self.power_data.set_index('Site Name')['Assigned Type-1'].to_dict()
        special_cases_2 = self.power_data.set_index('Site Name')['Assigned Type-2'].to_dict()


        def apply_special_case(row):
            if row['Part Number'] in ["3HE14798AA", "3HE09426AA"]:
                site_name = row['Site Name']
                if site_name in special_cases_1 and site_name in special_cases_2:
                    row['PS-1 PN'] = self.map_assigned_type(special_cases_1[site_name], row['Part Number'])
                    row['PS-2 PN'] = self.map_assigned_type(special_cases_2[site_name], row['Part Number'])
                    
                    row['Power Source'] = self.determine_power_source(row, row['Part Number'])
            return row

        # Apply special cases
        merged_data = merged_data.apply(apply_special_case, axis=1)
        merged_data.drop(columns=['Part Number'], inplace=True)
        return merged_data

    def map_assigned_type(self, assigned_type, part_number):
        """
        Map assigned type to power part numbers based on specific conditions.
        """
        if part_number == "3HE14798AA":
            if assigned_type == "AC Single":
                return "3HE10964AA"
            elif assigned_type == "Not Assigned":
                return "Not Installed"
            else:
                return "3HE10965AA"
        elif part_number == "3HE09426AA":
            if assigned_type == "AC Single":
                return "3HE10029AA"
            elif assigned_type == "Not Assigned":
                return "Not Installed"
            else:
                return "3HE10030AA"
        return None

    def determine_power_source(self, row, part_number):
        """
        Determine the power source based on PS-1 PN and PS-2 PN values.
        """
        ps1_pn = row['PS-1 PN']
        ps2_pn = row['PS-2 PN']

        if part_number == "3HE09426AA":
            """ if ps1_pn == "3HE10029AA" or ps2_pn == "3HE10029AA":
                if ps1_pn == "3HE10030AA" or ps2_pn == "3HE10030AA":
                    return "AC & DC" """
            if ((ps1_pn == "Not Installed" and ps2_pn == "3HE10030AA") or (ps2_pn == "Not Installed" and ps1_pn == "3HE10030AA") or (ps1_pn == "3HE10030AA" and ps2_pn == "3HE10030AA")):
                return "DC"
            elif ((ps1_pn == "Not Installed" and ps2_pn == "3HE10029AA") or (ps2_pn == "Not Installed" and ps1_pn == "3HE10029AA") or (ps1_pn == "3HE10029AA" and ps2_pn == "3HE10029AA")):
                return "AC"
            else:
                return "AC & DC"
            
        else:
            if ((ps1_pn == "Not Installed" and ps2_pn == "3HE10964AA") or (ps2_pn == "Not Installed" and ps1_pn == "3HE10964AA") or (ps1_pn == "3HE10964AA" and ps2_pn == "3HE10964AA")):
                return "AC"
            elif ((ps1_pn == "Not Installed" and ps2_pn == "3HE10965AA") or (ps2_pn == "Not Installed" and ps1_pn == "3HE10965AA") or (ps1_pn == "3HE10965AA" and ps2_pn == "3HE10965AA")):
                return "DC"
            else:
                return "AC & DC"

    def generate_summary_data(self, merged_data):
        # Filter out "Not Installed" from both PS-1 PN and PS-2 PN
        filtered_data = merged_data[(merged_data['PS-1 PN'] != "Not Installed") | (merged_data['PS-2 PN'] != "Not Installed")]

        # Initialize an empty dictionary to count occurrences of each part number
        part_number_counts = {}

        # Count occurrences of each part number in PS-1 PN
        for part_number in filtered_data['PS-1 PN']:
            if part_number and part_number != "Not Installed":
                if part_number in part_number_counts:
                    part_number_counts[part_number] += 1
                else:
                    part_number_counts[part_number] = 1

        # Count occurrences of each part number in PS-2 PN
        for part_number in filtered_data['PS-2 PN']:
            if part_number and part_number != "Not Installed":
                if part_number in part_number_counts:
                    part_number_counts[part_number] += 1
                else:
                    part_number_counts[part_number] = 1

        # Create the summary data
        summary_data = []
        for part_number, count in part_number_counts.items():
            if part_number in self.pw_desc_mapping:
                summary_data.append({
                    "Power Supply PN": part_number,
                    "QTY": count,
                    "Description": self.pw_desc_mapping[part_number]
                })          
        return summary_data


    def process_files(self, uploaded_files: list[str], temp_dir: str, start: int = 0, chunk_size: int = 10000):
        if self.data_processed:
            return []

        self.process_power_model_files(uploaded_files, temp_dir, start, chunk_size)
        self.process_chassis_model_files(uploaded_files, temp_dir, start, chunk_size)
        
        self.data_processed = True  # Mark data as processed

        table_data = self.merge_and_transform_data()

        summary_data = self.generate_summary_data(table_data)        
        self.data_processed = True  # Mark data as processed

        num_rows_table_data = len(table_data)
        print(f"Number of rows in table_data (list of dictionaries): {num_rows_table_data}")
        return table_data.to_dict(orient='records'),summary_data,self.data_processed
        #return table_data.to_dict(orient='records'), self.data_processed

    #This Function is Made for Summary Only to be called from Summary Controller
    def process_power_summary(self, uploaded_files: list[str], temp_dir: str, start: int = 0, chunk_size: int = 10000):
        self.process_power_model_files(uploaded_files, temp_dir, start, chunk_size)
        self.process_chassis_model_files(uploaded_files, temp_dir, start, chunk_size)
        
        self.data_processed = True  # Mark data as processed

        table_data = self.merge_and_transform_data()

        summary_data = self.generate_pw_summary(table_data)        
        self.data_processed = True  # Mark data as processed

        num_rows_table_data = len(table_data)
        print(f"Number of rows in table_data (list of dictionaries): {num_rows_table_data}")
        #del table_data
        # print(f"Power Summaray Printed below\n {summary_data}")
        #summary_data = pd.DataFrame(summary_data).to_dict(orient='records')
        return summary_data,self.data_processed
      
    def generate_pw_summary(self, merged_data):
        # Filter out "Not Installed" from both PS-1 PN and PS-2 PN
        filtered_data = merged_data[(merged_data['PS-1 PN'] != "Not Installed") | (merged_data['PS-2 PN'] != "Not Installed")]

        # Initialize an empty dictionary to count occurrences of each part number
        part_number_counts = {}

        # Count occurrences of each part number in PS-1 PN
        for part_number in filtered_data['PS-1 PN']:
            if part_number and part_number != "Not Installed":
                if part_number in part_number_counts:
                    part_number_counts[part_number] += 1
                else:
                    part_number_counts[part_number] = 1

        # Count occurrences of each part number in PS-2 PN
        for part_number in filtered_data['PS-2 PN']:
            if part_number and part_number != "Not Installed":
                if part_number in part_number_counts:
                    part_number_counts[part_number] += 1
                else:
                    part_number_counts[part_number] = 1

        # Create the summary data
        summary_data = []
        for part_number, count in part_number_counts.items():
            if part_number in self.pw_desc_mapping:
                summary_data.append({
                    "Part Number": part_number,
                    "QTY": count,
                    "Description": self.pw_desc_mapping[part_number]
                })          
        return summary_data

