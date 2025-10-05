import math
import sys



def logfunct(n):  ## take log2 of each value 
    
    if n <= 0:
        return 0
    return int(math.log2(n))


def parse(filename="trace.config"):
    ## function to read in the config file - I could have probably went about this in a smoother way
    # currently it reads in the file, looks for the matching string, then strips the value after the colon. 
    # Though the way i iterate to get the number of lines is probably glitchy if the config file changes
    # I include power of 2 check, and make sure the values don't go outside of the max size described in the pdf
    #I'm not sure if using a dict was the right approach but it made sense originally there was probably a better way
    
   # try:
        #print(f"check file: {filename}")

    with open(filename, 'r') as cofigdata:
        lines = []  # init list
        for line in cofigdata:
            #print(f" line {(line)}")
            stripline = line.strip()        # remove newlines and white spaces
            #print(f" line {(stripline)}")
            if stripline:                   # check if line is clean then add
                lines.append(stripline)     
                #print(f" line {(stripline)}")
                
    configurationvariables = {}     # create dict 

    i = 0
    while i < len(lines):
        line = lines[i]

        if "Data TLB configuration" in line:  # ensure in correct line then set dict var to be the value outside the : 
            configurationvariables['TLBsets'] = int(lines[i+1].split(':')[1].strip())  #DTLB sets  # looks at line below
            configurationvariables['TLBsetsize'] = int(lines[i+2].split(':')[1].strip())  #num sets  # looks at 2 lines below
            i += 3  # read through each line then ptconfig

        elif "Page Table configuration" in line:
            configurationvariables['ptvirtpages'] = int(lines[i+1].split(':')[1].strip())
            configurationvariables['ptphyspages'] = int(lines[i+2].split(':')[1].strip())
            configurationvariables['ptpagesize'] = int(lines[i+3].split(':')[1].strip())
            i += 4

        elif "Data Cache configuration" in line:
            configurationvariables['Dcachesets'] = int(lines[i+1].split(':')[1].strip())
            configurationvariables['Dcachesetsize'] = int(lines[i+2].split(':')[1].strip())
            configurationvariables['Dcachelinesize'] = int(lines[i+3].split(':')[1].strip())
            configurationvariables['Dwritepolicy'] = lines[i+4].split(':')[1].strip()
            i += 5

        elif "L2 Cache configuration" in line:
            configurationvariables['l2sets'] = int(lines[i+1].split(':')[1].strip())
            configurationvariables['l2setsize'] = int(lines[i+2].split(':')[1].strip())
            configurationvariables['l2linesize'] = int(lines[i+3].split(':')[1].strip())
            configurationvariables['l2writepolicy'] = lines[i+4].split(':')[1].strip()
            i += 5

        elif "Virtual addresses:" in line:
            configurationvariables['virtaddress'] = line.split(':')[1].strip()
            i += 1
        elif "TLB:" in line:
            configurationvariables['TLB'] = line.split(':')[1].strip()
            i += 1
        elif "L2 cache:" in line:
            configurationvariables['l2setting'] = line.split(':')[1].strip()
            i += 1
        else:
            i += 1

    
    def power2check(val):  ## check ito make sure each value in config is a power of 2
        if val <= 0:
            return False
        power = 1
        while power < val:
            power *= 2
        return power == val

    
    # check max sizes and power of 2 requirements
    if configurationvariables['TLBsets'] > 256:
        print(f"Error: DTLB sets ({configurationvariables['TLBsets']}) exceeds max 256")
        return None
   
    if not power2check(configurationvariables['TLBsets']):
        print(f"Error: DTLB sets ({configurationvariables['TLBsets']}) must be power of 2")
        return None
        
    if configurationvariables['Dcachesets'] > 8192:
        print(f"Error: DC sets ({configurationvariables['Dcachesets']}) exceeds max 8192")
        return None
   
    if not power2check(configurationvariables['Dcachesets']):
        print(f"Error: DC sets ({configurationvariables['Dcachesets']}) must be power of 2")
        return None
        
    # check line size limits + power of 2
    if configurationvariables['Dcachelinesize'] < 8:
        print(f"Error: DC line size ({configurationvariables['Dcachelinesize']}) must be at least 8")
        return None
    if not power2check(configurationvariables['Dcachelinesize']):
        print(f"Error: DC line size ({configurationvariables['Dcachelinesize']}) must be power of 2")
        return None
    
    # check associativ  
    if configurationvariables['TLBsetsize'] > 8:
        print(f"Error: DTLB associativity ({configurationvariables['TLBsetsize']}) exceeds max 8")
        return None
    
    if configurationvariables['Dcachesetsize'] > 8:
        print(f"Error: DC associativity ({configurationvariables['Dcachesetsize']}) exceeds max 8")
        return None
    
    if configurationvariables['l2setsize'] > 8:
        print(f"Error: L2 associativity ({configurationvariables['l2setsize']}) exceeds max 8")
        return None

    # check virt pages max . power 2
    if configurationvariables['ptvirtpages'] > 8192:
        print(f"Error: Virtual pages ({configurationvariables['ptvirtpages']}) exceeds max 8192")
        return None
    if not power2check(configurationvariables['ptvirtpages']):
        print(f"Error: Virtual pages ({configurationvariables['ptvirtpages']}) must be power of 2")
        return None
    
    # check phys pages max
    if configurationvariables['ptphyspages'] > 1024:
        print(f"Error: Physical pages ({configurationvariables['ptphyspages']}) exceeds max 1024")
        return None
    
    # check pg size power of 2
    if not power2check(configurationvariables['ptpagesize']):
        print(f"Error: Page size ({configurationvariables['ptpagesize']}) must be power of 2")
        return None
    
    # check L2 line size >= DC line size
    if configurationvariables['l2linesize'] < configurationvariables['Dcachelinesize']:
        print(f"Error: L2 line size ({configurationvariables['l2linesize']}) must be >= DC line size ({configurationvariables['Dcachelinesize']})")
        return None

    return configurationvariables





