I started this project bespoke for my dad to help him calculate the points for Dereham Runners AC's "Club 50" and "Club 100" awards.

--- OUTCOMES ---
- Good experience in creating a bespoke software for someone, having frequent discussions about how he wants it to work and then implementing these features as described.
- This was my first experience working with JSON files, so I leant a lot about them and thoight back to past projects where using these would have been much easier...
- This was also my first experience web scraping something from a real-world website (I previously only had experience scraping a website built for people learning how to web scrape) - but I figured it out without using a tutorial and was amazed when I finally got it working!
- I also learnt a lot about the importance of input validation, as I knew my dad would frequently make typos, so had to make sure these didn't crash the system. Also when we started using it I hasn't anticipated people having things like double barreled names, so next time I should think about all possibilities and anomalies that may arise before I finish a project.


--- DESCRIPTION ---
The way these awards work is that for certain distances there are specific times for each age category (called standards) that achieve different numbers of points.
Previously we had a speadsheet set up which automatically calculates the points from peoples times, but this was a slow process and frequently the laptop crashed, losing data.

So, I made this. It's a command line interface software, just ran in the terminal which has many different options.

Each person has their own 'profile' - a text file containing all of the races the person has done alongside the date, time and points awarded for each race. This is also where each person's age category is stored alongside their total points.

Inputting a race is as easy as specifying the race name, date and distance. The software then asks you to input peoples names alongside their times.

However, races with results on a TotalRaceTiming website (the company that times most races in norfolk) it is as easy as copy and pasting the URL of the race results. This web scrapes and automatically adds the correct amount of points to all Dereham Runners members based on the time they ran. This can also be done when adding parkruns (which are 1 point, up to 10 points total and for club 50 members only).

All in all I'm very happy with how this turned out, as when I started this project I never thought I would go as far as having to web scrape race data! I think my dad is pleased as well as he now has to spend much less time calculating the points and no more lost data (due to instant saving and frequent backups!) - However I expect there will still be many improvements to come for this system in the future.
