from datetime import datetime, timedelta
from re import sub
import xml.etree.ElementTree as ET
from sys import argv


filename=argv[1]

def convert_elapsed_times(increment):
    """
    converts elapsed times to correct format
    i.e.  "4.5" minutes.  WTF is that??!
    """
    delta = increment.split('.')
    min=delta[0]
    sec='{0:g}'.format(int(delta[1]) / 100 * 60) # e.g. convert .50 minutes to seconds, then strip off the trailing zero created by casting to an integer < 0. YUCK!
    elapsedTime = min + ':' + sec
    return elapsedTime


def get_section_header(filename, start):
    """
    get header data associated with each section ZDH{ZDH} and ZDP{ZDP}
    """
    with open(filename, 'r') as file:
        for line in file:
            if not line.startswith(start):
                continue
            else:
                line=line.strip()
                data=line.split('|')
    return data

def get_details():
    """
    get details that will be used for matching (according to the developer this doesn't work yet
    """
    pass

def load_sections(filename, start, end, _split=True):
    """
    find the second of the file starting with (TAG){ and ending with (TAG)}
    """
    data=[]
    with open(filename, 'r') as file:
        select = False
        for line in file:
            if line.strip() == start:
                select = True
            elif line.strip() == end:
                select = False
            elif select:
                line = line.strip()
                if _split:
                    data.append(line.split('|'))
                else:
                    data.append(line)
    return data


def create_profile():
    """
    Create the lines that will go into the dive_profile csv
    """
    global temp # temp is written to the source file only when it changes.
    header = "dive number","date","time", "max depth","duration","sample time","sample depth","sample temperature","sample pressure"
    xml = load_sections(filename, 'ZAR{', '}', _split=False)
    E = ET.fromstring('\n'.join(xml))
    stats = dict(l.split("=") for l in E.find('DIVESTATS').text.split(","))
    max_depth = stats['MAXDEPTH']
    duration = '{0:g}'.format(int(stats['EDT'])/100)
    source_header = get_section_header(filename, 'ZDH')
    dive_number = source_header[1]
    d = datetime.strptime(source_header[5], '%Y%m%d%H%M%S')
    date = d.strftime("%d.%m.%Y")
    list = load_sections(filename, 'ZDP{', 'ZDP}')
    outputFile = 'dive_{0}_profile_{1}.csv'.format(source_header[1], date)
    with open(outputFile, 'w') as f:
        f.write(', '.join(header) + '\n')
        for i in list:
            line=[]
            """ dive number """
            line.append(dive_number)
            """ date """
            line.append(date)
            """ time """
            line.append(d.strftime('%H:%M:%S'))
            """ max depth """
            line.append(max_depth)
            """ duration """
            line.append(duration)
            """ sample time """
            line.append(convert_elapsed_times(i[1]))
            """ sample depth """
            line.append(i[2])
            """ temp """
            try:
                if i[8] != "":
                    temp = i[8]
            except IndexError:
                temp = source_header[6]
            finally:
                line.append(temp)
            """ sample pressure """
            try:
                line.append(i[10])
                #line.append(str(float(i[10])/14.7))
            except IndexError:
                line.append("")
            f.write(', '.join(line) + '\n')
    return line

def create_details():
    """
    parse xml portions found in between the ZAR{ } tag
    :return:
    """
    line = []
    #header = "dive number", "date", "time", "location", "air temp", "Start Pressure", "End Pressure", "O2", "CYL. Size"
    header = "dive number", "date", "time", "max depth","duration","location", "air temp", "O2", "CYL. Size", "Weight", "Suit"
    source_header = get_section_header(filename, 'ZDH')
    dive_number = source_header[1]
    d = datetime.strptime(source_header[5], '%Y%m%d%H%M%S')
    date = d.strftime("%Y-%m-%d")
    time = d.strftime('%H:%M:%S')
    xml = load_sections(filename, 'ZAR{', '}', _split=False)
    E = ET.fromstring('\n'.join(xml))
    stats = dict(l.split("=") for l in E.find('DIVESTATS').text.split(","))
    max_depth = stats['MAXDEPTH']
    duration = '{0:g}'.format(int(stats['EDT']) / 100)
    outputFile = 'dive_{0}_details_{1}.csv'.format(source_header[1], date)
    with open(outputFile, 'w') as f:
        """ dive number """
        line.append(dive_number)
        """ date and time """
        d = datetime.strptime(source_header[5], '%Y%m%d%H%M%S')
        line.append(date)
        line.append(time)
        E = ET.fromstring('\n'.join(xml))
        """ max depth """
        line.append(max_depth)
        """ duration """
        line.append(duration)
        """ location """
        try:
            loc = dict(l.split("=") for l in E.find('LOCATION').text.split(","))
            try:
                line.append(loc['LOCNAME'].replace('[','').replace(']','') + '- '+ loc['DIVESITE'].replace('[','').replace(']',''))
            except KeyError:
                line.append("")
        except ValueError:
            print(E.find('LOCATION').text.split(','))
            line.append("")
        try:
            line.append(loc['AIRTEMP'])
        except KeyError:
            line.append("")
        """ tank """
        tank = dict(l.split("=") for l in E.find('TANK').text.split(","))
        #line.append(float(tank['STARTPRESSURE']/14.7))
        #line.append(float(tank['ENDPRESSURE']/14.7))
        line.append(tank['FO2'])
        line.append(tank['CYLSIZE'])
        """ gear """
        gear = dict(l.split("=") for l in E.find('GEAR').text.split(","))
        try:
            line.append(gear['INTERGRATEDWEIGHT'])
        except Exception:
            line.append('0')
        try:
            line.append(gear['SUIT'].replace('[','').replace(']',''))
        except Exception:
            line.append('')
        f.write(', '.join(header) + "\n")
        f.write(', '.join(line) + "\n")
    return line

def main():
    create_profile()
    create_details()

main()