def calcbits(configurationvariables):
    # calculated the index/ tag/ offset bits for ptable, dcache, and L2
    
  
 #tlb index bits, 
    configurationvariables['tlbindex'] = logfunct(configurationvariables['TLBsets'])   # Take log2 of dtlb
    
    # ptable index virt pages and offset bits

    configurationvariables['ptablebits'] = logfunct(configurationvariables['ptvirtpages'])
    configurationvariables['poffsetbits'] = logfunct(configurationvariables['ptpagesize'])

    # dcache index and offset
    configurationvariables['dcacheindex'] = logfunct(configurationvariables['Dcachesets'])
    configurationvariables['dcacheoffset'] = logfunct(configurationvariables['Dcachelinesize'])

        #  #l2 index and offset
    configurationvariables['l2cacheindex'] = logfunct(configurationvariables['l2sets'])
    configurationvariables['l2cacheoffset'] = logfunct(configurationvariables['l2linesize'])

    return configurationvariables



#### redid 
def memsimulation(config):

    # Check configuration flags
    virtmemoryon = config['virtaddress'].lower() == 'y'
    tlbon = config['TLB'].lower() == 'y'
    l2enabled = config['l2setting'].lower() == 'y'

    
    datacache = {}  # Init dictionary/  key= cache set index, value= list with tag, validbit, dirtybit

    l2cache = {} 
    
    pagetable = {}  #key = vpn/ value=phys pnum
    tlb = {}
    statoutput = {
        'dc_hits': 0, 'dc_misses': 0, 'l2hits': 0, 'l2misses': 0, # caches

        
        'dtlb_hits': 0, 'dtlb_misses': 0, 'pt_hits': 0, 'pt_faults': 0, # address translations
        
        'allreads': 0, 'allwrites': 0, 'page_table_refs': 0, 'disk_refs': 0, 'mainmemrefs': 0 # acces/mem
    }

    print("Virtual  Virt.  Page TLB    TLB TLB  PT   Phys        DC  DC          L2  L2")
    print("Address  Page # Off  Tag    Ind Res. Res. Pg # DC Tag Ind Res. L2 Tag Ind Res.")
    print("-------- ------ ---- ------ --- ---- ---- ---- ------ --- ---- ------ --- ----")

    # may need to make output screen bigger or else it prints off


   
    pageoffsetbits = config['poffsetbits']   # init
    dcindexbits = config['dcacheindex'] 
    dcoffsetbits = config['dcacheoffset']

    # compute sizes in powers of two
    pagebytes  = 1 << pageoffsetbits   # x bytes per page

    #  These were  incorrect tag calculations
    # linebytes  = 1 << dcoffsetbits     # bytes per DC line
    # numsets    = 1 << dcindexbits      # number of DC sets (not bytes)


    # Read from stdin 
    for line in sys.stdin: #grab each trace
        line = line.strip()
        if not line:
            continue
    
        try:
            # get the addresses 
            acctype, hexaddr = line.split(':')  # split up r/w and hex address
            address = int(hexaddr, 16)  # convert to int

            # Update read/write statistics
            if acctype == 'R':
                statoutput['allreads'] += 1
            else:
                statoutput['allwrites'] += 1

            pageoffset = address % pagebytes  #get page offset
            pagenumber = address // pagebytes # get page number can be virtual or physical!!

            #    incorrect tag calc
            # blocknumber = address // linebytes  # get block num
            # dc_index = blocknumber % numsets # calc data cache index
            # dctag = blocknumber // numsets # calc data cache tag


                # Init output field
            virtpagenum = ""
            tlbtagnum = ""
            tlbindex   = ""
            tlboutput  = ""
            
            ptoutput   = ""
            physpnum   = ""
            
            l2tag      = ""
            l2index    = ""
            l2result   = ""
            dcresult   = ""


            # Init isplay variables for correct tag/index  from cache functions
            dctagprint= ""     
            dcindexprint = ""       
            
            l2tagprint = ""      
            l2indexprint = ""    

            # check if virtual memory on
            if virtmemoryon:
                if tlbon: # and tlb on
                    
                    result = tlbaccess(address, acctype, tlb, pagetable, datacache, l2cache, config, statoutput)  # run simulation
                    virtpagenum = f"{result['virtpagenumber']:6x}"
                    physpnum    = f"{result['physpagenumber']:4x}"
                    tlbtagnum = f"{result['virtpagenumber'] >> config['tlbindex']:6x}"
                    tlbindex  = f"{result['virtpagenumber'] % (1 << config['tlbindex']):3x}"
                    tlboutput = f"{result['tlbresult']:4s}"
                    ptoutput  = f"{result['ptresult']:4s}"
                    dcresult  = f"{result['dcresult']['result']:4s}"

                    
                    dctagprint = result['dcresult']['tag']      # Get DC tag used by cache
                    dcindexprint = result['dcresult']['index']  # Get DC index used by cache
                    
                
                    # Handle L2 results when enabled and present
                    if l2enabled:
                        if result.get('l2result'):  # L2 was accessed on DC miss
                            l2result = f"{result['l2result']['result']:4s}"
                            l2tagprint = result['l2result']['tag']      # Get L2 tag used by cache
                            l2indexprint = result['l2result']['index']  # Get L2 index used by cache
                        else:  # L2 not accessed (DC hit), leave L2 fields empty
                            l2result = ""
                            l2tagprint = ""
                            l2indexprint = ""


                else:  # Virtual memory On **WITHOUT** TLB
                    
                    result = memorytrans(address, acctype, pagetable, datacache, l2cache, config, statoutput)
                    virtpagenum = f"{result['virtpagenumber']:6x}"
                    physpnum    = f"{result['physpagenumber']:4x}"
                    ptoutput    = f"{result['ptresult']:4s}"
                    dcresult    = f"{result['dcresult']['result']:4s}"
                
                    
                    dctagprint = result['dcresult']['tag']      # get  DC tags/indexes from cache function results
                    dcindexprint = result['dcresult']['index']  
                    
                    # Handle L2 results when enabled and present
                    if l2enabled:
                        if result.get('l2result'):  # L2 was accessed on DC miss
                            l2result = f"{result['l2result']['result']:4s}"
                            
                            l2tagprint = result['l2result']['tag']         # Gt L2 tags/indexes from cache function results
                            l2indexprint = result['l2result']['index']  
                                
                        else:  # L2 not accessed DC hit, leave L2 fields empty
                            l2result = ""
                            l2tagprint = ""
                            l2indexprint = ""
            
            else:  # ONLY Physical addresses 
                
                physpnum = f"{pagenumber:4x}"
                dc_result = alldatacache(address, acctype, datacache, config, statoutput,  l2cache=l2cache, l2enabled=l2enabled) 
                
                dcresult = f"{dc_result['result']:4s}"
                
                
                dctagprint = dc_result['tag']      # Gt L2 tags/indexes from cache function results
                dcindexprint = dc_result['index'] 
            
                

                # If DC miss and L2 enabled, access L2 then enforce inclusive policy
                if l2enabled and dc_result['result'] == 'miss':
                    l2_result_obj = l2datacache(address, acctype, l2cache, config, statoutput)
                    
                    # Force allocate in DC to maintain inclusive policy
                    alldatacache(address, acctype, datacache, config, statoutput, allocate=True)
                    
                    l2result = f"{l2_result_obj['result']:4s}"
                    l2tagprint = l2_result_obj['tag']      # Get L2 tags/indexes from cache function results
                    l2indexprint = l2_result_obj['index']
                
                else:  # DC hit or L2 disabled - no L2 access
                    l2result = ""
                    l2tagprint = ""
                    l2indexprint = ""
            
        
            print(f"{address:08x} {virtpagenum:>6} {pageoffset:4x} {tlbtagnum:>6} {tlbindex:>3} {tlboutput:>4} {ptoutput:>4} {physpnum:>4} {dctagprint:>6} {dcindexprint:>3} {dcresult:>4} {l2tagprint:>6} {l2indexprint:>3} {l2result:>4}")
            
            #print(f"{address:08x} {virtpagenum:>6} {pageoffset:>4x} {tlbtagnum:>6} {tlbindex:>3} {tlboutput:>4} {ptoutput:>4} {physpnum:>4} {dctagprint:>6} {dcindexprint:>3} {dcresult:>4} {l2tagprint:>6} {l2indexprint:>3} {l2result:>4}")
        except Exception as e:
            print(f"Error processing line '{line}': {e}")

    # Print stats at the end
    print()
    printstats(statoutput, config)




