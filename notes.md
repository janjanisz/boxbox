## Stage 0 (31 Oct 2026)

- The fastf1 library provides me with real F1 data of every lap of every driver, which tyre they were on, when they pitted and whether there was a safety car, in every race since 2018. I am using it because:
  - it's free.
  - it has good, lap-by-lap data: lap time, lap number, tyre compound (soft, medium, hard), tyre age (laps on that set of tyres), pit in and pit out laps and also track status (yellow flags, and safety cars)
  - it returns pandas DataFrames, which are easy for me to work with. 
This makes FastF1 fit my project well because it provides the exact data I need to measure tyre degradation and model pit strategy

- I'm using a virtual environment because: 
  - it keeps all of the projects separate, which is useful as different projects can use different libraries without them clashing. 
  - It makes the project reproducible on someone else's computer. Later on i will make a requirements file which has all the required libraries to run the project. 
  - Without a virtual  environment, simply updating a library in another project could break this project.

- I'm keeping .venv/ and cache/ out of GitHub because:
  - .venv/ is a very big file, which is specific to my Mac and which can be rebuilt with pip install. This makes uploading it pointless and it would add clutter to the repo.
  - cache/ is downloaded F1 data, making it a very big file. Its easy to download using the fastf1 library, making it pointless to upload. 
