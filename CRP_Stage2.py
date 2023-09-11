#This program opens the stage 1 WithDate files and loads them into a data frame
import csv
import glob
import os
from sqlHelper import sql
import termios
import sys
import tty
from pprint import pprint

color_reset = '\033[0m'
color_green = '\033[92m'
color_red = '\033[91m'
color_blue = '\033[94m'
color_yellow = '\033[93m'
color_magenta = '\033[95m'
color_cyan = '\033[96m'

#**************************************************************************************
#**                             TO-DO List                                           **
#**  -Import data via API directly from Cradlepoint                                  **
#**  -Find which entry is biggest by data usage                                      **
#**  -                                                                               **
#**  -ShowUsageByDateByIndex - ask for how many lines to print                       **
#**  -                                                                               **
#**  -                                                                               **
#**                                                                                  **
#**************************************************************************************

def SetupSQLConnection(debug_sql:bool=False) -> object:
    #conn = sql(dbHost="xnetkaos1", debug=debug_sql)  #sandbox
    #conn = sql(dbHost="jfbnetkaosd1", debug=debug_sql)  #dev
    conn = sql(dbHost="jfbnetkaosp1", debug=debug_sql)  #prod
    return conn

def SQLImportDataCSVFromDir(SourceDir:str, MoveFiles:bool=True, ShowResults:bool=True) -> list:
    #Will need to read in the file and find the date from the filename, then add the data to the database
    debug = False
    directory_to_read = SourceDir + "/OriginalFiles/"
    directory_to_move = directory_to_read + "Imported/"
    if debug:
        print(f'read dir = {directory_to_read}')
        print(f'move dir = {directory_to_move}')
    files_read = 0
    files_written = 0
    number_of_changes = 0
    file_list = glob.glob(directory_to_read + 'cradlepoint_stats-2*-[0-3][0-9].csv')
    if file_list is not None:
        conn = SetupSQLConnection(debug_sql=True)
        query_data = []
        for file in file_list:
            #initiate empty list for each file
            file_temp = []
            #read in each CSV file and dump it to file_temp
            with open(file) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    file_temp.append(row)
            files_read += 1
            #grab the date string out of the flie name
            file_date=file[len(file)-14:-4]
            #Add the date as an element at the end of each list member
            header_row = True
            for row in file_temp:
                if header_row:
                    #add date to the end of the header row
                    row.append('date')
                    header_row = False
                else:
                    query_data.append((row[0], row[2], file_date))
            if debug:
                print("Data to import...")
                print(type(query_data))
                pprint(query_data)
            if debug:
                print(f'The number of entries added was: {number_of_changes}')
            if MoveFiles:
                try:
                    #move file to DirToRead + \imported folder
                    #will overwrite if the destination file exists
                    if debug:
                        print(f'destination file is = {directory_to_move + file[len(file)-32:]}')
                    os.replace(file , directory_to_move + file[len(file)-32:]) #this just depends on the lenght of the file name
                    files_written += 1
                except:
                    print(f'Moving imported file {file} failed')
        #Push the full data set to import to the database
        number_of_changes = conn.executeMany(sql_statement='INSERT INTO cradlepoint_stats (Cradlepoint, MB_used, date) VALUES (%s, %s, %s)', data_list=query_data)
    else:
        print("There are no files to import")
        return SetupSQLConnection(output=False)
    if ShowResults:
        print(f'\n{files_read} Files read in')
        print(f'{number_of_changes} New database entries created')
        print(f'{files_written} Files moved to /imported')
        print(f'')
    return SQLListAllObjects(output=False)

def SQLListAllObjects(output:bool) -> list:
    #Display all currently know CP Objects
    conn = SetupSQLConnection(debug_sql=False)
    cp_list_of_dicts = conn.query('SELECT Cradlepoint FROM cradlepoint_stats').fetchall()
    temp_list = []
    for row in cp_list_of_dicts:
            temp_list.append(row["Cradlepoint"])
    cp_list = sorted(list(set(temp_list)))
    if output:
        for c1,c2,c3,c4,c5,c6 in zip(cp_list[::6], cp_list[1::6], cp_list[2::6], cp_list[3::6], cp_list[4::6], cp_list[5::6]):
            print (f'{c1:<20}{c2:<20}{c3:<20}{c4:<20}{c5:<20}{c6:<}')
    return cp_list

