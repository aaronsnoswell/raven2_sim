import sys
import os
import csv
import math
import shelve
from statistics import mean, stdev
from operator import add, sub, mul
import matplotlib.pyplot as plt


shelve_file = 'data.shelve'
# Main Code Starts Here
def parse_latest_run(reader):

    indices = [0,1,2,4,5,6,7]
    runlevel = 0
    packet_no = 111
    line_no = 0
    headers = reader.next()
    #print headers
    # Find the indices for the variables in the datashee
    runlevel_index = headers.index('field.runlevel'); 
    packet_index = headers.index('field.last_seq'); 
    mpos_index = headers.index('field.mpos0');
    dmpos_index = headers.index('field.mpos_d0');
    mvel_index = headers.index('field.mvel0');
    dmvel_index = headers.index('field.mvel_d0');
    dac_index = headers.index('field.current_cmd0');
    jpos_index = headers.index('field.jpos0');
    djpos_index = headers.index('field.jpos_d0');
    dpos_index = headers.index('field.pos_d0');
    pos_index = headers.index('field.pos0');
    try:
        err_index = headers.index('field.err_msg');
    except:
        err_index = -1

    # Skip the datasheet lines until runlevel = 3 and packet number is 1
    while (runlevel < 3) or (packet_no == 111) or (packet_no == 0):
        line = reader.next()
        runlevel = int(line[runlevel_index])
        packet_no = int(line[packet_index])
        #print runlevel
        line_no = line_no + 1
    print '\rStarted at Line = '+ str(line_no)+ ', Packet = '+str(packet_no)+', Run Level = '+str(runlevel)

    # Get the estimated desired and actual trajectories from the last run 
    est_dmpos = [[],[],[],[],[],[],[]] 
    est_mpos = [[],[],[],[],[],[],[]]
    est_mvel = [[],[],[],[],[],[],[]]
    est_dac = [[],[],[],[],[],[],[]]
    est_djpos = [[],[],[],[],[],[],[]]
    est_jpos = [[],[],[],[],[],[],[]]
    est_dpos = [[],[],[]]
    est_pos = [[],[],[]]
    err_msg = []
    packet_nums = []
    time = []

    i = 0
    past_line = ''
    for l in reader:
        # We are going to compare estimated ones, so shift one sample ahead
        if (i > 1) and (int(l[runlevel_index]) == 3):  
            if not(packet_no == int(l[packet_index])):	
                packet_nums.append(packet_no)
                time.append(float(line[0])-t0)
                for j in range(0,7):			
                    est_dmpos[j].append(float(line[dmpos_index+indices[j]])*math.pi/180)
                    est_mpos[j].append(float(line[mpos_index+indices[j]])*math.pi/180)
                    est_mvel[j].append(float(line[mvel_index+indices[j]])*math.pi/180)
                for j in range(0,7):
                    est_dac[j].append(float(line[dac_index+indices[j]]))
                for j in range(0,7):
                    est_djpos[j].append(float(line[djpos_index+indices[j]])*math.pi/180)
                    est_jpos[j].append(float(line[jpos_index+indices[j]])*math.pi/180)
                for j in range(0,3):
                    est_dpos[j].append(float(line[dpos_index+indices[j]])*math.pi/180)
                    est_pos[j].append(float(line[pos_index+indices[j]])*math.pi/180)
                try:			
                    err_msg.append(str(line[err_index]))
                except:
                    pass
            line = l
            packet_no = int(line[packet_index])
        else:
            t0 = float(line[0])
        i = i + 1;
    print len(est_mvel[0])
    print len(est_mpos[0])
    return est_mpos, est_mvel, est_dac, est_jpos, est_pos, err_msg, packet_nums, time 

def plot_pos(gold_pos, orig_pos, pos):
    f4, axarr4 = plt.subplots(3, 1, sharex=True)
    axarr4[0].set_title("End-Effector Positions (Gold Arm)")
    pos_labels = ['X','Y','Z']
    for j in range(0,3):
        axarr4[j].plot(gold_pos[j], 'g')
        axarr4[j].plot(orig_pos[j], 'k')
        axarr4[j].plot(pos[j], 'r')
        axarr4[j].set_ylabel(pos_labels[j])
    plt.show()
    return f4

