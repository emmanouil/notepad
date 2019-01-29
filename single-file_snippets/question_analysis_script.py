import os
import csv
import numpy as np
import matplotlib.pyplot as plt

print('working from'+os.getcwd())

#params
LIST_OF_STATEMENTS = ['S1','S2','S3','S4','S5','S6']
DATA_FILE_NAME = 'res-.csv'
EXCLUDE_IDS = [1, 2, 3]
LIST_OF_BAR_COLOURS = ['b', 'g','r','c','m','y','k','b', 'g','r','c']

#classes
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
        self.statem = statem
        self.mean = mean
        self.std = std


#functions
def isIDExluded(id_in):
    for i in EXCLUDE_IDS:
        if i == int(row["'ID'"]):
            return True
    return False


#globals
sets = Records()



#ENTRY POINT

#openfile
with open(DATA_FILE_NAME) as csvfile:
#iterate and parse
    reader = csv.DictReader(csvfile)
    for row in reader:
        if isIDExluded(int(row["'ID'"])):
            continue
        sets.newVideo(row)
        print(row)

#calc means
means = []
for vid in sets.videos:
    for s in LIST_OF_STATEMENTS:
        means.append(Mean(vid.id, s, np.mean(vid.__dict__[s]), np.std(vid.__dict__[s])))

#plot
ind = np.arange(len(means))  # the x locations for the groups
width = 0.2  # the width of the bars
fig, ax = plt.subplots()


i = 0
for statement in LIST_OF_STATEMENTS:
    i+=1
    tmp = []
    labels = []
    stds = []
    for m in means:
        if m.statem == statement:
            tmp.append(m.mean)
            labels.append(m.id)
            stds.append(m.std)
    ind = np.arange(len(tmp))
    ax.bar(ind + ((width/2)*i) , tmp, width, yerr=stds, color=LIST_OF_BAR_COLOURS[i%10], label=statement)
    i+=1
# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Scores')
ax.set_title('Scores by group and gender')
ax.set_xticks(ind)
ax.set_xticklabels(('G1', 'G2', 'G3', 'G4', 'G5'))
ax.legend()
plt.show()
print('done')
