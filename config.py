EXCHANGERS = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F"
]


EXCHANGER_COLORS = {

    "A": "#4C72B0",
    "B": "#DD8452",
    "C": "#55A868",
    "D": "#C44E52",
    "E": "#8172B2",
    "F": "#937860",

}


ROLLING_WINDOW = 24        # hours

MIN_FLOW = 500             # m3/day

STATE_DEADBAND = 2         # °C

LOOKBACK_DAYS = 7          # days of history used for the ranking averages

# An exchanger must be online continuously for more than this many days
# (ending at the report time) to qualify for a ranking. A simultaneous
# fleet-wide outage (plant emergency / shutdown) does not reset the streak.
# Exchangers that have just been brought into service do not qualify yet.
MIN_ONLINE_STREAK_DAYS = 7


# Data files

DATA_FILE = "data/E-560-180-Aug3.CSV"

EVENT_FILE = "data/2026 - E560 & 5611 Cleaning Log July 26.xlsx"
