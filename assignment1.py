import math

# read in configuration file, 

def read_config(filename="trace.config"):
    ## read in config
   
    
    try:
        print(f"check file: {filename}")

        with open(filename, 'r') as cofigdata:
            lines = []  # init list
            for line in cofigdata:
                #print(f" line {(line)}")
                stripline = line.strip()        # remove newlines and white spaces
                #print(f" line {(stripline)}")
                if stripline:                   # check if line is clean then add
                    lines.append(stripline)     
                    #print(f" line {(stripline)}")
                  
        configurationvariables = {}     # create dict will use later

        i = 0
        while i < len(lines):
            line = lines[i]

            if "Data TLB configuration" in line:  # ensure in correct line then set dict var to be the value outside the : 
                configurationvariables['TLBsets'] = int(lines[i+1].split(':')[1].strip())  #DTLB sets  # looks at line below
                configurationvariables['TLBsetsize'] = int(lines[i+2].split(':')[1].strip())  #num sets  # looks at 2 lines below
                i += 3  # go to next section

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

        return configurationvariables

    except Exception as error:
        print(f"Error reading config file: {error}")
        return None
    




def logfunct(n):  ## take log2 of each value 
    
    if n <= 0:
        return 0
    return int(math.log2(n))

def calcbits(configurationvariables):
    #use to calc index and offset bitsd

    # Take log2 of TLB (DTLB)
    configurationvariables['tlbindex'] = logfunct(configurationvariables['TLBsets'])

    # Do Ptable
    configurationvariables['ptablebits'] = logfunct(configurationvariables['ptvirtpages'])
    configurationvariables['poffsetbits'] = logfunct(configurationvariables['ptpagesize'])

    # Data cache
    configurationvariables['dcacheindex'] = logfunct(configurationvariables['Dcachesets'])
    configurationvariables['dcacheoffset'] = logfunct(configurationvariables['Dcachelinesize'])

    # L2 
    configurationvariables['l2cacheindex'] = logfunct(configurationvariables['l2sets'])
    configurationvariables['l2cacheoffset'] = logfunct(configurationvariables['l2linesize'])

    return configurationvariables







def printvars(configurationvariables):


    print(f"Data TLB contains {configurationvariables['TLBsets']} sets.")
    print(f"Each set contains {configurationvariables['TLBsetsize']} entries.")
    print(f"Number of bits used for the index is {configurationvariables['tlbindex']}.")
    
    print(f"Number of virtual pages is {configurationvariables['ptvirtpages']}.")
    print(f"Number of physical pages is {configurationvariables['ptphyspages']}.")
    print(f"Each page contains {configurationvariables['ptpagesize']} bytes.")
    print(f"Number of bits used for the page table index is {configurationvariables['ptablebits']}.")
    print(f"Number of bits used for the page offset is {configurationvariables['poffsetbits']}.")
    
    print(f"D-cache contains {configurationvariables['Dcachesets']} sets.")
    print(f"Each set contains {configurationvariables['Dcachesetsize']} entries.")
    print(f"Each line is {configurationvariables['Dcachelinesize']} bytes.")
    
    if configurationvariables['Dwritepolicy'].lower() == 'n':
        print("The cache uses a write-allocate and write-back policy.")
    else:
        print("The cache uses a write-through and no write-allocate policy.")
    
    print(f"Number of bits used for the index is {configurationvariables['dcacheindex']}.")
    print(f"Number of bits used for the offset is {configurationvariables['dcacheoffset']}.")
    
    print(f"L2-cache contains {configurationvariables['l2sets']} sets.")
    print(f"Each set contains {configurationvariables['l2setsize']} entries.")
    print(f"Each line is {configurationvariables['l2linesize']} bytes.")
    
    # L2 
    if configurationvariables['l2writepolicy'].lower() == 'n':
        print("The cache uses a write-allocate and write-back policy.")
    else:
        print("The cache uses a write-through and no write-allocate policy.")
    


    print(f"Number of bits used for the index is {configurationvariables['l2cacheindex']}.")
    print(f"Number of bits used for the offset is {configurationvariables['l2cacheoffset']}.")
    
    if configurationvariables['virtaddress'].lower() == 'y':
        print("The addresses read in are virtual addresses.")
    else:
        print("The addresses read in are physical addresses.")




#### step 2
def step2(config, trace_filename="trace.dat"):



    print("Virtual  Virt. Page TLB  TLB  TLB  PT   Phys DC   DC   L2   L2")
    print("Address  Page # Off  Tag  Ind  Res. Res. Pg # DC Tag Ind  Res. L2 Tag Ind  Res.")
    print("-------- ------ ---- ------ --- ---- ---- ---- ------ --- ---- ------ --- ----")

    #declaring new vars to avoid diction modifying
    pageoffsetbits = config['poffsetbits']   # still ints
    dcindexbits = config['dcacheindex'] 
    dcoffsetbits = config['dcacheoffset']



    # compute  sizes in powers of two
    pagebytes  = 1 << pageoffsetbits   # bytes per page
    linebytes  = 1 << dcoffsetbits     # bytes per DC line
    numsets    = 1 << dcindexbits      # number of DC sets (not bytes)





    with open(trace_filename, 'r') as tf:  #get trace.dat
        for line in tf:  #grab each trace
            line = line.strip()
            if not line:
                continue
            
            try:
                _, hexaddr = line.split(':')  # split up r/w and hex address
                address = int(hexaddr, 16)  # cnvert to int

                pageoffset = address % pagebytes  #get page offset
                physpagenumber = address // pagebytes # get page number

                blocknumber = address // linebytes  # get block num
                dc_index = blocknumber % numsets # calc data cache index
                dc_tag = blocknumber // numsets # cacl data cache tag


     
                print(f"{address:08x} {physpagenumber:6x} {pageoffset:4x} {'':>6} {'':>3} {'':>4} {'':>4} {physpagenumber:4x} {dc_tag:6x} {dc_index:3x} {'':>4} {'':>6} {'':>3} {'':>4}")
            except Exception as e:
                print(f"Error processing line '{line}': {e}")





if __name__ == "__main__":
    # just change the file name 
    configfile = "trace.config"
    configurationvariables = read_config(configfile)
    configurationvariables = calcbits(configurationvariables)
    printvars(configurationvariables)

    step2(configurationvariables, "trace.dat")  # step2 