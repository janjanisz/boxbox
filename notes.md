## Stage 0 - Project setup (31 Oct 2026)

### Why FastF1

The FastF1 library provides me with real F1 data of every lap of every driver, which tyre they were on, when they pitted and whether there was a safety car, in every race since 2018. I am using it because:
- It's free.
- It has good, lap-by-lap data: lap time, lap number, tyre compound (soft, medium, hard), tyre age (laps on that set of tyres), pit in and pit out laps and also track status (yellow flags and safety cars).
- It returns pandas DataFrames, which are easy for me to work with.

This matters for my project because FastF1 provides the exact data I need to measure tyre degradation and model pit strategy.

### Why a virtual environment

A virtual environment is a separate, private copy of Python just for this project, with its own libraries. I'm using one because:
- It keeps all of my projects separate, so different projects can use different libraries without them clashing.
- Without a virtual environment, simply updating a library in another project could break this project.
- It makes the project reproducible on someone else's computer. Later on I will make a requirements file which lists all the libraries needed to run the project.

This matters for my project because anyone (e.g. a recruiter) who downloads it from GitHub should be able to set it up and run it.

### What I keep out of GitHub

My .gitignore stops these from being uploaded:
- .venv/ – a very big folder, which is specific to my Mac and can be rebuilt with pip install. Uploading it is pointless and would add clutter to the repo.
- cache/ – downloaded F1 data, which makes it a very big folder. It's easy to download again using the FastF1 library, so uploading it is pointless.
- .ipynb_checkpoints/ and .DS_Store – autosave copies from Jupyter and hidden files from macOS, which are just clutter.

This matters for my project because the repo should only contain my own work (code, notebooks and notes), not anything a tool generated or that can be downloaded again.

## Stage 1 - F1 strategy basics (1 Nov 2026)

### Tyre compounds 
In Formula 1 races, there are 3 main types of Pirelli tyres available for use: 
- Soft compound tyres (fastest tyres, which wear the quickest)
- Medium compound tyres
- Hard compound tyres (slowest tyres, which wear the slowest) 

Other than these, there are also Intermediate and Wet tyres available for use by teams. These tyres have different amounts of tread (intermediate having less than wet) and are used in races affected by rain. 

This matters for my project because every lap has a tyre compound column, so I'll be able to model each compound's degradation separately. 
NOTE: I will ignore wet tyre and intermediate tyre compound laps, and focus on modelling the dry tyres for my project. 

### Two compound rule

In a dry race there is a rule which states that every driver must use at least 2 different dry compounds, which results in every driver pitting at least once in a race. The rule only applies in dry races – if a race goes wet, drivers don't have to use two dry compounds, which is one more reason I'm only using dry races.

This matters for my project because the aim is for my code to test lots of possible strategies and to pick the fastest. However, the code doesn't know the rules of F1, so I have to make it reject any strategy that uses 1 compound only, or it would otherwise possibly pick an illegal strategy. 

### Tyre degradation

Lap times become slower and slower as tyre compounds wear. Eventually a tyre can hit a "cliff", and lap times will suddenly increase by several seconds. 

This matters for my project because this is exactly what my model will predict - how much slower will laps become as tyre age increases (for each compound).

### Fuel levels

At the beginning of a race, cars start with approximately 100-110kg of fuel, of which they burn 1.5-2 kg per lap. As a rule of thumb, approximately 0.03s of lap time are gained as a kilo of fuel is burned, so around 0.05s/lap is gained per lap, as fuel is burned off. 

This matters for my project because fuel will be burned off at the same time as tyres will wear and this will mean that the effect of tyre wear alone will be hard to measure, as the two will partly cancel out lost time per lap. If I ignore fuel, it will look like the tyres are barely degrading. To solve this, I will need to account for fuel and compare my estimate with the rule of thumb I stated earlier. 

### Pitstop time loss

During a race a car has to pit at least once to change tyre compound which results in time lost during a lap - which I will call Pit-loss. This is due to a speed limit in the pit lane (which varies from track to track, but is usually around 80km/h) and also stopping for the tyre compound change itself. This makes a pitstop lap slower than a regular lap, by around 18-30 seconds depending on the track. 

This matters for my project because to compare strategies I'll need to add up the total race time for each one. As each pitstop adds time to the total time of the race, I will need to factor in a Pit-loss number for each track to account for this, and help my code choose the optimal strategy. 

### Safety Car and Virtual Safety Car

During a race a safety car (or a virtual safety car) can be deployed, causing every car on the racetrack to slow down. Normally, a pit stop costs between 18-30 seconds for a car without the deployment of a Safety Car or a VSC, due to being slow in the pit lane and having to stop for a tyre change, whilst everyone else is racing at full speed. However, as during a safety car or VSC everyone is driving more slowly, you lose much less time by pitting - only around 10-12 seconds (as an estimate). That's why teams often pit as soon as a Safety Car or VSC comes out - because it's a "cheap" pitstop.

This is important for my project because laps behind a safety car are slow because the drivers have been told to slow down, rather than because of the tyres being worn. If I keep these laps, my model would wrongly think that tyres got worse and degraded, when in reality they had not. Thus, I will remove Safety Car and VSC laps when I clean the data. FastF1 tells me which laps had a Safety Car or a VSC, so I can find them easily. 

### One stop vs Two stop strategies

In a one stop strategy you only lose time in the pit lane once, but end up running older and slower tyres for longer. In a two stop strategy you lose time in the pit lane twice, but run on newer, fresher, and faster tyres for longer. A two stop strategy is only going to be worth it if the time gained from fresher, newer tyres is greater than the extra time lost in the pit lane (extra pit-loss).

