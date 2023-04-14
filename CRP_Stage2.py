#This program opens the stage 1 WithDate files and loads them into a data frame
import csv
import glob
import os
import pandas as pd
import pickle
import sys


#**************************************************************************************
#**                             TO-DO List                                           **
#**  -Move Stage1 functionality into Stage2                                          **
#**  -Find which entry is biggest by data usage                                      **
#**  -On import if no files found skip                                               **
#**      -Look for duplicates???                                                     **
#**  -Add date first seen to summary data                                            **
#**  -Don't allow it to import duplicate data                                        **
#**  -ShowUsageByDateByIndex - ask for how many lines to print                       **
#**                                                                                  **
#**                                                                                  **
#**                                                                                  **
#**************************************************************************************


class CP_Usage:
    #Created the Cradlepoint objects
    def __init__(self, name):
        self.name = name
        #self.description = description
        self.DataUsage = pd.DataFrame(columns=['Date', 'MB_Used'])
        self.AvgUsage = 0.0  #avg across all usage entries
        self.HighUsage = 0.0  #highest single usage entry
        self.HighUsageDate = ''
        self.TotalUsage = 0.0  #sum of all usage entires
        self.NumberOfEntries = 0  #total number of usage entries
        self.DateFirstSeen = ''
    def __str__(self) -> str:
        return f'{self.name}'
    def __repr__(self) -> str:
        return f'{self.name}'

    def AddUsage(self, date, usage):
        usage=float(usage)
        #add data after last item
        self.DataUsage.loc[len(self.DataUsage.index)] = [date,usage]
        #convert Date column to type Date
        self.DataUsage['Date'] = pd.to_datetime(self.DataUsage['Date'])
        #update Avg, High, Total, Entries
        self.TotalUsage = self.DataUsage['MB_Used'].sum()
        ###self.HighUsageSeries = self.DataUsage.max(axis='index', numeric_only=True)
        ###self.HighUsage = self.HighUsageSeries[0]
        self.HighUsageSeries = self.DataUsage.loc[self.DataUsage['MB_Used'].idxmax()]
        self.HighUsageDate = self.HighUsageSeries[0].date()
        self.HighUsage = self.HighUsageSeries[1]
        self.NumberOfEntries = len(self.DataUsage.index)
        self.AvgUsage = self.TotalUsage / self.NumberOfEntries
        self.DateFirstSeen = self.DataUsage['Date'].min()


#===========================================================================        
def Stage1(ObjList):
    #Will need to read in the file and find the date from the filename, then either create a new object or run AddUsage
    directory_to_read = "c:/temp/CradlepointReportProject/OriginalFiles/"
    directory_to_write = "c:/temp/CradlepointReportProject/Stage1/"
    directory_to_move = "c:/Temp/CradlepointReportProject/OriginalFiles/imported/"
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
        
        #increment file counter
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
                #add the date to the end of each non-header row
                row.append(file_date)
    
        try:
            #dump the list back to a csv file with a new name
            file_to_write = directory_to_write + file[len(file)-32:-4] + '-WithDate.csv'
            with open(file_to_write, 'w', newline='') as csv_file:
                writefile = csv.writer(csv_file, delimiter=',')
                writefile.writerows(file_temp)
        except:
            print(f'Writing file {file} failed')
    else:
        #increment file counter
        files_written += 1
    try:
        #move file to C:\Temp\CradlepointReportProject\OriginalFiles\imported folder
        #will overwrite if the destination file exists
        os.replace(file , directory_to_move + file[len(file)-32:])
    except:
        print(f'Moving file {file} failed')

    #print counters
    print (f'{files_read} files read')
    print (f'{files_written} files written')

def SaveToFile(ObjList, SaveDir):
    #ObjList in this case should always be CPObjectList
    #SaveDir is the string path to save the file to
    if not os.path.exists(SaveDir):
        print(f'Save directory doesn''t exist, creating it now')
        os.mkdir(SaveDir)
    try:
        with open(SaveDir+'CPObject_save.pkl','wb') as file:
            pickle.dump(ObjList,file)
        print(f'File saved')
        return True
    except:
        print(f'File save failed.')
        return False

