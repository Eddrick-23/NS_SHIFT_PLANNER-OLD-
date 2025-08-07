import streamlit as st
from database import database as database
import pandas as pd
from st_btn_group import st_btn_group
import zipfile
import io
import os


st.set_page_config(page_title="Shift Planner",
                   page_icon=":military_helmet:", layout="wide")
st.title("[Shift Planner](%s)" %
         "https://github.com/Eddrick-23/NS_SHIFT_PLANNER#ns-shift-planner")

if "has_read_popup" not in st.session_state:
    st.session_state.has_read_popup = 0


@st.dialog("READ ME")
def readme():
    st.subheader("This project has been revamped at https://www.app.nsplanner.com/")
    st.subheader("Future support will be continued only for the new project, you may continue using this app, but it will not be updated.")
    st.subheader("Please **save** your work if you are going afk for at least 5-7 mins. The app WILL go to sleep and you will lose your progress. \n Sorry I'm too broke to pay for a database to autosave your work :/")
    st.write(
        "Click on the **[download zip]** button to save your work as a zip file")
    st.write("**Upload** the zip file to continue your work")

    st.write("Clicking the 'SHIFT PLANNER' title brings you to a readme")
    if st.button("Okay", use_container_width=True):
        st.session_state.has_read_popup = True
        st.rerun()


if not st.session_state.has_read_popup:
    readme()

if "has_rerun_on_upload" not in st.session_state:  # used when uploading zip file to app
    st.session_state.has_rerun_on_upload = None

if "undo_stack" not in st.session_state:  # track functions to undo
    # ("function name", parameter(s)) ->> if multiple parameters, will be stored in dictionary
    st.session_state.undo_stack = []
if "redo_stack" not in st.session_state:  # track functions to redo
    st.session_state.redo_stack = []

# load the database names

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
    st.session_state["💀DAY 1: MCC"] = database(location="MCC ", day=1)
if "😴DAY 1: HCC1" not in st.session_state:
    st.session_state["😴DAY 1: HCC1"] = database(location="HCC1", day=1)
if "💀DAY 2: MCC" not in st.session_state:
    st.session_state["💀DAY 2: MCC"] = database(location="MCC ", day=2)
if "😴DAY 2: HCC1" not in st.session_state:
    st.session_state["😴DAY 2: HCC1"] = database(location="HCC1", day=2)
if "NIGHT DUTY" not in st.session_state:
    st.session_state["NIGHT DUTY"] = database(location="MCC ", day=3)

if "D1Names" not in st.session_state:
    st.session_state.D1Names = set()
if "D2Names" not in st.session_state:
    st.session_state.D2Names = set()
if "D3Names" not in st.session_state:
    st.session_state.D3Names = set()

# session state to check last updated day, days that are not updated will used cached results from format_keys()
if "last_updated_day" not in st.session_state:
    # 4 default, rerun formatting for all days, else rerun for specified day, 0 no need rerun formatting, used cached results
    st.session_state.last_updated_day = 4


def update_LUD(active_database=None, custom=None):
    if custom is not None:
        st.session_state.last_updated_day = custom
        return
    match st.session_state[active_database].day:
        case 1:
            st.session_state.last_updated_day = 1
        case 2:
            st.session_state.last_updated_day = 2
        case 3:
            st.session_state.last_updated_day = 3
        case _:
            print("No matching database")


if "name_pool" not in st.session_state:
    st.session_state.name_pool = set()


def add_to_name_pool(name):
    n = name.strip().upper()

    if n == "HCC1" or n == "MCC":  # Invalid name as control centre location
        expander.warning("Invalid name!", icon=":material/error:")
        return
    if n in st.session_state.name_pool:
        expander.warning(f"{n} already exists!", icon=":material/error:")
        return
    st.session_state.name_pool.add(n)
    expander.success(f"Added {n}!")


def remove_from_name_pool(name_list):
    for n in name_list:
        st.session_state.name_pool.remove(n)
    expander.success(f"Removed {name_list}!")


expander = st.sidebar.expander("Name pool")
if st.session_state.name_pool == set():
    expander.subheader("All current names: None")
else:
    name_df = pd.DataFrame(data=st.session_state.name_pool, columns=["Names"])
    expander.subheader("All current names:")
    expander.dataframe(name_df, hide_index=True, use_container_width=True)
adding, removing = expander.columns(2)

name_add_to_pool = adding.text_input("Add name")
name_remove_from_pool = removing.multiselect(
    "Remove name(s)", options=st.session_state.name_pool)


add_pool_button = adding.button("Add name", on_click=add_to_name_pool, kwargs={
                                "name": name_add_to_pool}, use_container_width=True)

remove_pool_button = removing.button("Remove name(s)", on_click=remove_from_name_pool, kwargs={
                                     "name_list": name_remove_from_pool}, use_container_width=True)


