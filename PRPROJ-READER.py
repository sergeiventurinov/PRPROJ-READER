# -*- coding: UTF-8 -*-

import gzip, shutil, os
import xml.etree.ElementTree as ET


class Sequence:
  def __init__(self):
    self.id = id
    self.name = ''
    self.height = ''
    self.width = ''
    self.vidframerate = 0
    self.audframerate = 0
    self.timelime = [] #TrackID, file path, clip name, tape, timeline In, timeline Out, media IN, media OUT, media Frame Rate
    self.inBin = 0

class MasterClip:
  def __init__(self):
    self.id = '' # Id linking Bins and its instances in Sequences
    self.type = '' #Audio, Video, Other
    self.name = ''
    self.filePath = ''
    self.tapeName = ''
    self.frameRate = 0
    self.mediaStart = 0 #Media's start timecode
    self.mediaEnd = 0
    self.inBin = 0

class Bin:
  def __init__(self, name, selfid):
    self.id = selfid
    self.name = name
    self.contains = []
    self.inBin = None

  def ingest(self, clipid):
    self.contains.append(clipid)

  def contains (self, clipid):
    if clipid in self.contains:
      return True
    else:
      return False

def OpenProj(filename):

  fileInside = filename.replace('.prproj', '')  # el archivo dentro del prproj se llama igual y no tiene extensión
  with gzip.open(filename, 'rb') as f_in, open(fileInside, 'wb') as f_out:
    shutil.copyfileobj(f_in, f_out)
    f_out.close()
    f_in.close()
    xml_file_handle = open(fileInside, 'rb')
    xml_as_string = xml_file_handle.read()
    xml_file_handle.close()
    #os.remove(fileInside) #Interine File
  return xml_as_string

def SaveProj(xml, outFile):
  fileInside = outFile.replace('.prproj', '')
  f = open(fileInside, "a") #creamos archivo temporal
  f.write(xml)
  f.close()

  with open(fileInside, 'r') as f_in: #r o rb?
    with gzip.open(outFile, 'w') as f_out: #w o wb?
      shutil.copyfileobj(f_in, f_out)
      f_out.close()
      f_in.close()
  os.remove(fileInside)

