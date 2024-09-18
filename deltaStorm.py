import time, datetime

INTERVAL = 10*60 # seconds. 
STORM = 12*60*60 # seconds. Amount of time of no snow before next "storm" MUST be greater than 60
FLAKES = 18 # threshold number of snowflakes per interval to be qualified as "snowing"




def toggle(times, snowing):
    if times == []:
        return False
    
    m = min(times)
    r = max(times) - m
    
    delta = [0] * (int(r)//INTERVAL+1)
    
    for time in times:
        delta[int(time-m)//INTERVAL] += 1
        
    print(delta)
    if snowing == False:
        for f in reversed(delta[:int(STORM/INTERVAL)]): # check last STORM/INTERVAL intervals to see if they cross snowing threshold
            if f >= FLAKES:
                return True
            
        return False
    
    else:
        i = 0
        for f in reversed(delta):
            if f >= FLAKES:
                return False
            
            if i >= STORM/INTERVAL:
                return True
                
            i+=1
                
        return False # if list is not long enough yet
            
            
#ls = [0,1,2,12,13,43,42,55]
#print(toggle(ls, True))
    

def delta(times, snowing):
    ''' takes image data (self.imgpaths) list and calculates rate of snowfall for last INTERVAL '''
    if times == []:
        return False
    
    top = times[0]
    if snowing == False:
        flakes = 0
        for data in times:
            if top - data < INTERVAL:
                flakes += 1
            else:
                break
        
        if flakes > FLAKES:
            return True
        else:
            return False
            
    
    if snowing == True:
        flakes = 0
        #print(datetime.datetime.now().timestamp() - STORM*60)
        
        for data in times:
            if data > datetime.datetime.now().timestamp() - STORM*60:
                flakes +=1

        if flakes/(STORM/INTERVAL) < FLAKES:
            return True
        else:
            # need at least FLAKES flakes per interval to maintain storm status
            return False


        
   
def storm(dFlakes):
    ''' dFlakes: list of number of flakes in 0 second interval 
    
    For every interval, dFlakes indexes the number of flakes detected in that 10 second period.
    
    * This function iterates through the list of snowflakes/interval from newest to oldest.

    * If any of the rates of snowfall in that interval surpass the FLAKES threshold,
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
        if rate > FLAKES:
        
            return False
        
        if i > STORM*60/INTERVAL: # if the number of 60 second intervals is greater than the STORM interval * 60seconds/10seconds
            return True # new storm
        
        i+=1
    
        