def add_name(name, update_stacks="default", db=None, shifts=[], hours=0, restore=None):

    active_db = st.session_state.db_to_update
    if db is not None:
        active_db = db

    day = st.session_state[active_db].day

    update_LUD(active_db)
    parameters = {}  # {name: {data:d,hours:h},...}
    if restore is None:
        for n in name:
            st.session_state[active_db].add_name(
                name=n, shifts=shifts, hours=hours)
            st.session_state[f"D{day}Names"].add(n)
            parameters[n] = {"db": active_db, "shifts": shifts, "hours": hours}
    else:  # we pass in custom data to restore from undo/redo call
        for n in restore.keys():
            st.session_state[active_db].add_name(
                name=n, shifts=restore[n]["data"], hours=restore[n]["hours"])
            st.session_state[f"D{day}Names"].add(n)
            parameters[n] = {"db": active_db, "shifts": shifts, "hours": hours}

    if update_stacks in ["undo", "default"]:
        st.session_state.undo_stack.append(("add_name", parameters))
        if update_stacks == "default":
            st.session_state.redo_stack = []  # reset redo stack on new user input
    elif update_stacks == "redo":
        st.session_state.redo_stack.append(
            ("remove_name", {"db": active_db, "name": list(parameters.keys())}))


def remove_name(name_list, update_stacks="default", db=None):
    active_db = st.session_state.db_to_update
    if db is not None:
        active_db = db

    update_LUD(active_db)

    day = st.session_state[active_db].day
    parameters = {}  # {name: {data:d,hours:h},...}
    for n in name_list:
        parameters[n] = st.session_state[active_db].remove_name(n)
        st.session_state[f"D{day}Names"].remove(n)
        st.toast(f"{n} removed from {active_db}",
                 icon=":material/check_circle:")

    if update_stacks in ["undo", "default"]:
        st.session_state.undo_stack.append(
            ("remove_name", {"db": active_db, "params": parameters}))
        if update_stacks == "default":
            st.session_state.redo_stack = []  # reset redo_stack on new user input
    elif update_stacks == "redo":
        st.session_state.redo_stack.append(
            ("add_name", {"db": active_db, "params": parameters}))


# sidebar
st.session_state.db_to_update = st.sidebar.radio("Database", options=[
                                                 "💀DAY 1: MCC", "😴DAY 1: HCC1", "💀DAY 2: MCC", "😴DAY 2: HCC1", "NIGHT DUTY"], key="sidebaractivedb", horizontal=True)

sidebar_col11, sidebar_col12 = st.sidebar.columns(2)


def generate_options():
    '''
          returns a set of names that can be added to a specific database
    '''

    day_num = st.session_state[st.session_state.db_to_update].day

    # get all available names in that day
    names_in_day = st.session_state[f"D{day_num}Names"]

    # get all names in current database
    names_in_db = st.session_state[st.session_state.db_to_update].get_names()

    # return the set of names that can be added
    return st.session_state.name_pool - names_in_day.union(names_in_db)


name = sidebar_col11.multiselect(
    "Choose names to add", options=generate_options())
if sidebar_col11.button("Submit", use_container_width=True):
    add_name(name)
name_list = sidebar_col12.multiselect(
    label="Choose names to remove", options=st.session_state[st.session_state.db_to_update].get_names())
if sidebar_col12.button("Remove", use_container_width=True):
    remove_name(name_list)
st.sidebar.divider()


def rename_all(new_name, old_name, update_stacks="default"):

    # redraw all as we update names across multiple databases
    st.session_state.last_updated_day = 4

    new_name = new_name.strip().upper()
    if new_name in set().union(st.session_state.D1Names, st.session_state.D2Names, st.session_state.D3Names):
        st.toast(f"{new_name} already exists!", icon=":material/warning:")
        return
    # update the Name Pool
    st.session_state.name_pool.remove(old_name)
    st.session_state.name_pool.add(new_name)

    # update the day name session states
    for d in ["D1Names", "D2Names", "D3Names"]:
        if old_name in st.session_state[d]:
            st.session_state[d].remove(old_name)
            st.session_state[d].add(new_name)
    # update individual databases
    for db in ["💀DAY 1: MCC", "😴DAY 1: HCC1", "💀DAY 2: MCC", "😴DAY 2: HCC1", "NIGHT DUTY"]:
        if old_name in st.session_state[db].get_names():
            st.session_state[db].rename(new_name, old_name)

    # update call stack
    if update_stacks in ["undo", "default"]:
        st.session_state.undo_stack.append(
            ("rename_all", {"new_name": new_name, "old_name": old_name}))
        if update_stacks == "default":
            st.session_state.redo_stack = []
    elif update_stacks == 'redo':
        st.session_state.redo_stack.append(
            ("rename_all", {"new_name": new_name, "old_name": old_name}))

    st.toast(f"Renamed {old_name} to {new_name}",
             icon=":material/check_circle:")