def printstats(statoutput, config):  
    #Print final sim statistics 
    
    print("Simulation statistics \n")
    
    # TLB stats - always print
    dtlbtotal = statoutput.get('dtlb_hits', 0) + statoutput.get('dtlb_misses', 0)  # Get total access = hits+misses
    dtlbratio = statoutput.get('dtlb_hits', 0) / dtlbtotal if dtlbtotal > 0 else 0.0   # hits/total hits = hit ration
    print(f"dtlb hits        : {statoutput.get('dtlb_hits', 0)}")
    print(f"dtlb misses      : {statoutput.get('dtlb_misses', 0)}")
    print(f"dtlb hit ratio   : {dtlbratio:.6f}\n")
    
    # Page table stats 
    pagetabletotal = statoutput.get('pt_hits', 0) + statoutput.get('pt_faults', 0)  # total page table access = hits+ faults
    pt_hit_ratio = statoutput.get('pt_hits', 0) / pagetabletotal if pagetabletotal > 0 else 0.0  # ration = hits/ total
    
    print(f"pt hits          : {statoutput.get('pt_hits', 0)}")
    print(f"pt faults        : {statoutput.get('pt_faults', 0)}")
    print(f"pt hit ratio     : {pt_hit_ratio:.6f}\n")
    
   
     ## D cach statistics always print
    dcachetotal = statoutput.get('dc_hits', 0) + statoutput.get('dc_misses', 0)  # total datacach hits+mis
    dchitratio = statoutput.get('dc_hits', 0) / dcachetotal if dcachetotal > 0 else 0.0  # hit ratio
    print(f"dc hits          : {statoutput.get('dc_hits', 0)}")
    print(f"dc misses        : {statoutput.get('dc_misses', 0)}")
    print(f"dc hit ratio     : {dchitratio:.6f}\n")


    
    # L2 cach stats 
    l2cachetotal = statoutput.get('l2hits', 0) + statoutput.get('l2misses', 0)   # l2 cache hits+miss = total
    l2hitratio = statoutput.get('l2hits', 0) / l2cachetotal if l2cachetotal > 0 else 0.0  #l2 ration 
    print(f"L2 hits          : {statoutput.get('l2hits', 0)}")
    print(f"L2 misses        : {statoutput.get('l2misses', 0)}")
    print(f"L2 hit ratio     : {l2hitratio:.6f}\n")
    
    # Access type stats always on
    totalmemaccesses = statoutput.get('allreads', 0) + statoutput.get('allwrites', 0)     # get all access to memory for reads/writes
    readratio = statoutput.get('allreads', 0) / totalmemaccesses if totalmemaccesses > 0 else 0.0  # all read ration = allreads/totalmemaccess if no reads =0
    
    print(f"Total reads      : {statoutput.get('allreads', 0)}")
    print(f"Total writes     : {statoutput.get('allwrites', 0)}")
    print(f"Ratio of reads   : {readratio:.6f}\n")
    
    # Memory reference stat
    print(f"main memory refs : {statoutput.get('mainmemrefs', 0)}")
    print(f"page table refs  : {statoutput.get('page_table_refs', 0)}")
    print(f"disk refs        : {statoutput.get('disk_refs', 0)}\n")





