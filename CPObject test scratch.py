#CP1 = CP_Usage("CP1")
#CP2 = CP_Usage("CP2")
#CP3_1 = CP_Usage("CP3-1")

#CP2.AddUsage('5/7/9',092.1)
#CP2.AddUsage('3/30/23',783.209)
#CP2.AddUsage('4/22/2009',234.18)
#CP1.AddUsage('3/30/23',198.239)
#CP1.AddUsage('3/4/23',23.289)
#CP1.AddUsage('9/20/1975',395.57)
#CP1.AddUsage('4/28/2021',162.39)
#CP1.AddUsage('10/8/2004',167.235)
#CP1.AddUsage('5/9/07',89.12)
#CP1.AddUsage('10/28/2010',1874.97)
#CP1.AddUsage('11/19/1975',36)
#CP3_1.AddUsage('9/9/09',923)
#CP3_1.AddUsage('3/4/21',560.34)


#CPObjectList.append(CP1)
#CPObjectList.append(CP2)
#CPObjectList.append(CP3_1)


def ShowUsageRaw(ObjName):
    #ObjName must be a string
    #Shows full table unsorted
    for n in range(0,len(CPObjectList)):
        if str(ObjName) in CPObjectList[n].name:
            print(f'\nCradlepoint {CPObjectList[n].name} raw usage data')
            print(f'----------------------------------')
            print(CPObjectList[n].DataUsage)
            return
    print (f'**ShowUsageRaw ERROR** Cradlepoint {ObjName} does not exist')
    return 'ERROR'

   
def ShowUsageByDate(ObjName, asc_order = True):
    #ObjName must be a string
    #sort values by Date column
    Sort_text = 'oldest to newest'
    if not asc_order:
        Sort_text = 'newest to oldest'
    for n in range(0,len(CPObjectList)):
        if str(ObjName) in CPObjectList[n].name:
            CPObjectList[n].DataUsage.sort_values(by='Date', ascending=asc_order, inplace=True)
            print(f'\nCradlepoint {CPObjectList[n].name} data usage sorted by Date - {Sort_text}')
            print(f'----------------------------------')
            print(CPObjectList[n].DataUsage)
            return
    print (f'**ShowUsageByDate ERROR** Cradlepoint {ObjName} does not exist')


def ShowUsageByUsage(ObjName, asc_order = True):
    #ObjName muszt be a string
    #sort values by Usage column
    Sort_text = 'smallest to largest'
    if not asc_order:
        Sort_text = 'largest to smallest'
    for n in range(0, len(CPObjectList)):
        if str(ObjName) in CPObjectList[n].name:
            CPObjectList[n].DataUsage.sort_values(by='MB_Used', ascending=asc_order, inplace=True)
            print(f'\nCradlepoint {CPObjectList[n].name} data usage sorted by Usage Amount - {Sort_text}')
            print(f'---------------------------------------------------------')
            print(CPObjectList[n].DataUsage) 
            return
    print (f'**ShowUsageByUsage ERROR** Cradlepoint {ObjName} does not exist') 


    def OutputObjectInfo(TestObjNum):
    #Prints out details based on the index number from CPObjectList
    print(f'\n\n************************************')
    print(f'This is the output for {CPObjectList[TestObjNum].name}\n{CPObjectList[TestObjNum].DataUsage}\n')
    print(f'Total Usage (MB)\t\t{round(CPObjectList[TestObjNum].TotalUsage, 2):,} \nNumber of Entries\t\t{CPObjectList[TestObjNum].NumberOfEntries:,} \nAverage (MB)\t\t\t{round(CPObjectList[TestObjNum].AvgUsage, 2):,}')
    print(f'Highest 24h Usage (MB)\t\t{round(CPObjectList[TestObjNum].HighUsage, 2):,} \nDate of Highest 24h Usage\t{CPObjectList[TestObjNum].HighUsageDate}')


    # -=-=-=Dictionary work I started with=-=-=-
    #
    #def AddUsageDict(self, date, usage):
    #    self.DataUsage[date] = usage
    #def ShowUsageDict(self):
    #    print(f'Cradlepoint {self.name} data usage')
    #    print(f'----------------------------------')
    #    for date in self.DataUsage:
    #        print(f'Date: {date} Usage: {self.DataUsage[date]}')


