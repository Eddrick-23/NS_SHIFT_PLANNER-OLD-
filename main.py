import streamlit as st
from database import database as database
import pandas as pd
from st_btn_group import st_btn_group
import zipfile
import io
import os


st.set_page_config(page_title="Shift Planner",page_icon=":military_helmet:",layout="wide")
st.title("[Shift Planner](%s)" % "https://github.com/Eddrick-23/NS_SHIFT_PLANNER#ns-shift-planner")

if "has_rerun_on_upload" not in st.session_state: #used when uploading zip file to app
      st.session_state.has_rerun_on_upload = None

#create sidebar that takes some inputs

#load the database names

if "namesd1MCC" not in st.session_state:
        st.session_state.namesd1MCC = set()
if "namesd2MCC" not in st.session_state:
        st.session_state.namesd2MCC = set()
if "namesd1HCC1" not in st.session_state:
        st.session_state.namesd1HCC1 = set()
if "namesd2HCC1" not in st.session_state:
        st.session_state.namesd2HCC1 = set()
if "namesd3" not in st.session_state:
        st.session_state.namesd3 = set()

if "💀DAY 1: MCC" not in st.session_state:
      st.session_state["💀DAY 1: MCC"]= database(location="MCC ",day=1)
if "😴DAY 1: HCC1" not in st.session_state:
      st.session_state["😴DAY 1: HCC1"] = database(location="HCC1",day=1)
if "💀DAY 2: MCC" not in st.session_state:
      st.session_state["💀DAY 2: MCC"]= database(location="MCC ",day=2)
if "😴DAY 2: HCC1" not in st.session_state:
      st.session_state["😴DAY 2: HCC1"]= database(location="HCC1",day=2)
if "NIGHT DUTY" not in st.session_state:
      st.session_state["NIGHT DUTY"] = database(location="MCC ",day=3)

if "D1Names" not in st.session_state:
      st.session_state.D1Names = set()
if "D2Names" not in st.session_state:
      st.session_state.D2Names = set()
if "D3Names" not in st.session_state:
      st.session_state.D3Names = set()


def add_name(name):
      n = name.strip().upper()
      day = st.session_state[st.session_state.db_to_update].day

      if n == "HCC1" or n == "MCC": #Invalid name as control centre location
            st.sidebar.error("Invalid name!")

      if n not in st.session_state[st.session_state.db_to_update].get_names() and n not in st.session_state[f"D{day}Names"]:
            st.session_state[st.session_state.db_to_update].add_name(n)
            st.session_state[f"D{day}Names"].add(n)
            st.sidebar.success(f"{n} added!")
      else:
            st.sidebar.error("Name already exists!")
            
def remove_name(name_list):
      day = st.session_state[st.session_state.db_to_update].day

      for n in name_list:
         st.session_state[st.session_state.db_to_update].remove_name(n)
         st.session_state[f"D{day}Names"].remove(n)
         st.toast(f"{n} removed from {st.session_state.db_to_update}")


#sidebar
st.session_state.db_to_update = st.sidebar.radio("Database",options=["💀DAY 1: MCC","😴DAY 1: HCC1","💀DAY 2: MCC","😴DAY 2: HCC1","NIGHT DUTY"],key="sidebaractivedb",horizontal=True)

sidebar_col11,sidebar_col12 = st.sidebar.columns(2)

name = sidebar_col11.text_input("Enter Name:")
if sidebar_col11.button("Submit"):
      add_name(name)
name_list = sidebar_col12.multiselect(label="Choose names to remove",options=st.session_state[st.session_state.db_to_update].get_names())
if sidebar_col12.button("Remove"):
      remove_name(name_list)
