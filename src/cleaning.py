import pandas as pd

def clean_laps(laps, remove_restarts = True):
    """Remove laps that aren't normal racing laps from one race.

    Removes, in order: in laps and out laps, lap 1, laps FastF1 marks as inaccurate,
    laps with no lap time, laps that aren't fully in green flag conditions
    and (if remove_restarts is True) the lap after any Safety Car lap.
    Adds a LapTimeSeconds column.

    laps: the session.laps table for one race.
    remove_restarts: set to False to keep the laps after a Safety Car lap.

    Returns the cleaned laps and a funnel table of how many laps each step removed."""

    no_pits = laps.pick_wo_box()
    no_lap1 = no_pits[no_pits['LapNumber'] > 1]
    accurate = no_lap1[no_lap1['IsAccurate'] == True]
    cleaned = accurate[accurate['LapTime'].notna()]
    green = cleaned.pick_track_status('1')

    if remove_restarts:
        prev_status = laps.groupby('Driver')['TrackStatus'].shift(1)
        restart_laps = laps[prev_status.str.contains('4', na = False)]
        no_restart = green[~green.index.isin(restart_laps.index)]
    else:
        no_restart = green

    funnel = pd.DataFrame({
        'Step': ['Start', 'Remove in laps and out laps', 'Remove lap 1', 'Remove inaccurate laps', 'Remove laps with no lap time', 'Keep only green flag laps', 'Remove laps after a Safety Car lap'],
        'Laps left': [len(laps), len(no_pits), len(no_lap1), len(accurate), len(cleaned), len(green), len(no_restart)],
        'Laps removed': [0, len(laps) - len(no_pits), len(no_pits) - len(no_lap1), len(no_lap1) - len(accurate), len(accurate) - len(cleaned), len(cleaned) - len(green), len(green) - len(no_restart)],
    })

    no_restart = no_restart.copy()
    no_restart['LapTimeSeconds'] = no_restart['LapTime'].dt.total_seconds()

    return no_restart, funnel


def add_gap_ahead(laps, cleaned):
    """Add the gap to the car ahead to each cleaned lap.

    Uses every car's position and lap end time from the raw laps, so the car ahead is
    found even if its own lap was cleaned out. Adds the columns DriverAhead, GapAhead (seconds)
    and InTraffic (gap under 1.0s). The race leader has no car ahead, so GapAhead is empty for those laps.

    laps: the raw session.laps table for the race.
    cleaned: the cleaned laps from clean_laps().

    Returns the cleaned laps with the new columns. No laps are removed."""

    order = laps[['Driver', 'LapNumber', 'Position', 'Time']].dropna()

    car_ahead = order.copy()
    car_ahead['Position'] = car_ahead['Position'] + 1

    gaps = order.merge(car_ahead, on = ['LapNumber', 'Position'], suffixes = ('','Ahead'))
    gaps['GapAhead'] = (gaps['Time'] - gaps['TimeAhead']).dt.total_seconds()

    with_gaps = cleaned.merge(gaps[['Driver', 'LapNumber', 'DriverAhead', 'GapAhead']], on = ['Driver', 'LapNumber'], how = 'left')
    with_gaps['InTraffic'] = with_gaps['GapAhead'] < 1.0

    return with_gaps
