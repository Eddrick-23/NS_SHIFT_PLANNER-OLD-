# [NS SHIFT PLANNER](https://nsplanner.streamlit.app/)

## Updates
Update 0.1.0 (13/11/24)
- Replaced name selection for shift allocation to be a multi select widget
- Users can now allocate shifts to more than one person at a time
- Fixed minor exception handling during app running process

Update 0.2.0 (19/11/24)
- Added feature to rename a name across all databases
- Added feature to swap names within databases on the same day
- Added option to move hour count grid to the sidebar
- Hour count grid now displays in descending order by total hours, by defualt

Update 0.3.0 (7/12/24)
- Fixed bug where dataframes would appear stretched when the hide toggle is enabled.
- Added option to disable lunch and dinner break checks.

Update 1.0.0 (30/12/24)
- Added undo and redo feature
- Added option to allow shift validation to ignore overallocation(i.e. more than 4 people mounting at once).
- Changed behavior of full shift allocation
    - When either half of the hour is allocated, allocating a full shift will now allocate the full hour.
    - Allocating a full shift when the full hour is allocated will then deallocate the entire hour.
    - Note that the location of the already allocated half will be overriden to the currently set location.
        > **_Example:_**  
        [HCC1][] -(full allocation,location = MCC)-> [MCC][MCC] <br>
        [MCC][MCC] -(full allocation)-> [][]
- Button groups for shift allocation now toggle between disabled and active state. They are only redrawn when a different set of button groups are required.
- Added option for d2 to start at 0700 hrs. Note that the 0600 - 0700 time block will only be hidden when there are no shifts allocated in that time block. (This is for formatting purposes)
- Added name pool to allow adding and removing names from a common name pool. This is so that users only need to type the names once. **Removing names from the name pool however, will not remove the names from the databases(They will still be present on the grid).** Interactions with the name pool will not be tracked by undo/redo.
- Added option to start day 2 on 0700 hours. This will remove the column for 0600 (Only if no shift is allocated from 0600-0700 hrs)
- Added option to disable lunch and dinner checking.

Update 1.1.0 (10/03/25)
- added option for HCC2
- Algorithm checks do not cover HCC2 allocations as they are not always used, and may not be opened for the entire day.
- Algorithm checks now display the number of hours allocated compared to the target number of hours. E.g. 56h for Day 1, 60h for Day2, 21h for Day3. (Does not include HCC2 hours, HCC1 and MCC hours only)

## Notes
- This website is hosted on the free streamlit community cloud server. The app may go to sleep after a couple minutes of inactivity, **any unsaved work will disappear!**
- If you are going away from the computer, please [save](#saving-your-work) your progress. Sorry, I'm just a broke CPL 🫡

## How to use

### Adding names to database
- Activate sidebar
- Select database to update. Type name into input widget
- Only one name can be added to each day. E.g. The same name cannot be added to Day1:MCC and Day1:HCC1 etc.
- **Names are formatted automatically to upper case, and without excess white space**

### Removing names from database
- From the multi select widget above the "remove" button, choose names to remove
- Click remove to remove name from database
- Make sure to select the appropriate database to remove from

### Allocating shift
- Access the main page
- Select the appropriate database from the radio buttons
- Select the name(s) from the database. You may select more than 1.
- **Ensure the appropriate locations are set.** If the location is the same as the database. A green box is shown. If the location is different, the location will be displayed in the corresponding time block also highlighted in green
- Shift sizes are allocated in either 30 min or 1h blocks
    -  First 30 min allocates xx00 - xx30 hrs
    - Last 30 min allocates xx30 to xy00 hrs
    - Full allocates xx00 - xy00 hrs

### Shift Checking algorithms
- Lunch/Dinner break checks
    - If someone is not allocated a lunch or dinner break. The name will be highlighted in <span style="color:red">RED</span>
    - Lunch break: **1130-1330 hrs** Dinner break: **1700-1830 hrs**
    - A person must be have at least a **30 min break** in the respective time periods for their name to not be highlighted
- Shift validation
    - At the bottom of the main page there are 3 columns Day 1, Day 2 and Day 3.
    - The validation activates only when all shifts are allocated I.e. Day 1: 56hrs allocated, Day 2: 60 hrs allocated, Day 3: 21hrs allocated.
    - validation checks that there are 2 people mounting in each control centre at the same time. And also at least 3 people for HOTO @ 0600-0700 on day 3.
- Allowing more than 4 mounting personnel at once
    - clicking the **ignore overallocation** checkbox allows for more than 4 mounting personnel in total (algorithm will not output a warning)
    - This allows for cases where new personnel are shadowing and are not counted as strength.
### Saving your work
- Click the **Download Zip** button on the bottom of the sidebar.
- You will download a zip file called "Planning.zip"
### Resuming saved work
- Click the  **browse files** button on the bottom of the sidebar.
- Upload the saved zipfile and continue editing.
