# PRPROJ-READER
A simple python code to read what's inside a Premiere's project

29DEC21 - The code creates MasterClip, Sequence, and Bin elements stored in a list named projectMediaList. Sequence has a timeline attribute with all tracks and reffered clip disposition and content that could be linked with clips in projectMediaList and used to recreate the whole sequence.

21DEC21 - The code reads the prproj files and makes a Sequence Object containing all sequences and clips inside them with some metadata. The ratio to read prprojs timecodes' numbers still is not perfect. 