def SQLFindLargestObject() -> tuple:
    #Currently this function is not used
    #find the largest by single usage date
    #returns a tuple containing (Cradlepoint, MB_used, date) 
    conn = SetupSQLConnection()
    max_usage = conn.execute('SELECT Cradlepoint, MB_used, date FROM data_usage WHERE MB_used = (SELECT MAX(MB_used) FROM data_usage)').fetchone()
    return max_usage

def SQLTotalDays() -> int:
    conn = SetupSQLConnection()
    total_days = conn.query('SELECT COUNT(DISTINCT date) AS total_days from cradlepoint_stats').fetchone()
    return total_days

def WebSQLSystemDailyUsage() -> list:
    #Returns a list of dictionaries containg the total system usage for each day
    conn = SetupSQLConnection()
    system_daily_usage = conn.query('SELECT date, SUM(MB_used) AS total_mb_used FROM cradlepoint_stats GROUP BY date ORDER BY date DESC;').fetchall()
    return system_daily_usage

def WebSQLAllTimeSystemDataUsage() -> float:
    conn = SetupSQLConnection()
    all_time_usage = conn.query('SELECT SUM(MB_used) FROM cradlepoint_stats').fetchone()
    #pprint(all_time_usage)
    return all_time_usage

def WebSQLFindTopXHighestDays(top_x:int=10) -> dict:
    #Find and return the top X usage days of all time
    conn = SetupSQLConnection(debug_sql=False)
    query = 'SELECT Cradlepoint, MB_used, date FROM cradlepoint_stats ORDER BY MB_used DESC LIMIT {}'.format(top_x)
    max_usage_top_x = conn.query(query).fetchall()
    return max_usage_top_x

def SQLFindTopXHighestDays(top_x:int=10) -> None:
    #Find and display the top X usage days of all time
    conn = SetupSQLConnection(debug_sql=False)
    query = 'SELECT Cradlepoint, MB_used, date FROM cradlepoint_stats ORDER BY MB_used DESC LIMIT {}'.format(top_x)
    max_usage_top_x = conn.query(query).fetchall()
    print("\nCP Name             Data Usage(MB)  Date      ")
    print("==============================================")
    #print(f'max_usage_top_x = {max_usage_top_x}')
    for entry in max_usage_top_x:
        data_usage_formated = f'{round(entry["MB_used"],2):,}'
        print(f'{entry["Cradlepoint"]:<20}{data_usage_formated:<16}{entry["date"]}')
    print("")
    return

def WebSQLFindTopXDeviceUsage(top_x:int=10) -> dict:
    #Find and return top x highest all time usage
    conn = SetupSQLConnection(debug_sql=False)
    query = 'select Cradlepoint, SUM(MB_used) as Total_MB_Used from cradlepoint_stats group by Cradlepoint order by Total_MB_Used DESC Limit {}'.format(top_x)
    max_usage_top_x = conn.query(query).fetchall()
    #print(f'query response = {max_usage_top_x}')
    return max_usage_top_x

def WebSQLOutputObjectInfoByName(cp_name:str) -> dict:
    cp_info_dict = {}
    conn = SetupSQLConnection(debug_sql=False)
    max_usage_query = 'SELECT MAX(MB_used), date FROM cradlepoint_stats WHERE Cradlepoint = "{}"'.format(cp_name)
    max_usage = conn.query(max_usage_query).fetchone()
    earliest_date_query = 'SELECT date FROM cradlepoint_stats WHERE Cradlepoint = "{}" ORDER BY date ASC LIMIT 1'.format(cp_name)
    earliest_date = conn.query(earliest_date_query).fetchone()
    total_data_used_query = 'SELECT SUM(MB_used) FROM cradlepoint_stats WHERE Cradlepoint = "{}"'.format(cp_name)
    total_data_used = conn.query(total_data_used_query).fetchone()
    count_query = 'SELECT COUNT(MB_used) FROM cradlepoint_stats WHERE Cradlepoint = "{}"'.format(cp_name)
    count = conn.query(count_query).fetchone()
    cp_info_dict["CP_Name"] = cp_name
    cp_info_dict["Highest_Usage"] = round(max_usage["MAX(MB_used)"],2)
    cp_info_dict["Date_Highest_Usage"] = max_usage["date"]
    cp_info_dict["Date_First_Seen"] = earliest_date["date"]
    cp_info_dict["Total_Usage"] = round(total_data_used["SUM(MB_used)"],2)
    cp_info_dict["Count"] = count["COUNT(MB_used)"]
    cp_info_dict["Average_Usage"] = round(total_data_used["SUM(MB_used)"]/count["COUNT(MB_used)"], 2)
    return cp_info_dict