def printvars(configurationvariables):


    print(f"Data TLB contains {configurationvariables['TLBsets']} sets.")
    print(f"Each set contains {configurationvariables['TLBsetsize']} entries.")
    print(f"Number of bits used for the index is {configurationvariables['tlbindex']}. \n")
    
    print(f"Number of virtual pages is {configurationvariables['ptvirtpages']}.")
    print(f"Number of physical pages is {configurationvariables['ptphyspages']}.")
    print(f"Each page contains {configurationvariables['ptpagesize']} bytes.")
    print(f"Number of bits used for the page table index is {configurationvariables['ptablebits']}.")
    print(f"Number of bits used for the page offset is {configurationvariables['poffsetbits']}. \n")
    
    print(f"D-cache contains {configurationvariables['Dcachesets']} sets.")
    print(f"Each set contains {configurationvariables['Dcachesetsize']} entries.")
    print(f"Each line is {configurationvariables['Dcachelinesize']} bytes.")
    
    if configurationvariables['Dwritepolicy'].lower() == 'n':
        print("The cache uses a write-allocate and write-back policy.")
    else:
        print("The cache uses a write-through and no write-allocate policy.")
    
    print(f"Number of bits used for the index is {configurationvariables['dcacheindex']}.")
    print(f"Number of bits used for the offset is {configurationvariables['dcacheoffset']}. \n")
    
    print(f"L2-cache contains {configurationvariables['l2sets']} sets.")
    print(f"Each set contains {configurationvariables['l2setsize']} entries.")
    print(f"Each line is {configurationvariables['l2linesize']} bytes.")
    
    # L2 
    if configurationvariables['l2writepolicy'].lower() == 'n':
        print("The cache uses a write-allocate and write-back policy.")
    else:
        print("The cache uses a write-through and no write-allocate policy.")
    

    print(f"Number of bits used for the index is {configurationvariables['l2cacheindex']}.")
    print(f"Number of bits used for the offset is {configurationvariables['l2cacheoffset']}. \n")
    
    if configurationvariables['virtaddress'].lower() == 'y':
        print("The addresses read in are virtual addresses. \n")
    else:
        print("The addresses read in are physical addresses.\n")





def alldatacache(address, acctype, datacache, config, statoutput, l2cache=None, l2enabled=False, allocate=False):
   
   
   #Use a direct-mapped organization (set size = 1) and assume all references are reads
  #      $tracks hits and misses for each memory reference


    dcoffsetbits = config['dcacheoffset']     # log2(bytes per cache line)
    dcindexbits  = config['dcacheindex']      # log2(number of sets)

    linebytes  = 1 << dcoffsetbits            # bytes per cache line
    numsets    = 1 << dcindexbits             # total sets in cache


    blocknumber = address // linebytes        # which block of memory we're in
    datacacheindx = blocknumber % numsets      # which cache set we go to
    dctag       = blocknumber // numsets     # tag bits beyond index

    setsize = config['Dcachesetsize']     # Get associativity level
   
    writepolicy = config['Dwritepolicy'].lower()   #Check write policy n = write allocate  || y = no write allocate
    


# add allocation for inclusive cache policy after L2 fetch
    if allocate:  
        #sstatoutput['dc_misses'] += 1  # count as miss since DC didn't originally have it
        
        if setsize == 1:  # direct mapped cache
            oldtag, oldvalid, olddirty = datacache.get(datacacheindx, (None, False, False))  # get existing line if present
            if oldvalid and olddirty:  # if old valid + dirty then writeback
                statoutput['writeback'] = statoutput.get('writeback', 0) + 1
            datacache[datacacheindx] = (dctag, True, False)      # replace with new tag, valid, clean
        
        else:  # associative cache = setsize > 1
            cacheset = datacache.get(datacacheindx, [])     # get cache set or init empty list
            if len(cacheset) >= setsize:                    # cache full evict least recen used
                removetag, removevalid, removedirty = cacheset.pop(0)  # remove least recent used

                if removevalid and removedirty:              #  writeback if old valid & dirty
                    statoutput['writeback'] = statoutput.get('writeback', 0) + 1
            cacheset.append((dctag, True, False))            # add new entry at end (most recently used)
            datacache[datacacheindx] = cacheset             # then update cache 
        
        return {
            'index': f"{datacacheindx:3x}",
            'tag': f"{dctag:6x}",
            'result': 'miss'
        }

    # Start with direct map cach    

    if setsize == 1:
        if datacacheindx not in datacache: # if miss or empty/ init
            # datacache[datacacheindx] = None  # No line present initially
            datacache[datacacheindx] = (None, False, False)  # init valid/dirty bit for write allocate/writeback


        #  validbit check 
        tag, validbit, dirtybit = datacache[datacacheindx]  


            ## hit / miss handling direct mapped cach
            # chceck cache valid entry and matching tag  
        if validbit and tag == dctag:   #  validbit check
            statoutput['dc_hits'] += 1  # hit
            
            #IF hit + write policy
            if acctype == 'W':  
                if writepolicy == 'n':  #write allocate
                    dirtybit = True  # if write  add dirty bit
              
                else:   # no write allocate
                    # Write through immediately goes to next lvl /l2/main after writing to cache - wish i remembered this for the test
                    dirtybit = False  # no dirty bit since write through
                    #  write through to L2 or main memory
                    if l2enabled and l2cache is not None:
                        l2datacache(address, acctype, l2cache, config, statoutput)
                    else:
                        statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1                   

            datacache[datacacheindx] = (dctag, True, dirtybit)  # add dirty bit to tag
            return {
                'index': f"{datacacheindx:3x}",
                'tag':   f"{dctag:6x}",
                'result': 'hit'
            }



