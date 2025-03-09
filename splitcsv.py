import os
import csv

#currentdirpath = os.getcwd()
#filename = 'argos.csv'
#file_path = os.path.join(os.getcwd(), filename) #filepath to open

def get_file_path(filename):
    ''' - This gets the full path...file and terminal need  to be in same directory - '''
    file_path = os.path.join(os.getcwd(), filename)
    return file_path

pathOfFile = get_file_path('azurecosts.csv')
''' - Below opens and reads the csv file, then going to try to loop and write the rows out in files sorted by Billing Number - '''
with open(pathOfFile, 'rU') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)
    for row in reader:
        new_file_name = row[5][:5] + '.csv'
    ''' Create file named by billing number, and print the header to each file '''
    fb = open(new_file_name, 'w+')
    fb.write(str(header) + '\n')
    #fb.close()
with open(pathOfFile, 'rU') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        new_file_name = row[5][:5] + '.csv'
        ab = open(new_file_name, 'a')
        ab.write(str(row) + '\n')