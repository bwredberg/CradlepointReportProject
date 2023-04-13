#This program opens a Cradlepoint daily stats CSV and adds a date column and rewrites the file
import csv
import os
import glob

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



