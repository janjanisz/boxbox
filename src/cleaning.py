import pandas as pd 

def clean_laps(laps):
    no_pits = laps.pick_wo_box()
    no_lap1 = no_pits[no_pits['LapNumber'] > 1]
    accurate = no_lap1[no_lap1['IsAccurate'] == True]
    cleaned = accurate[accurate['LapTime'].notna()]
    green = cleaned.pick_track_status('1')

    funnel = pd.DataFrame({
        'Step': ['Start', 'Remove in laps and out laps', 'Remove lap 1', 'Remove inaccurate laps', 'Remove laps with no lap time', 'Keep only green flag laps'],
        'Laps left': [len(laps), len(no_pits), len(no_lap1), len(accurate), len(cleaned), len(green)],
        'Laps removed': [0, len(laps) - len(no_pits), len(no_pits) - len(no_lap1), len(no_lap1) - len(accurate), len(accurate) - len(cleaned), len(cleaned) - len(green)],
    })

    green = green.copy()
    green['LapTimeSeconds'] = green['LapTime'].dt.total_seconds()

    return green, funnel

def add_gap_ahead(laps, cleaned): 
    order = laps[['Driver', 'LapNumber', 'Position', 'Time']].dropna()

    car_ahead = order.copy()
    car_ahead['Position'] = car_ahead['Position'] + 1

    gaps = order.merge(car_ahead, on = ['LapNumber', 'Position'], suffixes = ('','Ahead'))
    gaps['GapAhead'] = (gaps['Time'] - gaps['TimeAhead']).dt.total_seconds()

    with_gaps = cleaned.merge(gaps[['Driver', 'LapNumber', 'DriverAhead', 'GapAhead']], on = ['Driver', 'LapNumber'], how = 'left')
    with_gaps['InTraffic'] = with_gaps['GapAhead'] < 1.0

    return with_gaps