def openSequence(xml, id): #FALTA HACER ESTO VINCULADO A GETMEDIALIST IDs

  openId = id
  root = ET.fromstring(xml)
  n = 0

  for sequences in root.findall('./Sequence'):
    #print (len(seq), n)
    id =  sequences.get('ObjectUID')
    if openId == id:
      # First Check Video Tracks
      for trackGroupIDs in sequences.findall('TrackGroups/TrackGroup/Second/.[@ObjectRef]'):
        ObjectRef = trackGroupIDs.get('ObjectRef') #Referencia al ID de VideoTrackGroups

        for videoTrackGroup in root.findall('.//VideoTrackGroup'):
          if ObjectRef == videoTrackGroup.get('ObjectID'):
            for tracksID in videoTrackGroup.findall('TrackGroup/Tracks/Track'):
              trackID = tracksID.get('ObjectURef')

              #Link between TrackGroups & ClipTrackItems via ClipTrack
              for videoClipTracks in root.findall('.//VideoClipTrack'):
                videoClipTrackID = videoClipTracks.get('ObjectUID')
                if videoClipTrackID == trackID:
                  videoClipTrackID = videoClipTracks.find('ClipTrack/Track/ID').text
                  for trackItems in videoClipTracks.findall('ClipTrack/ClipItems/TrackItems/TrackItem'):
                    trackItem = trackItems.get('ObjectRef')

                    #Retrieving more information from each VideoClipTrackItem
                    for videoClipTrackItems in root.findall('.//VideoClipTrackItem'):
                      videoClipTrackItem = videoClipTrackItems.get ('ObjectID')
                      if videoClipTrackItem == trackItem:
                        start = int(videoClipTrackItems.find('ClipTrackItem/TrackItem/Start').text)
                        start = start / 8441789933
                        #print ('Clip Start position in Timeline: ', start)
                        end = int(videoClipTrackItems.find('ClipTrackItem/TrackItem/End').text)
                        end = (end / 8441789933)-1
                        #print ('Clip End position in Timeline: ', end)

                        #Now Retrieving more information from each SubClip Linked
                        subClipRef = videoClipTrackItems.find('ClipTrackItem/SubClip').get('ObjectRef') #SubClip's Ref links with SubCLips
                        for subclips in root.findall('.//SubClip'):
                          subclip = subclips.get('ObjectID')
                          if subclip == subClipRef:
                            if subclips.find('MasterClip') != None:
                              masterClipRef = subclips.find('MasterClip').get('ObjectURef') #This must be linked with clips' ID
                            else:
                              masterClipRef= None

                            #Retrieving Relative Amount of frames available since start of MasterClip
                            clipRef = subclips.find('Clip').get('ObjectRef')
                            for videoclips in root.findall('.//VideoClip'):
                              videoclip = videoclips.get('ObjectID')
                              if videoclip == clipRef:
                                clipTimecodeIn = int(videoclips.find('Clip/InPoint').text)
                                clipTimecodeOut = int(videoclips.find('Clip/OutPoint').text)

                    # Add Info to the sequences' clip list.
                    #Buscar secuencia y agregar lista de clips ahora.
                    for sequence in projectMediaList:
                        if sequence.id == openId:
                          sequence.timeline.append((('VTRK' + videoClipTrackID), masterClipRef, start, end, clipTimecodeIn, clipTimecodeOut))

      #Now Check Audio Tracks
      for trackGroupIDs in sequences.findall('TrackGroups/TrackGroup/Second/.[@ObjectRef]'):
        ObjectRef = trackGroupIDs.get('ObjectRef')  # Referencia al ID de VideoTrackGroups

        for audioClipTrackID in root.findall('.//AudioTrackGroup'):
          if ObjectRef == audioClipTrackID.get('ObjectID'):

            for trackID in audioClipTrackID.findall('TrackGroup/Tracks/Track'):
              trackID = trackID.get('ObjectURef')

              #Link between TrackGroups & ClipTrackItems via ClipTrack
              for audioClipTracks in root.findall('.//AudioClipTrack'):
                audioClipTrack = audioClipTracks.get('ObjectUID')
                if audioClipTrack == trackID:
                  audioClipTrackID = audioClipTracks.find('ClipTrack/Track/ID').text
                  for trackItems in audioClipTracks.findall('ClipTrack/ClipItems/TrackItems/TrackItem'):
                    trackItem = trackItems.get('ObjectRef')
                    #print ('Audio Clip inside Track') #:', trackItem)

                    #Retrieving more information from each AudioClipTrackItem
                    for audioClipTrackItems in root.findall('.//AudioClipTrackItem'):
                      audioClipTrackItem = audioClipTrackItems.get ('ObjectID')
                      if audioClipTrackItem == trackItem:
                        start = int(audioClipTrackItems.find('ClipTrackItem/TrackItem/Start').text)
                        start = start / 8441789933
                        #print ('Clip Start position in Timeline: ', start)
                        end = int(audioClipTrackItems.find('ClipTrackItem/TrackItem/End').text)
                        end = (end / 8441789933)-1
                        #print ('Clip End position in Timeline: ', end)

                        #Now Retrieving more information from each SubClip Linked
                        subClipRef = audioClipTrackItems.find('ClipTrackItem/SubClip').get('ObjectRef') #SubClip's Ref links with SubCLips
                        for subclips in root.findall('.//SubClip'):
                          subclip = subclips.get('ObjectID')
                          if subclip == subClipRef:
                            if subclips.find('MasterClip') != None:
                              masterClipRef = subclips.find('MasterClip').get('ObjectURef')
                            else:
                              masterClipRef= None

                            # Retrieving Relative Amount of frames available since start of MasterClip
                            #masterClipRef = subclips.find('Clip').get('ObjectRef')
                            for audioclips in root.findall('.//AudioClip'):
                              audioclip = audioclips.get('ObjectID')
                              if audioclip == masterClipRef:
                                clipTimecodeIn = int(audioclips.find('Clip/InPoint').text)
                                clipTimecodeOut = int(audioclips.find('Clip/OutPoint').text)

                    # Add Info to the sequences' clip list.
                    # Buscar secuencia y agregar lista de clips ahora.
                    for sequence in projectMediaList:
                      if sequence.id == openId:
                        sequence.timeline.append((('ATRK' + audioClipTrackID), masterClipRef, start, end, clipTimecodeIn, clipTimecodeOut))
      n += 1

