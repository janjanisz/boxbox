## Stage 0 - Project setup (31 Oct 2026)

### Why FastF1

The FastF1 library provides me with real F1 data of every lap of every driver, which tyre they were on, when they pitted and whether there was a safety car, in every race since 2018. I am using it because:
- The library is free, but its timing data needs an F1 TV subscription.
- It has good, lap-by-lap data: lap time, lap number, tyre compound (soft, medium, hard), tyre age (laps on that set of tyres), pit in and pit out laps and also track status (yellow flags and safety cars).
- It returns pandas DataFrames, which are easy for me to work with.

This matters for my project because FastF1 provides the exact data I need to measure tyre degradation and model pit strategy.

### Why a virtual environment

A virtual environment is a separate, private copy of Python just for this project, with its own libraries. I'm using one because:
- It keeps all of my projects separate, so different projects can use different libraries without them clashing.
- Without a virtual environment, simply updating a library in another project could break this project.
- It makes the project reproducible on someone else's computer. Later on I will make a requirements file which lists all the libraries needed to run the project.

This matters for my project because anyone (e.g. a recruiter) who downloads it from GitHub and has an F1 TV subscription should be able to set it up and run it.

### What I keep out of GitHub

My .gitignore stops these from being uploaded:
- .venv/ – a very big folder, which is specific to my Mac and can be rebuilt with pip install. Uploading it is pointless and would add clutter to the repo.
- cache/ – downloaded F1 data, which makes it a very big folder. It's easy to download again using the FastF1 library, so uploading it is pointless.
- .ipynb_checkpoints/ and .DS_Store – autosave copies from Jupyter and hidden files from macOS, which are just clutter.

This matters for my project because the repo should contain my own work (code, notebooks and notes) and the charts I choose to keep as outputs, not clutter that a tool generates or data that can be downloaded again.

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

In a dry race there is a rule which states that every driver must use at least 2 different dry compounds, which normally means a driver who finishes the race pits at least once (a red flag can allow a tyre change without a normal pit stop). The rule doesn't apply if a driver has used intermediate or wet tyres, which is one more reason I'm only using dry races.

This matters for my project because the aim is for my code to test lots of possible strategies and to pick the fastest. However, the code doesn't know the rules of F1, so I have to make it reject any strategy that uses 1 compound only, or it would otherwise possibly pick an illegal strategy. 

### Tyre degradation

Lap times become slower and slower as tyre compounds wear. Eventually a tyre can hit a "cliff", where lap times suddenly jump. 

This matters for my project because this is exactly what my model will predict - how much slower will laps become as tyre age increases (for each compound).

### Fuel levels

Cars can use up to 110kg of fuel in a race, and they get lighter and faster as it burns off. As unverified rules of thumb, a car burns around 1.5-2kg per lap and gains around 0.03s of lap time per kilo burned, which would make it around 0.05s/lap faster. I haven't confirmed these numbers, so I will test the fuel effect against my own data. 

This matters for my project because fuel will be burned off at the same time as tyres will wear and this will mean that the effect of tyre wear alone will be hard to measure, as the two will partly cancel out lost time per lap. If I ignore fuel, it will look like the tyres are barely degrading. To solve this, I will need to account for fuel and compare my estimate with the rule of thumb I stated earlier. 

### Pitstop time loss

During a race a car has to pit at least once to change tyre compound which results in time lost across the in-lap and out-lap - which I will call Pit-loss. This is due to a speed limit in the pit lane (usually 80km/h, but lower at some tracks, such as 60km/h at Monaco) and also stopping for the tyre compound change itself. This makes a pitstop slower than staying out on track, by roughly 20-25 seconds depending on the track. 

This matters for my project because to compare strategies I'll need to add up the total race time for each one. As each pitstop adds time to the total time of the race, I will need to factor in a Pit-loss number for each track to account for this, and help my code choose the optimal strategy. 

### Safety Car and Virtual Safety Car