st.sidebar.text("Rename")  # rename a name across all databases
new_name = st.sidebar.text_input("Enter New Name:")
old_name = st.sidebar.selectbox(label="Old name", options=set().union(
    st.session_state.D1Names, st.session_state.D2Names, st.session_state.D3Names))
st.sidebar.button(label="Rename", on_click=rename_all, kwargs={
                  "new_name": new_name, "old_name": old_name}, use_container_width=True)

st.sidebar.divider()


def name_in_same_database(names, database):
    db_names = database.get_names()
    if names[0] in db_names and names[1] in db_names:
        return True  # returns True if both names in current database
    else:  # returns the name that is not in the database
        for n in names:
            if n not in db_names:
                return n


def swap_names(names, day_for_swapping=None, update_stacks="default"):
    # redraw all as we can swap names across databases
    st.session_state.last_updated_day = 4
    day = st.session_state.day_for_swapping
    if day_for_swapping is not None:
        day = day_for_swapping
    if day == 3:
        st.session_state["NIGHT DUTY"].swap_names(names[0], names[1])
    else:
        mcc_db = st.session_state[f"💀DAY {day}: MCC"]
        hcc1_db = st.session_state[f"😴DAY {day}: HCC1"]

        mcc_check = name_in_same_database(names, database=mcc_db)
        hcc1_check = name_in_same_database(names, database=hcc1_db)
        # case 1 both names in mcc_db
        if mcc_check == True:
            mcc_db.swap_names(names[0], names[1])
        # case 2 both names in hcc1_db
        elif hcc1_check == True:
            hcc1_db.swap_names(names[0], names[1])
        # case 3 both names in different database
        else:
            mcc_db.rename(new_name=mcc_check, old_name=hcc1_check)
            hcc1_db.rename(new_name=hcc1_check, old_name=mcc_check)

    if update_stacks in ["default", "undo"]:
        st.session_state.undo_stack.append(
            ("swap_names", {"day_for_swapping": day, "names": names}))
        if update_stacks == "default":
            st.session_state.redo_stack = []  # reset redo stack on new user input
    elif update_stacks == "redo":
        st.session_state.redo_stack.append(
            ("swap_names", {"day_for_swapping": day, "names": names}))


st.sidebar.write("Swap names")

st.session_state.day_for_swapping = st.sidebar.radio(
    label="DAY", options=[1, 2, 3], horizontal=True)
st.session_state.names_to_swap = st.sidebar.multiselect(
    label="Choose 2 names", options=st.session_state[f"D{st.session_state.day_for_swapping}Names"], max_selections=2)

if len(st.session_state.names_to_swap) == 2:
    st.sidebar.button(label="Swap", on_click=swap_names, kwargs={
                      "names": st.session_state.names_to_swap}, use_container_width=True)
st.sidebar.divider()

st.session_state.d2start07 = st.sidebar.toggle(
    "Day 2 starts at 0700", on_change=update_LUD, kwargs={"custom": 2})
st.session_state.check_lunch_dinner = not st.sidebar.toggle(
    "Disable Lunch & Dinner Check", value=False, on_change=update_LUD, kwargs={"custom": 4})
st.session_state.hided1_grid = st.sidebar.toggle(
    "Hide DAY 1 grid", on_change=update_LUD, kwargs={"custom": 1})
st.session_state.hided2_grid = st.sidebar.toggle(
    "Hide DAY 2 grid", on_change=update_LUD, kwargs={"custom": 2})
st.session_state.hided3_grid = st.sidebar.toggle(
    "Hide DAY 3 grid", on_change=update_LUD, kwargs={"custom": 3})

# back to main page

col1, col2 = st.columns(2)

with col1:
    st.session_state.active_database = st.radio(label="Database", options=[
                                                "💀DAY 1: MCC", "😴DAY 1: HCC1", "💀DAY 2: MCC", "😴DAY 2: HCC1", "NIGHT DUTY"], horizontal=True)
    st.session_state.active_name = st.multiselect(
        label="Name(s)", options=st.session_state[st.session_state.active_database].get_names())
with col2:
    st.session_state.active_allocation_size = st_btn_group(mode="radio", buttons=[{"label": "First 30 min", "value": "001"}, {"label": "Full", "value": "002"}, {
                                                           "label": "Last 30 min", "value": "30"}], key="allocation_size", merge_buttons=True, size="compact", radio_default_index=1)
    st.session_state.active_location = st.radio(label="Location", options=[
                                                "MCC ", "HCC1"])  # whitespace after MCC for standard cell size
# button groups