def getMediaList (xml):

  root = ET.fromstring(xml)
  nbin = 0
  mediaList = []

  #Find ProjectItem list of Bins and its content's ObjectURefs)
  for bins in root.findall('.//ProjectItemContainer/..[@ObjectUID]'):
    try:
      binName = (bins.find('ProjectItem/Name')).text
      binId = bins.get('ObjectUID')
      matchs = 0 #check for matchs in mediaList

      # if not duplicated
      for instance in mediaList:
        if isinstance (instance, Bin):
          if instance.id == binId:
            matchs +=1
      if matchs == 0:
        mediaList.append(Bin(binName, binId))
        nbinPos = len(mediaList) - 1
    except:
      print ('')

    #Get ObjectURefs to later match with Masterclips IDs
    for items in bins.findall('ProjectItemContainer/Items/Item'):
      itemID = items.get('ObjectURef')

      #If its a Bin
      try:
        for items2 in root.findall('./BinProjectItem'):
          binId2 = items2.get ('ObjectUID')
          if binId2 == itemID:
            binName = items2.find('ProjectItem/Name').text
            print ('Bin inside Bin', binName)
            nbin += 1
            mediaList.append(Bin(binName, binId2))
            nbinPos = len(mediaList) - 1
            mediaList[nbinPos].inBin = binId #this Works Wrong

      except:
        print ('')

      #Find Ref in ClipProjectItems's matching Objects IDs
      for clipProjectItems in root.findall('.//MasterClip/..[@ObjectUID]'):
        clipProjectItem = clipProjectItems.get('ObjectUID')
        if clipProjectItem == itemID:
          masterIdRef = clipProjectItems.find('MasterClip').get('ObjectURef')
          #print ('Match', masterIdRef)
          for masterClips in root.findall('./MasterClip'):
            masterClipID = masterClips.get('ObjectUID') # This is The global ID to link with project's bin
            auvidRef = (masterClips.find('Clips/Clip')).get('ObjectRef')
            if masterClipID == masterIdRef:
              if masterClips.find('LoggingInfo') != None:
                clipLoggingRef = masterClips.find('LoggingInfo').get('ObjectRef')

                #Search for ClipLoggingInfo with matching ObjectRef
                for clipLoggings in root.findall('ClipLoggingInfo'):
                  clipLoggingID = clipLoggings.get('ObjectID')

                  if clipLoggingID == clipLoggingRef:
                    try:
                      clipName = clipLoggings.find('ClipName').text
                      if clipName == None:
                        clipName = clipLoggings.find('Name').text
                    except:
                      clipName = 'Not Available'
                      #Aqui ver Texto
                    print ('In Bin ', binName,'Clip ', clipName)
                    try:
                      tapeName = clipLoggings.find('TapeName').text
                      print ('TapeName:', tapeName)
                    except:
                      tapeName = 'Not Available'
                      print ('TapeName:', tapeName)
                    try:
                      mediaInP = int(clipLoggings.find('MediaInPoint').text)
                      mediaInP = (mediaInP / 8441789933)
                      print ('Media Start position:',mediaInP)
                    except:
                      mediaInP = 0
                    try:
                      mediaOutP = int(clipLoggings.find('MediaOutPoint').text)
                      mediaOutP = (mediaOutP / 8441789933) - 1
                      print ('Media End position:',mediaOutP)
                    except:
                      mediaOutP = 0
                    try:
                      mediaFrameR = int(clipLoggings.find('MediaFrameRate').text)
                      mediaFrameR = round((10594584000 * 23.976) / mediaFrameR, 3)
                      print ('Medias Original Frame Rate :', mediaFrameR)
                    except:
                      mediaFrameR = None

                    #Find AudioClip and VideoClip link with MasterClip
                    for auvidIDs in root.findall('.//Clip/..[@ObjectID]'):
                      try:
                        auvidMediaSourceRef = auvidIDs.find('Clip/Source').get('ObjectRef')
                        auvidID = auvidIDs.get('ObjectID')
                        if auvidID ==  auvidRef:
                          auvidID = auvidIDs.get('ObjectID')
                          classID = auvidIDs.get('ClassID')
                          if classID == '9308dbef-2440-4acb-9ab2-953b9a4e82ec' or classID == 'b8830d03-de02-41ee-84ec-fe566dc70cd9':
                            classID = 'Media'

                          #If it's Media
                          try:
                            for MediaSources in root.findall('.//MediaSource/..[@ObjectID]'):
                              MediaSource = MediaSources.get('ObjectID')
                              if MediaSource == auvidMediaSourceRef: #A clip is found

                                # Create Instance of Clip
                                mediaList.append(MasterClip())
                                mediaList[(len(mediaList)-1)].id = masterClipID  # Id linking Bins and its instances in Sequences
                                mediaList[(len(mediaList)-1)].name = clipName
                                mediaList[(len(mediaList)-1)].tapeName = tapeName
                                mediaList[(len(mediaList)-1)].frameRate = mediaFrameR
                                mediaList[(len(mediaList)-1)].mediaStart = mediaInP  # Media's start timecode
                                mediaList[(len(mediaList)-1)].mediaEnd = mediaOutP
                                mediaList[(len(mediaList) - 1)].inBin = binId
                                mediaList[nbinPos].ingest(masterClipID)

                                if MediaSources.find('MediaSource/Media').get('ObjectURef') != None:
                                  mediaRef = MediaSources.find('MediaSource/Media').get('ObjectURef')
                                  for medias in root.findall('.//Media'):
                                    mediaID = medias.get('ObjectUID')
                                    if mediaID == mediaRef:
                                      filePath = medias.find('FilePath').text
                                      mediaList[(len(mediaList) - 1)].filePath = filePath
                                      try:  # Internal Premiere's clips have non valid a numeric reference for file path
                                        filePath = int(filePath)
                                        filePath = 'Not Available'
                                        mediaList[(len(mediaList) - 1)].filePath = filePath
                                        # print ('Its file path is ', filePath)
                                      except:
                                        print ('Its file path is ', filePath)

                                print ('clip', mediaList[(len(mediaList) - 1)])
                          except:
                            print ('')
                          #If Sequence
                          try:
                            for sequenceIDs in root.findall('.//SequenceSource/..[@ObjectID]'):
                              sequenceSourceID = sequenceIDs.get('ObjectID')
                              if sequenceSourceID == auvidMediaSourceRef:
                                sequenceRef = sequenceIDs.find('SequenceSource/Sequence').get('ObjectURef') #Link w/ Sequences Id

                                for sequences in root.findall('./Sequence'):
                                  sequenceID = sequences.get('ObjectUID')
                                  if sequenceID == sequenceRef:
                                    seqHeight = sequences.find('Node/Properties/MZ.Sequence.PreviewFrameSizeHeight').text
                                    seqWidth = sequences.find('Node/Properties/MZ.Sequence.PreviewFrameSizeWidth').text
                                    print ('Sequence is', seqWidth, 'x', seqHeight)

                                    # Now FrameRates
                                    for trackGroupIDs in sequences.findall('TrackGroups/TrackGroup/Second/.[@ObjectRef]'):
                                      ObjectRef = trackGroupIDs.get('ObjectRef')  # Referencia al ID de VideoTrackGroups

                                      for videoTrackGroup in root.findall('.//VideoTrackGroup'):
                                        if ObjectRef == videoTrackGroup.get('ObjectID'):
                                          # Frame Rate del Video TrackGroup
                                          seqVidFrameRate = int(videoTrackGroup.find('TrackGroup/FrameRate').text)
                                          seqVidFrameRate = round((10594584000 * 23.976) / (seqVidFrameRate), 3)
                                          print ('Video FrameRate: ', seqVidFrameRate, 'fps')

                                      for audioTrackGroup in root.findall('.//AudioTrackGroup'):
                                        if ObjectRef == audioTrackGroup.get('ObjectID'):
                                          # Frame Rate del Audio TrackGroup
                                          seqAudFrameRate = audioTrackGroup.find('TrackGroup/FrameRate').text
                                          seqAudFrameRate = int(seqAudFrameRate)
                                          seqAudFrameRate = (5292000 * 48000) / (seqAudFrameRate)
                                          print ('Audio FrameRate: ', seqAudFrameRate, 'kHz')

                                    #Create Instance of Sequence
                                    mediaList.append(Sequence())
                                    mediaList[(len(mediaList)-1)].id = sequenceID
                                    mediaList[(len(mediaList)-1)].name = clipName
                                    mediaList[(len(mediaList)-1)].height = seqHeight
                                    mediaList[(len(mediaList)-1)].width = seqWidth
                                    mediaList[(len(mediaList)-1)].vidframerate = seqVidFrameRate
                                    mediaList[(len(mediaList)-1)].audframerate = seqAudFrameRate
                                    mediaList[(len(mediaList) - 1)].inBin = binId
                                    mediaList[nbinPos].ingest(sequenceID)


                          except:
                            print ('')

                      except:
                        print ('')
  nbin +=1
  return mediaList


def timecoder(frames, timebase):
  if timebase <1000:
    h = int(frames / (timebase * 3600))
    m = int(frames / (timebase * 60)) % 60
    s = int((frames % (timebase * 60)) / timebase)
    f = int(frames % (timebase * 60) % timebase)
    return "%02d:%02d:%02d:%02d" % (h, m, s, f)
  else:
    h = int(frames / (timebase * 3600))
    m = int(frames / (timebase * 60)) % 60
    s = int((frames % (timebase * 60)) / timebase)
    f = int(frames % (timebase * 60) % timebase)
    mseg = 1000 * f / timebase
    return "%02d:%02d:%02d:%03d" % (h, m, s, mseg)


projectXml = OpenProj('test.prproj') #Your Project File Here
projectMediaList = getMediaList(projectXml)
seqID = '90b9a44d-f408-4616-b5d0-d48bf905137a' #This is temporal and should be activated by selecting a sequence retrieved. Here put yours.
projectSequences = openSequence(projectXml, seqID)
#SaveProj (xml,'proyectonuevo.prproj')

#Frame & Frequency Factors for Calculus
#X=(10594584000*23,976)/framerate
#x = (5292000*48000)/freq
#1 frame = 8441789933 * dur # 8475666401,209865089699074