st.sidebar.divider()
def rename_all(new_name,old_name):
      new_name = new_name.strip().upper()
      if new_name in set().union(st.session_state.D1Names,st.session_state.D2Names,st.session_state.D3Names):
            st.sidebar.warning(f"{new_name} already exists!")
            return
      #update the day name session states
      for d in ["D1Names","D2Names","D3Names"]:
            if old_name in st.session_state[d]:
                  st.session_state[d].remove(old_name)
                  st.session_state[d].add(new_name)
      #update individual databases
      for db in ["💀DAY 1: MCC","😴DAY 1: HCC1","💀DAY 2: MCC","😴DAY 2: HCC1","NIGHT DUTY"]:
            if old_name in st.session_state[db].get_names():
                  st.session_state[db].rename(new_name,old_name)
      st.sidebar.success(f"Renamed {old_name} to {new_name}")
st.sidebar.text("Rename") #rename a name across all databases
new_name = st.sidebar.text_input("Enter New Name:")
old_name = st.sidebar.selectbox(label="Old name",options=set().union(st.session_state.D1Names,st.session_state.D2Names,st.session_state.D3Names))
st.sidebar.button(label="Rename",on_click=rename_all,kwargs={"new_name":new_name,"old_name":old_name})

st.sidebar.divider()
def name_in_same_database(names,database):
      db_names = database.get_names()
      if names[0] in db_names and names[1] in db_names:
            return True #returns True if both names in current database
      else: # returns the name that is not in the database
            for n in names:
                  if n not in db_names:
                        return n
def swap_names(names):
      if st.session_state.day_for_swapping == 3:
            st.session_state["NIGHT DUTY"].swap_names(names[0],names[1])
      else:
            mcc_db = st.session_state[f"💀DAY {st.session_state.day_for_swapping}: MCC"]
            hcc1_db = st.session_state[f"😴DAY {st.session_state.day_for_swapping}: HCC1"]

            mcc_check = name_in_same_database(names,database=mcc_db)
            hcc1_check = name_in_same_database(names,database=hcc1_db)
            #case 1 both names in mcc_db
            if mcc_check == True:
                  mcc_db.swap_names(names[0],names[1])
            #case 2 both names in hcc1_db
            elif hcc1_check == True:
                  hcc1_db.swap_names(names[0],names[1])
            #case 3 both names in different database
            else:
                  mcc_db.rename(new_name = mcc_check,old_name = hcc1_check)
                  hcc1_db.rename(new_name = hcc1_check,old_name = mcc_check)

st.sidebar.write("Swap names")
st.session_state.day_for_swapping = st.sidebar.radio(label="DAY",options=[1,2,3],horizontal=True)
st.session_state.names_to_swap = st.sidebar.multiselect(label="Choose 2 names",options=st.session_state[f"D{st.session_state.day_for_swapping}Names"],max_selections=2)
if len(st.session_state.names_to_swap) == 2:
      st.sidebar.button(label="Swap",on_click=swap_names,kwargs={"names":st.session_state.names_to_swap})
st.sidebar.divider()

st.session_state.hided1_grid = st.sidebar.toggle("Hide DAY 1 grid")
st.session_state.hided2_grid = st.sidebar.toggle("Hide DAY 2 grid")
st.session_state.hided3_grid = st.sidebar.toggle("Hide DAY 3 grid")
st.session_state.check_lunch_dinner = not st.sidebar.toggle("Disable Lunch & Dinner Check", value=False)
#back to main page

col1, col2 = st.columns(2)

with col1:
      st.session_state.active_database = st.radio(label="Database",options=["💀DAY 1: MCC","😴DAY 1: HCC1","💀DAY 2: MCC","😴DAY 2: HCC1","NIGHT DUTY"],horizontal=True)
      st.session_state.active_name = st.multiselect(label="Name(s)",options=st.session_state[st.session_state.active_database].get_names())
with col2:
      st.session_state.active_allocation_size = st_btn_group(mode="radio",buttons=[{"label":"First 30 min","value":"001"},{"label":"Full","value":"002"},{"label":"Last 30 min","value":"30"}],key="allocation_size",merge_buttons=True,size="compact",radio_default_index=1)
      st.session_state.active_location = st.radio(label="Location",options=["MCC ","HCC1"]) #whitespace after MCC for standard cell size
