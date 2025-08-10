from __future__ import print_function
import re
import pdfplumber
import time
import matplotlib.pyplot as plt
import numpy as np
import sys
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

if __name__ == '__main__':
    filename = sys.argv[1];
    with pdfplumber.open(filename) as pdf:   #open the schedule pdf and extract its text
        page = pdf.pages[0]
        text = page.extract_text()

    tet = text.split("\n")
    prog = re.compile(r'[A-Z]{2,5} [0-9]{3}')      #parameters for the course title
    dayprog = re.compile(r'\bSUN|MON|TUE|WED|THU')  #parameters for the days
    cls = prog.findall(text)

    courses = [["", "","",""],["", "","",""],["", "","",""],["", "","",""],["", "","",""],["", "","",""]];    #empty matrix for keeping the information gathered(title and day)

    i = -1;
    x= 0;

    for line in tet:    #reads the text line by line
        if prog.findall(line):
            coursename = prog.findall(line); #takes the title first at the begingning of every array
            x=0;
            i= i+1;
            courses[i][0] = coursename
            
        if dayprog.findall(line):   #takes the day and puts it after the title so that they stay relative
            x= x+1;
            courses[i][x] = (dayprog.findall(line))
            
    hour = [];
    prog = re.compile(r'[0-9]{1,2}[:][0-9]{2}[a-z]{2}.')     #extracts the hours when the class starts and ends (in the correct order)
    for line in text.split():
        if prog.match(line):
            hour.append(line);

    loc = []; 
    locprog = re.compile(r'\b[A-B]-')
    for line in text.split():
        if locprog.match(line):
            loc.append(line);

    b=hour;
    entry =[re.split("-", entry, maxsplit=9) for entry in b]  #removes the dash from the hours and seprates them

    shourz = [];
    ehourz = [];

    sount =0;
    newhour = [];
    start= [];
    end= [];
    count = 0;

    for string in entry:   
        for lime in string:
            def convert(time_string):
                date_var = time.strptime(time_string, '%I:%M%p')      #turns the hours to 24 hours and splits the minutes

                return date_var

            my_time = convert(lime)
            
            
            if my_time.tm_min == 15:                      #changes the minutes to deciml points for the graph
                newhour.append(my_time.tm_hour + .25);
                
            if my_time.tm_min == 30:
                newhour.append(my_time.tm_hour + .5);
                
            if my_time.tm_min == 45:
                newhour.append(my_time.tm_hour + .75);
                
            if my_time.tm_min == 0:
                newhour.append(my_time.tm_hour); 
                
            
            if sount == 0:                              #puts the odd in start and the even to the end
                start.append(newhour[count]); 
                shourz.append(str(my_time.tm_hour)+":"+str(my_time.tm_min))
                sount = 1; 
            else:
                end.append(newhour[count]); 
                ehourz.append(str(my_time.tm_hour)+":"+str(my_time.tm_min))
                sount = 0; 
            
            
            count+=1;

    last = []; 
    for i, j in zip(end,start):
    
        last.append(i - j)                          #finds out how long each class lasts for


    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def CreateGoogleEvent(i, x, date):
                creds = None
                if os.path.exists('token.json'):
                    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'credintials.json', SCOPES)
                        creds = flow.run_local_server(port=0)
                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())

                try:
                    service = build('calendar', 'v3', credentials=creds)
                    event = {
                        'summary': cls[i],
                        'location': loc[x],
                        'start': {
                            'dateTime': date+'T'+shourz[x]+':00',
                            'timeZone': 'Etc/GMT-3',
                        },
                        'end': {
                            'dateTime': date+'T'+ehourz[x]+':00',
                            'timeZone': 'Etc/GMT-3',
                        },
                        'recurrence': [
                            'RRULE:FREQ=WEEKLY;COUNT=16'
                        ],
                        'reminders': {
                            'useDefault': False,
                            'overrides': [
                            {'method': 'popup', 'minutes': 15},
                            ],
                        },
                        }

                    event = service.events().insert(calendarId='primary', body=event).execute()
                    print('Event created: %s' % (event.get('htmlLink')))

                except HttpError as error:
                    print('An error occurred: %s' % error)


    fig, gnt = plt.subplots()

    # Setting X-axis limits
    gnt.set_xlim(-0.1, 5.1)
    gnt.set_ylim(8, 20)

    # Setting labels for x-axis and y-axis 
    #gnt.set_xlabel('SUN                              MON                              TUE                          WED                             THU')
    gnt.set_ylabel('time')

    ax = plt.gca()
    ax.invert_yaxis()

    # Setting ticks on y-axis
    gnt.set_yticks([9, 10,11, 12, 13, 14, 15, 16, 17, 18, 19, 20])

    # Labelling tickes of y-axis
    gnt.set_yticklabels(['9:00am', '10:00am', '11:00am','12:00pm','1:00pm','2:00pm','3:00pm','4:00pm','5:00pm','6:00pm','7:00pm', '8:00pm'])

    gnt.set_xticks([0.5, 1.5, 2.5, 3.5, 4.5])
    gnt.set_xticklabels(['SUN', 'MON', 'TUE', 'WED', 'THU'])  #labels the x-axis with the days of the week

    # Setting graph attribute and colours 
    gnt.grid(True)
    gnt.grid(True, axis='y')  # Only show horizontal grid lines
    gnt.grid(False, axis='x')  # Hide vertical grid lines to avoid confusion with tick marks
    colour= ['#4CA7E3', '#DAF7A6', '#FFC300', '#FF5733', '#D74A4A', 'tab:Green']

    # Function to estimate text width and adjust bar width
    def get_text_width(text, fontsize=10):
        return max(0.8, len(str(text)) * 0.08)

    # Declaring a bar in schedule
    i=0;
    x=0;
    date = "";
    bar_padding = 0.05  # Small padding around bars
    while(i<6 and i < len(courses) and i < len(cls)):         #inputs the courses as broken bars 
        col = colour[i];
        for day in courses[i]:
            # Calculate bar width based on text content
            course_text = str(cls[i]) if i < len(cls) and cls[i] else ""
            time_text = str(hour[x]) if x < len(hour) else ""
            text_width = max(get_text_width(course_text), get_text_width(time_text))
            
            # Ensure bar width doesn't exceed day column (0.9 max width)
            bar_width = min(text_width, 0.9)
            
            if day == ["SUN"]:              # checks days to graphs them
                bar_start = 0.5 - bar_width/2
                gnt.broken_barh([(bar_start, bar_width)], (start[x], last[x]), facecolors =col)
                plt.text(0.5, start[x] + last[x]/2, course_text, ha="center", va="center", fontsize=8, weight='bold')      #course title
                plt.text(0.5, start[x] + last[x]*0.8, time_text, ha="center", va="center", fontsize=7)    #course timing
                date = "2023-09-03";
                #CreateGoogleEvent(i,x, date)
                x=x+1;
            elif day == ["MON"]:
                bar_start = 1.5 - bar_width/2
                gnt.broken_barh([(bar_start, bar_width)], (start[x], last[x]), facecolors =col)
                plt.text(1.5, start[x] + last[x]/2, course_text, ha="center", va="center", fontsize=8, weight='bold')
                plt.text(1.5, start[x] + last[x]*0.8, time_text, ha="center", va="center", fontsize=7)
                date = "2023-09-04";
                #CreateGoogleEvent(i,x, date)
                x=x+1;
            elif day == ["TUE"]:
                bar_start = 2.5 - bar_width/2
                gnt.broken_barh([(bar_start, bar_width)], (start[x], last[x]), facecolors =col)
                plt.text(2.5, start[x] + last[x]/2, course_text, ha="center", va="center", fontsize=8, weight='bold')
                plt.text(2.5, start[x] + last[x]*0.8, time_text, ha="center", va="center", fontsize=7)
                date = "2023-09-05";
                #CreateGoogleEvent(i,x, date)
                x=x+1;
            elif day == ["WED"]:
                bar_start = 3.5 - bar_width/2
                gnt.broken_barh([(bar_start, bar_width)], (start[x], last[x]), facecolors =col)
                plt.text(3.5, start[x] + last[x]/2, course_text, ha="center", va="center", fontsize=8, weight='bold')
                plt.text(3.5, start[x] + last[x]*0.8, time_text, ha="center", va="center", fontsize=7)
                date = "2023-09-06";
                #CreateGoogleEvent(i,x,date)
                x=x+1;
            elif day == ["THU"]:
                bar_start = 4.5 - bar_width/2
                gnt.broken_barh([(bar_start, bar_width)], (start[x], last[x]), facecolors =col)
                plt.text(4.5, start[x] + last[x]/2, course_text, ha="center", va="center", fontsize=8, weight='bold')
                plt.text(4.5, start[x] + last[x]*0.8, time_text, ha="center", va="center", fontsize=7)
                date = "2023-09-07";
                #CreateGoogleEvent(i,x,date)
                x=x+1;
        i=i+1;

    
    gnt.set_axisbelow(True)
    plt.rcParams["figure.figsize"] = (10,7)  #resizes the graph
    plt.savefig("schdule.png")