def allocate_shift(n, hour, allocation_size, db, loc):  # call back function for buttons
    # set up appropriate timeblock to query
    # actual time block e.g if left half @1200 > 1200/ right half > 1230
    main_time_block = hour + ":00:00"
    # other half if left half @1200, other half = 1230 etc.
    other_time_block = hour + ":30:00"
    if allocation_size[0] == "30":
        main_time_block, other_time_block = other_time_block, main_time_block  # swap
    # check first if shift is allocated
    allocation_state1 = st.session_state[db].is_shift_allocated(
        time_block=main_time_block, name=n)
    allocation_state2 = None
    first_half_loc = st.session_state[db].get_shift_location(
        time_block=main_time_block, name=n)
    if allocation_size[0] == "002":  # for full time block allocation
        allocation_state2 = st.session_state[db].is_shift_allocated(
            other_time_block, name=n)
        second_half_loc = st.session_state[db].get_shift_location(
            time_block=other_time_block, name=n)

        # check for custom time block removal/allocation from undo/redo call stack
        if allocation_size[1] == 1:
            st.session_state[db].add_shift(
                location=allocation_size[2], time_block=main_time_block, name=n)
            st.session_state[db].add_shift(
                location=allocation_size[3], time_block=other_time_block, name=n)

            # to store in redo stack the previous state
            return n, 1, first_half_loc, second_half_loc
        else:
            pass

        allocate_both = [allocation_state1, allocation_state2]
        both_same_loc = first_half_loc == second_half_loc

        # if both allocated, and both same location, deallocate to both
        if all(allocate_both) and both_same_loc:
            st.session_state[db].remove_shift(
                time_block=main_time_block, name=n)
            st.session_state[db].remove_shift(
                time_block=other_time_block, name=n)
            return n, 1, first_half_loc, second_half_loc

        # if at least on half not allocated, allocated to both using same current location (previous location overriden)
        else:
            allocation_portion = [False, False]

            # first half not allocated, or first half different location
            if (not allocate_both[0]) or (first_half_loc != loc):
                st.session_state[db].add_shift(
                    location=loc, time_block=main_time_block, name=n)
                allocation_portion[0] = True
            if (not allocate_both[1]) or (second_half_loc != loc):
                st.session_state[db].add_shift(
                    location=loc, time_block=other_time_block, name=n)
                allocation_portion[1] = True

            # return state to store in call_stack
            return n, 1, first_half_loc, second_half_loc

    else:  # for half time block allocation
        if allocation_size[1] == 1:
            # set custom location if function call is from undo/redo
            loc = allocation_size[2]

        if not allocation_state1:  # if shift not allocated, allocate shift
            st.session_state[db].add_shift(
                location=loc, time_block=main_time_block, name=n)
        else:
            st.session_state[db].remove_shift(
                time_block=main_time_block, name=n)

        return n, 1, first_half_loc, 0


def allocate_all(hour, a_size, names=st.session_state.active_name, db=None, loc=None, update_stacks="default", custom_allocation=None):
    # [a_size, int, location1,location2] last 3 variables are for full shift allocation tracking
    allocation_size = {}
    active_database = st.session_state.active_database
    active_location = st.session_state.active_location

    if db is not None:
        active_database = db

    update_LUD(active_database=active_database)

    if loc is not None:
        active_location = loc
    if custom_allocation is not None:
        # in case we pass in custom dict with specific allocation for each person
        allocation_size = custom_allocation
    else:
        for n in names:
            allocation_size[n] = a_size  # convert to dict format
    allocation_size_tracker = {}
    for n in names:
        name, i, first_loc, second_loc = allocate_shift(
            n, hour, allocation_size=allocation_size[n], db=active_database, loc=active_location)
        allocation_size_tracker[name] = [
            allocation_size[name][0], i, first_loc, second_loc]  # update dictionary
    if update_stacks in ["undo", "default"]:
        st.session_state.undo_stack.append(("allocate_all", {"db": active_database, "hour": hour, "names": names,
                                           "a_size": a_size, "loc": active_location, "allocation_size_tracker": allocation_size_tracker}))
        if update_stacks == "default":
            st.session_state.redo_stack = []  # reset redo stack
    elif update_stacks == "redo":
        st.session_state.redo_stack.append(("allocate_all", {"db": active_database, "hour": hour, "names": names,
                                           "a_size": a_size, "loc": active_location, "allocation_size_tracker": allocation_size_tracker}))