#button groups

def allocate_shift(n,hour): #call back function for buttons

      # set up appropriate timeblock to query
      main_time_block = hour + ":00:00" #actual time block e.g if left half @1200 > 1200/ right half > 1230
      other_time_block = hour+ ":30:00"  #other half if left half @1200, other half > 1230 etc.
      if st.session_state.active_allocation_size == "30":
            main_time_block,other_time_block = other_time_block,main_time_block #swap
      #check first if shift is allocated
      allocation_state1 = st.session_state[st.session_state.active_database].is_shift_allocated(time_block=main_time_block,name = n)
      allocation_state2 = None
      if st.session_state.active_allocation_size == "002":
            allocation_state2 = st.session_state[st.session_state.active_database].is_shift_allocated(other_time_block, name = n)
      #deal with allocation_state1
      if not allocation_state1: #if shift not allocated, allocate shift
            st.session_state[st.session_state.active_database].add_shift(location = st.session_state.active_location,time_block = main_time_block,name = n)
      else: 
            st.session_state[st.session_state.active_database].remove_shift(time_block = main_time_block,name = n)
      
      if allocation_state2 != None:
            if not allocation_state2: #allocate other half for FULL SHIFT OPTION
                  st.session_state[st.session_state.active_database].add_shift(location = st.session_state.active_location,time_block = other_time_block,name = n)
            else:
                  st.session_state[st.session_state.active_database].remove_shift(time_block = other_time_block,name = n)

def allocate_all(hour):
      for n in st.session_state.active_name:
            allocate_shift(n,hour)

def create_button_group():
    #set the time ranges first
    default_day_range = ["06","07","08","09","10","11","12","13","14","15","16","17","18","19","20"]
    if st.session_state.active_database == "NIGHT DUTY":
          default_day_range = ["21","22","23","00","01","02","03","04","05","06"]
    time_range = ["06","07","08","09","10","11","12","13","14","15","16","17","18","19","20"]
    if st.session_state.active_database in ["💀DAY 1: MCC","😴DAY 1: HCC1"]: #if day 1, remove 0600
              default_day_range.pop(0)
    if st.session_state.active_allocation_size in ["001","002"]:
         time_range = [item + "00" for item in default_day_range]
         
    elif st.session_state.active_allocation_size in ["30"]:
          time_range  = [item + "30" for item in default_day_range]

    
    #create the buttons:
    n_buttons = len(time_range)
    buttons,_ = st.columns([0.99,0.01])
    cols = buttons.columns(n_buttons)
    for n in range(n_buttons):
          with cols[n]:
                st.button(label=time_range[n],use_container_width=True,on_click=allocate_all,kwargs={"hour":time_range[n][:2]})

if st.session_state.active_name != []:
      create_button_group()

#displaying dataframes
def format_keys(df1,df2):
        '''
            df1(pandas dataframe)
            df2(pandas dataframe)
            
            dataframes should have the same format. Merging the dataframes will just join the names.
            The "DAY" and "Time" Columns should be the same.

            This function reads two dataframes and returns formatted timeblocks that fit both dataframes. Such that they are always aligned.
        '''
        keys = []
        joined = []
        #iterate over df two rows at a time
        # we join the time slots only if 
        #1) no slots allocated at all in that 1h block
        #2) slots are allocated to the same person in that 1h block
        joined_df = df1.merge(df2)
        for i in range(0,len(joined_df),2):
            #get two rows at a time
            rows = joined_df.iloc[i:i+2]
            join_blocks = True
            for c in rows.columns[2:]:
                v1,v2 = rows[c].iloc[0],rows[c].iloc[1]

                if v1 != v2:
                    join_blocks = False
                    break
            keys.append(rows.Time.iloc[0][:-3]) #slice string for HH:MM format
            if join_blocks:
                joined.append(True)
            if not join_blocks:
                keys.append(rows.Time.iloc[1][:-3]) #slice string for HH:MM format
                joined.append(False)


        return keys, joined