During a race a safety car (or a virtual safety car) can be deployed, causing every car on the racetrack to slow down. Normally, a pit stop costs roughly 20-25 seconds for a car without the deployment of a Safety Car or a VSC, due to being slow in the pit lane and having to stop for a tyre change, whilst everyone else is racing at full speed. However, as during a safety car or VSC everyone is driving more slowly, you lose much less time by pitting - around 12 seconds at the tracks I found figures for. That's why teams often pit as soon as a Safety Car or VSC comes out - because it's a "cheap" pitstop.

This is important for my project because laps behind a safety car are slow because the drivers have been told to slow down, rather than because of the tyres being worn. If I keep these laps, my model would wrongly think that tyres got worse and degraded, when in reality they had not. Thus, I will remove Safety Car and VSC laps when I clean the data. FastF1 tells me which laps had a Safety Car or a VSC, so I can find them easily. 

### One stop vs Two stop strategies

In a one stop strategy you only lose time in the pit lane once, but end up running older and slower tyres for longer. In a two stop strategy you lose time in the pit lane twice, but run on newer, fresher, and faster tyres for longer. A two stop strategy is only going to be worth it if the time gained from fresher, newer tyres is greater than the extra time lost in the pit lane (extra pit-loss).

Example: if the pit loss is 22 s and the fresher tyres are 0.4 s/lap faster over the last 40 laps, the two stop gains 16 s but loses 22 s in the extra stop – so the one stop wins by 6 s.

This matters for my project as this will be the main question that my project will answer. Once I know how fast each tyre wears and how much a pit stop costs (in terms of time), I can work out the total race time for different strategies, and see whether one stop or two stops would have been faster in each race.

## Stage 2 - First race (2 Nov 2026)

### Getting the data 

I decided that I wanted to work with data from the 2023 F1 season. I chose to work with one season only because it will keep the cars and tyres comparable, which working with multiple seasons might not because cars and tyres can change between seasons. Furthermore, 22 races provides more than enough lap data to work with. I started by loading the 2023 Bahrain Grand Prix with `fastf1.get_session(2023, 'Bahrain', 'R')` and `session.load()`. When I first did this I received multiple errors and every download failed because FastF1 gets its timing data from F1's live timing service, which requires an F1 TV subscription. As I already had one, I signed in from the terminal using `python -m fastf1 auth f1tv --authenticate`, which saves a login token on my Mac, not in my project, meaning my email and password never go on GitHub. The only downside to this is that the token expires every few days, so I have to sign in again when loading fails. 

This is important, as anyone who would like to reproduce my project from scratch would need to re-download the data, however to do that you need an F1 TV subscription. I will mention this in my README.

### What the columns mean

session.laps is a table with one row per lap per driver. In the case of the Bahrain Grand Prix, there are 1056 laps and 31 columns of data. 

- Driver: 3-letter driver code (e.g. VER = Verstappen, or HAM = Hamilton).
- Team: The driver's team.
- LapNumber: Which lap of the race it is.
- LapTime: Tells us how long each lap took. An issue I encountered was that it was stored in timedelta (e.g. 0 days 00:01:39.019), which would be problematic for me as I need plain numbers for the maths in my model. To solve this issue I converted the data into a new column, LapTimeSeconds, which provided me the LapTime in seconds (e.g. 99.019). I did this using `.dt.total_seconds()`.
- Stint: Tells us which set of tyres the driver is on (1st, 2nd, 3rd, etc.). This number usually increases by 1 after a pitstop, but not always (e.g. Piastri has 1 pit-in but only 1 stint).
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
  - 5 = red flag
  - 6 = virtual safety car deployed
  - 7 = virtual safety car ending
  - If the column displays multiple digits during one lap (e.g. 12), this means that the conditions of the racetrack changed during the lap.
- IsAccurate: FastF1's own check on if the lap time is reliable.

### Analysis on Verstappen's Bahrain Grand Prix