## Direct mapped cach on miss 
# y = no write allocate
        
        if acctype == 'W' and writepolicy == 'y':  
            statoutput['dc_misses'] += 1   #  miss

            if l2enabled and l2cache is not None:
                l2datacache(address, acctype, l2cache, config, statoutput)
            else:
                statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1
            # goes immmediately to main/l2
            return {
                'index': f"{datacacheindx:3x}",           
                'tag':   f"{dctag:6x}",            
                'result': 'miss'
            }
        
        # write allocate + write-back on miss

        statoutput['dc_misses'] += 1   # else miss  first read / mismatched tag
        # if L2 disabled, DC miss goes directly to main memory
        if not l2enabled:
            statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1
    
        # Before overwriting check for right back
        oldtag, oldvalid, olddirty = datacache[datacacheindx] # Replace the old with new tag for direct mapped / always replace policy
        if oldvalid and olddirty:  # if old valid & dirt - writeback
            statoutput['writeback'] = statoutput.get('writeback', 0) + 1

        # if write allocate + write back 
        if writepolicy == 'n':  
            dirtybit = True if acctype == 'W' else False

        else:  # write through + no write allocate on read miss = allocate
            dirtybit = False  # no dirty bits in write-through
        datacache[datacacheindx] = (dctag, True, dirtybit)  # Store 

        return {
            'index': f"{datacacheindx:3x}",           
            'tag':   f"{dctag:6x}",            
            'result': 'miss'
        }
    
    
    
    # ### deal with0 assocociativity >1 
        # assoc>1 creates multiple cache lines
    else:
        
        if datacacheindx not in datacache:
            datacache[datacacheindx] = []  #  list to store tag, valid/dirty

        cacheset = datacache[datacacheindx]  # Get list of cache we're working with in set

      
        for i, (tag, validbit, dirtybit) in enumerate(cacheset):   # on hit check all cache lines/ways for hit update for dirty bit 
            if validbit and tag == dctag: # if hit
              
                statoutput['dc_hits'] += 1  # update

                # Add write policy  
                # write allocate / write back
                if acctype == 'W':
                    if writepolicy == 'n':  
                        dirtybit = True  # update dirtbit if write
                   
                    else:  # write through/no write allocate policy
                        dirtybit = False  # no dirty bit needed since we write through
                        #statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1  # write through to main

                        if l2enabled and l2cache is not None:
                            l2datacache(address, acctype, l2cache, config, statoutput)
                        else:
                            statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1

                # lru on hit 
                hit_entry = (tag, True, dirtybit)  # move hit entry to endmost recently used 
                cacheset.pop(i)  # Remove the hit entry from its current position
                cacheset.append(hit_entry)   # add most rec used
                return {
                    'index': f"{datacacheindx:3x}",   
                    'tag':   f"{dctag:6x}",      
                    'result': 'hit'
                }

       
        # if miss  set assoc>1
        if acctype == 'W' and writepolicy == 'y':  # write through  + no write 
            
            statoutput['dc_misses'] += 1   # miss
            # Write through to L2 or main memory (no allocate in DC)
            if l2enabled and l2cache is not None:
                l2datacache(address, acctype, l2cache, config, statoutput)
            else:
                statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1
            return {
                'index': f"{datacacheindx:3x}",           
                'tag':   f"{dctag:6x}",            
                'result': 'miss'
            }

        statoutput['dc_misses'] += 1   # if not hit record cache miss


        # if L2 disabled, DC miss goes directly to main memory
        if not l2enabled:
            statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1


       # lru cachhe not full
        if len(cacheset) < setsize:  #  Handle cache line replacement
            # cache set is not full  add new entry at end 
            #cacheset.append((dctag, True))  # Add new cache line without replacement
           
           
            if writepolicy == 'n':  # write allocate  /write back
                dirtybit = True if acctype == 'W' else False  # update write all
            else:  # write through  + no write on read miss=  allocate
                dirtybit = False  # no dirty bit write through
            cacheset.append((dctag, True, dirtybit)) 
            return {
                'index': f"{datacacheindx:3x}",
                'tag':   f"{dctag:6x}",
                'result': 'miss'
            }

            
        else:
            # cache is full  need to evict least recently used entry
            #  index 0 = lru
            #  end = most recently used
            removetag, removevalid, removedirty =cacheset.pop(0)  # remove lru 

            if removevalid and removedirty:
                statoutput['writeback'] = statoutput.get('writeback', 0) + 1 
            
            if writepolicy == 'n':  # write allocate  / write back
                dirtybit = True if acctype == 'W' else False  
            
            else:  # write through  + no write alloc on read miss =  allocate
                dirtybit = False # 
            cacheset.append((dctag, True, dirtybit))  

        return {
            'index': f"{datacacheindx:3x}",           
            'tag':   f"{dctag:6x}",            
            'result': 'miss'
        }


## the l2 cache is just a rewrite of the datacache so the code is reused 


def l2datacache(address, acctype, l2cache, config, statoutput):
   #Use a direct-mapped organization (set size = 1) and assume all references are reads
  #      $tracks hits and misses for each memory reference

    l2offsetbits = config['l2cacheoffset']     # log2(bytes per cache line)
    l2indexbits  = config['l2cacheindex']      # log2(number of sets)

    linebytes  = 1 << l2offsetbits            # bytes per cache line
    numsets    = 1 << l2indexbits             # total sets in cache

    blocknumber = address // linebytes        # which block of memory we're in
    l2cacheindx = blocknumber % numsets      # which cache set we go to
    l2tag       = blocknumber // numsets     # tag bits beyond index

  
    setsize = config['l2setsize']     # Get associativity level
    
   
    writepolicy = config['l2writepolicy'].lower()   #Check write policy n = write allocate  || y = no write allocate
    

    # Start with direct map cache    
    if setsize == 1:
        # if miss or empty/ init
        if l2cacheindx not in l2cache:
            # l2cache[l2cacheindx] = None  # No line present initially
            l2cache[l2cacheindx] = (None, False, False)  # init valid/dirty bit for write allocate/writeback


        #  validbit check 
        tag, validbit, dirtybit = l2cache[l2cacheindx]  

            ## hit / miss handling direct mapped cache
            # check cache valid entry and matching tag  
        if validbit and tag == l2tag:   #  validbit check
            statoutput['l2hits'] += 1  # hit
            
            #IF hit + write policy
            if acctype == 'W':  
                if writepolicy == 'n':  #write allocate
                    dirtybit = True  # if write  add dirty bit
              
                else:   # no write allocate
                    # Write through immediately goes to next lvl /main after writing to cache - wish i remembered this for the test
                    dirtybit = False  # no dirty bit since write through
                    statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1   # write though to main


            l2cache[l2cacheindx] = (l2tag, True, dirtybit)  # add dirty bit to tag
            return {
                'index': f"{l2cacheindx:3x}",
                'tag':   f"{l2tag:6x}",
                'result': 'hit'
            }