def SQLOutputObjectInfoByName(cp_name:str, master_cp_list:list) -> None:
    #Prints out details based on the index number from CPObjectList
    debug = False
    if cp_name in master_cp_list:
        conn = SetupSQLConnection(debug_sql=False)
        max_usage_query = 'SELECT MAX(MB_used), date FROM cradlepoint_stats WHERE Cradlepoint = "{}"'.format(cp_name)
        max_usage = conn.query(max_usage_query).fetchone()
        if debug:
            print(f'max_usage = {max_usage}')
            print(f'max usage data = {max_usage["MAX(MB_used)"]}')
            print(f'max usage date = {max_usage["date"]}')
        #earliest_date = conn.execute('SELECT date FROM data_usage WHERE Cradlepoint = ? ORDER BY date ASC LIMIT 1', (cp_name,)).fetchone()
        earliest_date_query = 'SELECT date FROM cradlepoint_stats WHERE Cradlepoint = "{}" ORDER BY date ASC LIMIT 1'.format(cp_name)
        earliest_date = conn.query(earliest_date_query).fetchone()
        if debug:
            print(f'earliest date = {earliest_date}')
            print(f'earliest date date = {earliest_date["date"]}')
        #total_data_used = conn.execute('SELECT SUM(MB_used) FROM data_usage WHERE Cradlepoint = ?', (cp_name,)).fetchone()
        total_data_used_query = 'SELECT SUM(MB_used) FROM cradlepoint_stats WHERE Cradlepoint = "{}"'.format(cp_name)
        total_data_used = conn.query(total_data_used_query).fetchone()
        if debug:
            print(f'total_data_used = {total_data_used}')
            print(f'total data used data = {total_data_used["SUM(MB_used)"]}')
        #count = conn.execute('SELECT COUNT(MB_used) FROM data_usage WHERE Cradlepoint = ?', (cp_name,)).fetchone()
        count_query = 'SELECT COUNT(MB_used) FROM cradlepoint_stats WHERE Cradlepoint = "{}"'.format(cp_name)
        count = conn.query(count_query).fetchone()
        if debug:
            print(f'Count = {count}')
            print(f'count count = {count["COUNT(MB_used)"]}')

        print('\n')
        print('='*42)
        print(f'Date first seen\t\t\t{earliest_date["date"]}')
        print(f'Total Usage (MB)\t\t{round(total_data_used["SUM(MB_used)"], 2):,}') 
        print(f'Number of Entries\t\t{count["COUNT(MB_used)"]:,}')
        print(f'Average (MB)\t\t\t{round(total_data_used["SUM(MB_used)"]/count["COUNT(MB_used)"], 2):,}')
        print(f'Highest 24h Usage (MB)\t\t{round(max_usage["MAX(MB_used)"], 2):,}')
        print(f'Date of Highest 24h Usage\t{max_usage["date"]}')
        return
    else:
        print(f'{color_red}No Cradlepoint found by that name{color_reset}')
        return
    