- Strategy: Verstappen carried out a two stop strategy going from Soft --> Soft --> Hard compound tyres during the race. He pitted at the end of lap 14 and the end of lap 36.
- The set of soft compound tyres which Verstappen started on had a TyreLife of 4 on lap 1. FreshTyre was also False, which tells me that he started the race on a used set of Soft compound tyres - probably from qualifying. After each of his stops TyreLife restarted at 1, but FreshTyre was False for his second set of Softs and True only for the Hards. So TyreLife restarting at 1 doesn't prove that a set was new, and I need to check this during cleaning. 
- The first lap was slower (99.0s) because of the standing start and the IsAccurate column was marked with False. 
- In-laps (lap 14 and 36) were about 3 seconds slower and out laps (laps 15 and 37) were about 20 seconds slower (both compared to a normal lap, with no pitstop). Combined this is around 23 seconds (approximately) of pit loss, which fits the roughly 20-25 seconds estimate in Stage 1. 
- Laps 41 and 42 were much slower compared to other non-pitstop laps (120.5s and 104.8s). The reason for this is because of a Virtual Safety Car, indicated by the TrackStatus column for these laps showing 126 and 671 respectively.
- During Verstappen's first stint, his lap times stayed flat at about 98.0s on laps 3-7, then rose to about 98.6s by lap 12. Overall he got about 0.5s slower (the first three clean laps averaged 98.01s and the last three 98.52s), however it's important to note that fuel burning off was making the car faster at the same time. This leads me to believe that the tyre degradation at the time is probably bigger than this 0.5s implies it to be. 
- During Verstappen's second stint, lap times stayed roughly flat (the first three clean laps averaged 97.69s and the last three 97.79s), even though the tyres were ageing. I think fuel burn may have been hiding some of the tyre wear, but this one stint can't prove that.
- Verstappen's third stint on hard compound tyres was his fastest with lap times ranging from 96.2s to 97.4s (with VSC laps omitted). I think this is because the car had the least fuel in the tank by the end of the race. 

What I've learnt from this, and why it matters:

- Moving forward I will need to remove: lap 1, in laps, out laps and yellow flag/Safety Car/Virtual Safety Car laps before modelling tyre degradation. This is because those laps have slower times but not because of tyre degradation.  
- Stint 2 and 3 showed me that I can't just look at lap times alone to see degradation. I will need to account for fuel, or my model would show that tyres barely degrade.

## Stage 3 - The "aha" chart (3 Nov 2026)

### Verstappen chart 

I plotted Verstappen's lap times against lap number and coloured each dot by tyre compound. Having done that, you can now read the graph and interpret key events from his race using it. 
- Lap 1 was slightly slow (99.0s) and this is due to the standing start at the beginning of the race. 
- Each of his two pit stops show up as a pair of slow laps. In laps (lap 14 and lap 36) were both around 101s and out laps (lap 15 and 37) were both around 118s.
- Laps 41 and 42 were slow (120.5s and 104.8s) and this is because of a Virtual Safety Car deployment, which I can confirm by looking at the TrackStatus values, which for these laps were 126 and 671. He did not pit on either of these laps and I can confirm this as PitInTime and PitOutTime are empty on both laps.

To compare the three stints that Verstappen had during the race, I averaged the first three and last three clean laps of each one. 
Note: I define clean lap by green flag conditions (TrackStatus 1) on any lap bar lap 1 or an in/out lap.
- Stint 1 (Soft compound tyres): 98.01s to 98.52s --> about 0.5s slower at the end of the stint compared to the start
- Stint 2 (Soft compound tyres): 97.69s to 97.79s --> about 0.1s slower at the end of the stint compared to the start (basically negligible difference as it's such a small change, and one race can't tell me what caused it).
- Stint 3 (Hard compound tyres): 96.56s to 96.63s --> again, about 0.1s slower at the end of the stint compared to the start (same reason as in stint 2). This was his fastest stint.

### Why I zoomed in

On the graph I plotted using matplotlib, the y-axis had to stretch to about 120s to fit Verstappen's slowest laps. Verstappen's clean laps only ranged from about 96.2s to 98.6s, which meant that with such a large range on the y-axis they looked almost flat making it hard to see any changes within a stint. Using `plt.ylim(95.5, 99.5)` decreased the range of the y-axis and zoomed in on Verstappen's clean laps and cut the pit and VSC laps off the chart. 
Note: The VSC and pit in/out laps are still in the data and I'll remove them during cleaning. 

