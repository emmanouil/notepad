import sys
import json
import os
import datetime
import re
import random
import pickle

FILE_LIST = [
    "A002C001_140325E3", "20140325_121238", "Take5_Nexus5", "20140325_121245", "20140325_131253", "IMG_0367", "VID_20140325_131247",
    "VID_20140325_131249"
]
#we exclude static views
STATIC_VIEWS = ["A002C001_140325E3", "VID_20140325_131249"]
NETWORK_INTERVAL_MS = 500
#probability of changing quality after the interval
P_of_Qswitch = [0.002, 0.05, 0.002, 0.05, 0.002, 0.002, 0.05, 0.002]
#P boost when link is good and we are in bad Q
P_GOOD_BOOST = 0.2
#if the quality of the link is good, it has higher P to return to HiQ
L_quality_good = [True, False, True, False, True, True, False, True]
#filename + suffix = metric filename
METRIC_SUFFIX = "_metrics.json"
DIR = "C:\\Users\\theid\\Desktop\\tests\\fake_test\\test_2\\"
metrics = []
metric_ids = []

#initial network trace
network_trace = [[0, 0, 0, 0, 0, 0, 0, 0]]
#initial Sc
scs = [{
    "id": "A002C001_140325E3",
    "index": 0,
    "rep": 0,
    "t_video": 537.4,
    "t_abs": 537.4,
    "t_elapsed": 0.0,
    "is_buffering": False,
    "is_buffer_full": False,
    "n_buffered": 0,
    "t_buffered": 0,
    "Score": 0
}]

TEST = '4-10'
INFILE = 'Scs' + TEST + '.json'
LOGFILE = 'python_script.log'
OUTDIR = 'p_out'
PL_FILE = 'clips-list.txt'
V_OUT_FILE = 'clips' + TEST + '.mp4'
S_OUT_FILE = 'score' + TEST + '.csv'
MIN_LENGTH_S = 0


##	Log
#
#	lvl = None log to console
#		< 0 ERROR
#		> 0 INFO
#		= 0 Debug
def log(msg, lvl):
    now = datetime.datetime.now()
    str_now = '\n' + str(now.day) + '/' + str(now.month) + '/' + str(now.year) + ' ' + str(now.hour) + ':' + str(now.minute) + ':' + str(
        now.second) + ' '
    str_now = str_now.ljust(19)
    with open(DIR + LOGFILE, 'a') as logfile:
        if (lvl is None):    #normal
            print(msg)
        elif (lvl < 0):    #error
            print('\033[31;1m' + '[ERROR]\t' + '\033[0m' + msg)
            logfile.write(str_now + '[ERROR]\t' + msg)
        elif (lvl > 0):    #info
            print('\033[32m' + '[INFO]\t' + '\033[0m' + msg)
            logfile.write(str_now + '[INFO]\t' + msg)
        elif (lvl == 0):    #dbg
            print('\033[35;1m' + '[DEBUG]\t' + '\033[0m' + msg)
            logfile.write(str_now + '[DEBUG]\t' + msg)


def load_file(id, suffix):
    log('Processing file: ' + id + suffix, 1)
    with open(DIR + id + suffix, 'r') as file_in:
        return json.load(file_in)


def load_files():
    for fn in FILE_LIST:
        metrics.append(load_file(fn, METRIC_SUFFIX))
        metric_ids.append(fn)


def next_value(cur_value, P_in, isGood):
    if (isGood and cur_value > 0):
        p_switch = P_in + P_GOOD_BOOST
    else:
        p_switch = P_in
    if (random.random() < p_switch):
        if (cur_value == 0):
            return 2
        if (cur_value == 2):
            return 0
    return cur_value


#inputs the previous states of network (reps) and returns the next
def network_state(previous_state):
    current_state = []
    for i in range(0, len(P_of_Qswitch)):
        current_state.append(next_value(previous_state[i], P_of_Qswitch[i], L_quality_good[i]))
    return current_state