def SQLShowUsageByName(cp_name:str, master_cp_list:list, UsageOutput_type:str, asc_order_int:int=1, max_rows:int=None, value:int=1000) -> None:
    #UsageOutput_type should be a str in ['Raw','date','MB_used','GreaterThan']
    #value is an int for the data cutoff to return
    #determine sort order and output text
    if UsageOutput_type == 'date':
        if int(asc_order_int) == 2:
            Sort_text = 'newest to oldest'
            asc_order = 'DESC'
        else:
            Sort_text = 'oldest to newest'
            asc_order = 'ASC'
    elif UsageOutput_type == 'MB_used':
        if int(asc_order_int) == 2:
            Sort_text = 'largest to smallest'
            asc_order = 'DESC'
        else:
            Sort_text = 'smallest to largest'
            asc_order = 'ASC'
    #output the results
    if cp_name in master_cp_list:
        conn = SetupSQLConnection(debug_sql=False)        
        if UsageOutput_type == 'Raw':
            raw_query = 'SELECT MB_used, date FROM cradlepoint_stats WHERE Cradlepoint = "{}"'.format(cp_name)
            cp_usage_data = conn.query(raw_query).fetchall()
            print(f'\nCradlepoint {cp_name} raw usage data')
            print('-' * len(f'Cradlepoint {cp_name} raw usage data'))
            print("Date\t\tUsage(MB)")
            print('-' * len(f'Cradlepoint {cp_name} raw usage data'))
            for entry in cp_usage_data:
                print(f'{entry["date"]}\t{round(entry["MB_used"],2):,}')
        elif UsageOutput_type in ['date','MB_used']:
            usage_query = 'SELECT MB_used, date FROM cradlepoint_stats WHERE Cradlepoint = "{}" ORDER BY {} {}'.format(cp_name, UsageOutput_type, asc_order)
            cp_usage_data = conn.query(usage_query).fetchall()
            print(f'\nCradlepoint {cp_name} data usage sorted by {UsageOutput_type} - {Sort_text}')
            print('-' * (2 + len(f'Cradlepoint {cp_name} data usage sorted by {UsageOutput_type} - {Sort_text}')))
            print("Date\t\tUsage(MB)")
            print('-' * (2 + len(f'Cradlepoint {cp_name} data usage sorted by {UsageOutput_type} - {Sort_text}')))
            for entry in cp_usage_data:
                print(f'{entry["date"]}\t{round(entry["MB_used"],2):,}')
        elif UsageOutput_type == 'GreaterThan':
            #output = ObjList[Index].DataUsage.query('MB_Used >= @value')
            greaterthan_query = 'SELECT MB_used, date FROM cradlepoint_stats WHERE Cradlepoint = "{}" AND MB_used > {} ORDER BY MB_used DESC'.format(cp_name, value)
            cp_usage_data = conn.query(greaterthan_query).fetchall()
            print(f'\nCradlepoint {cp_name} data usage greater than {value}MB')
            print('=' * (2+ len(f'\nCradlepoint {cp_name} data usage greater than {value}MB')))
            print("Date\t\tUsage(MB)")
            print('=' * (2+ len(f'\nCradlepoint {cp_name} data usage greater than {value}MB')))
            for entry in cp_usage_data:
                print(f'{entry["date"]}\t{round(entry["MB_used"],2):,}')
            return
        else:
            print(f'\nThere are no entries greater than or equal to {value}MBs for that Cradlepoint')
            return   
    else:
        print (f'{color_red}**ShowUsageByName {UsageOutput_type} ERROR** There is no Cradlepoint by name {cp_name}{color_reset}')
        return

def WebSQLShowUsageByName(cp_name:str, sort_by_value:str, sort_order_value:str, response_limit:int, min_data_usage:str) -> dict:
    #value is an int for the data cutoff to return
    debug=False
    if debug:
        print(f'min_data_usage original = {min_data_usage}')
    if min_data_usage:
        min_data_usage = int(min_data_usage)
    else:
        min_data_usage = 0
    if debug:
        print(f'cp_name = {cp_name}')
        print(f'sort by value = {sort_by_value}')
        print(f'sort order value = {sort_order_value}')
        print(f'min_data_usage = {min_data_usage}')
        print(f'min_usage_data_type = {type(min_data_usage)}')
    if sort_by_value == 'Usage':
        sort_by_value = 'MB_used'
    else:
        sort_by_value = 'date'
    if debug:
        print(f'NEW sort by value = {sort_by_value}')
    if min_data_usage != 0 and sort_by_value != 'date':
        #valid query: SELECT MB_used, date FROM cradlepoint_stats WHERE Cradlepoint = "ROA-CP1" AND MB_used > 1000 ORDER BY MB_used DESC LIMIT 9999;
        usage_query = 'SELECT MB_used, date FROM cradlepoint_stats WHERE Cradlepoint = "{}" AND MB_used > {} ORDER BY {} {} LIMIT {}'.format(cp_name, min_data_usage, sort_by_value, sort_order_value, response_limit)
    elif min_data_usage == 0:
        usage_query = 'SELECT MB_used, date FROM cradlepoint_stats WHERE Cradlepoint = "{}" ORDER BY {} {} LIMIT {}'.format(cp_name, sort_by_value, sort_order_value, response_limit)
    else:
        print('Your query is broken')
    conn = SetupSQLConnection()        
    cp_usage_data = conn.query(usage_query).fetchall()
    if debug:
        for row in cp_usage_data:
            print(f'row["MB_used"] = {row["MB_used"]}')
            print(f'row["date"] = {row["date"]}')
    return cp_usage_data