def create_button_group():
    # set the time ranges first
    default_day_range = ["06", "07", "08", "09", "10", "11",
                         "12", "13", "14", "15", "16", "17", "18", "19", "20"]
    if st.session_state.active_database == "NIGHT DUTY":
        default_day_range = ["21", "22", "23", "00",
                             "01", "02", "03", "04", "05", "06"]
    time_range = ["06", "07", "08", "09", "10", "11", "12",
                  "13", "14", "15", "16", "17", "18", "19", "20"]
    # if day 1, remove 0600
    if st.session_state.active_database in ["💀DAY 1: MCC", "😴DAY 1: HCC1"]:
        default_day_range.pop(0)
    if st.session_state.active_allocation_size in ["001", "002"]:
        time_range = [item + "00" for item in default_day_range]

    elif st.session_state.active_allocation_size in ["30"]:
        time_range = [item + "30" for item in default_day_range]

    # create the buttons:
    n_buttons = len(time_range)
    cols = st.columns(n_buttons)
    for n in range(n_buttons):
        with cols[n]:
            st.button(label=time_range[n], use_container_width=True, on_click=allocate_all, kwargs={"hour": time_range[n][:2], "a_size": [
                      st.session_state.active_allocation_size, 0]}, disabled=st.session_state.active_name == [])


create_button_group()


# displaying dataframes
def format_keys(df1, df2):
    '''
        df1(pandas dataframe)
        df2(pandas dataframe)

        dataframes should have the same format. Merging the dataframes will just join the names.
        The "DAY" and "Time" Columns should be the same.

        This function reads two dataframes and returns formatted timeblocks that fit both dataframes. Such that they are always aligned.
    '''
    keys = []
    joined = []
    # iterate over df two rows at a time
    # we join the time slots only if
    # 1) no slots allocated at all in that 1h block
    # 2) slots are allocated to the same person in that 1h block
    joined_df = df1
    if df2 is not None:
        joined_df = df1.merge(df2)
    for i in range(0, len(joined_df), 2):
        # get two rows at a time
        rows = joined_df.iloc[i:i+2]
        join_blocks = True
        for c in rows.columns[2:]:
            v1, v2 = rows[c].iloc[0], rows[c].iloc[1]

            if v1 != v2:
                join_blocks = False
                break
        keys.append(rows.Time.iloc[0][:-3])  # slice string for HH:MM format
        if join_blocks:
            joined.append(True)
        if not join_blocks:
            # slice string for HH:MM format
            keys.append(rows.Time.iloc[1][:-3])
            joined.append(False)

    return (keys, joined)


# session states which cache the formatted dataframes
if "d1MCC_df" not in st.session_state:
    st.session_state.d1MCC_df = None
if "d1HCC1_df" not in st.session_state:
    st.session_state.d1HCC1_df = None
if "d2MCC_df" not in st.session_state:
    st.session_state.d2MCC_df = None
if "d2HCC1_df" not in st.session_state:
    st.session_state.d2HCC1_df = None
if "nightduty_df" not in st.session_state:
    st.session_state.nightduty_df = None


def displayd1_grid():
    if not st.session_state.hided1_grid:
        # if day updated, redraw dataframes, and update the cache
        if st.session_state.last_updated_day in [1, 4]:
            k, j = format_keys(
                st.session_state["💀DAY 1: MCC"].data, st.session_state["😴DAY 1: HCC1"].data)
            st.session_state.d1MCC_df = st.session_state["💀DAY 1: MCC"].generate_formatted_df(
                keys=k, joined=j, check_lunch_dinner=st.session_state.check_lunch_dinner)
            st.session_state.d1HCC1_df = st.session_state["😴DAY 1: HCC1"].generate_formatted_df(
                keys=k, joined=j, check_lunch_dinner=st.session_state.check_lunch_dinner)

        with st.container():
            st.data_editor(st.session_state.d1MCC_df, hide_index=True,
                           use_container_width=True, disabled=True)
            st.data_editor(st.session_state.d1HCC1_df, hide_index=True,
                           use_container_width=True, disabled=True)


displayd1_grid()


def displayd2_grid():
    if not st.session_state.hided2_grid:
        if st.session_state.last_updated_day in [2, 4]:
            k, j = format_keys(
                st.session_state["💀DAY 2: MCC"].data, st.session_state["😴DAY 2: HCC1"].data)
            st.session_state.d2MCC_df = st.session_state["💀DAY 2: MCC"].generate_formatted_df(
                keys=k, joined=j, check_lunch_dinner=st.session_state.check_lunch_dinner)
            st.session_state.d2HCC1_df = st.session_state["😴DAY 2: HCC1"].generate_formatted_df(
                keys=k, joined=j, check_lunch_dinner=st.session_state.check_lunch_dinner)
        with st.container():
            if st.session_state.d2start07:
                # check if 0600 block is empty or all unfilled
                mcc_0600 = st.session_state.d2MCC_df.data["06:00"].empty or (
                    st.session_state.d2MCC_df.data["06:00"] == "0   ").all()
                hcc1_0600 = st.session_state.d2HCC1_df.data["06:00"].empty or (
                    st.session_state.d2HCC1_df.data["06:00"] == "0   ").all()
                if "06:30" in st.session_state.d2MCC_df.data.columns:
                    mcc_0600 = False
                if "06:30" in st.session_state.d2MCC_df.data.columns:
                    hcc1_0600 = False
                if all([mcc_0600, hcc1_0600]):
                    col_order_mcc = st.session_state.d2MCC_df.data.columns.to_list()
                    col_order_mcc.remove("06:00")
                    col_order_hcc1 = st.session_state.d2HCC1_df.data.columns.to_list()
                    col_order_hcc1.remove("06:00")
                    st.data_editor(st.session_state.d2MCC_df, hide_index=True,
                                   use_container_width=True, column_order=col_order_mcc, disabled=True)
                    st.data_editor(st.session_state.d2HCC1_df, hide_index=True,
                                   use_container_width=True, column_order=col_order_hcc1, disabled=True)
                    return

            st.data_editor(st.session_state.d2MCC_df, hide_index=True,
                           use_container_width=True, disabled=True)
            st.data_editor(st.session_state.d2HCC1_df, hide_index=True,
                           use_container_width=True, disabled=True)