def ShowUsageRawByIndex(ObjList, Index, max_rows):
    #ObjList should be CPObjectList
    #Index must be an int
    #ObjList[Index].DataUsage.set_option('display.max_rows', 500)
    #pd.set_option('display.max_columns', 500)
    #pd.set_option('display.width', 1000)
    if Index >= 0 and Index <= len(ObjList):
        print(f'\nCradlepoint {ObjList[Index].name} raw usage data')
        print(f'----------------------------------')
        with pd.option_context('display.max_rows', max_rows):
            print(ObjList[Index].DataUsage)
        return
    elif Index == -1:
        print(f'No Cradlepoint found by that name')
        return
    else:
        print (f'**ShowUsageRawByIndex ERROR** There is no Cradlepoint at index {Index}')
        return

def ShowUsageByDateByIndex(ObjList, Index, asc_order_int = 1, max_rows=0):
    #ObjList should be CPObjectList
    #Index must be an int
    #asc_order_int is either 1 or 2, if it is anything other than 2 consider it 1
    #max_rows is an int - how many rows to display in the resulting output
    #sort values by Date column
    Sort_text = 'oldest to newest'
    asc_order = True
    if int(asc_order_int) == 2:
        Sort_text = 'newest to oldest'
        asc_order = False
    if Index >= 0 and Index <= len(ObjList):
        ObjList[Index].DataUsage.sort_values(by='Date', ascending=asc_order, inplace=True)
        print(f'\nCradlepoint {ObjList[Index].name} data usage sorted by Date - {Sort_text}')
        print(f'----------------------------------')
        if max_rows == 0:
            max_rows = None
            #This option prints all rows in the df
            with pd.option_context('display.max_rows', max_rows):
                print(ObjList[Index].DataUsage)
        else:
            #This option prints only the number of rows specified from the top of the list
            print(ObjList[Index].DataUsage.head(max_rows))
        return
    elif Index == -1:
        print(f'No Cradlepoint found by that name')
        return
    else:    
        print (f'**ShowUsageByDateByIndex ERROR** There is no Cradlepoint at the index {Index}')
        return
 
def ShowUsageByUsageByIndex(ObjList, Index, asc_order_int = 1):
    #ObjList should be CPObjectList
    #Index must be an int
    #asc_order_int is either 1 or 2, if it is anything other than 2 consider it 1 
    #sort values by Usage column
    Sort_text = 'smallest to largest'
    asc_order = True
    if int(asc_order_int) == 2:
        Sort_text = 'largest to smallest'
        asc_order = False
    if Index >= 0 and Index <= len(ObjList):
        ObjList[Index].DataUsage.sort_values(by='MB_Used', ascending=asc_order, inplace=True)
        print(f'\nCradlepoint {ObjList[Index].name} data usage sorted by Usage Amount - {Sort_text}')
        print(f'---------------------------------------------------------')
        print(ObjList[Index].DataUsage) 
        return
    elif Index == -1:
        print(f'No Cradlepoint found by that name')
        return
    else:
        print (f'**ShowUsageByUsageByIndex ERROR** There is no Cradlepoint at the index {Index}') 
        return

def ShowUsageGreaterThanByIndex(ObjList, Index, value):
    #ObjList should be CPObjectList
    #Index must be an int
    #value is the number of MB for which we are finding items greater than
    #Currently not sorted
    if Index >= 0 and Index <= len(ObjList):
        output = ObjList[Index].DataUsage.query('MB_Used >= @value')
        if not output.empty:
            print(f'\nCradlepoint {ObjList[Index].name} data usage greater than {value}')
            print(f'==============================================')
            print(output)
            return
        else:
            print(f'\nThere are no entries greater than or equal to {value}MBs for that Cradlepoint')
            return
    elif Index == -1:
        print(f'No Cradlepoint found by that name')
        return
    else:    
        print (f'**ShowUsageGreaterThan ERROR** There is no Cradlepoint at the index {Index}')
        return

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