#fill network_trace with available reps of
def emulate_network():
    for t in range(0, 200000, NETWORK_INTERVAL_MS):
        i = t / NETWORK_INTERVAL_MS
        network_trace.append(network_state(network_trace[i]))
    return network_trace


def find_entry_at_time(t_in, metric):
    for entry in metric:
        if (entry["t_elapsed"] >= t_in):
            return entry


#returns scores at time given, excluding the static views
def find_scores_at_time(t_in):
    i = 0
    curr_scores = []
    for metric in metrics:
        score_in = find_entry_at_time(t_in, metric)
        score_in["id"] = metric_ids[i]
        if (STATIC_VIEWS.count(metric_ids[i]) > 0):
            i += 1
            continue
        score_in["index"] = i
        curr_scores.append(score_in)
        i += 1
    return curr_scores


def find_score_for_id(scores_in, id_in):
    for score in scores_in:
        if score["id"] == id_in:
            return score["S"]


#sorts list according to score
def clean_and_sort_scores(scores_in):
    scores_in = sorted(scores_in, cmp=None, key=lambda k: k['S'], reverse=True)
    return scores_in


def should_switch(current_t, next_switch_t):
    if (current_t >= next_switch_t):
        return True
    return False


def get_switch_view(scores, curr_stream_id, prev_stream_id):
    S_max = 0
    id_max = ""
    for score in scores:
        if score["id"] in STATIC_VIEWS or score["id"] == curr_stream_id or score["id"] == prev_stream_id:
            continue
        if S_max < score['S']:
            S_max = score['S']
            id_max = score['id']
    return id_max


#simulated player - not used for now
p = {
    "emulated_time": 0.0,
    "active_stream_id": "A002C001_140325E3",
    "active_stream_index": 0,
    "active_representation": 0,
    "is_playing": True
}


class Segment:
    def __init__(self, t_start, duration, stream_index, representation):
        self.t_start = t_start
        self.duration = duration
        self.index = stream_index
        self.representation = representation


class Buffer:
    def __init__(self, size_segs):
        self.size_segs = size_segs
        self.segs = []

    def push_segment(self, seg_in):
        self.segs.append(seg_in)

    def update(self, t_now):
        todel = []
        #remove possible duplicates (shouldn't happen)
        for i in range(0, len(self.segs) - 1):
            j = 0
            for s in self.segs:
                if self.segs[i].t_start == s.t_start:
                    j += 1
                    if (j > 1):
                        self.segs.remove(s)
        #calculate length
        for i in range(0, len(self.segs)):
            s = self.segs[i]
            if (s.t_start + s.duration < t_now):
                todel.append(s)
        for s in todel:
            self.segs.remove(s)
        return self.get_duration(t_now)

    def get_duration(self, t_now):
        dur = 0.0
        for s in self.segs:
            if (s.t_start + s.duration >= t_now):
                dur += s.t_start + s.duration - t_now
        return dur

    def peek_segment_at_time(self, t_now):
        for s in self.segs:
            if (s.t_start <= t_now <= s.t_start + s.duration):
                return s
        return


def is_stream_available(index_in, rep_in, t_in):
    if (network_trace[int(t_in)][index_in] <= rep_in):
        return True
    return False


#segment duration (in s)
seg_duration = 2.0
#buffer size (in segs)
buffer_size = 2
#buffer object
b = Buffer(buffer_size)
#request example (this will add the initial segment)
request = {
    'status': 'PENDING',    #(possible values: 'EMPTY', 'FAILED', 'EXECUTED', 'PENDING')
    'index': 0,
    'representation': 0,
    'segment_t': 0
}
scene_logs = []


def new_request(index, rep, starttime):
    global request
    request['status'] = 'PENDING'
    request['index'] = index
    request['representation'] = rep
    request['segment_t'] = starttime