## Direct mapped cache on miss 
# y = no write allocate
        
        if acctype == 'W' and writepolicy == 'y':  
           
            # goes immediately to main/l2
            statoutput['l2misses'] += 1   #  miss
            return {
                'index': f"{l2cacheindx:3x}",           
                'tag':   f"{l2tag:6x}",            
                'result': 'miss'
            }
        
        # write allocate + write-back on miss

        statoutput['l2misses'] += 1   # else miss  first read / mismatched tag
        statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1   # add main memory references for l2
    
        # Before overwriting check for write back
        oldtag, oldvalid, olddirty = l2cache[l2cacheindx] # Replace the old with new tag for direct mapped / always replace policy
        if oldvalid and olddirty:  # if old valid & dirty - writeback
            statoutput['l2writeback'] = statoutput.get('l2writeback', 0) + 1
            statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1   # add main memory references for l2

        # if write allocate + write back 
        if writepolicy == 'n':  
            dirtybit = True if acctype == 'W' else False

        else:  # write through + no write allocate on read miss = allocate
            dirtybit = False  # no dirty bits in write-through
        l2cache[l2cacheindx] = (l2tag, True, dirtybit)  # Store 

        return {
            'index': f"{l2cacheindx:3x}",           
            'tag':   f"{l2tag:6x}",            
            'result': 'miss'
        }
    
    
    # ### deal with associativity >1 
        # assoc>1 creates multiple cache lines
    else:
        
        if l2cacheindx not in l2cache:
            l2cache[l2cacheindx] = []  #  list to store tag, valid/dirty

        cacheset = l2cache[l2cacheindx]  # Get list of cache we're working with in set

      
        for i, (tag, validbit, dirtybit) in enumerate(cacheset):   # on hit check all cache lines/ways for hit update for dirty bit 
            if validbit and tag == l2tag: # if hit
              
                statoutput['l2hits'] += 1  # update

                # Add write policy  
                # write allocate / write back
                if acctype == 'W':
                    if writepolicy == 'n':  
                        dirtybit = True  # update dirtbit if write
                   
                    else:  # write through/no write allocate policy
                        dirtybit = False  # no dirty bit needed since we write through
                        statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1  # ADD THIS LINE

                # lru on hit 
                hit_entry = (tag, True, dirtybit)  # move hit entry to endmost recently used 
                cacheset.pop(i)  # Remove the hit entry from its current position
                cacheset.append(hit_entry)   # add most rec used
                return {
                    'index': f"{l2cacheindx:3x}",   
                    'tag':   f"{l2tag:6x}",      
                    'result': 'hit'
                }

       
        # if miss  - set assoc>1
        if acctype == 'W' and writepolicy == 'y':  # write through  + no write 
            
            statoutput['l2misses'] += 1   # miss
            statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1  # write through to main

            return {
                'index': f"{l2cacheindx:3x}",           
                'tag':   f"{l2tag:6x}",            
                'result': 'miss'
            }

        statoutput['l2misses'] += 1   # if not hit record cache miss
        statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1   # add main memory references for l2

       # lru cache not full
        if len(cacheset) < setsize:  #  Handle cache line replacement
            # cache set is not full  add new entry at end 
            #cacheset.append((l2tag, True))  # Add new cache line without replacement
           
           
            if writepolicy == 'n':  # write allocate  /write back
                dirtybit = True if acctype == 'W' else False  # update write all
            else:  # write through  + no write on read miss=  allocate
                dirtybit = False  # no dirty bit write through
            cacheset.append((l2tag, True, dirtybit)) 
            return {
                'index': f"{l2cacheindx:3x}",
                'tag':   f"{l2tag:6x}",
                'result': 'miss'
            }

        else:
            # cache is full  need to evict least recently used entry
            #  index 0 = lru
            #  end = most recently used
            removetag, removevalid, removedirty =cacheset.pop(0)  # remove lru 

            if removevalid and removedirty:
                statoutput['l2writeback'] = statoutput.get('l2writeback', 0) + 1 
                statoutput['mainmemrefs'] = statoutput.get('mainmemrefs', 0) + 1   # add main memory references for l2
            
            if writepolicy == 'n':  # write allocate  / write back
                dirtybit = True if acctype == 'W' else False  
            
            else:  # write through  + no write alloc on read miss =  allocate
                dirtybit = False # 
            cacheset.append((l2tag, True, dirtybit))  

        return {
            'index': f"{l2cacheindx:3x}",           
            'tag':   f"{l2tag:6x}",            
            'result': 'miss'
        }



