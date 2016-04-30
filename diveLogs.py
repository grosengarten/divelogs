from datetime import datetime, timedelta

filename='source_dive_84.ATOM 3.0.8148.zxu'


def convert_elapsed_times(increment):
    """
    converts elapsed times to correct format
    i.e.  "4.5" minutes.  WTF is that??!
    """
    #dateObj, increment
    delta = increment.split('.')
    min=delta[0]
    sec='{0:g}'.format(int(delta[1]) / 100 * 60) # e.g. convert .50 minutes to seconds, then strip off the trailing zero created by casting to an integer < 0. YUCK!
    elapsedTime = min + ':' + sec
    #absoluteTime = dateObj + timedelta(minutes=int(min), seconds=int(sec))
    #print(min, sec, absoluteTime)
    return elapsedTime


def get_section_header(filename, start):
    with open(filename, 'r') as file:
        for line in file:
            if not line.startswith(start):
                continue
            else:
                line=line.strip()
                data=line.split('|')
    return data


def load_sections(filename, start, end):
    data=[]
    with open(filename, 'r') as file:
        copy = False
        for line in file:
            if line.strip() == start:
                copy = True
            elif line.strip() == end:
                copy = False
            elif copy:
                line = line.strip()
                data.append(line.split('|'))
    return data


def create_profile():
    """
    ZDH|84|1|I|Q30S|20151011094900|58|120.0|PO2|
    |2.00|89||1.11||||||3275|
    Elapsed Dive Time (hr:min),Depth(FT),Nitrogen Bar Graph,Oxygen Bar Graph,Ascent Rate(FPM),Air Time Remaining,Dive Time Remaining,Deco Time (hr:min),Stop Depth(FT),Temperature(FT),PO2,Tank,Pressure Reading(PSI),Link Status,Dive Status
    00:00:00,9,0,0,(0-10),01:31,09:59,00:00,0,58,0.38,1,3455,Linked,,0.0
    "66","2016-04-23","13:45:00","0:30","1.962","11.111",
    """
    header="dive number","date","time","sample time","sample depth","sample temperature","sample pressure"
    source_header=get_section_header(filename, 'ZDH')
    #print(source_header[5])
    d = datetime.strptime(source_header[5], '%Y%m%d%H%M%S')
    date=d.strftime("%Y-%m-%d")
    #print(source_header)
    list=load_sections(filename, 'ZDP{', 'ZDP}')
    #print(header)
    for i in list:
        global temp = i[7]

        print(i[1])
        #delta = datetime.strptime(list[0], '%H:%M:%S')
        #adjTime = d + timedelta(delta)
        line=[]
        line.append(source_header[1])
        line.append(date)
        #line.append(adjTime)
        line.append(d.strftime('%H:%M:%S'))
        line.append(convert_elapsed_times(i[1]))
        try:
            line.append(i[7])
        except IndexError:
            line.append(source_header[6])
        print(line)


def main():
    create_profile()
    #convert_relative_times()

main()