displayd2_grid()

bottom_col1, bottom_col2 = st.columns([0.2, 0.8])


def displayd3_grid():
    if not st.session_state.hided3_grid:
        if st.session_state.last_updated_day in [3, 4]:
            k, j = format_keys(st.session_state["NIGHT DUTY"].data, None)
            st.session_state.nightduty_df = st.session_state["NIGHT DUTY"].generate_formatted_df(
                keys=k, joined=j)
        with st.empty():
            bottom_col2.data_editor(st.session_state.nightduty_df,
                                    hide_index=True, use_container_width=True, disabled=True)


displayd3_grid()


# hour counter
def display_hours():
    hours = {}
    d1MCC = st.session_state["💀DAY 1: MCC"].hours
    d1HCC1 = st.session_state["😴DAY 1: HCC1"].hours
    d2MCC = st.session_state["💀DAY 2: MCC"].hours
    d2HCC1 = st.session_state["😴DAY 2: HCC1"].hours
    nightduty = st.session_state["NIGHT DUTY"].hours

    for key, val in d1MCC.items():
        if key not in hours:
            hours[key] = [0, 0, 0]
        hours[key][0] = val

    for key, val in d1HCC1.items():
        if key not in hours:
            hours[key] = [0, 0, 0]
        hours[key][0] = val

    for key, val in d2MCC.items():
        if key not in hours:
            hours[key] = [0, 0, 0]
        hours[key][1] = val
    for key, val in d2HCC1.items():
        if key not in hours:
            hours[key] = [0, 0, 0]
        hours[key][1] = val
    for key, val in nightduty.items():
        if key not in hours:
            hours[key] = [0, 0, 0]
        hours[key][2] = val

    for key, val in hours.items():
        val.append(sum(val))

    df = pd.DataFrame(data=hours, index=["DAY 1", "DAY 2", "DAY 3", "TOTAL"]).T
    df = df.sort_values(by=["TOTAL"], ascending=False)
    # add whitespace so this row will always be either first or last in sorting
    df.loc[" TOTAL  "] = df.sum()

    return df


hour_count = display_hours()
st.session_state.hour_count_on_sidebar = st.sidebar.toggle(
    label="Display hour count on sidebar", value=True)
if st.session_state.hour_count_on_sidebar:
    st.sidebar.dataframe(hour_count, use_container_width=True,
                         height=(len(hour_count)+1)*35 + 3)
    bottom_col1.header("NIGHT DUTY")
else:
    bottom_col1.dataframe(hour_count, use_container_width=True)
st.sidebar.divider()
# uploading and downloading files

# Function to extract and read CSV files from the zip archive


def extract_and_read_csv(zip_file):
    # Create a temporary directory to extract files to
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall("extracted_files")

    # List the CSV files in the extracted folder
    csv_files = [f for f in os.listdir(
        "extracted_files") if f.endswith('.csv')]

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


def create_zip():
    # takes all dataframes from each database, convert to csv, store as zip file

    buf = io.BytesIO()
    # set the mode parameter to x to create and write a new file
    with zipfile.ZipFile(buf, "x") as myzip:
        # convert df to .csv and name it
        myzip.writestr(
            "DAY1MCC.csv", st.session_state["💀DAY 1: MCC"].data.to_csv())
        myzip.writestr(
            "DAY1HCC1.csv", st.session_state["😴DAY 1: HCC1"].data.to_csv())
        myzip.writestr(
            "DAY2MCC.csv", st.session_state["💀DAY 2: MCC"].data.to_csv())
        myzip.writestr(
            "DAY2HCC1.csv", st.session_state["😴DAY 2: HCC1"].data.to_csv())
        myzip.writestr("NIGHTDUTY.csv",
                       st.session_state["NIGHT DUTY"].data.to_csv())

    return buf


