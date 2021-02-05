import sys
import csv
import re
from collections import Counter
import datetime
import time

title_artist_cell = 2       # the zero-based index of the cell in the EVT file that holds the track title and artist name

###
# Log errors/status messages 
###
def log (message):
    print (message)


###
# Find the end character position of the LONGEST stretch of whitespace in this cell
###
def find_end_of_spaces (cell):

    # Find all the groups of whitespace in the cell
    spaces = re.finditer(r"[\s]+", cell.strip())

    # initialize info about our longest chunk of whitespace
    longest_so_far = {
        "max_length": 0,
        "current_end": len(cell) - 1
    }

    # Go through each section of whitespace we found
    for space in spaces:

        # If it's the longest whitespace we've found so far
        if len (space.group(0)) > longest_so_far["max_length"]:

            # this is the longest one so far - update the "longest" info
            longest_so_far["max_length"] = len (space.group(0))
            longest_so_far["current_end"] = space.span()[1]

    # return the end character position of the longest whitespace block we found
    return longest_so_far["current_end"]


###
# Main function - process an input EVT file and save it as properly-formatted CSV
###
def process_file (source_file):

    schedule_date = datetime.date.today()

    # output filename: the source name but a CSV extension
    dest_file = re.compile(r"\.[^\.]+$").sub(".csv",source_file)

    log (dest_file)

    # Open the source file to read as a CSV (with custom delimiter)
    with open(source_file, "r", encoding="latin-1", newline='') as source:
        reader = csv.reader(source, delimiter='|')

        ## Load the lines into a list
        evt = []
        for line in reader:
            evt.append(line)

        log (len(evt))

        ## Make a list of the cutoff points for separating track from artist (approximated by the end of the longest string of spaces - not precise but we'll use the most common cutoff in the next step to cover over individual anomalies)
        cutoffs = []
        for line in evt:
            cutoffs.append(find_end_of_spaces(line[title_artist_cell].strip()))

        ## Use the most common cutoff  (i.e., where most cells end their longest string of spaces)
        occurence_count = Counter(cutoffs)
        common_cutoff = occurence_count.most_common(1)[0][0]

        log ("Common cutoff: " + str(common_cutoff))

        ## Give each row a "next GVT Simple" time code so we know the limit for that section
        simple_cutoff_time = schedule_date
        for line in reversed(evt):

            log (line)

            # parse the title/author cell to find the "GTL Simple" time code
            simple_update = re.findall(r"^[\s]*(([\d]+[^\s\d\w]?){3})[\s]+GTL Simple", line[title_artist_cell])

            # If this is a "Simple update" row, update the cutoff time (which will be set for all previous rows since we're going through the rows in reverse)
            if len (simple_update) > 0:

                # get the timecode string
                time_string = simple_update[0][0]

                # turn it into a datetime.datetime.object
                cutoff_datetime = datetime.datetime.strptime(time_string,"%H:%M:%S")

                # convert to a datetime.time object  (as required for datetime.combine next)
                cutoff_time = datetime.time(cutoff_datetime.hour, cutoff_datetime.minute, cutoff_datetime.second)

                # combine the time cutoff into the existing cutoff time (which already has the date)
                simple_cutoff_time = datetime.datetime.combine(simple_cutoff_time, cutoff_time)

            # this line's cutoff time is whatever the most recent one we found (when going in reverse: i.e., the time for the NEXT "Simple Update" row, which we don't want to go past)
            line.append (simple_cutoff_time)


        ## Write out the info we want to the destination file
        with open(dest_file, "w+", encoding='utf-8', newline='') as destination:

            out = csv.writer(destination)

            # column headers
            out.writerow (["Song Title", "Artist", "Length", "Start Time", "End Time"])

            # initalize the start and end times (with time zeroed out)
            start_time = datetime.datetime.combine(schedule_date, datetime.time())
            end_time = start_time

            ## Assemble/write each line to the new CSV
            for line in evt:

                # temporary string of the full cell to work with while we split it up
                title_artist = line[title_artist_cell]

                # change the original cell to just the song title
                song_title = title_artist[0:common_cutoff].strip()
                line[title_artist_cell] = song_title

                # insert another cell right after it for the artist name
                artist_name = title_artist[common_cutoff:len(title_artist)].strip()
                line.insert (title_artist_cell+1, artist_name)

                # set the start time of THIS row to the end time of the PREVIOUS row
                start_time = end_time

                ## Should we skip this row? (we should if we're past the cutoff time of the next "Simple Update")
                cutoff_time = line[len(line) - 1]       # the cutoff time should be in the last cell of the line, since we appended it earlier when finding "Simple Update" times
                if start_time > cutoff_time and not song_title.lower().strip().endswith("gtl simple"):
                    continue


                # calculate the end time for this row by ADDING the length of the track
                track_time = datetime.datetime.strptime(line[title_artist_cell+2],"%H:%M:%S")
                delta = datetime.timedelta (hours=track_time.hour, minutes=track_time.minute, seconds=track_time.second)
                end_time = start_time + delta



                # format the start/end times for insertion into the CSV
                start_time_str = start_time.strftime("%m/%d/%Y %H:%M:%S")
                end_time_str = end_time.strftime("%m/%d/%Y %H:%M:%S")


                # write the row
                out.writerow(line[title_artist_cell:title_artist_cell+3] + [start_time_str, end_time_str])
