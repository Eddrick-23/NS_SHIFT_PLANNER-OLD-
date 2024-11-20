# [NS SHIFT PLANNER](https://nsplanner.streamlit.app/)

## Updates
Update 0.1 (13/11/24)
- Replaced name selection for shift allocation to be a multi select widget
- Users can now allocate shifts to more than one person at a time
- Fixed minor exception handling during app running process

Update 0.2 (19/11/24)
- Added feature to rename a name across all databases
- Added feature to swap names within databases on the same day
- Added option to move hour count grid to the sidebar
- Hour count grid now displays in descending order by total hours, by defualt

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
### Saving your work
- Click the **Download Zip** button on the bottom of the sidebar.
- You will download a zip file called "Planning.zip"
### Resuming saved work
- Click the  **browse files** button on the bottom of the sidebar.
- Upload the saved zipfile and continue editing.
