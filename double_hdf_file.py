import sys
import time
import h5py

in_out_nexus_name = sys.argv[1]

# double the events
h5test = h5py.File(in_out_nexus_name, 'r+')

entry_root = h5test['entry']
instrument_root = entry_root['instrument']

t0 = time.time()

num_added_events = 0
for bank_name in instrument_root:
    # skip non-bank entry
    if bank_name.count('bank') == 0:
        continue
    bank_number = str(bank_name).split('bank')[1]
    # skip non-data bank entry
    if bank_number.isdigit() is False:
        continue

    # get all 5 entries under bank
    bank_now = instrument_root[bank_name]
    event_id = bank_now['event_id']
    event_index = bank_now['event_index']
    event_time_offset = bank_now['event_time_offset']
    event_time_zero = bank_now['event_time_zero']
    total_counts = bank_now['total_counts']
    if total_counts[0] < 10:
        print ('{} is skipped.  Total counts = {}'.format(bank_name, total_counts[0]))
        continue
    else:
        print ('{} is about to resize from {}'.format(bank_name, event_id.shape[0]))

    # add events
    num_events_i = event_id.shape[0]
    print ('Number of events = {}'.format(num_events_i))

    event_id.resize((num_events_i * 2,))
    event_time_offset.resize((num_events_i * 2,))
    print ('Resize to {}, {}'.format(event_id.shape[0], event_time_offset.shape[0]))

    event_id[num_events_i:2 * num_events_i] = event_id[0:num_events_i]
    event_time_offset[num_events_i:2 * num_events_i] = event_time_offset[0:num_events_i] + 100.
    event_index[0:num_events_i] = event_index[0:num_events_i] * 2

    print ('Confirmed of resizing:  {}, {}'.format(event_id.shape[0], event_time_offset.shape[0]))

    num_added_events += num_events_i
    total_counts[0] = 2 * num_events_i

    t1 = time.time()
    print ('Using time: {}.'.format(t1 - t0))

# END-FOR

print ('Added {} events'.format(num_added_events))

# print (time.time())

h5test.close()

# check