Example: if the pit loss is 22 s and the fresher tyres are 0.4 s/lap faster over the last 40 laps, the two stop gains 16 s but loses 22 s in the extra stop – so the one stop wins by 6 s.

This matters for my project as this will be the main question that my project will answer. Once I know how fast each tyre wears and how much a pit stop costs (in terms of time), I can work out the total race time for different strategies, and see whether one stop or two stops would have been faster in each race.

## Stage 2 - First race (2 Nov 2026)

### Getting the data 

I decided that I wanted to work with data from the 2023 F1 season. I chose to work with one season only because it will keep the cars and tyres comparable, which working with multiple seasons might not due to rule changes in F1 occurring every couple of years. Furthermore, 22 races provides more than enough lap data to work with. I started by loading the 2023 Bahrain Grand Prix with `fastf1.get_session(2023, 'Bahrain', 'R')` and `session.load()`. When I first did this I received multiple errors and every download failed because FastF1 gets its timing data from F1's live timing service, which requires an F1 TV subscription. As I already had one, I signed in from the terminal using `python -m fastf1 auth f1tv --authenticate`, which saves a login token on my Mac, not in my project, meaning my email and password never go on GitHub. The only downside to this is that the token expires every few days, so I have to sign in again when loading fails. 

This is important, as anyone who would like to reproduce my project from scratch would need to re-download the data, however to do that you need an F1 TV subscription. I will mention this in my README.

### What the columns mean

session.laps is a table with one row per lap per driver. In the case of the Bahrain Grand Prix, there are 1056 laps and 31 columns of data. 

- Driver: 3-letter driver code (e.g. VER = Verstappen, or HAM = Hamilton).
- Team: The driver's team.
- LapNumber: Which lap of the race it is.
- LapTime: Tells us how long each lap took. An issue I encountered was that it was stored in timedelta (e.g. 0 days 00:01:39.019), which would be problematic for me as I need plain numbers for the maths in my model. To solve this issue I converted the data into a new column, LapTimeSeconds, which provided me the LapTime in seconds (e.g. 99.019). I did this using `.dt.total_seconds()`.
- Stint: Tells us which set of tyres the driver is on (1st, 2nd, 3rd, etc.). This number increases by 1 after every pitstop.
- Compound: Tells us what type of tyre the driver is on - SOFT, MEDIUM or HARD (or INTERMEDIATE/WET in the rain).
- TyreLife: How many laps the set of tyres being used has done (the tyre's age measured in laps). It doesn't always start at 1 because some sets of tyres may have already been used in qualifying prior to the race.
- PitInTime: Shows the time at which a driver enters the pits. The data is only filled in on laps when a driver enters the pits; on other laps it is simply empty (NaT).
  - Note: The lap during which a driver enters the pits can be called an "in lap".
- PitOutTime: Shows the time at which a driver exits the pits. The data is only filled in on laps when a driver exits the pits; on other laps it is simply empty (NaT).
  - Note: The lap during which a driver exits the pits can be called an "out lap".
- TrackStatus: Shows what is currently happening on the racetrack.
  - 1 = green flag conditions
  - 2 = yellow flag conditions
  - 4 = safety car
  - 6/7 = virtual safety car
  - If the column displays multiple digits during one lap (e.g. 12), this means that the conditions of the racetrack changed during the lap.
- IsAccurate: FastF1's own check on if the lap time is reliable.

### Analysis on Verstappen's Bahrain Grand Prix

- Strategy: Verstappen carried out a two stop strategy going from Soft --> Soft --> Hard compound tyres during the race. He pitted at the end of lap 14 and the end of lap 36.
- The set of soft compound tyres which Verstappen started on had a TyreLife of 4 on lap 1. However after each of his stops, the new tyres which he used both had a TyreLife of 1. This tells me that he had a used set of Soft Compound tyres at the start of the race - from qualifying. 
- The first lap was slower (99.0s) because of the standing start and the IsAccurate column was marked with False. 
- In-laps (lap 14 and 36) were about 3 seconds slower and out laps (laps 15 and 37) were about 20 seconds slower (both compared to a normal lap, with no pitstop). Combined this is around 24 seconds (approximately) of pit loss, which matches the 18-30 seconds estimate I made in Stage 1. 
- Laps 41 and 42 were much slower compared to other non-pitstop laps (120.5s and 104.8s). The reason for this is because of a Virtual Safety Car, indicated by the TrackStatus column for these laps showing 126 and 671 respectively.
- During Verstappen's first stint, his lap times slowly increased from about 98.0s to 98.6s over laps 2-13. This is around 0.06s lost per lap, however it's important to note that fuel burning off was making the car faster at the same time. This leads me to believe that the tyre degradation at the time is probably bigger than what the 0.06s per lap implies it to be. 
- During Verstappen's second stint, contrary to the first one the lap times decreased over the course of the stint (97.8s to 97.4s). Despite the tyres getting older and degrading lap by lap, I think that the reason for the decrease in lap time is the fuel effect. The car became lighter at a fast enough rate to mask the effect of tyre degradation (which alone would have increased the lap times).
- Verstappen's third stint on hard compound tyres was his fastest with lap times ranging from 96.2s to 97.4s (with VSC laps omitted). I think this is because the car had the least fuel in the tank by the end of the race. 

What I've learnt from this, and why it matters:

- Moving forward I will need to remove: lap 1, in laps, out laps and Safety Car/Virtual Safety Car laps before modelling tyre degradation. This is because those laps have slower times but not because of tyre degradation.  
- Stint 2 and 3 showed me that I can't just look at lap times alone to see degradation. I will need to account for fuel, or my model would show that tyres barely degrade.