def LoadFromFile(SaveDir, debug=False):
    #SaveDir is the string path to save the file to
    ObjList = []  #Load into an empty list
    if debug:
        print(SaveDir+'CPObject_save.pkl')
        Pause()
    if os.path.isfile(SaveDir+'CPObject_save.pkl'):
        try:
            with open(SaveDir+'CPObject_save.pkl','rb') as file:
                ObjList = pickle.load(file)
            print(f'File load succeeded\n')
        except:
            print(f'File load failed.\n')
        if debug:
            print(ObjList)
            Pause()
        return ObjList
    else:
        print(f'Save file can''t be found.')

def CreateNewObject(ObjList, DeviceName):
    #DeviceName must be a string
    #Add a new Cradlepoint Object into the Object List
    ObjList.append(CP_Usage(DeviceName))

def ImportDataCSVFromDir(ObjList, DirToRead, MoveFiles=True, ShowResults=True):
    #Parses a passed directory path and reads in all CSVfiles that match the file name
    #MoveFiles Boolean True = move the read in files to the imported directory, False = leave the read in files where they are
    #ShowResults Boolean True = show result stats at the end of the import, False = skip the result stats
    DirToMove = DirToRead + "imported\\"
    files_read = 0
    files_written = 0
    new_objects = 0

    for file in glob.glob(DirToRead + 'cradlepoint_stats-2*-WithDate.csv'):
        #read in each CSV file and ...
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            files_read += 1
            header_row = True
            for row in csv_reader:
                if header_row:
                    #Skip this row
                    header_row = False
                else:
                    for n in range(0,len(ObjList)):
                        if str(row[0]) in ObjList[n].name:            
                            #This will match if row[0] matches CPObjectList[n].name and write data to existing object
                            #'Device_Name': row[0], 'date':row[3], 'MB_Used': row[2]
                            ObjList[n].AddUsage(row[3],row[2])
                            #quit iteration if you've found it
                            break
                    else:
                        CreateNewObject(ObjList, row[0])
                        new_objects += 1
                        #write data to object
                        #Since we just added the object we should be able to reference the last object in the list
                        #'Device_Name': row[0], 'date':row[3], 'MB_Used': row[2]
                        ObjList[len(ObjList)-1].AddUsage(row[3],row[2])
        if MoveFiles:
            try:
                #move file to DirToRead + \imported folder
                #will overwrite if the destination file exists
                os.replace(file , DirToMove + file[len(file)-41:]) #this just depends on the lenght of the file name
                files_written += 1
            except:
                print(f'Moving file {file} failed')
    if ShowResults:
        print(f'\n{files_read} Files read in')
        print(f'{new_objects} New CP objects created')
        print(f'{files_written} Files moved to /imported')
        print(f'')

def FindObjectIndex(ObjList, DeviceName):
    #ObjList should be CPObjectList
    #DeviceName must be a string
    #search through the Cradlepoint Object list for any object with the given name and return its index number
    for n in range(0,len(ObjList)):
        if str(DeviceName) in ObjList[n].name:
            return n
    return -1 #No object with that name found

#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