def LoadFrontEndMenu() -> None:
    print(f''                                         )
    print(f'*****************************************')  #41 *'s
    print(f'* Cradlepoint Usage Reporting Main Menu *')
    print(f'*****************************************')  #41 *'s
    print(f'1) Import new data files'                 )
    print(f''                                         )
    print(f''                                         )
    print(f'4) Show usage by device name'             )
    print(f''                                         )
    print(f''                                         )
    print(f''                                         )
    print(f'8) Exit'                                  )
    print(f'*****************************************')  #41 *'s

def LoadUsageMenu() -> None:
    print(f''                                         )
    print(f'*****************************************')  #41 *'s
    print(f'*           Show Usage Menu             *')
    print(f'*****************************************')  #41 *'s
    print(f'1) Show raw usage data'                   )
    print(f'2) Show usage data sorted by date'        )
    print(f'3) Show usage data sorted by amount'      )
    print(f'4) Show usage summary for a device'       )
    print(f'5) Show usage above 1000MB for a device'  )
    print(f'6) Show top 15 all time usage days'       )
    print(f'7) List all devices'                      )
    print(f'8) Exit to main menu'                     )
    print(f'*****************************************')  #41 *'s    

def WindowsPause() -> None:
    # Windows pause
    #"Press any key to continue . . ."
    os.system('pause')
    return

def Pause() -> None:
    # Linux pause
    print("Press any key to continue...")
    # Save the current terminal settings
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        # Set the terminal to raw mode so that it doesn't require Enter key press
        tty.setcbreak(sys.stdin.fileno())
        # Read a single character (will not wait for Enter)
        sys.stdin.read(1)
    finally:
        # Restore the terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    return

def GetUserMenuInput(Prompt:str, OptionList:list, type_=int, debug:bool=False):
    #Prompt = string - is the user prompt
    #OptionList = list - should include all valid input options
    #type_ = string - should be a valid type like int, str, float, etc...
    while True:
        try:
            if type_ == str:
                UserInput = type_(input(Prompt)).upper()
            else:    
                UserInput = type_(input(Prompt))
        except ValueError:
            print(f'Sorry, I didn''t understand that. Please Try again.')
            continue
        if not UserInput in OptionList:
            print(f'Sorry, you didn''t select a valid option from this list. Please try again.')
            continue
        else:
            break
    if debug:
        print(f'UserInput = {UserInput}')
    return UserInput

def GetUserObjectInput(Prompt:str) -> str:
    #Prompt = string - should be a Cradlepoint device name
    while True:
        try:
            UserInput = input(Prompt)
        except ValueError:
            print(f'Sorry, I didn''t understand that. Please Try again.')
            continue
        else:
            break
    return UserInput.upper()

