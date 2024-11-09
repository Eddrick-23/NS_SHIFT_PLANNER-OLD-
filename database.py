import pandas as pd

class database():
    '''
        custom batabase for streamlit front end.
        Database stores allocated shift for each person by day
    '''
    def __init__(self, location,day,use_default=True,data=None):
        '''
            location(str):
                location of mount. Can be MCC or HCC1
            day(int):
                1 or 2. Affects the timeblocks indexing. day 2 starts from 0600 instead of 0700
        '''
        self.names = set() #names in this days data base
        self.location = location
        self.day = day
        self.hours = {} #stores hour data in name:hour format
        if use_default:
            self.load_data()
        else:
            self.data = data
        
    def load_data(self):
        df = pd.read_csv("raw.csv")
        df = df[df["DAY"] == self.day]
        df = df.reset_index(drop=True)
        self.data = df
        
    def set_data(self,data):
        self.data = data
        self.names = set(data.columns[2:].tolist())
        #update the hours

        if len(self.names) == 0:
            pass

        else:
            for c in self.data.columns[2:]: #for each column
                total_hours = 0
                freq = self.data[c].value_counts().to_dict()
                if "MCC " in freq:
                    total_hours += freq["MCC "] * 0.5
                if "HCC1" in freq:
                    total_hours += freq["HCC1"] * 0.5
                
                self.hours[c] = total_hours


    def get_names(self):
        return self.names.copy()
    
    def add_name(self, name):
        '''
            name(str):
                Name will be formatted to upper case

        '''
        upper_name = name.upper()
        self.names.add(upper_name)
        self.data[upper_name] = ["0   "] * len(self.data.index) # each cell is 4 characters long
        self.hours[name] = 0

    def remove_name(self, name):
        '''
            name(str):
                Name will be formatted to upper case
        '''
        upper_name = name.upper()
        self.data.drop(upper_name,axis=1, inplace = True)
        self.names.remove(upper_name)
        del self.hours[name]
    
    def is_shift_allocated(self,time_block, name):
        '''
            time_block(str):
                str in "HH:MM:SS" Format. In 30 min intervals
            
            name(str):
                name of person. Must already exist in column
        '''
        return self.data.loc[(self.data.Time == time_block), name.upper()].iloc[0] != "0   "


    def add_shift(self, location, time_block, name):
        '''
            location(str):
                "MCC" or "HCC1"
            time_block(str):
                str in "HH:MM:SS" Format. In 30 min intervals
            name(str):
                name of person. Must already exist in column
        '''
        if self.day == 3:
            location = "MCC " #default location for night duty

        self.data.loc[(self.data.Time == time_block), name.upper()] = location
        self.hours[name] += 0.5

    def remove_shift(self, time_block,name):
        '''
            time_block(str):
                str in "HH:MM:SS" Format. In 30 min intervals
            name(str):
                name of person. Must already exist in column
        '''
        self.data.loc[(self.data.Time == time_block), name.upper()] = "0   "
        self.hours[name] -= 0.5
    

    def format_keys(self):
        keys = []
        joined = []
        #iterate over df two rows at a time
        # we join the time slots only if 
        #1) no slots allocated at all in that 1h block
        #2) slots are allocated to the same person in that 1h block
        for i in range(0,len(self.data),2):
            #get two rows at a time
            rows = self.data.iloc[i:i+2]
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
    
    def check_lunch_and_dinner(self):
        #checks if someone has no lunch/dinner break.
        #names will be returned in an array

        #lunch  = 1130-1330 >> I.e. cannot start from 1100 and end at 1330 without break
        #dinner = 1700-1830 >> cannot start at 1700 and end at 1830 without break
        result = set() #stores names who don't have breaks
        lunch = self.data[(self.data["Time"] >= "11:00:00") & (self.data["Time"] <= "13:00:00")]
        dinner = self.data[(self.data["Time"] >= "17:00:00") & (self.data["Time"] <= "18:00:00")]
        
        for c in lunch.columns[2:]: #check lunch
            if "0   " not in lunch[c].array:
                result.add(c)
        for c in dinner.columns[2:]: #check dinner
            if c not in result and "0   " not in dinner[c].array:
                result.add(c)
        return result
        
    def highlight_cells(self,s):
        # Create an empty DataFrame to hold the styles
        styles = pd.DataFrame('', index=s.index, columns=s.columns)
        names_to_highlight = None
        if self.day == 1 or self.day == 2:
            names_to_highlight = self.check_lunch_and_dinner()
        
        for col in s.columns:
            for row in range(len(s)):
                if s[col][row] == "MCC " or s[col][row] == "HCC1" :
                    styles.at[row,col] = 'background-color: green;'
                
                elif names_to_highlight != None and s[col][row] in names_to_highlight:
                    styles.at[row,col] = 'background-color: red;'
                else:
                    styles.at[row,col] = 'background-color: white'
        return styles
    def highlight_values(self,val):
        
        if val == self.location:
            return 'color: green'
        elif val == "0   ":
            return 'color: white'
        else:
            return 'color: black'
    def generate_formatted_df(self,keys =None, joined = None):
        #if no formatting given, use class method
        if not (keys and joined):
            keys,joined = self.format_keys() #get formatted keys with joined time blocks
        if self.day == 3: #separate formatting for day3
            #create formatted dataframe
            df = pd.DataFrame(columns=keys)

            #create filtered dataframe containing only the required timeblocks
            formatted_time_list = [f"{time[:5]}:00" for time in keys]
            filtered_df = self.data.loc[self.data.Time.isin(formatted_time_list)]
            filtered_df = filtered_df.set_index(["Time"])
            formatted_dict = filtered_df.apply(lambda row: [col for col in row.index if row[col] == "MCC "], axis=1).to_dict()
            df = pd.DataFrame(dict([(key[:-3], pd.Series(value)) for key, value in formatted_dict.items()]))
            df = df.fillna("0   ")
            styled_df = df.style.apply(self.highlight_cells, axis=None)
            styled_df.map(self.highlight_values)
            return styled_df
        
        formatted_data = {}

        #formatting for day == 1 and day == 2
        for c in self.data.columns[2:]:
            formatted_data[c] = []
        for c in self.data.columns[2:]:
            joined_copy = joined.copy()
            data = self.data[c].to_list()
            for i in range(0,len(data),2):
                first,second = data[i],data[i+1]
                to_join = joined_copy.pop(0) # check whether this pair is joined
                
                formatted_data[c].append(first)
                if not to_join:
                    formatted_data[c].append(second)

        # Create a DataFrame with formatted time stamps
        df = pd.DataFrame(columns=[f"DAY{self.day}: {self.location}"] + keys)

        ## Add the new row to the DataFrame
        for k in formatted_data.keys():
            df.loc[len(df)] = [k] + formatted_data[k] #values is a formatted list

        #format the dataframe
        styled_df = df.style.apply(self.highlight_cells, axis=None)
        styled_df.map(self.highlight_values)

        return styled_df
    
