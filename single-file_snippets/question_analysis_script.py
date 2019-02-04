import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import json
import pandas as pd
import math



print('working from' + os.getcwd())

# params
LIST_OF_STATEMENTS = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
LIST_OF_NEGATIVE_STATEMENTS = ['S1', 'S2', 'S4', 'S6']
LIST_OF_VIDEO_PAIRS =[['010101', '010201'],['020101', '020201'],['020102','020202'],['030101','030201'],['030102','030202']]
ORDER_OF_VIDEOS ={'010101':0, '010201':1,'020101':2, '020201':3,'020102':4,'020202':5,'030101':6,'030201':7,'030102':8,'030202':9}
DATA_FILE_NAME = 'res-.csv'
EXCLUDE_IDS = [1, 2, 3]
LIST_OF_BAR_COLOURS = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'b', 'g', 'r', 'c']
LIST_OF_BAR_HATCHES = ['/', '-', '+', 'x', '\\', '*', 'o', 'O', '.']
LIST_OF_MARKER_STYLES = ['o', '^', 'v', 's', 'D', '*']
SHOW_PLOT1 = False
SHOW_PLOT2 = True
SHOW_PLOT3 = False
SHOW_PLOT4 = False

FLUSH_MEANS_TO_FILE = False

# classes


class Records:

    def __init__(self):
        self.videos = []

    def videoExists(self, id_in):
        for vid in self.videos:
            if vid[id] is id_in:
                return True
        return False

    def newVideo(self, rec_in):
        for vid in self.videos:
            if vid[id] == rec_in["'VID'"]:
                vid.newEntry(rec_in)
                return
        self.videos.append(Video(rec_in))


class Video:

    def __init__(self, rec_in):
        self.id = rec_in["'VID'"]
        self.S1 = [int(rec_in["'S1'"])]
        self.S2 = [int(rec_in["'S2'"])]
        self.S3 = [int(rec_in["'S3'"])]
        self.S4 = [int(rec_in["'S4'"])]
        self.S5 = [int(rec_in["'S5'"])]
        self.S6 = [int(rec_in["'S6'"])]
        self.entries = 1

    def __getitem__(self, id_in):
        return self.id

    def newEntry(self, rec_in):
        self.S1.append(int(rec_in["'S1'"]))
        self.S2.append(int(rec_in["'S2'"]))
        self.S3.append(int(rec_in["'S3'"]))
        self.S4.append(int(rec_in["'S4'"]))
        self.S5.append(int(rec_in["'S5'"]))
        self.S6.append(int(rec_in["'S6'"]))
        self.entries += 1


class Mean:

    def __init__(self, vid_id, statem, mean, std):
        self.id = vid_id
        self.order = ORDER_OF_VIDEOS[vid_id]
        self.statem = statem
        self.mean = mean
        self.std = std


# functions
def isIDExluded(id_in):
    for i in EXCLUDE_IDS:
        if i == int(row["'ID'"]):
            return True
    return False


#plots
def plot1():
    #
    # plot
    # barchart
    #  - original values ; with error bars
    ind1 = np.arange(len(means))  # the x locations for the groups
    width = 0.1  # the width of the bars
    fig1, ax1 = plt.subplots()

    i = 0
    for statement in LIST_OF_STATEMENTS:
        tmp = []
        labels = []
        stds = []
        for m in means:
            if m.statem == statement:
                tmp.append(m.mean)
                labels.append(m.id)
                stds.append(m.std)
        ind1 = np.arange(len(tmp))
        ax1.bar(ind1 - 0.3 + ((width) * i), tmp, width, yerr=stds, color=LIST_OF_BAR_COLOURS[i % 10], label=statement)
        i += 1
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax1.set_ylim(1, 5)   #y axis limits
    ax1.set_ylabel('Scores')
    ax1.set_xlabel('Video ID')
    ax1.set_title('Scores per Statement by Video ID')
    ax1.set_xticks(ind1)
    ax1.set_xticklabels(labels)
    ax1.legend()
    ax1.grid(which = 'major', axis='y', linestyle='--')
    plt.show()




def plot2():
    #
    # plot
    # barchart
    # - complementary values; without error bars
    ind2 = np.arange(len(means_compl))  # the x locations for the groups
    width = 0.1  # the width of the bars
    fig2, ax2 = plt.subplots()

    i = 0
    for statement in LIST_OF_STATEMENTS:
        tmp = []
        labels = []
        stds = []
        for m in means_compl:
            if m.statem == statement:
                tmp.append(m.mean)
                labels.append(m.id)
                stds.append(m.std)
        ind2 = np.arange(len(tmp))
        ax2.bar(ind2 - 0.3 + ((width) * i), tmp, width, color=LIST_OF_BAR_COLOURS[i % 10], edgecolor='black', label=statement)
        i += 1
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax2.set_ylim(1, 5)   #y axis limits
    ax2.set_ylabel('Scores (Complementary)')
    ax2.set_xlabel('Video ID')
    #ax2.set_title('Complementary Scores per Statement by Video ID')
    ax2.set_xticks(ind2)
    ax2.set_xticklabels(labels)
    ax2.legend(loc='upper right')
    ax2.grid(which = 'major', axis='y', linestyle='--')
    plt.show()