def FrontEndMenu_UserInputEval(SourceDir:str, master_cp_list:list, UserInput:int, NumberPrompt:str, DeviceNamePrompt:str) -> None:
    #ObjList should be CPObjectList
    #UserInput is an int, the users choice
    #NumberPrompt is a str and is the text the user is prompted
    #DeviceNamePrompt is a str and is the text the user is prompted 
    match UserInput:
        case 1:  #Import new data files
            print(f'Loading files from {SourceDir}OriginalFiles\\...')
            #Pause()
            master_cp_list = SQLImportDataCSVFromDir(SourceDir=SourceDir, MoveFiles=True, ShowResults=True)
            Pause()
            LoadFrontEndMenu()
            FrontEndMenu_UserInputEval(SourceDir=SourceDir, 
                                       master_cp_list=master_cp_list, 
                                       UserInput=GetUserMenuInput(Prompt=PromptForMenuNumber, OptionList=FrontEndMenuOptions, type_=int, debug=False), 
                                       NumberPrompt=PromptForMenuNumber, 
                                       DeviceNamePrompt=PromptForDeviceName)
        case 4:  #Show usage by device name
            LoadUsageMenu()
            UsageMenu_UserInputEval(SourceDir=SourceDir,
                                    master_cp_list=master_cp_list,
                                    UserInput=GetUserMenuInput(NumberPrompt, UsageMenuOptions, type_=int),
                                    NumberPrompt=NumberPrompt,
                                    DeviceNamePrompt=DeviceNamePrompt)
        case 8:  #Exit program
            print(f'Goodbye')
        case _:
            print(f'FrontEndMenu_UserInputEval - Not a valid option')

def UsageMenu_UserInputEval(SourceDir:str, master_cp_list:list, UserInput:int, NumberPrompt:int, DeviceNamePrompt:str) -> None:
    match UserInput:
        case 1:  #Show raw usage data
            SQLShowUsageByName(cp_name=GetUserObjectInput(Prompt=DeviceNamePrompt),
                               master_cp_list=master_cp_list,
                               UsageOutput_type='Raw', 
                               asc_order_int=1,
                               max_rows=None)
            print(f'')
            Pause()
            LoadUsageMenu()
            #This calls this function again from inside - concerned about this, but don't have a better way right now
            UsageMenu_UserInputEval(SourceDir=SourceDir,
                                    master_cp_list=master_cp_list,
                                    UserInput=GetUserMenuInput(Prompt=NumberPrompt, OptionList=UsageMenuOptions, type_=int),
                                    NumberPrompt=NumberPrompt,
                                    DeviceNamePrompt=DeviceNamePrompt)
        case 2:  #Show usage data sorted by date
            #the first prompt gets the device name, the second prompt is a choice between 1 and 2 for sort order
            SQLShowUsageByName(cp_name=GetUserObjectInput(Prompt=DeviceNamePrompt),
                               master_cp_list=master_cp_list,
                               UsageOutput_type='date', 
                               asc_order_int=GetUserMenuInput(Prompt=PromptForDateSortOrder,OptionList=SortOrderOptions,type_=int),
                               max_rows=None)
            print(f'')
            Pause()
            LoadUsageMenu()
            UsageMenu_UserInputEval(SourceDir=SourceDir,
                                    master_cp_list=master_cp_list,
                                    UserInput=GetUserMenuInput(Prompt=NumberPrompt, OptionList=UsageMenuOptions, type_=int),
                                    NumberPrompt=NumberPrompt,
                                    DeviceNamePrompt=DeviceNamePrompt)
        case 3:  #Show usage data sorted by amount
            SQLShowUsageByName(cp_name=GetUserObjectInput(Prompt=DeviceNamePrompt),
                               master_cp_list=master_cp_list,
                               UsageOutput_type='MB_used', 
                               asc_order_int=GetUserMenuInput(Prompt=PromptForUsageSortOrder, OptionList=SortOrderOptions,type_=int),
                               max_rows=None)
            print(f'')
            Pause()
            LoadUsageMenu()
            UsageMenu_UserInputEval(SourceDir=SourceDir,
                        master_cp_list=master_cp_list,
                        UserInput=GetUserMenuInput(Prompt=NumberPrompt, OptionList=UsageMenuOptions, type_=int),
                        NumberPrompt=NumberPrompt,
                        DeviceNamePrompt=DeviceNamePrompt)
        case 4:  #Show usage data sorted by amount
            SQLOutputObjectInfoByName(cp_name=GetUserObjectInput(Prompt=DeviceNamePrompt), master_cp_list=master_cp_list)
            print(f'')
            Pause()
            LoadUsageMenu()
            UsageMenu_UserInputEval(SourceDir=SourceDir,
                        master_cp_list=master_cp_list,
                        UserInput=GetUserMenuInput(Prompt=NumberPrompt, OptionList=UsageMenuOptions, type_=int),
                        NumberPrompt=NumberPrompt,
                        DeviceNamePrompt=DeviceNamePrompt)
        case 5:  #Show usage above 1000MB for a device
            SQLShowUsageByName(cp_name=GetUserObjectInput(Prompt=DeviceNamePrompt),
                               master_cp_list=master_cp_list,
                               UsageOutput_type="GreaterThan",
                               asc_order_int=1,
                               max_rows=None,
                               value=1000)
            print("")
            Pause()
            LoadUsageMenu()
            UsageMenu_UserInputEval(SourceDir=SourceDir,
                                    master_cp_list=master_cp_list,
                                    UserInput=GetUserMenuInput(Prompt=NumberPrompt, OptionList=UsageMenuOptions, type_=int),
                                    NumberPrompt=NumberPrompt,
                                    DeviceNamePrompt=DeviceNamePrompt)
        case 6: #Show top ten usage by day
            SQLFindTopXHighestDays(top_x=15)
            Pause()
            LoadUsageMenu()
            UsageMenu_UserInputEval(SourceDir=SourceDir,
                        master_cp_list=master_cp_list,
                        UserInput=GetUserMenuInput(Prompt=NumberPrompt, OptionList=UsageMenuOptions, type_=int),
                        NumberPrompt=NumberPrompt,
                        DeviceNamePrompt=DeviceNamePrompt)
        case 7:  #Show list of all devices
            SQLListAllObjects(output=True)
            print(f'')
            Pause()
            LoadUsageMenu()
            UsageMenu_UserInputEval(SourceDir=SourceDir,
                master_cp_list=master_cp_list,
                UserInput=GetUserMenuInput(Prompt=NumberPrompt, OptionList=UsageMenuOptions, type_=int),
                NumberPrompt=NumberPrompt,
                DeviceNamePrompt=DeviceNamePrompt)
        case 8:  #Exit to main menu
            LoadFrontEndMenu()
            FrontEndMenu_UserInputEval(SourceDir=SourceDir,
                                       master_cp_list=master_cp_list,
                                       UserInput=GetUserMenuInput(PromptForMenuNumber, FrontEndMenuOptions, type_=int),
                                       NumberPrompt=PromptForMenuNumber,
                                       DeviceNamePrompt=PromptForDeviceName)
        case _:
            print(f'{color_red}UsageMenu_UserInputEval - Not a valid option{color_reset}')