def ShowUsageByIndex(ObjList, UsageOutput_type, Index, asc_order_int = 1, max_rows=None, value=750):
    #ObjList should be CPObjectList
    #UsageOutput_type should be a str in ['Raw','Date','MB_Used']
    #Index must be an int
    #asc_order_int must be an int
    #max_rows must be an int
    #value is an int for the data cutoff to return
    
    #determine sort order and output text
    if UsageOutput_type == 'Date':
        if int(asc_order_int) == 2:
            Sort_text = 'newest to oldest'
            asc_order = False
        else:
            Sort_text = 'oldest to newest'
            asc_order = True
    elif UsageOutput_type == 'MB_Used':
        if int(asc_order_int) == 2:
            Sort_text = 'largest to smallest'
            asc_order = False
        else:
            Sort_text = 'smallest to largest'
            asc_order = True
    #output the results
    if Index >= 0 and Index <= len(ObjList):
        if UsageOutput_type == 'Raw':
            print(f'\nCradlepoint {ObjList[Index].name} raw usage data')
            print('-' * len(f'Cradlepoint {ObjList[Index].name} raw usage data'))
            with pd.option_context('display.max_rows', max_rows):
                print(ObjList[Index].DataUsage)
        elif UsageOutput_type in ['Date','MB_Used']:
            ObjList[Index].DataUsage.sort_values(by=UsageOutput_type, ascending=asc_order, inplace=True)
            print(f'\nCradlepoint {ObjList[Index].name} data usage sorted by {UsageOutput_type} - {Sort_text}')
            print('-' * (2 + len(f'Cradlepoint {ObjList[Index].name} data usage sorted by {UsageOutput_type} - {Sort_text}')))
            if max_rows == None:
                #This option prints all rows in the df
                with pd.option_context('display.max_rows', max_rows):
                    print(ObjList[Index].DataUsage)
            else:
                #This option prints only the number of rows specificed from the top of the list
                print(ObjList[Index].DataUsage.head(max_rows))
        elif UsageOutput_type == 'GreaterThan':
            output = ObjList[Index].DataUsage.query('MB_Used >= @value')
            if not output.empty:
                output.sort_values(by='MB_Used', ascending=False, inplace=True)
                print(f'\nCradlepoint {ObjList[Index].name} data usage greater than {value}')
                print('=' * (2+ len(f'\nCradlepoint {ObjList[Index].name} data usage greater than {value}')))
                print(output)
                return
            else:
                print(f'\nThere are no entries greater than or equal to {value}MBs for that Cradlepoint')
                return   
    elif Index == -1:
        print(f'No Cradlepoint found by that name')
        return
    else:
        print (f'**ShowUsageByIndex {UsageOutput_type} ERROR** There is no Cradlepoint at index {Index}')
        return

#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

def ListAllObjects(ObjList):
    #Display all currently know CP Objects
    #  good enough for now, but should figure out how to format this
    #  see  https://stackoverflow.com/questions/1524126/how-to-print-a-list-more-nicely
    print(*ObjList)
    return

def ObjectExists(ObjName):
    #ObjName must be a string
    #search through the Cradlepoint Object list for any object with the given name
    for n in range(0,len(CPObjectList)):
        if str(ObjName) in CPObjectList[n].name:
            return True
    return False 

def OutputObjectInfoByIndex(ObjList, Index):
    #Prints out details based on the index number from CPObjectList
    if Index >= 0 and Index <= len(ObjList):
        print('='*41)
        print(f'Date first seen\t\t{ObjList[Index].DateFirstSeen}')
        print(f'Total Usage (MB)\t\t{round(ObjList[Index].TotalUsage, 2):,}') 
        print(f'Number of Entries\t\t{ObjList[Index].NumberOfEntries:,}')
        print(f'Average (MB)\t\t\t{round(ObjList[Index].AvgUsage, 2):,}')
        print(f'Highest 24h Usage (MB)\t\t{round(ObjList[Index].HighUsage, 2):,}')
        print(f'Date of Highest 24h Usage\t{ObjList[Index].HighUsageDate}')
        return
    elif Index == -1:
        print(f'No Cradlepoint found by that name')
        return
    else:
        print (f'**ShowObjectInfoByIndex ERROR** There is no Cradlepoint at the index {Index}') 
        return

def Pause():
    #"Press any key to continue . . ."
    os.system('pause')
    return

def LoadFrontEndMenu():
    print(f''                                         )
    print(f'*****************************************')  #41 *'s
    print(f'* Cradlepoint Usage Reporting Main Menu *')
    print(f'*****************************************')  #41 *'s
    print(f'1) Load saved data file'                  )
    print(f'2) Save data to file'                     )
    print(f''                                         )
    print(f'3) Import new data files'                 )
    print(f'4) Show usage by device name'             )
    print(f''                                         )
    print(f'8) Exit'                                  )
    print(f'*****************************************')  #41 *'s
   

def LoadUsageMenu():
    print(f''                                         )
    print(f'*****************************************')  #41 *'s
    print(f'*           Show Usage Menu             *')
    print(f'*****************************************')  #41 *'s
    print(f'1) Show raw usage data'                   )
    print(f'2) Show usage data sorted by date'        )
    print(f'3) Show usage data sorted by amount'      )
    print(f'4) Show usage summary for a device'       )
    print(f'5) Show usage above 750MB for a device'   )
    print(f''                                         )
    print(f'7) List all devices'                      )
    print(f'8) Exit to main menu'                     )
    print(f'*****************************************')  #41 *'s    


