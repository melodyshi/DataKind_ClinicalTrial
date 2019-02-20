#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 21:24:52 2018

This program performs basic data manipulation and wrangling for
a cancer clinical trial study records that has 10,000 rows.
It drops some columns and rows, computes duration between dates, and
separates data in a single column into multiple columns that are more 
appropriate and valueable for analytic purposes while keeping 
the original column.

* Step 1: Drop columns
* Step 2: Drop study records that are not "interventional"
* Step 3: Split column "Study Designs"
* Step 4: Add column "Intervention Methods"
* Step 5: Compute and add column "Duration (yr)"

The output is a CSV file named 'Data_after_processing.csv'

@author: Melody Shi
"""

import csv
import time
import datetime
from time import strptime

def get_index(header,columns):
    """
        Get a list of index of certain columns in the table header
        
        Parameters
        ----------
        header: list
            a table header
        columns: list
            column names in the header that the user wants to get indices for
               
        Returns
        -------
        index_list: list
            a list of indices
    """
    index_list = []
    for col in columns:  
        index_list.append(header.index(col))
    return index_list

def drop_cols(row,index_to_drop):
    """
        Drop entries in a row
        
        Parameters
        ----------
        row: list
            a row in a table
        index_to_drop: list
            indices of entries that the user wants to drop
               
        Returns
        -------
        row: list
            the row after certain entries are dropped
    """
    ele_to_remove = []
    for index in index_to_drop:
        ele_to_remove.append(row[index])
    for ele in ele_to_remove:
        row.remove(ele)
    return row

def add_cols(row,cols_to_add):
    """
        Add entries in a row
        
        Parameters
        ----------
        row: list
            a row in a table
        cols_to_add: list
            column names to add
               
        Returns
        -------
        row: list
            the row after columns are added
    """
    for col in cols_to_add:
        row.append(col)
    return row

def select_entry(row, header, feature):
    """
        Select an entry in a row
        
        Parameters
        ----------
        row: list
            a row in a table
        header: list
            the table header
        feature: str
            a column name the user wants to select
               
        Returns
        -------
        entry: str
            an entry in a row that is selected
    """
    return row[header.index(feature)]

def insert_entry(row,header,feature,entry):
    """
        Insert an entry in a row, append 'null's to the end to make the header
        and the row are of the same length
        
        Parameters
        ----------
        row: list
            a row in a table
        header: list
            the table header
        feature: str
            a column name the user wants to insert entry for
        entry: str
            a value to be inserted into an entry
            
        Returns
        -------
        row: list
            the row after an entry is inserted
    """
    add_null = len(header) - len(row)
    if add_null != 0:
        for i in range(add_null):
            row.append('null')
        row[header.index(feature)] = entry
    else:
        row[header.index(feature)] = entry
    return row

def split_multivalue_entry(row, header, feature):
    """
        Create a dictionary that describes a multi-value entry
        
        Parameters
        ----------
        row: list
            a row in a table
        header: list
            the table header
        feature: str
            a column name the user wants to create a dictionary for
            
        Returns
        -------
        dictionary: dict
          
    """
    entry = select_entry(row,header,feature)
    item_list = entry.strip().split('|') # split by '|' and get items 
    dictionary = {}
    for item in item_list:
        key_value_list = item.split(':')
        try:
            # first item in the list is key, second is value
            dictionary[key_value_list[0].strip()] = [key_value_list[1].strip()]
        except:
            dictionary[key_value_list[0].strip()].append(key_value_list[1].strip())
    return dictionary

def to_datetime(raw_date):
    """
        Convert an unstructured date string to a datetime object
        
        Parameters
        ----------
        raw_date: str
            a date string in the row
            
        Returns
        -------
        date_obj: datetime object
          
    """
    date_list = raw_date.replace(",","").split() # remove the commar and split by space
    day = 15 # day defaults to 15 to deal with missing day values
    
    if len(date_list) == 2: # if only month and year are available
        mon = date_list[0]
        year = int(date_list[1].strip())
    elif len(date_list) == 3: # if month, day and year are all available
        mon = date_list[0].strip()
        day = int(date_list[1].strip())
        year = int(date_list[2].strip())

    mon = strptime(mon,"%B").tm_mon # convert month name to an integer representing the month
    date_obj = datetime.date(year,mon,day) # build a datetime object
    return date_obj

def main():
    output = 'Data_after_processing2.csv'
    with open('Raw_ClinicalTrial.csv',encoding='utf-8',errors='ignore') as f1, open(output,'w', newline='') as f2:
        reader = csv.reader(f1,delimiter=',')
        spamwriter = csv.writer(f2, delimiter=',')
        
        # instantiate counters
        counter = 0 
        dropped_records = 0
        processed_rows = 0
        header = []
        index_to_drop = []
        
        for row in reader:

            # print progress message after processing every 100 records
            if counter == 100:
                time.sleep(0.05) # slow down the progress for the user to glance through progress message
                counter = 0
                print("...{:.2f}% done, processed {} rows".format((processed_rows/10000)*100, processed_rows))
            
            # get header, only execute once in the loop
            if processed_rows == 0:
                header += row         
                counter += 1
                processed_rows += 1
                continue
            
            # drop and add new columns in the header, only execute once in the loop
            if index_to_drop == []:
                
                # drop columns
                print('''......Dropping columns\n''')
                index_to_drop = get_index(header, ['Rank','Acronym','Status',
                                                     'Sponsor/Collaborators','Locations','Funded Bys',
                                                     'Other IDs','Study Documents',
                                                   'URL','First Posted', 'Results First Posted', 'Last Update Posted'])
                header = drop_cols(header,index_to_drop)
                time.sleep(1) # pause a second for the user to read the process
                
                print("......Dropping study records\n")
                time.sleep(1)
                # break up columns with multi-value entries
                print('''......Splitting column: 'Study Design'\n''')
                cols_to_add = ['Allocation','Intervention Model',
                'Masking','Primary Purpose']      
                header = add_cols(header,cols_to_add)
                time.sleep(1)
                
                print("......Adding column: 'Intervention Methods'\n")
                header = add_cols(header,['Intervention Methods'])
                time.sleep(1)
                
                print("......Computing and adding column: 'Duration (yr)'\n")
                header = add_cols(header,['Duration (yr)'])
                time.sleep(1)
                
                # write the header
                spamwriter.writerow(header)
                print("Total records to process: 10000")
                print()
                time.sleep(1)
                
                continue

            # drop columns in every row
            row = drop_cols(row,index_to_drop)
            
            # only keep study records of type 'Interventional', drop observational studies for now
            if select_entry(row,header,'Study Type').strip() != 'Interventional':
                dropped_records += 1
                processed_rows += 1
                counter += 1
                continue
            
            # split a multi-value column 'Study Design' into new columns 'Allocation',
            # 'intervention Model','Masking','Primary Purpose'
            # while keeping the original column
            try:
                interventional_dict = split_multivalue_entry(row, header, 'Study Designs')
            except:
                dropped_records += 1
                processed_rows += 1
                counter += 1
                continue 
            
    
            try:
                row = insert_entry(row,header,'Allocation','|'.join(interventional_dict['Allocation']))
            except:
                pass # entry defaults to 'null' for any missing key or value
            try:
                row = insert_entry(row,header,'Intervention Model','|'.join(interventional_dict['Intervention Model']))
            except:
                pass            
            try:
                row = insert_entry(row,header,'Masking','|'.join(interventional_dict['Masking']))
            except:
                pass                
            try:
                row = insert_entry(row,header,'Primary Purpose','|'.join(interventional_dict['Primary Purpose']))
            except:
                pass 
            
            # Add a new column 'Intervention Methods' based on 'Interventions'
            # while keeping the original column
            try:
                intervention_methods = '|'.join(split_multivalue_entry(row,header,'Interventions').keys())
                row = insert_entry(row,header,'Intervention Methods',intervention_methods)
            except:
                dropped_records += 1
                processed_rows += 1
                counter += 1
                continue
            
            # Compute and add a new column 'Duration (yr)'
            try:
                start_date = to_datetime(select_entry(row, header, 'Start Date'))
                completion_date = to_datetime(select_entry(row, header,'Completion Date'))
                duration_day = (completion_date-start_date).days # get duration in days
                duration_year = int(round(duration_day/30/12)) # round to years
            except:
                duration_year = "null"

            row = insert_entry(row,header,'Duration (yr)',duration_year)
            
                
            processed_rows += 1
            counter += 1
            
            # after processing a row, write it
            spamwriter.writerow(row)
        
        # after exiting for loop, print the last progress message, should be 100% done
        print("...{:.2f}% done, processed {} rows".format((processed_rows/10000)*100, processed_rows))
        print()
        print('Total records dropped: '+str(dropped_records))
        print('Remaining records: '+str(10000 - dropped_records))
        print('Please see output file: '+output)
 
if __name__ == "__main__":
    main()