def displayd1_grid():
      if not st.session_state.hided1_grid:
            k,j = format_keys(st.session_state["💀DAY 1: MCC"].data,st.session_state["😴DAY 1: HCC1"].data)
            st.data_editor(st.session_state["💀DAY 1: MCC"].generate_formatted_df(keys = k, joined = j,check_lunch_dinner = st.session_state.check_lunch_dinner),hide_index=True,use_container_width=True,disabled=True)
            st.data_editor(st.session_state["😴DAY 1: HCC1"].generate_formatted_df(keys = k, joined = j,check_lunch_dinner = st.session_state.check_lunch_dinner),hide_index=True,use_container_width=True,disabled = True)

displayd1_grid()


def displayd2_grid():
      if not st.session_state.hided2_grid:
            k,j = format_keys(st.session_state["💀DAY 2: MCC"].data,st.session_state["😴DAY 2: HCC1"].data)
            st.data_editor(st.session_state["💀DAY 2: MCC"].generate_formatted_df(keys = k, joined = j,check_lunch_dinner = st.session_state.check_lunch_dinner),hide_index=True,use_container_width=True,disabled=True)
            st.data_editor(st.session_state["😴DAY 2: HCC1"].generate_formatted_df(keys = k, joined = j,check_lunch_dinner = st.session_state.check_lunch_dinner),hide_index=True,use_container_width=True,disabled=True)
      
displayd2_grid()

bottom_col1,bottom_col2 = st.columns([0.2,0.8])

def displayd3_grid():
      if not st.session_state.hided3_grid:
            bottom_col2.data_editor(st.session_state["NIGHT DUTY"].generate_formatted_df(),hide_index=True,use_container_width=True,disabled=True)

displayd3_grid()  

#hour counter
def display_hours():
      hours = {} 
      d1MCC = st.session_state["💀DAY 1: MCC"].hours
      d1HCC1 = st.session_state["😴DAY 1: HCC1"].hours
      d2MCC = st.session_state["💀DAY 2: MCC"].hours
      d2HCC1 = st.session_state["😴DAY 2: HCC1"].hours
      nightduty = st.session_state["NIGHT DUTY"].hours

      for key,val in d1MCC.items():
            if key not in hours:
                  hours[key] = [0,0,0]
            hours[key][0] = val
      
      for key,val in d1HCC1.items():
            if key not in hours:
                  hours[key] = [0,0,0]
            hours[key][0] = val
      
      for key,val in d2MCC.items():
            if key not in hours:
                  hours[key] = [0,0,0]
            hours[key][1] = val
      for key,val in d2HCC1.items():
            if key not in hours:
                  hours[key] = [0,0,0]
            hours[key][1] = val
      for key,val in nightduty.items():
            if key not in hours:
                  hours[key] = [0,0,0]
            hours[key][2] = val
      
      for key,val in hours.items():
            val.append(sum(val))
      
      df = pd.DataFrame(data=hours,index=["DAY 1","DAY 2","DAY 3","TOTAL"]).T
      df = df.sort_values(by=["TOTAL"],ascending=False)
      df.loc[" TOTAL  "] = df.sum() # add whitespace so this row will always be either first or last in sorting
      
      return df

hour_count = display_hours()

st.session_state.hour_count_on_sidebar = st.sidebar.toggle(label="Display hour count on sidebar",value=True)
if st.session_state.hour_count_on_sidebar:
      st.sidebar.dataframe(hour_count,use_container_width=True,)
      bottom_col1.header("NIGHT DUTY")
else:     
      bottom_col1.dataframe(hour_count,use_container_width=True)

st.sidebar.divider()
#uploading and downloading files

