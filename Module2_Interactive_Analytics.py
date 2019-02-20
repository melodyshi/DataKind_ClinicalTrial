#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 08:28:52 2018

This program supports two functionalities:
* Plotting horizontal bar charts
* Plotting heatmaps

It is user interactive. The user can choose from the engines and 
a list of cancers to generate visualization based on a preprocessed 
Cancer Clinical Trial Dataset.

Overview of dataset:

* NCT Number
* Title
* Study Results
* Conditions
* Interventions
* Outcome Measures
* Gender
* Age
* Phases
* Enrollment
* Study Type
* Study Designs
* Start Date
* Primary Completion Date
* Completion Date
* Allocation
* Intervention Model
* Masking
* Primary Purpose
* Intervention Methods
* Duration (yr)

Note: Please install/UPDATE all packages required to run the program

@author: Melody
"""
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

matplotlib.style.use('ggplot') # look pretty


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

def compute_average(num_list):
    """
        Compute the mean of a list of numbers
        
        Parameters
        ----------
        num_list: list
            a list of numbers
               
        Returns
        -------
        mean: float
            mean of the list of numbers
    """
    sum = 0
    count = 0
    for num in num_list:
        sum += int(num)
        count += 1
    return sum/count
def cancer_to_average_duration(): 
    """
        Get average trial duration in years grouped by cancer type in the dataset

        Returns
        -------
        cancer_to_duration: dict
            a dictionary of cancer type as keys to average trial duration as values
    """
    with open('Data_after_processing.csv',encoding='utf-8',errors='ignore') as f:
        reader = csv.reader(f,delimiter=',')
        header = []
        get_header = True
        cancer_to_duration = {}
        for row in reader:
            # get header, only execute once in the loop
            if get_header:
                header += row
                get_header = False
                continue
            conditions, duration = select_entry(row, header, 'Conditions'),select_entry(row, header, 'Duration (yr)')
            if duration == 'null':
                continue
            
            # split, get duration as a list if there are multiple conditions in an entry
            if '|' in conditions:
                for condition in conditions.split('|'):
                    if condition.strip() not in cancer_to_duration:
                        cancer_to_duration[condition.strip()] = [duration]
                    else:
                        cancer_to_duration[condition.strip()].append(duration)
            else:
                if conditions.strip() not in cancer_to_duration:
                    cancer_to_duration[conditions.strip()] = [duration]
                else:
                    cancer_to_duration[conditions.strip()].append(duration)
                    
    # compute the average duration for each cancer
    for key in cancer_to_duration:
        average = compute_average(cancer_to_duration[key])
        cancer_to_duration[key] = average
    return cancer_to_duration
        
        
def cancer_to_frequency(): 
    """
        Count study records grouped by cancer type

        Returns
        -------
        cancer_to_frequency: dict
            a dictionary of cancer type as keys to number of trials as values
    """
    with open('Data_after_processing.csv',encoding='utf-8',errors='ignore') as f:
        reader = csv.reader(f,delimiter=',')
        header = []
        get_header = True
        cancer_to_frequency = {}
        for row in reader:
            if get_header:
                header += row
                get_header = False
                continue
            conditions = select_entry(row, header, 'Conditions')
            
            # split, count records if there are multiple conditions in an entry
            if '|' in conditions:
                for condition in conditions.split('|'):
                    if condition.strip() not in cancer_to_frequency:
                        cancer_to_frequency[condition.strip()] = 1
                    else:
                        cancer_to_frequency[condition.strip()] += 1
            else:
                if conditions.strip() not in cancer_to_frequency:
                    cancer_to_frequency[conditions.strip()] = 1
                else:
                    cancer_to_frequency[conditions.strip()] += 1
    return cancer_to_frequency

def cancer_to_intervention_percentage(cancer_count):
    """
        Get cancer to intervention methods to intervention utilization
        
        Parameters
        ----------
        cancer_count: dict
            a dictionary returned by calling cancer_to_frequency
            
        Returns
        -------
        cancer_to_intervention_percentage: dict
            a dictionary of dictionary           
                Cancer type being the first layer keys 
                Intervention Methods being the second layer keys
                Intervention utilization(percentage) grouped by cancer and intervention methods as values
    """
    with open('Data_after_processing.csv',encoding='utf-8',errors='ignore') as f:
        reader = csv.reader(f,delimiter=',')
        header = []
        get_header = True
        cancer_to_intervention_percentage = {}
        
        # make a copy of cancer to frequency, update later to be cancer to intervention methods
        cancer_count_copy = cancer_count.copy() 
        for key in cancer_count_copy:
            # clear the original value, substituted by an empty dictionary
            cancer_count_copy[key] = {}
            
        for row in reader:
            # get header, only execute once in the loop
            if get_header:
                header += row
                get_header = False
                continue           
            conditions, interventions = select_entry(row, header, 'Conditions'),select_entry(row, header, 'Intervention Methods')
            
            # split if the entry has multiple conditions
            if '|' in conditions:    
                for condition in conditions.split('|'):
                    condition = condition.strip()
                    
                    # split if the entry has multiple interventions,
                    # get number of each intervention utilized for a certain cancer
                    if '|' in interventions:
                        for intervention in interventions.split("|"):
                            intervention = intervention.strip()
                            if intervention in cancer_count_copy[condition]:
                                cancer_count_copy[condition][intervention] += 1

                            else:
                                cancer_count_copy[condition][intervention] = 1   

                    else:
                        intervention = interventions.strip()
                        if intervention in cancer_count_copy[condition]:
                            cancer_count_copy[condition][intervention] += 1
                        else:
                            cancer_count_copy[condition][intervention] = 1
           
            else:
                condition = conditions.strip()
                if '|' in interventions:
                    for intervention in interventions.split("|"):
                        #print(intervention)
                        intervention = intervention.strip()
                        if intervention in cancer_count_copy[condition]:
                            cancer_count_copy[condition][intervention] += 1
                        else:
                            cancer_count_copy[condition][intervention] = 1                        
                else:
                    intervention = interventions.strip()
                    if intervention in cancer_count_copy[condition]:
                        cancer_count_copy[condition][intervention] += 1
                    else:
                        cancer_count_copy[condition][intervention] = 1
    
    # make a copy of cancer to intervention methods to count dictionary
    # update later to get cancer to intervention percentage
    cancer_to_intervention_percentage = cancer_count_copy.copy()
    
    # get intervention utilization using intervention method count/total cancer type
    for condition in cancer_count_copy:
        cancer_num = cancer_count[condition]
   
        for intervention in cancer_count_copy[condition]:
            cancer_to_intervention_percentage[condition][intervention] = cancer_count_copy[condition][intervention]/cancer_num
    return cancer_to_intervention_percentage


def draw_hbar(choice_of_cancers=None):
    """
        Plot a horizontal bar chart based on user's choice of cancers
        
        Parameters
        ----------
        choice_of_cancers: list (Optional, defaults to None)
            a list of cancers the the user chooses

    """    
    plt.clf()
    cancer_duration_dict = cancer_to_average_duration()
    
    if choice_of_cancers == None:
        choice_of_cancers = ['Breast Cancer','Pancreatic Cancer','Lung Cancer','Colon Cancer',
     'Bladder Cancer','Liver Cancer','Brain Cancer','Skin Cancer','Prostate Cancer',
     'Colorectal Cancer','Head and Neck Cancer','Ovarian Cancer']
        
    duration_list = [cancer_duration_dict[key] for key in choice_of_cancers]
    group_mean = compute_average(duration_list)
    
    #fig, ax = plt.subplots(figsize=(20,10))
    #plt.figure(figsize=(25,10))
    

    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    #label the figure
    plt.xlabel('Avg. Trial Duration (in Yrs)')
    plt.title('Cancer by Avg. Trial Duration')
    plt.axvline(group_mean, ls='--', color='m')
    plt.barh(choice_of_cancers, duration_list)
    #plt.rcParams['figure.figsize'] = (500,500)
    #plt.rcParams['figure.autolayout'] = True
    plt.tight_layout()
    plt.savefig("h-bar.png")
    
    plt.show()
    #plt.close()

def draw_heatmap(choice_of_cancers=None):
    """
        Plot a heatmap based on user's choice of cancers
        
        Parameters
        ----------
        choice_of_cancers: list (Optional, defaults to None)
            a list of cancers the the user chooses

    """  
    plt.clf()
    cancer_count = cancer_to_frequency()
    master_dict = cancer_to_intervention_percentage(cancer_count)
    
    # default choice is all cancers
    if choice_of_cancers == None:
        choice_of_cancers = ['Breast Cancer','Pancreatic Cancer','Lung Cancer','Colon Cancer',
     'Bladder Cancer','Liver Cancer','Brain Cancer','Skin Cancer','Prostate Cancer',
     'Colorectal Cancer','Head and Neck Cancer','Ovarian Cancer']

    intervention_list = ['Behavioral','Biological','Device','Genetic','Procedure','Radiation']
    
    # build a 2d numpy array to parse in as heatmap parameter
    percentage_list_2d = []
    for cancer in choice_of_cancers:
        percentage_list = []
        for intervention in intervention_list:
            if intervention in master_dict[cancer]:
                percentage_list.append(master_dict[cancer][intervention])
            else:
                percentage_list.append(0)
        percentage_list_2d.append(percentage_list)
    percentage_array = np.array(percentage_list_2d)
    
    # plot setting
    #
    fig, ax = plt.subplots(figsize=(25, 10))
    ax.xaxis.tick_top() # xlabels on the top
    sns.set(font_scale=1.4)
    fig = sns.heatmap(percentage_array, annot=True, 
                annot_kws={"size": 20},linewidths=2, linecolor='white',
               xticklabels = intervention_list,
               yticklabels = choice_of_cancers,cmap='Oranges',
               cbar_kws={'label': 'Intervention Utilization'})
    ax.set_title('Non-Drug Intervention by Cancer')
    plt.xticks(rotation=45) # xlabels rotated a little bit
    
    plt.tight_layout()# avoid cutting off x-labels when saving the figure
    
    output = fig.get_figure()

    output.savefig("heatmap.png")
    plt.show()
    #plt.close()

def main():
    """
        The user-interactive main function of the program.
        Prompt the user for choices of engine and a list of cancers for visualization
    """ 
    print()
    print("This program generates two types of graphs based on Cancer Clinical Trial Dataset:")
    print()
    print("* 1. Horizontal Bar Chart: Cancer by Avg. Trial Duration")
    print("* 2. Heatmap: Non-Drug Intervention Utilization by Cancer")
    print("===============================================")
    
    while True:
        choice_of_engine = input("Please enter your choice of engine(1/2): ")
        if choice_of_engine not in ['1','2']:
            print("===================ERROR=======================")
            print("This is not a valid choice. Try again.")
            print()
            continue
        else:
            break

    print()
    print("===============================================")
    print("Please choose from a list of cancers to create the graph:")
    print()
    print("* 1. Breast Cancer")
    print("* 2. Pancreatic Cancer")
    print("* 3. Lung Cancer")
    print("* 4. Colon Cancer")
    print("* 5. Bladder Cancer")
    print("* 6. Liver Cancer")
    print("* 7. Brain Cancer")
    print("* 8. Leukemia")
    print("* 9. Prostate Cancer")
    print("* 10. Colorectal Cancer")
    print("* 11. Head and Neck Cancer")
    print("* 12. Ovarian Cancer")
    print()
    print("Please select at least 3 cancers for better visualization.")    
    
    while True:
        print("===============================================")
        print("Enter your choice, separated by commar (e.g. 1,2,3). ")
        print()
        print("To choose all, simply press enter. ")
        print()
        
        user_choice = input("Enter \"quit\" to exit the program: ")
        
        if user_choice.lower() == 'quit':
            break
        
        if user_choice == "":

            if choice_of_engine == '1':
                print("===============================================")
                print("...generating horizontal bar graph")
                draw_hbar()
                print("Please see 'h_bar.png' for output chart.")
                break
            elif choice_of_engine == '2':
                print("===============================================")
                print("...generating heatmap")
                draw_heatmap()
                print("Please see 'heatmap.png' for output chart.")
                break
            
        keepGoing = False
        for choice in user_choice.split(","):
            choice = choice.strip()
            if not choice.isnumeric():
                print("===================ERROR=======================")
                print("This is not a valid choice. Try again.")
                print()
                keepGoing = True
                break
                
            if int(choice) > 12 or int(choice) < 1:
                print("===================ERROR====================")
                print("Choice must be between 1 and 12, inclusive. Try again.")
                print()
                keepGoing = True
                break
        if keepGoing:
            continue

        all_choice = ['Breast Cancer','Pancreatic Cancer','Lung Cancer','Colon Cancer',
     'Bladder Cancer','Liver Cancer','Brain Cancer','Leukemia','Prostate Cancer',
     'Colorectal Cancer','Head and Neck Cancer','Ovarian Cancer']
        
        choice_of_cancers = [all_choice[int(choice.strip())-1] for choice in user_choice.split(",")]

        if choice_of_engine == '1':
            print("===============================================")
            print("...generating horizontal bar graph")
            draw_hbar(choice_of_cancers = choice_of_cancers)
            print("Please see 'h_bar.png' for output chart.")
            break
            
        elif choice_of_engine == '2':
            print("===============================================")
            print("...generating heatmap")
            draw_heatmap(choice_of_cancers = choice_of_cancers)
            print("Please see 'heatmap.png' for output chart.")
            break
            
     
if __name__ == "__main__":
    main()
            
   
        