def plot3():
    #
    # plot
    # scatter
    # - complementary values; without error bars
    ind3 = np.arange(len(means_compl))  # the x locations for the groups
    width = 0.1  # the width of the bars
    fig3, ax3 = plt.subplots()

    i = 0
    for statement in LIST_OF_STATEMENTS:
        tmp = []
        labels = []
        stds = []
        for m in means_compl:
            if m.statem == statement:
                tmp.append(m.mean)
                labels.append(m.id)
                stds.append(m.std)
        jj = np.arange(len(tmp))
        ax3.scatter(jj , tmp, s = 50, marker = LIST_OF_MARKER_STYLES[i % 10], color=LIST_OF_BAR_COLOURS[i % 10], label = statement, alpha=1, edgecolors='none')
        i += 1
    # Add some text for labels, title and custom x-axis tick labels, etc.
    #ax3.tick_params=(axis='x', which ='both', length=6, width=2)
    ax3.set_ylim(1, 5)   #y axis limits
    ax3.set_ylabel('Scores (Complementary)')
    ax3.set_xlabel('Video ID')
    #ax2.set_title('Complementary Scores per Statement by Video ID')
    ax3.set_xticks(jj)
    ax3.set_xticklabels(labels)
    ax3.legend()
    ax3.grid(which = 'major', axis='y', linestyle='--')
    plt.show()


def plot4(video_ids):
    #
    # plot
    # radar
    # - complementary values; without error bars
    
    # ------- PART 1: Create background
   
    # number of variables
    N = len(LIST_OF_STATEMENTS)
    
    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]
    
    # Initialise the spider plot
    ax = plt.subplot(111, polar=True)
    
    # If you want the first axis to be on top:
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    
    # Draw one axe per variable + add labels labels yet
    plt.xticks(angles[:-1], LIST_OF_STATEMENTS)
    
    # Draw ylabels
    ax.set_rlabel_position(30)
    plt.yticks([0,1,2,3,4,5], [0,1,2,3,4,5], color="grey", size=7)
    plt.ylim(0,5)
    
    
    # ------- PART 2: Add plots
    
    # Plot each individual = each line of the data
    # I don't do a loop, because plotting more than 3 groups makes the chart unreadable

    tmp = []
    labels = []
    for statement in LIST_OF_STATEMENTS:
        for m in means_compl:
            if m.statem == statement and m.id == video_ids[0]:
                tmp.append(m.mean)
                labels.append(m.id)


    # Ind1
    values=tmp
    values += values[:1]
    ax.plot(angles, values, 'g', linewidth=1, linestyle='dashed', label=video_ids[0], marker='o', markersize=3)
    ax.fill(angles, values, 'g', alpha=0.05)
    

    tmp = []
    labels = []
    for statement in LIST_OF_STATEMENTS:
        for m in means_compl:
            if m.statem == statement and m.id == video_ids[1]:
                tmp.append(m.mean)
                labels.append(m.id)

    # Ind2
    values=tmp
    values += values[:1]
    ax.plot(angles, values, 'b', linewidth=1, linestyle='dashdot', label=video_ids[1], marker='o', markersize=3)
    ax.fill(angles, values, 'b', alpha=0.05)
    
    # Add legend
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
    plt.show()










# globals
sets = Records()

# ENTRY POINT

# openfile
with open(DATA_FILE_NAME) as csvfile:
    #iterate and parse
    reader = csv.DictReader(csvfile)
    for row in reader:
        if isIDExluded(int(row["'ID'"])):
            continue
        sets.newVideo(row)
        print(row)

#
# calc means
means = []
for vid in sets.videos:
    for s in LIST_OF_STATEMENTS:
        means.append(Mean(vid.id, s, np.mean(vid.__dict__[s]), np.std(vid.__dict__[s])))

#
# calc complementary means
vids_compl = {}
means_compl = []
for vid in sets.videos:
    for s in LIST_OF_STATEMENTS:
        vids_compl[s] = []
        if s in LIST_OF_NEGATIVE_STATEMENTS:
            for z in range(len(vid.__dict__[s])):
                vids_compl[s].append(6.0 - vid.__dict__[s][z])
        else:
            vids_compl[s] = vid.__dict__[s]
        means_compl.append(Mean(vid.id, s, np.mean(vids_compl[s]), np.std(vids_compl[s])))


#sort by video ID
#means_compl.sort(key=lambda x: x.id, reverse=False)
#means.sort(key=lambda x: x.id, reverse=False)
#sort by order
means_compl.sort(key=lambda x: x.order, reverse=False)
means.sort(key=lambda x: x.order, reverse=False)



#
# plot
# barchart
#  - original values ; with error bars
if SHOW_PLOT1:
    plot1()



#
# plot
# barchart
# - complementary values; without error bars
if SHOW_PLOT2:
    plot2()





#
# plot
# scatter
# - complementary values; without error bars
if SHOW_PLOT3:
    plot3()


#
# plot
# radar
# - complementary values; without error bars
if SHOW_PLOT4:
    plot4(LIST_OF_VIDEO_PAIRS[4])





print('done')



#other test stuff
if FLUSH_MEANS_TO_FILE:
    plimmplom = '['
    for juju in means:
        plimmplom += json.dumps(juju.__dict__)+',\n'
    plimmplom += ']'
    text_file.open("data_out.json", "w")
    text_file.write(plimmplom)
    text_file.close()
