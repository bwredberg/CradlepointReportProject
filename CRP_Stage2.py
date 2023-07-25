#This program opens the stage 1 WithDate files and loads them into a data frame
import csv
import glob
import os
import sqlite3

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

def SetupSQLConnection():
    conn = sqlite3.connect('C:\\Temp\\CradlepointReportProject\\cradlepoint_usage.db')
    conn.row_factory = sqlite3.Row
    return conn

def SQLImportDataCSVFromDir(SourceDir:str, MoveFiles:bool=True, ShowResults:bool=True) -> list:
    #Will need to read in the file and find the date from the filename, then add the data to the database
    directory_to_read = SourceDir + "OriginalFiles\\"
    directory_to_move = directory_to_read + "Imported\\"
    #db_table = "data_usage"
    files_read = 0
    files_written = 0
    for file in glob.glob(directory_to_read + 'cradlepoint_stats-2*-[0-3][0-9].csv'):
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
        data = []
        for row in file_temp:
            if header_row:
                #add date to the end of the header row
                row.append('date')
                header_row = False
            else:
                #add the date to the end of each non-header rowq
                #row.append(file_date)
                data.append((row[0], row[2], file_date))
        conn = SetupSQLConnection()
        conn.executemany('INSERT INTO data_usage (Cradlepoint, MB_used, date) VALUES (?, ?, ?)', data)
        conn.commit()
        conn.close()
        if MoveFiles:
            try:
                #move file to DirToRead + \imported folder
                #will overwrite if the destination file exists
                os.replace(file , directory_to_move + file[len(file)-32:]) #this just depends on the lenght of the file name
                files_written += 1
            except:
                print(f'Moving imported file {file} failed')
    if ShowResults:
        print(f'\n{files_read} Files read in')
        #print(f'{new_objects} New CP objects created')
        print(f'{files_written} Files moved to /imported')
        print(f'')
    return SQLListAllObjects(output=False)

def SQLListAllObjects(output:bool) -> list:
    #Display all currently know CP Objects
    conn = SetupSQLConnection()
    conn.row_factory = lambda cursor, row: row[0]
    cp_list = conn.execute('SELECT Cradlepoint FROM data_usage').fetchall()
    cp_list = sorted(set(cp_list))
    if output:
        for c1,c2,c3,c4,c5,c6 in zip(cp_list[::6], cp_list[1::6], cp_list[2::6], cp_list[3::6], cp_list[4::6], cp_list[5::6]):
            print (f'{c1:<20}{c2:<20}{c3:<20}{c4:<20}{c5:<20}{c6:<}')
    conn.close()
    return cp_list

def SQLFindLargestObject() -> tuple:
    #Currently this function is not used
    #find the largest by single usage date
    #returns a tuple containing (Cradlepoint, MB_used, date) 
    conn = SetupSQLConnection
    max_usage = conn.execute('SELECT Cradlepoint, MB_used, date FROM data_usage WHERE MB_used = (SELECT MAX(MB_used) FROM data_usage)').fetchone()
    conn.close()
    return max_usage

def SQLFindTopXHighestDays(top_x:int=10) -> None:
    #Find and display the top X usage days of all time
    conn = SetupSQLConnection()
    query = 'SELECT Cradlepoint, MB_used, date FROM data_usage ORDER BY MB_used DESC LIMIT {}'.format(top_x)
    max_usage_top_x = conn.execute(query).fetchall()
    print("\nCP Name             Data Usage(MB)  Date      ")
    print("==============================================")
    for entry in max_usage_top_x:
        data_usage_formated = f"{round(entry[1],2):,}"
        print(f'{entry[0]:<20}{data_usage_formated:<16}{entry[2]}')
    print("")
    conn.close()
    return

def WebSQLOutputObjectInfoByName(cp_name:str) -> dict:
    cp_info_dict = {}
    conn = SetupSQLConnection()
    max_usage = conn.execute('SELECT MAX(MB_used), date FROM data_usage WHERE Cradlepoint = ?', (cp_name,)).fetchone()
    earliest_date = conn.execute('SELECT date FROM data_usage WHERE Cradlepoint = ? ORDER BY date ASC LIMIT 1', (cp_name,)).fetchone()
    total_data_used = conn.execute('SELECT SUM(MB_used) FROM data_usage WHERE Cradlepoint = ?', (cp_name,)).fetchone()
    count = conn.execute('SELECT COUNT(MB_used) FROM data_usage WHERE Cradlepoint = ?', (cp_name,)).fetchone()
    cp_info_dict["CP_Name"] = cp_name
    cp_info_dict["Highest_Usage"] = round(max_usage[0],2)
    cp_info_dict["Date_Highest_Usage"] = max_usage[1]
    cp_info_dict["Date_First_Seen"] = earliest_date[0]
    cp_info_dict["Total_Usage"] = round(total_data_used[0],2)
    cp_info_dict["Count"] = count[0]
    cp_info_dict["Average_Usage"] = round(total_data_used[0]/count[0], 2)
    return cp_info_dict