def switch_stream(t_in, rep):
    global curr_stream_id
    global curr_stream_index
    global prev_stream_id

    curr_scores = find_scores_at_time(t_in)
    curr_scores = clean_and_sort_scores(curr_scores)

    tmp_index = 0
    for i in range(0, len(curr_scores)):
        if curr_scores[i]['id'] == curr_stream_id or curr_scores[i]['id'] == prev_stream_id:
            continue
        else:
            tmp_index = i
            break

    if (curr_scores[tmp_index]['S'] > 0.75):
        next_switch_t = t_in + 12
        print('next stream switch at ', next_switch_t, 'with score ', curr_scores[tmp_index]['S'])
    elif (curr_scores[tmp_index]['S'] > 0.60):
        next_switch_t = t_in + 8
        print('next stream switch at ', next_switch_t, 'with score ', curr_scores[tmp_index]['S'])
    else:
        next_switch_t = t_in + 4
        print('next stream switch at ', next_switch_t, 'with score ', curr_scores[tmp_index]['S'])
    #do the req
    new_request(curr_scores[tmp_index]['index'], rep, t_in)
    print('requested to switch Stream to ', curr_scores[tmp_index]['id'])
    return next_switch_t


curr_stream_id = ""
curr_stream_index = -1
prev_stream_id = ""
next_stream_id = ""

def recreate_scs():

    #current time
    t = 0.0

    #next switch time
    next_switch_t_s = 2.0
    #is the stream playing
    isPlaying = True
    #is the stream buffering
    isBuffering = False
    #is the buffer full
    isBufferFull = False
    #virtual buffer size (in s)
    B_size = 2.5
    #current representation (0 - High, or 2 - Low)
    curr_rep = 0
    #time of buffered video remaining
    b_t_remaining = 2.0
    #rest of vars
    global curr_stream_id
    curr_stream_id = "A002C001_140325E3"
    global curr_stream_index
    curr_stream_index = 0
    global prev_stream_id
    prev_stream_id = "A002C001_140325E3"
    global next_stream_id
    next_stream_id = "A002C001_140325E3"
    last_Qswitch_t = 0.0
    last_Sswitch_t = 0.0
    last_fetched_segment_end_t = 2.0

    #emulate timeline
    for t_ms in range(0, 200000, NETWORK_INTERVAL_MS):
        global request

        #update time
        t = t_ms / float(1000)

        #fullfill requests
        if request['status'] == 'PENDING':
            if is_stream_available(request['index'], request['representation'], request['segment_t']):
                s_in = Segment(request['segment_t'], seg_duration, request['index'], request['representation'])
                b.push_segment(s_in)
                request['status'] = 'EXECUTED'
                last_fetched_segment_start_t = request['segment_t']
                curr_rep = request['representation']
            else:
                request['status'] = 'FAILED'
                print('failed request')

        if request['status'] == 'EXECUTED':
            print('we successfully requested new segment for starting time ', request['segment_t'], ' representation ',
                  request['representation'], ' and stream index ', request['index'])
            request['status'] = 'EMPTY'

        #update scores
        curr_scores = find_scores_at_time(t)
        curr_scores = clean_and_sort_scores(curr_scores)
        #update buffer
        b_t_remaining = b.update(t)

        #check if we had a switch in Q or S
        tmp_s = b.peek_segment_at_time(t)
        if tmp_s is not None:
            if tmp_s.index != curr_stream_index:
                curr_stream_index = tmp_s.index
                prev_stream_id = curr_stream_id
                curr_stream_id = FILE_LIST[tmp_s.index]
                curr_rep = tmp_s.representation
                last_Sswitch_t = t - NETWORK_INTERVAL_MS / float(1000)
            if tmp_s.representation != curr_rep:
                curr_rep = tmp_s.representation
                last_Qswitch_t = t - NETWORK_INTERVAL_MS / float(1000)
        else:
            print('failed to fetch segment')

        if b_t_remaining == 0.0:
            print('ZERO BUFFER')
            isBuffering = True
            isBufferFull = False
        elif 0.5 >= b_t_remaining > 0:
            print('FINAL ITTER')
            isBuffering = False
            isBufferFull = False
        elif 1.5 >= b_t_remaining > 0.5:
            print('between 0.5 and 1.5')
            isBuffering = False
            isBufferFull = False
        elif 2.5 >= b_t_remaining > 1.5:
            print('FULL')
            isBuffering = False
            isBufferFull = True
        else:
            log('abnormal buffer value', -1)

