# PRPROJ-READER (ADOBE PREMIERE's OPEN SOURCE API)
A simple python code that reads what's inside a Premiere's project.


Hi, my name is Sergio and I’m a film editor. 
I’m not a programmer, but, as a challenge, I wanted to figure out
how Premiere Projects work.

Premiere Project files are essentially a GZip file containing a text file with an XML code within. 

That XML code contains many objects (Most of them described here https://ppro-scripting.docsforadobe.dev/_/downloads/en/latest/pdf) 
that are bond between ObjectID and REF attribute’s values.
I just followed the leads one object gave to find its relationship with another, and figured out a «map», retrieving attributes 
I considered relevant for clips, sequences, folders, as: names, framerates, frame sizes, in points, out points, etc.

I started to dig into Python and worked on a 800 hundred line’s code that sort of reverse-engineers this structure and extracts this basic information. From this I could make basic operations like: creating srt files from text clips, returning the original names to merged clips, changing multiple parameters of a project file at once like scale and position, etc. My code surely is full of basic programming errors. Sorry, it’s not my professional area. 

This excursion to deep understanding of Project files has the spirit of Play. It made me wonder basic questions about Premiere’s functioning. 

My ultimate interest is to learn about coding and NLE inner work. I invite you to dig in into this world and join me if you are interested.