# Function to extract and read CSV files from the zip archive
def extract_and_read_csv(zip_file):
    # Create a temporary directory to extract files to
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall("extracted_files")

    # List the CSV files in the extracted folder
    csv_files = [f for f in os.listdir("extracted_files") if f.endswith('.csv')]

    # Create a dictionary to store DataFrames
    dfs = {}

    # Read each CSV file into a pandas DataFrame
    for csv_file in csv_files:
        file_path = os.path.join("extracted_files", csv_file)
        df = pd.read_csv(file_path)
        dfs[csv_file] = df

    # Clean up: Remove the extracted files after reading
    for csv_file in csv_files:
        os.remove(os.path.join("extracted_files", csv_file))

    return dfs


st.session_state.zip_file = st.sidebar.file_uploader(label="Upload zip of saved work",type="zip")

if st.session_state.zip_file is not None and not st.session_state.has_rerun_on_upload:
    # Convert uploaded file to BytesIO object
    zip_file_bytes = io.BytesIO(st.session_state.zip_file.read())
    
    # Extract and read CSV files into DataFrames
    dataframes = extract_and_read_csv(zip_file_bytes)
    
    # Display the DataFrames
    st.session_state["💀DAY 1: MCC"].set_data(dataframes["DAY1MCC.csv"].drop('Unnamed: 0', axis=1).replace(0,"0   "))
    st.session_state.namesd1MCC = st.session_state["💀DAY 1: MCC"].names
    st.session_state["💀DAY 2: MCC"].set_data(dataframes["DAY2MCC.csv"].drop('Unnamed: 0', axis=1).replace(0,"0   "))
    st.session_state.namesd2MCC = st.session_state["💀DAY 2: MCC"].names
    st.session_state["😴DAY 1: HCC1"].set_data(dataframes["DAY1HCC1.csv"].drop('Unnamed: 0', axis=1).replace(0,"0   "))
    st.session_state.namesd1HCC1 = st.session_state["😴DAY 1: HCC1"].names
    st.session_state["😴DAY 2: HCC1"].set_data(dataframes["DAY2HCC1.csv"].drop('Unnamed: 0', axis=1).replace(0,"0   "))
    st.session_state.namesd2HCC1 = st.session_state["😴DAY 2: HCC1"].names
    st.session_state["NIGHT DUTY"].set_data(dataframes["NIGHTDUTY.csv"].drop('Unnamed: 0', axis=1).replace(0,"0   "))
    st.session_state.namesd3 = st.session_state["NIGHT DUTY"].names
    st.session_state.D1Names = st.session_state.namesd1MCC.union(st.session_state.namesd1HCC1)
    st.session_state.D2Names = st.session_state.namesd2MCC.union(st.session_state.namesd2HCC1)
    st.session_state.D3Names = st.session_state.namesd3.copy()
    st.session_state.has_rerun_on_upload = True
    st.rerun()

def create_zip():
      #takes all dataframes from each database, convert to csv, store as zip file

      buf = io.BytesIO()
      with zipfile.ZipFile(buf, "x") as myzip: # set the mode parameter to x to create and write a new file
            myzip.writestr("DAY1MCC.csv", st.session_state["💀DAY 1: MCC"].data.to_csv()) # convert df to .csv and name it
            myzip.writestr("DAY1HCC1.csv", st.session_state["😴DAY 1: HCC1"].data.to_csv()) 
            myzip.writestr("DAY2MCC.csv", st.session_state["💀DAY 2: MCC"].data.to_csv()) 
            myzip.writestr("DAY2HCC1.csv", st.session_state["😴DAY 2: HCC1"].data.to_csv())
            myzip.writestr("NIGHTDUTY.csv",st.session_state["NIGHT DUTY"].data.to_csv())

      return buf


st.sidebar.download_button(label="Download zip",data=create_zip().getvalue(),file_name="Planning.zip",mime="data/zip",use_container_width=True)