#*****************************************************#
#**              Main Program Area                  **#
#*****************************************************#
CPObjectList = [] #create empty object list
SourceDir = '/home/g528525/python/CradlepointReportProject' #location where the source files exist
#SaveFileDir = SourceDir + 'Save_File\\' #location where the save file exists
FrontEndMenuOptions = [1,4,8] #These are the valid selections for the Front end menu
UsageMenuOptions = [1,2,3,4,5,6,7,8] #These are the valid selections for the Usage menu
SortOrderOptions = [1,2] #These are the valid selections for ascending or decending order
StringMenuOpions = ['YES','NO','Y','N'] #These are the valid selections for Yes/No questions
PromptForDeviceName = 'Please enter a device name: '
PromptForMenuNumber = 'Please enter a number from the list: '
PromptForDateSortOrder = 'Choose 1 for Oldest to Newest or 2 for Newest to Oldest: '
PromptForUsageSortOrder = 'Choose 1 for Smallest to Largest or 2 for Largest to Smallest: '
#PromptForLoad = 'CPObjectList is not empty are you sure you want to overwrite it with saved data? (Yes or No) '
#PromptForSave = 'Are you sure you want to overwrite the existing save file? (Yes or No) '
#PromptForExit = 'The data has not been saved.  Are you sure you want to continue without saving it? (Yes or No) '

if __name__ == "__main__":
    master_cp_list = SQLListAllObjects(output=False)
    LoadFrontEndMenu()
    FrontEndMenu_UserInputEval(SourceDir=SourceDir,
                            master_cp_list=master_cp_list,
                            UserInput=GetUserMenuInput(PromptForMenuNumber, FrontEndMenuOptions, type_=int),
                            NumberPrompt=PromptForMenuNumber,
                            DeviceNamePrompt=PromptForDeviceName)