def pagetablereq(virtpage, pagetable, config, statoutput, tlb=None, datacache=None, l2cache=None):
   
    # Page table simulation for virt to physical page mappings on tlb miss
    # on hit - return phys page nume and update lru / miss sim page fault creating free physical page or remove lru if mem full
    # then update tlb/dc & l2 references to miss 
    #Maps virtual page numbers to physical page numbers
    
   
    numphyspages = config['ptphyspages']   #  find totaly phys pages

    
    statoutput['page_table_refs'] = statoutput.get('page_table_refs', 0) + 1  #check access
    
    #if hit
    if virtpage in pagetable:
        statoutput['pt_hits'] = statoutput.get('pt_hits', 0) + 1  #hit
        
        
        physpage = pagetable[virtpage]  #get phys page num
        del pagetable[virtpage]  # lru place page at end
        pagetable[virtpage] = physpage 
        
        return {'result': 'hit', 'physpage': physpage}


    # page fault, access disc to read in data  
    statoutput['pt_faults'] = statoutput.get('pt_faults', 0) + 1
    statoutput['disk_refs'] = statoutput.get('disk_refs', 0) + 1
    
    # add free pages 
    if len(pagetable) < numphyspages:
        # find the lowest physical page number that is not used yet
        allocatedpages = []
        for p in pagetable.values():
            allocatedpages.append(p)

        physpage = None
        for n in range(numphyspages):
            if n not in allocatedpages:
                physpage = n
                break

        # Create new virtual-to-physical mapping
        pagetable[virtpage] = physpage
        return {'result': 'miss', 'physpage': physpage}
    

    # if no free pages use lru

    lruvirtpage = list(pagetable.keys())[0]   # get first key
    evictedphyspage = pagetable[lruvirtpage] # swap
    del pagetable[lruvirtpage] # delete


    # calc address range for evicted physical pages###
    pagesize = config['ptpagesize']  # get page size in bytes /256 bytes

    evicpagestartaddr = evictedphyspage * pagesize  # find it in memory = evictedphyspage*pagesize
    evicpagendaddr = evicpagestartaddr + pagesize  # ending address of evicted page
    
    ## if tlb exists invalidate tlb entries pointing to evicted physical page
    if tlb is not None:  
        for tlbindx in list(tlb.keys()):  # loop through all tlb sets
            tlbset = tlb[tlbindx]           # get tlb set
            newset = []  # build new set with invalidated entries


            for tag, valid, pp in tlbset:  # remove tlb entries pointing to evicted physical page
                if pp == evictedphyspage:  # if entry points to evicted page
                    newset.append((tag, False, pp))  # remove
                else:
                    newset.append((tag, valid, pp))  # keep 
            tlb[tlbindx] = newset  # update tlb set
    
    
    # invalidate dc lines in evicted page address range
    if datacache is not None:  # if dc exists
        dcoffsetbits = config['dcacheoffset']  # get offset bits
        dcindexbits = config['dcacheindex']  # get index bits
        linebytes = 1 << dcoffsetbits  # calc bytes per line
        setsize = config['Dcachesetsize']  # get associativity

        
        for dc_idx in list(datacache.keys()):  # loop through all dc sets in direct mapped caches
            if setsize == 1: 
                tag, valid, dirty = datacache[dc_idx]  # get cache line
                if valid:                             
                    blocknumber = (tag << dcindexbits) + dc_idx  # reconstruct block number
                    addr = blocknumber * linebytes        # get phys starting address

                    if evicpagestartaddr <= addr < evicpagendaddr:  # if addr in evicted page range
                        datacache[dc_idx] = (tag, False, dirty)      # invalidate line

            
            else:        # Case for associative caches

                cacheset = datacache[dc_idx]  # get cache set
                newset = []  # build new set with invalidated entries

                for tag, valid, dirty in cacheset:    # invalidate lines mapping to evicted page address 
                    if valid:  
                        blocknumber = (tag << dcindexbits) + dc_idx  # reconstruct block number
                        addr = blocknumber * linebytes  # get physical starting address


                        if evicpagestartaddr <= addr < evicpagendaddr:  # if addr in evicted page range
                            newset.append((tag, False, dirty))  # invalidate line
                        else:
                            newset.append((tag, valid, dirty))  # dont change

                    else:
                        newset.append((tag, valid, dirty))  # dont change invalid entries
                datacache[dc_idx] = newset  # update cache set to main
    


    # invalidate l2 lines in evicted page address range
    if l2cache is not None:  # if l2 exists
        l2offsetbits = config['l2cacheoffset']  # get offset bits
        l2indexbits = config['l2cacheindex']  # get index bits
        linebytes = 1 << l2offsetbits  # calc bytes per line
        setsize = config['l2setsize']  # get associativity
        
        for l2_idx in list(l2cache.keys()):  # loop through all l2 sets
            
            
            if setsize == 1:  # direct mapped cache
                tag, valid, dirty = l2cache[l2_idx]  # get cache line
    
                if valid:  # if line is valid
                    blocknumber = (tag << l2indexbits) + l2_idx  # reconstruct block number
                    addr = blocknumber * linebytes  # calc address
    
                    if evicpagestartaddr <= addr < evicpagendaddr:  # if addr in evicted page range
                        l2cache[l2_idx] = (tag, False, dirty)  # invalidate line
           
            else:  # associative cache
                cacheset = l2cache[l2_idx]  # get cache set
                newset = []  # build new set with invalidated entries
    
                for tag, valid, dirty in cacheset:  # check each line in set
                    if valid:  # if line is valid
                        blocknumber = (tag << l2indexbits) + l2_idx  # reconstruct block number
                        addr = blocknumber * linebytes  # calc address
    
                        if evicpagestartaddr <= addr < evicpagendaddr:  # if addr in evicted page range
                            newset.append((tag, False, dirty))  # invalidate line
                        else:
                            newset.append((tag, valid, dirty))  # keep unchanged
    
                    else:
                        newset.append((tag, valid, dirty))  # dont change invalid entries
                l2cache[l2_idx] = newset  # update cache set
    
    # Assign the freed physical page to our new virtual page
    pagetable[virtpage] = evictedphyspage
    
    return {'result': 'miss', 'physpage': evictedphyspage}




def memorytrans(virtaddress, acctype, pagetable, datacache, l2cache, config, statoutput): ## implement page table (7)
      # Memory address translation function to handle virtual to physical address mapping
    #  For virtual address enabled but TLB is off
    
    pagesizebytes = config['ptpagesize']     # get each page's size
    
            # split virtual addr into vpn and offset
    virtpagenumber = virtaddress // pagesizebytes  # which virtual page
    pageoffset = virtaddress % pagesizebytes       # offset within that page
    
  
    ptresult = pagetablereq(virtpagenumber, pagetable, config, statoutput, tlb=None, datacache=datacache, l2cache=l2cache)  # find  phys page in page table/TLB is disabled 
    physpagenumber = ptresult['physpage']
    
    
    physaddress = (physpagenumber * pagesizebytes) + pageoffset  # get physical address using same phys page & offset
    
    dcresult = alldatacache(physaddress, acctype, datacache, config, statoutput, l2cache=l2cache, l2enabled=config['l2setting'].lower() == 'y')
    # check cache hierarchy w/ phys address

    
     # access L2 cache if DC miss
    l2result = None
    if dcresult['result'] == 'miss':
        l2result = l2datacache(physaddress, acctype, l2cache, config, statoutput)
        # allocate in DC to maintain inclusive policy
        alldatacache(physaddress, acctype, datacache, config, statoutput, l2cache=l2cache, l2enabled=config['l2setting'].lower() == 'y', allocate=True)


    # Return output
    return {
        'virtaddress': virtaddress,
        'virtpagenumber': virtpagenumber,
        'pageoffset': pageoffset,
        'ptresult': ptresult['result'],
        'physpagenumber': physpagenumber,
        'physaddress': physaddress,
        'dcresult': dcresult,
        'l2result': l2result
    }