def SQLOutputObjectInfoByName(cp_name:str, master_cp_list:list) -> None:
    #Prints out details based on the index number from CPObjectList
    if cp_name in master_cp_list:
        conn = SetupSQLConnection()
        max_usage = conn.execute('SELECT MAX(MB_used), date FROM data_usage WHERE Cradlepoint = ?', (cp_name,)).fetchone()
        earliest_date = conn.execute('SELECT date FROM data_usage WHERE Cradlepoint = ? ORDER BY date ASC LIMIT 1', (cp_name,)).fetchone()
        total_data_used = conn.execute('SELECT SUM(MB_used) FROM data_usage WHERE Cradlepoint = ?', (cp_name,)).fetchone()
        count = conn.execute('SELECT COUNT(MB_used) FROM data_usage WHERE Cradlepoint = ?', (cp_name,)).fetchone()
        #print(f'total_data_used = {total_data_used}')
        #print(f"Max usage = {max_usage}")
        #print(f'Earliest date = {earliest_date}')
        #print(f'Count = {count}')
        conn.close()
        print('='*42)
        print(f'Date first seen\t\t\t{earliest_date[0]}')
        print(f'Total Usage (MB)\t\t{round(total_data_used[0], 2):,}') 
        print(f'Number of Entries\t\t{count[0]:,}')
        print(f'Average (MB)\t\t\t{round(total_data_used[0]/count[0], 2):,}')
        print(f'Highest 24h Usage (MB)\t\t{round(max_usage[0], 2):,}')
        print(f'Date of Highest 24h Usage\t{max_usage[1]}')
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
        conn = SetupSQLConnection()        
        if UsageOutput_type == 'Raw':
            query = 'SELECT MB_used, date FROM data_usage WHERE Cradlepoint = ?'
            cp_usage_data_tuple = conn.execute(query, (cp_name,)).fetchall()
            #print(cp_usage_data_tuple)
            print(f'\nCradlepoint {cp_name} raw usage data')
            print('-' * len(f'Cradlepoint {cp_name} raw usage data'))
            print("Date\t\tUsage(MB)")
            print('-' * len(f'Cradlepoint {cp_name} raw usage data'))
            for entry in cp_usage_data_tuple:
                print(f"{entry[1]}\t{round(entry[0],2):,}")
        elif UsageOutput_type in ['date','MB_used']:
            query = 'SELECT MB_used, date FROM data_usage WHERE Cradlepoint = ? ORDER BY {} {}'.format(UsageOutput_type, asc_order)
            cp_usage_data_tuple = conn.execute(query, (cp_name,)).fetchall()
            #print(cp_usage_data_tuple)
            print(f'\nCradlepoint {cp_name} data usage sorted by {UsageOutput_type} - {Sort_text}')
            print('-' * (2 + len(f'Cradlepoint {cp_name} data usage sorted by {UsageOutput_type} - {Sort_text}')))
            print("Date\t\tUsage(MB)")
            print('-' * (2 + len(f'Cradlepoint {cp_name} data usage sorted by {UsageOutput_type} - {Sort_text}')))
            for entry in cp_usage_data_tuple:
                print(f"{entry[1]}\t{round(entry[0],2):,}")
        elif UsageOutput_type == 'GreaterThan':
            #output = ObjList[Index].DataUsage.query('MB_Used >= @value')
            query = 'SELECT MB_used, date FROM data_usage WHERE Cradlepoint = ? AND MB_used > ? ORDER BY MB_used DESC'
            cp_usage_data_tuple = conn.execute(query, (cp_name, value,)).fetchall()
            #print(cp_usage_data_tuple)
            print(f'\nCradlepoint {cp_name} data usage greater than {value}MB')
            print('=' * (2+ len(f'\nCradlepoint {cp_name} data usage greater than {value}MB')))
            print("Date\t\tUsage(MB)")
            print('=' * (2+ len(f'\nCradlepoint {cp_name} data usage greater than {value}MB')))
            for entry in cp_usage_data_tuple:
                print(f"{entry[1]}\t{round(entry[0],2):,}")
            return
        else:
            print(f'\nThere are no entries greater than or equal to {value}MBs for that Cradlepoint')
            return   
    else:
        print (f'{color_red}**ShowUsageByName {UsageOutput_type} ERROR** There is no Cradlepoint by name {cp_name}{color_reset}')
        return

def WebSQLShowUsageByName(cp_name:str, sort_by_value:str, sort_order_value:str) -> tuple:
    #value is an int for the data cutoff to return
    debug=False
    if debug:
        print(f'cp_name = {cp_name}')
        print(f'sort by value = {sort_by_value}')
        print(f'sort order value = {sort_order_value}')
    if sort_by_value == 'Usage':
        sort_by_value = 'MB_used'
    else:
        sort_by_value = 'date'
    if debug:
        print(f'NEW sort by value = {sort_by_value}')
    conn = SetupSQLConnection()        
    query = 'SELECT MB_used, date FROM data_usage WHERE Cradlepoint = ? ORDER BY {} {}'.format(sort_by_value, sort_order_value)
    cp_usage_data_tuple = conn.execute(query, (cp_name,)).fetchall()
    #tuple = MB_used, date
    if debug:
        for row in cp_usage_data_tuple:
            print(f'row[0] = {row[0]}')
            print(f'row[1] = {row[1]}')
    #print(cp_usage_data_tuple)
    return cp_usage_data_tuple

def Pause() -> None:
    #"Press any key to continue . . ."
    os.system('pause')
    return

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
    return UserInput

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
                               asc_order_int=GetUserMenuInput(Prompt=PromptForDateSortOrder, OptionList=SortOrderOptions,type_=int),
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
SourceDir = 'C:\\Temp\\CradlepointReportProject\\' #location where the source files exist
SaveFileDir = SourceDir + 'Save_File\\' #location where the save file exists
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