# TODO evaluate state
#first check for programmed stream switches
        if (next_switch_t_s == t + NETWORK_INTERVAL_MS / float(1000) and not isBuffering):
            print('we will request to change stream. current stream status: ', request['status'])
            next_switch_t_s = switch_stream(next_switch_t_s, curr_rep)
            # starttime = next_switch_t_s
            # if (curr_scores[0]['S'] > 0.75):
            #     next_switch_t_s += 12
            #     print('next stream switch at ', next_switch_t_s, 'with score ', curr_scores[0]['S'])
            # elif (curr_scores[0]['S'] > 0.60):
            #     next_switch_t_s += 8
            #     print('next stream switch at ', next_switch_t_s, 'with score ', curr_scores[0]['S'])
            # else:
            #     next_switch_t_s += 4
            #     print('next stream switch at ', next_switch_t_s, 'with score ', curr_scores[0]['S'])
            # #do the req
            # new_request(curr_scores[0]['index'], curr_rep, starttime)
            print('requested to switch Stream')
        elif isBuffering:
            if request['status'] != ['EMPTY'] or request['status'] != ['FAILED']:
                print('buffering - we switch to LoQ')
                tmp_rep = 2
                next_switch_t_s = switch_stream(last_fetched_segment_start_t + seg_duration, tmp_rep)
            else:
                print('TODO req status is ' + request['status'])
        else:
            if isBufferFull:
                print('TODO do nothing - buffer full')
            else:
                if 0.5 >= b_t_remaining > 0:
                    if curr_rep == 0 and not isBuffering:    #we are in HiQ and keep HiQ
                        if request['status'] == 'PENDING':
                            print('we are skipping HiQ request - we have a pending request')
                        elif request['status'] == 'EMPTY':
                            new_request(curr_stream_index, 0, t + b_t_remaining)
                            print('fetch HiQ seg request issued for seg at time ', t + b_t_remaining)
                        else:
                            log('Unknown Request status', -1)
                    elif curr_rep > 0 and t - last_Sswitch_t < 2.0:    #we 'just' switch stream to LoQ and switching to HiQ
                        if request['status'] == 'PENDING':
                            print('we are skipping switch to HiQ- we have a pending request')
                        else:
                            tmp_rep = 0
                            print('req status ', request['status'])
                            new_request(curr_stream_index, tmp_rep, t + b_t_remaining)
                            print('switch to HiQ (from LoQ)- seg request issued for seg at time ', t + b_t_remaining)
                    else:    #we are in LoQ and stay in LoQ
                        print('TODO fetch LoQ seg')
                else:
                    print('do not nothing, time left in buffer: %f', b_t_remaining)
        scene_logs.append({
            'id': curr_stream_id,
            'index': curr_stream_index,
            'rep': curr_rep,
            't_abs': 'TODO',
            't_elapsed': t,
            'is_buffering': isBuffering,
            'is_buffer_full': isBufferFull,
            'Score': find_score_for_id(curr_scores, curr_stream_id)
        })


# TODO issue request

# TODO update logs

#whether we should use generated network trace, or use existing (for comparison)
trace_exists = True


def main():
    load_files()    #load them in metrics
    if trace_exists:
        with open(DIR + 'net_trace.pickle', 'rb') as fp:
            global network_trace
            network_trace = pickle.load(fp)
    else:
        traces = emulate_network()    #load them in network_trace
        with open(DIR + 'net_trace.pickle', 'wb') as fp:
            pickle.dump(traces, fp)
    recreate_scs()
    input('continue?')
    #That's All Folks!
    exit(0)


if __name__ == '__main__':
    main()