def tlblookup(virtpage, tlb, config, statoutput):
    ## tlb with lru replacement 
    # search tlb to find virt to phys page translations & matches / hits
    # if hit then lru, else +miss 
    
    tlbsets = config['TLBsets']        # get tlb sets, assoc, index
    tlbsetsize = config['TLBsetsize']  
    tlbindexbits = config['tlbindex']  
    
    tlbindex = virtpage % (1 << tlbindexbits)  # calc tlb index 
    tlbtag = virtpage >> tlbindexbits          # calc tlb tag
    
    ## Count total TLB access
    statoutput['dtlb_refs'] = statoutput.get('dtlb_refs', 0) + 1
    
    if tlbindex not in tlb:     # init tlb set if needed
        tlb[tlbindex] = []
    
    tlbset = tlb[tlbindex]      # get the tlb set we're working with
    
    # check for hit in tlb set
    for i, (tag, validbit, physpage) in enumerate(tlbset):   
        if validbit and tag == tlbtag:      # if hit
            statoutput['dtlb_hits'] = statoutput.get('dtlb_hits', 0) + 1    # update stats
            
            # lru on hit - move to end = most recently used
            hitentry = tlbset.pop(i)        # remove from current position
            tlbset.append(hitentry)        # add to end
            return {'result': 'hit', 'physpage': physpage}
    
    # if miss
    statoutput['dtlb_misses'] = statoutput.get('dtlb_misses', 0) + 1
    return {'result': 'miss', 'tlbtag': tlbtag, 'tlbindex': tlbindex}




def tlbupdate(virtpage, physpage, tlb, config, statoutput):
    ## Update TLB with new virt to phys mapping after page table access /miss
    
    tlbsets = config['TLBsets']         # get config vars
    tlbsetsize = config['TLBsetsize']   
    tlbindexbits = config['tlbindex']   
    
    tlbindex = virtpage % (1 << tlbindexbits)   # calc index
    tlbtag = virtpage >> tlbindexbits           # calc tag
    
    if tlbindex not in tlb:     # init if needed
        tlb[tlbindex] = []
    
    tlbset = tlb[tlbindex]      # get tlb set
    
    # Add new entry with lru replacement
    if len(tlbset) < tlbsetsize:        # tlb set not full
        tlbset.append((tlbtag, True, physpage))     # add new entry
    else:       # tlb set full - evict lru
        tlbset.pop(0)       # remove lru (first entry)
        tlbset.append((tlbtag, True, physpage))     # add new entry at end




def tlbaccess(virtaddress, acctype, tlb, pagetable, datacache, l2cache, config, statoutput):
    ## Complete memory access with TLB for translation / access ptable / DC // L2
    # call tlblookup for translation, check miss if miss get pagetablereq update tlb
    ## reuses almost all step 7 code just added TLB layer
    
    pagesizebytes = config['ptpagesize']        # get page size
    
    # Break virtual address into page number and offset
    virtpagenumber = virtaddress // pagesizebytes       # get virt page num
    pageoffset = virtaddress % pagesizebytes            # get page offset
    
    # Try tlb first
    tlbresult = tlblookup(virtpagenumber, tlb, config, statoutput)
    
    if tlbresult['result'] == 'hit':        # tlb hit
        physpagenumber = tlbresult['physpage']      # use cached translation
        ptresult = 'hit'  # PT result is hit since TLB had it
    else:       # tlb miss - access page table
        ptresult_obj = pagetablereq(virtpagenumber, pagetable, config, statoutput, tlb=tlb, datacache=datacache, l2cache=l2cache)
        physpagenumber = ptresult_obj['physpage']
        ptresult = ptresult_obj['result']
        
        # Update TLB with page table result
        tlbupdate(virtpagenumber, physpagenumber, tlb, config, statoutput)
    
    # construct physical address and access caches
    physaddress = (physpagenumber * pagesizebytes) + pageoffset
    
    # Access cache hierarchy
    dcresult = alldatacache(physaddress, acctype, datacache, config, statoutput, l2cache=l2cache, l2enabled=config['l2setting'].lower() == 'y')
    
    l2result = None
    if dcresult['result'] == 'miss':        # if dc miss check l2
        l2result = l2datacache(physaddress, acctype, l2cache, config, statoutput)
        alldatacache(physaddress, acctype, datacache, config, statoutput, l2cache=l2cache, l2enabled=config['l2setting'].lower() == 'y', allocate=True)    

        
    # Return with TLB information added
    return {
        'virtaddress': virtaddress,
        'virtpagenumber': virtpagenumber,
        'pageoffset': pageoffset,
        'tlbresult': tlbresult['result'],
        'ptresult': ptresult,
        'physpagenumber': physpagenumber,
        'physaddress': physaddress,
        'dcresult': dcresult,
        'l2result': l2result
    }




if __name__ == "__main__":
    configfile = "trace.config"  
    configurationvariables = parse(configfile)
    configurationvariables = calcbits(configurationvariables)
    printvars(configurationvariables)
    
    memsimulation(configurationvariables) 

    # To run in cmd: python assignment1.py < "trace.dat"  replace with whatever trace file needed
    #python assignment1.py < "trace.dat"


#if __name__ == "__main__":
  #  configfile = "trace copy.config" 
 #   configurationvariables = parse(configfile)
 #   configurationvariables = calcbits(configurationvariables)
#    printvars(configurationvariables)
#
#    memsimulation(configurationvariables, "trace.dat") 
    
## To run, change the files for the config file / .dat file in any combination. 