def plot_pos_stdev(pos_stdev, pos_mean):
    f4, axarr4 = plt.subplots(3, 2, sharex=True)
    axarr4[0][0].set_title("End-Effector Positions (STDEV)")
    axarr4[0][1].set_title("End-Effector Positions (MEAN +- STDEV)")
    pos_labels = ['X','Y','Z']
    #plot stdev
    for j in range(0,3):
        axarr4[j][0].plot(pos_stdev[j], 'g')
        axarr4[j][0].set_ylabel(pos_labels[j])
    #plot Mean +- stdev
    for j in range(0,3):
        axarr4[j][1].plot(map(add,pos_mean[j], map(lambda x:x*2.58,pos_stdev[j])), 'g')
        axarr4[j][1].plot(map(sub,pos_mean[j], map(lambda x:x*2.58,pos_stdev[j])), 'r')
    plt.show()
    return f4

def _compute(all_files):
    size = 3000
    all_x = []
    all_y = []
    all_z = []
    x_mean = []
    y_mean = []
    z_mean = []
    x_stdev = []
    y_stdev = []
    z_stdev = []
    all_mpos0 = []
    all_mpos1 = []
    all_mpos2 = []
    mpos0_mean = []
    mpos1_mean = []
    mpos2_mean = []
    mpos0_stdev = []
    mpos1_stdev = []
    mpos2_stdev = []

    for f in all_files:
        with open(f) as infile:
            reader = csv.reader(x.replace('\0', '') for x in infile)
            mpos, mvel, dac, jpos, pos, err, packet_nums, t = parse_latest_run(reader)

            # Store each value to separate array
            all_x.append(pos[0])
            all_y.append(pos[1])
            all_z.append(pos[2])
            all_mpos0.append(mpos[0])
            all_mpos1.append(mpos[1])
            all_mpos2.append(mpos[2])

    all_x = map(list, zip(*all_x))
    all_y = map(list, zip(*all_y))
    all_z = map(list, zip(*all_z))
    all_pos = [all_x, all_y, all_z]
    all_pos_mean = [x_mean, y_mean, z_mean]
    all_pos_stdev = [x_stdev, y_stdev, z_stdev]
    for i, axis in enumerate(all_pos):
        for packet in axis:
            all_pos_mean[i].append(mean(packet))
            all_pos_stdev[i].append(stdev(packet))

    all_mpos0 = map(list, zip(*all_mpos0))
    all_mpos1 = map(list, zip(*all_mpos1))
    all_mpos2 = map(list, zip(*all_mpos2))
    all_mpos = [all_mpos0, all_mpos1, all_mpos2]
    all_mpos_mean = [mpos0_mean, mpos1_mean, mpos2_mean]
    all_mpos_stdev = [mpos0_stdev, mpos1_stdev, mpos2_stdev]
    for i, axis in enumerate(all_mpos):
        for packet in axis:
            all_mpos_mean[i].append(mean(packet))
            all_mpos_stdev[i].append(stdev(packet))

    myshelve = shelve.open(shelve_file)
    myshelve['all_pos_mean'] = all_pos_mean
    myshelve['all_pos_stdev'] = all_pos_stdev
    myshelve['all_mpos_mean'] = all_mpos_mean
    myshelve['all_mpos_stdev'] = all_mpos_stdev
    myshelve.close()

if __name__ == '__main__':

    usage = 'Usage: python ' + sys.argv[0] + ' <dir>'

    if len(sys.argv) != 2:
        print(usage)
        sys.exit(0)

    # Get all csv files in current directory and subdirectories
    all_files = []
    for root, dirs, files in os.walk(sys.argv[1]):
        for f in files:
            if f.endswith('csv') and not f.startswith('mfi2'):
                all_files.append(os.path.join(root,f))

    # Open each file and analyze

    if os.path.isfile(shelve_file):
        myshelve = shelve.open(shelve_file)
        all_pos_mean = myshelve['all_pos_mean']
        all_pos_stdev = myshelve['all_pos_stdev']
        all_mpos_mean = myshelve['all_mpos_mean']
        all_mpos_stdev = myshelve['all_mpos_stdev']
    else:
        #_compute_mean(all_files)
        _compute(all_files)
        myshelve = shelve.open(shelve_file)
        all_pos_mean = myshelve['all_pos_mean']
        all_pos_stdev = myshelve['all_pos_stdev']
        all_mpos_mean = myshelve['all_mpos_mean']
        all_mpos_stdev = myshelve['all_mpos_stdev']

    plot_pos_stdev(all_pos_stdev, all_pos_mean)
    plot_pos_stdev(all_mpos_stdev, all_mpos_mean)
    