def GetUserMenuInput(Prompt, OptionList, type_=int, debug = False):
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

def GetUserObjectInput(Prompt):
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

def FrontEndMenu_UserInputEval(ObjList, Saved, UserInput, NumberPrompt, DeviceNamePrompt):
    #ObjList should be CPObjectList
    #Saved is a boolean to track if the file has been saved or not
    #UserInput is an int, the users choice
    #NumberPrompt is a str and is the text the user is prompted
    #DeviceNamePrompt is a str and is the text the user is prompted 
    match UserInput:
        case 1:  #Load saved data file
            if ObjList == []:
                ObjList = LoadFromFile(SaveFileDir, debug=False)
            else:
                if GetUserMenuInput(PromptForLoad,StringMenuOpions,type_=str) == "Yes":
                    ObjList = LoadFromFile(SaveFileDir, debug=False)
                else:
                    print(f'File Load cancelled.\n')
            LoadFrontEndMenu()
            FrontEndMenu_UserInputEval(ObjList, Saved, GetUserMenuInput(PromptForMenuNumber, FrontEndMenuOptions, type_=int), PromptForMenuNumber, PromptForDeviceName)
        case 2:  #Save data to file
            print(f'You selected menu option 2 - Save data to file')
            if GetUserMenuInput(PromptForSave, StringMenuOpions, type_=str) == "Yes":
                Saved = SaveToFile(ObjList, SaveFileDir)
            else:
                print(f'File save cancelled.')
            LoadFrontEndMenu()
            FrontEndMenu_UserInputEval(ObjList, Saved, GetUserMenuInput(PromptForMenuNumber, FrontEndMenuOptions, type_=int), PromptForMenuNumber, PromptForDeviceName)
        case 3:  #Import new data files
            print(f'This will load new CSV files from {SourceDir}')
            Pause()
            ImportDataCSVFromDir(ObjList, SourceDir, MoveFiles=True, ShowResults=True)
            Pause()
            LoadFrontEndMenu()
            FrontEndMenu_UserInputEval(ObjList, Saved, GetUserMenuInput(PromptForMenuNumber, FrontEndMenuOptions, type_=int), PromptForMenuNumber, PromptForDeviceName)
        case 4:  #Show usage by device name
            LoadUsageMenu()
            UsageMenu_UserInputEval(ObjList, Saved, GetUserMenuInput(NumberPrompt, UsageMenuOptions, type_=int), NumberPrompt, DeviceNamePrompt)
        case 8:  #Exit program
            answers = ['NO','N']
            if not Saved:
                if GetUserMenuInput(PromptForExit, StringMenuOpions, type_=str, debug=False) in answers:
                    print(f'Exit cancelled')
                    LoadFrontEndMenu()
                    FrontEndMenu_UserInputEval(ObjList, Saved, GetUserMenuInput(PromptForMenuNumber, FrontEndMenuOptions, type_=int), PromptForMenuNumber, PromptForDeviceName)
                else:
                    print(f'Goodbye')
        case _:
            print(f'FrontEndMenu_UserInputEval - Not a valid option')