### Comparing three drivers 

I compared three drivers: Verstappen, Sainz and Hamilton. I made sure that they had all completed all 57 laps before analysing them. On the graph each driver got one colour and this is because colouring by compound (such as on the Verstappen graph) wouldn't show whose dot was whose. To avoid the issue of the y-axis range making the dots on the graph looking flat, I used `plt.ylim(95, 102)`. This left me with a readable graph which I could analyse and compare three drivers from. 

Pit stops (in laps):
When pitting you have both an in lap and an out lap. Here I am only noting down the in lap however it is important to know that if the driver rejoins the race, the out lap is the lap directly after the in lap (e.g. if the in lap is lap 4 then the out lap is lap 5)
- Verstappen: laps 14 and 36 (Soft, Soft, Hard)
- Sainz: laps 13 and 31 (Soft, Hard, Hard) 
- Hamilton: laps 12 and 30 (Soft, Hard, Hard) 

Average of the first three and last three clean laps of each stint: 
I calculated these values as they give a simple estimate of the change in lap times from the start of a stint, to the end of a stint. I calculated it only using clean laps, as defined above. 

- Stint 1: Verstappen 98.01s to 98.52s, Sainz 99.05s to 100.38s, Hamilton 99.25s to 100.45s
- Stint 2: Verstappen 97.69s to 97.79s, Sainz 98.19s to 98.54s, Hamilton 98.48s to 98.34s
- Stint 3: Verstappen 96.56s to 96.63s, Sainz 97.49s to 97.99s, Hamilton 97.75s to 98.11s 

Analysis: 
- All three drivers lost the most time in their first stint. Verstappen lost around 0.5s, Sainz around 1.3s and Hamilton around 1.2s.
- Verstappen was the fastest driver in the first stint, with both Sainz and Hamilton being over a second slower in their first stints.
- All three drivers were the fastest in their third stints (out of all three stints). Verstappen was the fastest of all three at the end in his third stint. 
- Both Verstappen and Sainz got slower from the start to the end of their second stints, however Hamilton got faster with his lap times decreasing by about 0.1s
- Sainz had one slow lap (lap 45) which lasted 99.56s, even though that lap had green flag conditions and he didn't pit. I don't know why yet. 

Limits of my comparison: 

- In the second stints, Verstappen was on soft compound tyres, whilst Sainz and Hamilton were both on hard compound tyres making it not a like-for-like comparison.
- This is a very small dataset (as it is only one race) and averages only use six laps from each stint (emphasising how little data is used). 

Hypotheses:

- Verstappen led in his first stint, so he may have had clean air which could have decreased his lap times. In the early laps Sainz ran 4th and Hamilton ran 5th, so they both may have been held up in traffic thus increasing their lap times. I haven't checked this yet. 
- The later stints being faster fits with fuel burning off, masking some of the tyre wear. However, the two charts cannot separate the two effects of fuel burning off and tyre degradation. 

### Why this matters for my project

- Before I start modelling anything I need to clean the data. I need to remove lap 1, pit laps (both in and out laps) and yellow flag and Safety Car/VSC laps, as they would distort my model as they are slow laps for reasons which are not tyre degradation. 
- Traffic might also affect lap times which I need to deal with when I clean the data. 
- Lap times alone don't directly measure tyre wear as fuel burn happens at the same time. My model will need to account for both to be accurate. 
- I need to check odd results like Sainz's lap 45 before assuming I know the cause of the anomaly. 

## Stage 4 - Choosing my races (5 Nov 2026)

In this stage I needed to decide which 2023 races I should use to train my model on, remove the wet races and also choose which dry races to hold back for testing. I wanted a mix of tyre wear in my test races, however I had not yet measured tyre wear and looked into it in detail. To solve this, I looked for sources on how hard each track was on tyres. While doing this, I found out that Pirelli had brought in a new and updated slick tyre to the British Grand Prix (round 10). In turn, I checked my reasoning to why I used only one season, because that only depended on the tyres staying comparable. 