st.sidebar.download_button(label="Download zip", data=create_zip().getvalue(
), file_name="Planning.zip", mime="data/zip", use_container_width=True)
st.session_state.zip_file = st.sidebar.file_uploader(
    label="Upload zip of saved work", type="zip")

if st.session_state.zip_file is not None and not st.session_state.has_rerun_on_upload:
    # Convert uploaded file to BytesIO object
    zip_file_bytes = io.BytesIO(st.session_state.zip_file.read())

    # Extract and read CSV files into DataFrames
    dataframes = extract_and_read_csv(zip_file_bytes)

    # Display the DataFrames
    st.session_state["💀DAY 1: MCC"].set_data(
        dataframes["DAY1MCC.csv"].drop('Unnamed: 0', axis=1).replace(0, "0   "))
    st.session_state.namesd1MCC = st.session_state["💀DAY 1: MCC"].names
    st.session_state["💀DAY 2: MCC"].set_data(
        dataframes["DAY2MCC.csv"].drop('Unnamed: 0', axis=1).replace(0, "0   "))
    st.session_state.namesd2MCC = st.session_state["💀DAY 2: MCC"].names
    st.session_state["😴DAY 1: HCC1"].set_data(
        dataframes["DAY1HCC1.csv"].drop('Unnamed: 0', axis=1).replace(0, "0   "))
    st.session_state.namesd1HCC1 = st.session_state["😴DAY 1: HCC1"].names
    st.session_state["😴DAY 2: HCC1"].set_data(
        dataframes["DAY2HCC1.csv"].drop('Unnamed: 0', axis=1).replace(0, "0   "))
    st.session_state.namesd2HCC1 = st.session_state["😴DAY 2: HCC1"].names
    st.session_state["NIGHT DUTY"].set_data(
        dataframes["NIGHTDUTY.csv"].drop('Unnamed: 0', axis=1).replace(0, "0   "))
    st.session_state.namesd3 = st.session_state["NIGHT DUTY"].names
    st.session_state.D1Names = st.session_state.namesd1MCC.union(
        st.session_state.namesd1HCC1)
    st.session_state.D2Names = st.session_state.namesd2MCC.union(
        st.session_state.namesd2HCC1)
    st.session_state.D3Names = st.session_state.namesd3.copy()
    st.session_state.name_pool = (st.session_state.D1Names.union(
        st.session_state.D2Names)).union(st.session_state.D3Names)
    st.session_state.has_rerun_on_upload = True
    st.session_state.last_updated_day = 4
    st.rerun()


# UNDO AND REDO
def execute_undo():
    if st.session_state.undo_stack == []:  # in case of double button click causing call on empty list
        return
    action = st.session_state.undo_stack.pop()  # pop last executed function

    if action[0] == "add_name":  # we remove name
        parameters = action[1]
        for n in parameters.keys():
            remove_name(name_list=list(parameters.keys()),
                        update_stacks="redo", db=parameters[n]["db"])
            return  # only need to call once since all names are removed from same db
    elif action[0] == "remove_name":  # we add name
        parameters = action[1]["params"]
        # for n in parameters.keys():
        #       add_name(name=[n],update_stacks="redo", db=action[1]['db'],hours=parameters[n]["hours"],shifts = parameters[n]["data"])

        add_name(name=list(parameters.keys()), update_stacks="redo",
                 db=action[1]["db"], restore=parameters)

    elif action[0] == "rename_all":  # reverse renaming process
        parameters = action[1]
        rename_all(new_name=parameters["old_name"],
                   old_name=parameters["new_name"], update_stacks="redo")

    elif action[0] == "allocate_all":
        parameters = action[1]
        allocate_all(hour=parameters["hour"], names=parameters["names"], db=parameters["db"], a_size=parameters["a_size"],
                     loc=parameters["loc"], update_stacks="redo", custom_allocation=parameters["allocation_size_tracker"])

    elif action[0] == "swap_names":
        parameters = action[1]
        swap_names(
            names=parameters["names"], day_for_swapping=parameters["day_for_swapping"], update_stacks="redo")


def execute_redo():
    if st.session_state.redo_stack == []:  # incase off double button click causing call on empty list
        return
    action = st.session_state.redo_stack.pop()

    if action[0] == "add_name":
        parameters = action[1]['params']
        # for n in parameters.keys():
        #       add_name(name=[n],update_stacks="undo", db=action[1]['db'],hours=parameters[n]["hours"],shifts = parameters[n]["data"])
        add_name(name=None, db=action[1]["db"],
                 restore=parameters, update_stacks="undo")
    if action[0] == "remove_name":
        parameters = action[1]
        remove_name(name_list=parameters["name"],
                    update_stacks="undo", db=parameters["db"])
    elif action[0] == "rename_all":  # reverse renaming process
        parameters = action[1]
        rename_all(new_name=parameters["old_name"],
                   old_name=parameters["new_name"], update_stacks="undo")
    elif action[0] == "allocate_all":
        parameters = action[1]
        allocate_all(hour=parameters["hour"], names=parameters["names"], db=parameters["db"], a_size=parameters["a_size"],
                     loc=parameters["loc"], update_stacks="undo", custom_allocation=parameters["allocation_size_tracker"])

    elif action[0] == "swap_names":
        parameters = action[1]
        swap_names(
            names=parameters["names"], day_for_swapping=parameters["day_for_swapping"], update_stacks="undo")