def UsageMenu_UserInputEval(ObjList, Saved, UserInput, NumberPrompt, DeviceNamePrompt):
    match UserInput:
        case 1:  #Show raw usage data
            ShowUsageByIndex(ObjList, 'Raw', FindObjectIndex(ObjList, GetUserObjectInput(DeviceNamePrompt)), asc_order_int = 1, max_rows=None)
            print(f'')
            Pause()
            LoadUsageMenu()
            #This calls this function again from inside - concerned about this, but don't have a better way right now
            UsageMenu_UserInputEval(ObjList, Saved, GetUserMenuInput(NumberPrompt, UsageMenuOptions, type_=int), NumberPrompt, DeviceNamePrompt)
        case 2:  #Show usage data sorted by date
            #the first prompt gets the device name, the second prompt is a choice between 1 and 2 for sort order
            ShowUsageByIndex(ObjList, 'Date', FindObjectIndex(ObjList, GetUserObjectInput(DeviceNamePrompt)), GetUserMenuInput(PromptForDateSortOrder,SortOrderOptions,type_=int), max_rows=None)
            print(f'')
            Pause()
            LoadUsageMenu()
            UsageMenu_UserInputEval(ObjList, Saved, GetUserMenuInput(NumberPrompt, UsageMenuOptions, type_=int), NumberPrompt, DeviceNamePrompt)
        case 3:  #Show usage data sorted by amount
            ShowUsageByIndex(ObjList, 'MB_Used', FindObjectIndex(ObjList, GetUserObjectInput(DeviceNamePrompt)), GetUserMenuInput(PromptForUsageSortOrder,SortOrderOptions,type_=int), max_rows=None)
            print(f'')
            Pause()
            LoadUsageMenu()
            UsageMenu_UserInputEval(ObjList, Saved, GetUserMenuInput(NumberPrompt, UsageMenuOptions, type_=int), NumberPrompt, DeviceNamePrompt)
        case 4:  #Show usage data sorted by amount
            OutputObjectInfoByIndex(ObjList, FindObjectIndex(ObjList, GetUserObjectInput(DeviceNamePrompt)))
            print(f'')
            Pause()
            LoadUsageMenu()
            UsageMenu_UserInputEval(ObjList, Saved, GetUserMenuInput(NumberPrompt, UsageMenuOptions, type_=int), NumberPrompt, DeviceNamePrompt)
        case 5:  #Show usage above 750MB for a device
            #ShowUsageGreaterThanByIndex(ObjList, FindObjectIndex(ObjList, GetUserObjectInput(DeviceNamePrompt)),750)
            ShowUsageByIndex(ObjList, 'GreaterThan', FindObjectIndex(ObjList, GetUserObjectInput(DeviceNamePrompt)), asc_order_int = 1, max_rows=None, value=750)
            print(f'')
            Pause()
            LoadUsageMenu()
            UsageMenu_UserInputEval(ObjList, Saved, GetUserMenuInput(NumberPrompt, UsageMenuOptions, type_=int), NumberPrompt, DeviceNamePrompt)
        case 7:  #Show list of all devices
            ListAllObjects(ObjList)
            print(f'')
            Pause()
            LoadUsageMenu()
            UsageMenu_UserInputEval(ObjList, Saved, GetUserMenuInput(NumberPrompt, UsageMenuOptions, type_=int), NumberPrompt, DeviceNamePrompt)
        case 8:  #Exit to main menu
            LoadFrontEndMenu()
            FrontEndMenu_UserInputEval(ObjList, Saved, GetUserMenuInput(NumberPrompt,FrontEndMenuOptions,type_=int), NumberPrompt, DeviceNamePrompt)
        case _:
            print(f'UsageMenu_UserInputEval - Not a valid option')


#*****************************************************#
#**              Main Program Area                  **#
#*****************************************************#
CPObjectList = [] #create empty object list
FileSaved = False
SourceDir = 'C:\\Temp\\CradlepointReportProject\\Stage2\\' #location where the source files exist
SaveFileDir = SourceDir + 'Save_File\\' #location where the save file exists
FrontEndMenuOptions = [1,2,3,4,8] #These are the valid selections for the Front end menu
UsageMenuOptions = [1,2,3,4,5,7,8] #These are the valid selections for the Usage menu
SortOrderOptions = [1,2] #These are the valid selections for ascending or decending order
StringMenuOpions = ['YES','NO','Y','N'] #These are the valid selections for Yes/No questions
PromptForDeviceName = 'Please enter a device name: '
PromptForMenuNumber = 'Please enter a number from the list: '
PromptForDateSortOrder = 'Choose 1 for Oldest to Newest or 2 for Newest to Oldest: '
PromptForUsageSortOrder = 'Choose 1 for Smallest to Largest or 2 for Largest to Smallest: '
PromptForLoad = 'CPObjectList is not empty are you sure you want to overwrite it with saved data? (Yes or No) '
PromptForSave = 'Are you sure you want to overwrite the existing save file? (Yes or No) '
PromptForExit = 'The data has not been saved.  Are you sure you want to continue without saving it? (Yes or No) '

LoadFrontEndMenu()
FrontEndMenu_UserInputEval(CPObjectList, FileSaved, GetUserMenuInput(PromptForMenuNumber, FrontEndMenuOptions, type_=int), PromptForMenuNumber, PromptForDeviceName)
