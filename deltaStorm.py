import time

INTERVAL = 10 # seconds. MUST be same as time in .after() in getImgSubset in START.py
STORM = 1 # minutes. Amount of time of no snow before next "storm"
FLAKES = 2 # threshold number of snowflakes per 10 seconds to be qualified as "snowing"

def delta(images: list[list[str, int, int, int]]):
    ''' takes image data (self.imgpaths) list and calculates rate of snowfall for last INTERVAL '''

    flakes = 0
    top = images[0][1]
    for data in images:
        if top - data[1] < INTERVAL:
            flakes += 1
        else:
            break

    return flakes


def storm(dFlakes: list[int]):
    ''' dFlakes: list of number of flakes in 10 second interval 
    
    For every 10 second interval, dFlakes indexes the number of flakes detected in that 10 second period.
    
    * This function iterates through the list of snowflakes/10 seconds from newest to oldest.

    * If any of the rates of snowfall in that interval surpass the FLAKES threshold (set to 2 flakes per 10 seconds),
    it is considered to still be snowing.

    * If one hour (STORM constant) passes where no intervals have more than 2 snowflakes (FLAKES constant), the storm 
    is considered to be over.

    IF CURRENTLY IN STORM:
    Returns True is storm is over
    Returns False if storm continues

    IF CURRENTLY NOT IN STORM:
    Returns True is storm hasn't started
    Returns False if storm has started

    Call only if currently in storm
    '''

    i = 0
    for rate in reversed(dFlakes): 
        if rate > 2:
            return False
        
        if i > STORM*60/INTERVAL: # if the number of 10 second intervals is greater than the STORM interval * 60seconds/10seconds
            return True # new storm
        
        i+=1
    
        