undo_col, redo_col = st.sidebar.columns(2)
undo_col.button("UNDO", use_container_width=True,
                on_click=execute_undo, disabled=st.session_state.undo_stack == [])
redo_col.button("REDO", use_container_width=True,
                on_click=execute_redo, disabled=st.session_state.redo_stack == [])

# shift validation
day1warnings, day2warnings, day3warnings, validation_options = st.columns(
    (.3, .3, .3, .1))


def validate_shifts(df1, df2, day):
    '''
    Method checks that approriate strength is allocated to control centres for mounting hours
    Best to call when hours are all allocated as computation is resource heavy
    '''
    result = []
    if day == 1 or day == 2:
        joined_df = df1.merge(df2)

        for idx, row in joined_df.iterrows():
            freq_data = row[2:].value_counts()  # get count of MCC and HCC1

            if "HCC1" not in row.values and "MCC " not in row.values:
                result.append(
                    f"WARNING(INSUFFICIENT STRENGTH):At {row.Time}. No one in both control centres.")
            elif "HCC1" not in row.values:  # Check if no one in HCC1
                result.append(
                    f"WARNING(MISALLOCATION): At {row.Time}. MCC:{freq_data.MCC}. No one in HCC1.")
            elif "MCC " not in row.values:  # Check if no one in MCC
                result.append(
                    f"WARNING(MISALLOCATION): At {row.Time}. HCC1:{freq_data.HCC1}. No one in MCC.")
            elif freq_data["MCC "] + freq_data.HCC1 < 4:  # Check if insufficient strength
                result.append(
                    f"WARNING(INSUFFICIENT STRENGTH): At {row.Time}. MCC:{freq_data['MCC ']}, HCC1:{freq_data.HCC1}")
            # Check if either MCC or HCC1 not exactly 2
            elif (freq_data.HCC1 != 2 or freq_data["MCC "] != 2) and not (st.session_state.ignore_overallocation):
                result.append(
                    f"WARNING(MISALLOCATION): At {row.Time}. MCC:{freq_data['MCC ']}, HCC1:{freq_data.HCC1}")
    elif day == 3:
        for idx, row in df1.iterrows():
            freq_data = row[2:].value_counts()  # get count of MCC
            if not hasattr(freq_data, "MCC "):
                result.append(
                    f"WARNING(INSUFFICIENT STRENGTH, NEED 2): AT Day {row.Time}. MCC:0")
            elif row.Time not in ["06:00:00", "06:30:00"] and freq_data['MCC '] < 2:
                result.append(
                    f"WARNING(INSUFFICIENT STRENGTH, NEED 2): AT Day {row.DAY},{row.Time}. MCC:{freq_data['MCC ']})")
            elif row.Time in ["06:00:00", "06:30:00"] and freq_data['MCC '] < 3:
                result.append(
                    f"WARNING(INSUFFICIENT STRENGTH, NEED AT LEAST 3): AT Day {row.Time}. MCC:{freq_data['MCC ']})")

    return result


day1warnings.text("DAY 1")
day2warnings.text("DAY 2")
day3warnings.text("DAY 3")
st.session_state.ignore_overallocation = validation_options.checkbox(
    label="ignore overallocation")

if hour_count["DAY 1"].iloc[-1] >= 56:
    warnings = validate_shifts(
        st.session_state["💀DAY 1: MCC"].data, st.session_state["😴DAY 1: HCC1"].data, day=1)
    if warnings == []:
        day1warnings.write("Shifts validated. No warnings")

    else:
        for w in warnings:
            day1warnings.write(w)
if hour_count["DAY 2"].iloc[-1] >= 60:
    warnings = validate_shifts(
        st.session_state["💀DAY 2: MCC"].data, st.session_state["😴DAY 2: HCC1"].data, day=2)

    if warnings == []:
        day2warnings.write("Shifts validated. No warnings")

    else:
        for w in warnings:
            day2warnings.write(w)

if hour_count["DAY 3"].iloc[-1] >= 21:
    warnings = validate_shifts(
        df1=st.session_state["NIGHT DUTY"].data, df2=None, day=3)

    if warnings == []:
        day3warnings.write("Shifts validated. No warnings")

    else:
        for w in warnings:
            day3warnings.write(w)
