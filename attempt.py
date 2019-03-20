import os

path = 'C:\\Users\\cyber\\Documents\\SleepyHeadData\\Profiles\\John Doe\\PRS1_J16898757AD79'


def read_files():
    session_summaries = {}  # .001
    event_data = {}  # .002
    time_details = {}  # .004
    waveform_data = {}  # .005

    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith(".001"):
                with open(os.path.join(root, name), 'rb') as f:
                    session_summaries[name] = str(f.read())
            elif name.endswith(".002"):
                with open(os.path.join(root, name), 'rb') as f:
                    event_data[name] = str(f.read())
            elif name.endswith(".004"):
                with open(os.path.join(root, name), 'rb') as f:
                    time_details[name] = str(f.read())
            elif name.endswith(".005"):
                with open(os.path.join(root, name), 'rb') as f:
                    waveform_data[name] = str(f.read())

    return session_summaries, event_data, time_details, waveform_data


session_summaries, event_data, time_details, waveform_data = read_files()
