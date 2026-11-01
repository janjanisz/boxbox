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