day1warnings,day2warnings,day3warnings,validation_options = st.columns((.3,.3,.3,.1))

def validate_shifts(df1,df2,day):
      '''
      Method checks that approriate strength is allocated to control centres for mounting hours
      Best to call when hours are all allocated as computation is resource heavy
      '''
      result = []
      if day == 1 or day == 2:
            joined_df = df1.merge(df2)

            for idx,row in joined_df.iterrows():
                  freq_data = row[2:].value_counts() #get count of MCC and HCC1
                  
                  if  "HCC1" not in row.values and "MCC " not in row.values:
                        result.append(f"WARNING(INSUFFICIENT STRENGTH):At {row.Time}. No one in both control centres.")
                  elif "HCC1" not in row.values: # Check if no one in HCC1
                        result.append(f"WARNING(MISALLOCATION): At {row.Time}. MCC:{freq_data.MCC}. No one in HCC1.")
                  elif "MCC " not in row.values: # Check if no one in MCC
                        result.append(f"WARNING(MISALLOCATION): At {row.Time}. HCC1:{freq_data.HCC1}. No one in MCC.")
                  elif freq_data["MCC "] + freq_data.HCC1 < 4: # Check if insufficient strength
                        result.append(f"WARNING(INSUFFICIENT STRENGTH): At {row.Time}. MCC:{freq_data['MCC ']}, HCC1:{freq_data.HCC1}")
                  elif (freq_data.HCC1 != 2 or freq_data["MCC "] != 2) and not(st.session_state.ignore_overallocation): # Check if either MCC or HCC1 not exactly 2
                        result.append(f"WARNING(MISALLOCATION): At {row.Time}. MCC:{freq_data['MCC ']}, HCC1:{freq_data.HCC1}")
      elif day == 3:
            for idx,row in df1.iterrows():
                  freq_data = row[2:].value_counts() #get count of MCC
                  if not hasattr(freq_data,"MCC "):
                        result.append(f"WARNING(INSUFFICIENT STRENGTH, NEED 2): AT Day {row.Time}. MCC:0")
                  elif row.Time not in ["06:00:00","06:30:00"] and freq_data['MCC ']< 2:
                        result.append(f"WARNING(INSUFFICIENT STRENGTH, NEED 2): AT Day {row.DAY},{row.Time}. MCC:{freq_data['MCC ']})")
                  elif row.Time in ["06:00:00","06:30:00"] and freq_data['MCC '] < 3:
                        result.append(f"WARNING(INSUFFICIENT STRENGTH, NEED AT LEAST 3): AT Day {row.Time}. MCC:{freq_data['MCC ']})")
      
      return result

day1warnings.text("DAY 1")
day2warnings.text("DAY 2")
day3warnings.text("DAY 3")
st.session_state.ignore_overallocation = validation_options.checkbox(label="ignore overallocation")

if hour_count["DAY 1"].iloc[-1] >= 56:
      warnings = validate_shifts(st.session_state["💀DAY 1: MCC"].data,st.session_state["😴DAY 1: HCC1"].data,day=1)
      if warnings == []:
            day1warnings.write("Shifts validated. No warnings")

      else:
            for w in warnings:
                  day1warnings.write(w)
if hour_count["DAY 2"].iloc[-1] >= 60:
      warnings = validate_shifts(st.session_state["💀DAY 2: MCC"].data,st.session_state["😴DAY 2: HCC1"].data,day=2)

      if warnings == []:
            day2warnings.write("Shifts validated. No warnings")
      
      else:
            for w in warnings:
                  day2warnings.write(w)

if hour_count["DAY 3"].iloc[-1] >=21:
      warnings = validate_shifts(df1=st.session_state["NIGHT DUTY"].data,df2=None,day=3)

      if warnings == []:
            day3warnings.write("Shifts validated. No warnings")
      
      else:
            for w in warnings:
                  day3warnings.write(w)