### Why one season

Originally I stated that I am using one season because cars and tyres can change between seasons, so keeping to 2023 keeps my lap times comparable. If lap times change within my data, the cause is more likely to be something like tyre age than a difference between years. 

However, after doing some research on the 2023 season, I found out that the tyres may not have been the same all year. Formula 1 reported in May 2023 that Pirelli were set to bring a new slick tyre spec to the British Grand Prix, which was round 10 (https://www.formula1.com/en/latest/article.pirelli-set-to-introduce-new-slick-tyre-spec-at-silverstone.UxGxS3zoIJvaEdVCjEOs3.html). After the race, Mario Isola said "the new construction was working as expected" (https://www.grandprix247.com/2023/07/11/pirelli-the-new-tyre-construction-working-as-expected/). Neither article says whether it covered all compounds or all later races and I have not yet measured what effect the new slick tyre spec could have had on lap times. 

To compensate for this, I decided to hold back races from both before Silverstone (Australian and Spanish Grand Prixs) and after it (Japanese and United States Grand Prixs), so that my final test of the model covers both periods. This is useful because if all of my test races came from one side of the change, a good score would only show that my model works on that specific version/model of tyres. It would not tell me whether it works on the other version too. With two test races on each side of the tyre change, my final test of my model will cover both periods, and I will be able to make a better conclusion on my model and its accuracy as a result.

My training races also cover both periods, with 6 races from before the British Grand Prix (round 10), and 10 races from round 10 onwards. This means that my model will not only learn from one version of the tyres. Furthermore, it also means that I can compare the test scores from each side of the tyre change. If the scores were very different, that could be a sign that the change of tyres altered the way the tyres degraded. However it is important to note that it would not prove that concretely, as there are only 2 races on each side and as they are on different tracks - the sample size of test races is too small to make any certain conclusions. 
This does not remove the problem, but it means that my test does not rely on only one side of the change and gives me a way to check for it. 

### Finding wet races and cleaning the data

I wanted to clean my data to remove any races where there were either intermediate or wet tyre compounds used, as i mentioned in earlier stages. To do this, I listed the 2023 races with `fastf1.get_event_schedule`, which gave me 22 races. After that, I loaded each race and counted the laps driven on intermediate or wet tyres, of which only 2 races had any. 
- Monaco Grand Prix: 399 intermediate laps and 45 wet laps --> 444 in total.
- Dutch Grand Prix: 325 intermediate laps and 3 wet laps --> 328 in total.

I decided to drop any race with at least 1 lap on intermediate or wet tyre compounds, which ended up only being the two i listed above. This left me with 20 races of data that I could work with to train and test my model on. 
Note: What I did to clean the race data still keeps races where it rained, but no intermediate or wet tyre compounds were used. 

### Why I hold some races back

My model will need testing on some races that it has never seen. If I only tested it on races it trained on the score would look much better than it really is and as a result I would also not know if It would work on a new track that it hadn't seen before.

### The races I held back 

I decided to hold back 4 races, and I kept 16 races for training my model. Before choosing which races i held back, I counted the clean laps in all 20 dry races. I did this using my clean lap rule from earlier stages. The reason I did this was because clean laps are the laps I can actually use to both train and test my model on, so a race with very few of them would make a weak race to test my model on. I found out that the lowest clean lap count for a race was 644 laps at the Las Vegas Grand Prix, so I did not rule out any race to hold back for testing for this reason alone. Furthermore, I also split the counts by tyre compound and I did this because I wanted to see which tyres each race could test my model on. 

- Japanese Grand Prix
  - Main reason: High tyre wear track
  - Tyre wear evidence: Pirelli says the asphalt has "some of the highest levels of roughness and abrasion seen all season" (https://www.pitpass.com/76172/Japanese-GP-Preview-Pirelli).
  - What it tests: mostly Hard compound tyres (418 clean laps) and Medium compound tyres (212).
  - Limit: it has the fewest clean laps of my 4 races (686) and only 56 on Soft compound tyres.

- United States Grand Prix
  - Main reason: Medium tyre wear (my own classification), to test a track that was expected to be less extreme than Qatar.
  - Tyre wear evidence: GPblog reported that Pirelli expected "much more controllable tyre wear" compared with Qatar (https://www.gpblog.com/en/news/pirelli-preview-gp-united-states-cota.html).
  - What it tests: mostly Medium compound tyres (514 clean laps) and Hard compound tyres (391), with 912 clean laps in total.
  - Limit: the comparison is only with Qatar, which I found out that Mario Isola called "a very challenging circuit for tyres" (https://www.gpblog.com/en/news/241194/pirelli-warns-of-tyre-wear-gp-qatar-2023.html). This shows Austin was expected to be easier than Qatar, but it does not prove that it is a medium wear track, so this is my own judgement. It also only has 7 clean laps on Softs.

- Australian Grand Prix
  - Main reason: Medium/normal tyre wear 
  - Tyre wear evidence: Pirelli's preview says energy demands on the tyres are "about average for the season" with "contained levels of abrasion" (https://www.pitpass.com/74783/Australian-GP-Preview-Pirelli).
  - What it tests: mostly Hard compound tyres, with 655 clean laps out of 756 in total.
  - Limit: it only has 8 clean laps on soft compound tyres and 93 clean laps on Medium compound tyres. 

- Spanish Grand Prix
  - Main reason: Low tyre wear (my own classification). It also gives my test more clean laps on Softs from before Silverstone.
  - Tyre wear evidence: Mario Isola said "initial analysis suggests that degradation on all the compounds was lower, even with the softest C3" (https://press.pirelli.com/2023-spanish-grand-prix---sunday/).
  - What it tests: all three tyre compounds, with at least 324 clean laps on each (1207 clean laps in total).
  - Limit: the page does not say what the tyre degradation was lower than and the sentence before it mentions that track temperature was much lower than the year before. This may only describe this race and not the track in general, so classing it as a low wear track is my own assumption/interpretation of the quote.

I will not analyse or look into these 4 races until after i have trained my model. If I studied them now, what I see and learn could influence how I build my model. Furthermore they would no longer be unseen and I need some unseen races to test my model on. 

### What I need to remember

- Spain is my low wear track, but this is my own assumption from one post race comment. I did not find a source that directly calls any of my 4 races a low wear track, and the descriptions come from different articles. 
- 324 of the 395 clean Soft compound tyre laps in my test races come from Spain, so the test will say less about Soft compound tyres at other tracks.
- The Canadian Grand Prix has 35 laps with no compound recorded. I cannot tell which tyre those laps were on from this data, so I need to decide how to deal with them when I clean the data.

## Stage 5  - Cleaning part 1 (8 Nov 2026)

In this stage I began to clean my data, and I started with the Bahrain Grand Prix. The aim was to remove any laps that would be misleading for my model for the reasons of being either slow or unreliable for reasons other than tyre wear. The reason I chose to clean the Bahrain Grand Prix data first was because I already know this race well from earlier stages of my project.

### What I removed and why

- In laps and out laps: I removed these laps as they include time spent in the pit lane and as a result would look like laps with huge tyre wear (due to the increased lap time) when they are not. I used `laps.pick_wo_box()`, which only keeps laps where `PitInTime` and `PitOutTime` are both empty. Note: this is the same check I used for my clean lap rule in Stage 3. 
- Lap 1: I removed this lap for all drivers because it is slow for all of them due to the standing start and not the tyres degrading. 
- Inaccurate laps: `IsAccurate` is FastF1's own ruling system for whether it trusts the timing of a particular lap, so I only kept the laps where it was `IsAccurate == True` 
- Laps with no lap time: these laps will be useless to me as my model will not be able to learn anything from a lap with no lap time. 

### How many laps each step removed. 

| Step | Laps left | Laps removed |
|---|---:|---:|
|Start | 1056 | 0 | 
| Remove in laps and out laps | 954 | 102 |
| Remove lap 1 | 934 | 20 |
| Remove inaccurate laps | 914 | 20 |
| Remove laps with no lap time | 914 | 0 |

To summarise, I went from 1056 laps total for the Bahrain Grand Prix to 914 laps (142 laps were removed). 

### How FastF1 decides if a lap is accurate

It was important to me to understand what my inaccurate lap step was actually removing, as I did not understand how FastF1 decides if `IsAccurate` is True or False. I did this by using Claude to help me go through FastF1's code for the function that sets it, `_check_lap_accuracy` in `fastf1/core.py` (version 3.9.0). This function runs automatically when I call `session.load()` and it goes through every lap of every driver. 

A lap is only marked as accurate if it passes all 4 of its checks:
1. It has to be a normal racing lap which had complete data. This means that it cannot be: an in or out lap, it cannot be a lap that FastF1 created to fill in missing data, its track status has to be green or yellow (1, 2, 12, or 21) and it has to have a lap time and all three sector times. 
2. The three sector times have to add up to its lap time, to within 0.003s. If they do not then something is wrong with the timing data. 
3. The lap before it cannot be a Safety Car lap (track status 4), as the first lap after a Safety Car often has problems with the timing. 
4. Its lap time has to match the time between the end of the previous lap and the end of this one to within 0.003s.

With these 4 checks in place, if any one of them fails for a given lap, it will be marked as inaccurate. It was important to me that I understood this as it explains to me what I saw in the results of my data cleaning. 

### What I found when I checked the removed laps. 

Before I researched and understood my inaccurate step, I investigated the 20 laps that it removed. I found out that all of them were on laps 40, 41, 42 and had a TrackStatus of 126, 671 or 2671. All 3 of these codes contain a 6, which means a Virtual Safety Car had been deployed on those laps. This means that those 20 laps failed check 1 of the inaccurate lap checks, because their track status was not green or yellow. Furthermore, one of the 20 laps was Leclerc's lap 40, which had no lap time at all. 

My last step (removing laps with no lap time), removed zero laps. This is because check 1 had already marked every lap with no lap time as inaccurate, so the inaccurate step had already removed the only one at Bahrain (Leclerc's lap 40). This means that this step will always remove 0 laps when it comes after the inaccurate laps step. Despite this, I have decided to keep it as a safety check to make sure nothing goes wrong or missed. 

### Why the order matters. 

The number of laps that each step will remove depends on the steps that came before it. As an example, whilst 142 laps in the whole race are marked as inaccurate, only 20 were removed at the inaccurate lap step. This is because my first two steps had already removed the other 122 laps. My counts show what each step removed at that point in my cleaning, not how many laps in the race have that problem overall. 

### What I still need to do going forward. 

- 25 of my 914 laps are yellow flag laps (19 have TrackStatus 21 and 6 have TrackStatus 12). FastF1 counts yellow flag laps as accurate, so my inaccurate lap step kept these laps. However, as I planned in stages 2 and 3, I will remove these laps in my further cleaning steps as they are slow for reasons that are not tyre wear. I do not need to remove Safety Car or VSC laps separately, because check 1 already marks them as inaccurate, so my inaccurate lap step removes them. For Bahrain, this will leave 889 laps, which matches the 889 clean laps for Bahrain in my stage 4 table. 
- In Stage 3 I said that traffic might also affect lap times and that I would need to deal with this when cleaning my data. Whilst I have not done this yet I will look into it in further stages of my data cleaning. 
- When I loaded my races in Stage 4, FastF1 warned that "all laps marked as inaccurate" for one driver each at the Italian, Singapore, Qatar, and Sao Paulo Grand Prix. My inaccurate step could remove all of those drivers' laps, so I need to check this when I run my cleaning on more races. 
- In stage 4 I found that the Canadian Grand Prix has 35 laps with no compound recorded. None of my steps in this stage so far have been able to remove laps of such nature, so I still will need to decide how I want to deal with them. 
