# PRPROJ-READER
A simple python code to read what's inside a Premiere's project.


Hi, my name is Sergio and I’m a film editor. 
I’m not a programmer, but, as a challenge, I wanted to figure out
how Premiere Projects work.

Editors face lot of problems when using softwares as Premiere, and are
constantly finding solutions for them. I think programming is a tool that
can help achieve solutions in a more efficient way.

What I found out is that Premiere Project files are essentially a GZip file containing
a text file with an XML code within. 

That XML code contains many objects —tags— that are bond between ObjectID and REF attribute’s values.
I just followed the leads one object gave, to another, and figured out this «map», retrieving attributes 
I considered relevant for clips, sequences, folders, as: names, framerates, frame sizes, in points, out points, etc.

I started to dig into Python and worked on a 500 hundred line’s code that sort of decodes this structure and extracts this basic information. From this I could make basic operations like: creating srt files from text clips, returning the original names to merged clips, changing multiple parameters of a project file at once like scale and position, etc. My code surely is full of basic programming errors. Sorry, it’s not my professional area. 

This excursion to deep understanding of Project files has the spirit of Play. It made me wonder basic questions about Premiere’s functioning, like need of its complexity —this intermediate objects I couldn’t still figure out why they exist, or why some variables are coded in intermediate equations. 

My ultimate interest is to learn about coding and NLE inner work. I invite you to dig in into this world and join me if you are interested.

28NOV22 - Updated File Structure

29DEC21 - The code creates MasterClip, Sequence, and Bin elements stored in a list named projectMediaList. Sequence has a timeline attribute with all tracks and reffered clip disposition and content that could be linked with clips in projectMediaList and used to recreate the whole sequence.

21DEC21 - The code reads the prproj files and makes a Sequence Object containing all sequences and clips inside them with some metadata. The ratio to read prprojs timecodes' numbers still is not perfect. 
