# -*- coding: UTF-8 -*-

import gzip, shutil, os
from os.path import exists
import xml.etree.ElementTree as ET

class Sequence:
  def __init__(self):
    self.id = id
    self.name = ''
    self.height = 0
    self.width = 0
    self.vidframerate = 0
    self.audframerate = 0
    self.timeline = [] #TrackID, file path, clip name, tape, timeline In, timeline Out, media IN, media OUT, media Frame Rate
    self.inBin = 0

class MasterClip:
  def __init__(self):
    self.id = '' # Id linking Bins and its instances in Sequences
    self.type = '' #Audio, Video, Other
    self.name = ''
    self.filePath = ''
    self.online = True
    self.tapeName = ''
    self.frameRate = 0
    self.mediaStart = 0
    self.mediaEnd = 0
    self.inBin = 0

class Bin:
  def __init__(self, name, selfid, parent):
    self.id = selfid
    self.name = name
    self.parent = parent
    self.inBin = None

  def ingest(self, clipid):
    self.contains.append(clipid)

  def contains (self, clipid):
    if clipid in self.contains:
      return True
    else:
      return False

def OpenProj(filename):

  try:
    fileInside = filename.replace('.prproj', '')  # el archivo dentro del prproj se llama igual y no tiene extensión
    with gzip.open(filename, 'rb') as f_in, open(fileInside, 'wb') as f_out:
      shutil.copyfileobj(f_in, f_out)
      f_out.close()
      f_in.close()
      xml_file_handle = open(fileInside, 'rb')
      xml_as_string = xml_file_handle.read()
      xml_file_handle.close()
      #os.remove(fileInside) #Interine File
    print ('Retrieved data from File')
    return xml_as_string
  except:
    print ('Could not retrieve data from .prpoj')

def SaveProj(xml, outFile):
  fileInside = outFile.replace('.prproj', '')
  f = open(fileInside, "wb") #creamos archivo temporal
  f.write(xml)
  f.close()

  with open(fileInside, 'rb') as f_in:
    with gzip.open(outFile, 'w') as f_out:
      f_out.writelines(f_in)
      f_out.close()
      f_in.close()
  os.remove(fileInside) #Borra archivo temporal

def openSequence(xml):

  #openId = projectMediaList[index].id
  root = ET.fromstring(xml)
  n = 0

  #Cambiar este enfoque, rastrear todas las secuencias y cargarlas en el MediaList

  for sequences in root.findall('./Sequence'):
    id = sequences.get('ObjectUID')
    print ('')
    print ('Reading Sequence', id)

    # First Check Video Tracks

    for trackGroupIDs in sequences.findall('TrackGroups/TrackGroup/Second/.[@ObjectRef]'):
      ObjectRef = trackGroupIDs.get('ObjectRef') #Referencia al ID de VideoTrackGroups

      for videoTrackGroup in root.findall('.//VideoTrackGroup'):
        if ObjectRef == videoTrackGroup.get('ObjectID'):
          frameRateFactor = int(videoTrackGroup.find('TrackGroup/FrameRate').text) #For frame rate calculus
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
                      start = start / frameRateFactor
                      #print ('Clip Start position in Timeline: ', start)
                      end = int(videoClipTrackItems.find('ClipTrackItem/TrackItem/End').text)
                      end = end / frameRateFactor
                      #print ('Clip End position in Timeline: ', end)

                      #To search text content / Scale Info / Motion Attributes.

                      try:
                        componentRef = videoClipTrackItems.find('ClipTrackItem/ComponentOwner/Components').get('ObjectRef')
                        for componentIDs in root.findall('./VideoComponentChain'):
                          componentID = componentIDs.get('ObjectID')
                          vidcomponentChainRef = componentIDs.find('ComponentChain/Components/Component').get('ObjectRef')
                          if componentID == componentRef:
                            for filtersID in root.findall('VideoFilterComponent'):
                              filterID = filtersID.get ('ObjectID')
                              if filterID == vidcomponentChainRef:
                                print ('Accessing clip attribute')

                                #Text Clip?

                                try:
                                  text = filtersID.find('Component/InstanceName').text
                                  print('Text Found:', text)
                                except:
                                  print('')
                                try:
                                  for filtersREFs in filtersID.findall('Component/Params/Param'):
                                    filterREF = filtersREFs.get('ObjectRef')

                                    #Position

                                    try:
                                      for atts2IDs in root.findall('PointComponentParam'):
                                        att2ID = atts2IDs.get('ObjectID')
                                        if att2ID == filterREF:
                                          filterName = atts2IDs.find('Name').text
                                          print('Filter found: ', filterName)

                                          if filterName == 'Position':

                                            posStart = atts2IDs.find('StartKeyframe').text
                                            # Position has 14 values. Second matters and includes x & y mutiplied by sequence's width and height respectively
                                            #print (posStart)
                                            posStart = posStart.split(',')
                                            position = posStart[1].split(':')

                                            # Find clip's position
                                            #position[0] = int(position[0])
                                            #position[1] = int(position[1])

                                            print ('Clip Position:', position[0],',', position[1])

                                            # STILL NEED TO FIND HOW TO FIGURE THIS OUT (KEYFRAMES)

                                            # posVarying = int(pos) #Clip's scale in timeline.
                                            # try: #For keyframes
                                            #  posVarying = posIDs.find('StartKeyframe').text
                                            # except:
                                            #  pass
                                    except:
                                      position = None

                                    #Other Attributes

                                    for attsIDs in root.findall('VideoComponentParam'):
                                      attID = attsIDs.get ('ObjectID')
                                      if attID == filterREF:
                                        filterName = attsIDs.find('Name').text
                                        print ('Filter found: ',filterName)

                                        if filterName == 'Scale':
                                            scale = attsIDs.find('CurrentValue').text
                                            scale = int(scale) * 2 #Clip's scale in timeline.
                                            #print (scale)
                                            attsIDs.find('CurrentValue').text = str(scale)

                                            #Second place scale appears in Premiere's XMLs

                                            scalesKf = attsIDs.find('StartKeyframe').text
                                            #print (scalesKf)
                                            scalesKf = scalesKf.split(',')
                                            #print (scalesKf)
                                            l = len(scalesKf[1])
                                            scalesKf[1] = scalesKf[1][:l - 1]
                                            scale2 = int(scalesKf[1]) # * 2
                                            #print (scale2)
                                            #scalesKf = scalesKf[0] + ',' + str(scale2) + '.' + ',' + scalesKf[2] + ',' + scalesKf[3] + ',' + scalesKf[
                                            #             4] + ',' + scalesKf[5] + ',' + scalesKf[6] + ',' + scalesKf[
                                            #             7]
                                            #attsIDs.find('StartKeyframe').text = scalesKf
                                            scale = scale2
                                            print ('Scale:', scale)

                                        if filterName == 'Rotation':
                                          rotStart = attsIDs.find('StartKeyframe').text
                                          # Rotation has 8 values. Second matters
                                          # print (posStart)
                                          rotStart = rotStart.split(',')
                                          rotation = rotStart[1].split('.')
                                          rotation = rotation [0]
                                          print ('Rotation Value:', rotation)

                                  #If Variables not assigned, then assign value None

                                  try:
                                    position
                                  except NameError:
                                    position = None
                                  try:
                                    scale
                                  except NameError:
                                    scale = None
                                  try:
                                    rotation
                                  except NameError:
                                    rotation = None
                                except:
                                  print ('')
                                try:
                                  text
                                except NameError:
                                  text = None
                      except:
                        # When Project has no modification in this parameters, doesnt create even tags
                        try:
                          position
                        except NameError:
                          position = None
                        try:
                          scale
                        except NameError:
                          scale = None
                        try:
                          rotation
                        except NameError:
                          rotation = None
                        try:
                          text
                        except NameError:
                          text = None

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

                  #Add Attributes to Sequence in ProjectMediaList
                  n2 = 0
                  for searchSeq in projectMediaList:
                    if type(projectMediaList[n2]) is Sequence:
                      if projectMediaList[n2].id == id:
                        projectMediaList[n2].timeline.append((('VTRK' + videoClipTrackID), masterClipRef, start, end, clipTimecodeIn, clipTimecodeOut, scale, position, rotation, text))
                        #print ('Sequence', projectMediaList[n2].name, 'succesfully read')
                    n2 += 1

    #Now Check Audio Tracks

    for trackGroupIDs in sequences.findall('TrackGroups/TrackGroup/Second/.[@ObjectRef]'):
      ObjectRef = trackGroupIDs.get('ObjectRef')  # Referencia al ID de VideoTrackGroups

      for audioClipTrackID in root.findall('.//AudioTrackGroup'):
        if ObjectRef == audioClipTrackID.get('ObjectID'):
          audRateFactor = int(audioClipTrackID.find('TrackGroup/FrameRate').text)
          #print ('Audio Frame Rate', audRateFactor)
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
                      start = start / audRateFactor
                      #print ('Clip Start position in Timeline: ', start)
                      end = int(audioClipTrackItems.find('ClipTrackItem/TrackItem/End').text)
                      end = end / audRateFactor
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

                  # Add Attributes to Sequence in ProjectMediaList
                  n2 = 0
                  for searchSeq in projectMediaList:
                    if type(projectMediaList[n2]) is Sequence:
                      if projectMediaList[n2].id == id:
                        projectMediaList[n2].timeline.append((('ATRK' + videoClipTrackID), masterClipRef, start, end, clipTimecodeIn, clipTimecodeOut))
                    n2 += 1

    n += 1
  xml = ET.tostring(root, encoding='UTF-8')
  return xml

def getMediaList (xml):

  print ('Getting File Structure')

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
        mediaList.append(Bin(binName, binId, None))
        nbinPos = len(mediaList) - 1
    except:
      pass

    #Get ObjectURefs to later match with Masterclips IDs
    for items in bins.findall('ProjectItemContainer/Items/Item'):
      itemID = items.get('ObjectURef')

      #If its a Bin
      try:
        for items2 in root.findall('./BinProjectItem'):
          binId2 = items2.get ('ObjectUID')
          if binId2 == itemID:
            binName2 = items2.find('ProjectItem/Name').text
            print ('')
            print ('Bin', binName2, 'inside Bin', binName)
            nbin += 1
            mediaList.append(Bin(binName2, binId2))
            nbinPos = len(mediaList) - 1
            mediaList[nbinPos].inBin = binId

      except:
        pass

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
                      print('')
                      print('In Bin', binName, 'element named', clipName, 'found')
                    except:
                      clipName = 'Pending'
                      print ('')
                      print('In Bin', binName, 'Non Clip Element found')

                    try:
                      tapeName = clipLoggings.find('TapeName').text
                      print ('TapeName:', tapeName)
                    except:
                      tapeName = 'Not Available'
                      print ('TapeName:', tapeName)
                    try:
                      mediaFrameR = int(clipLoggings.find('MediaFrameRate').text)
                      mediaFrameR = round((10594584000 * 23.976) / mediaFrameR, 3)
                      if mediaFrameR == 0.0:
                        mediaFrameR = None
                      print('Medias Original Frame Rate :', mediaFrameR)
                    except:
                      mediaFrameR = None
                    try:
                      mediaInP = int(clipLoggings.find('MediaInPoint').text)
                      mediaFr = int(clipLoggings.find('MediaFrameRate').text)
                      mediaInP = round((mediaInP / mediaFr))
                      print ('Media Start position:', mediaInP)
                    except:
                      mediaInP = 0
                    try:
                      mediaOutP = int(clipLoggings.find('MediaOutPoint').text)
                      mediaFr = int(clipLoggings.find('MediaFrameRate').text)
                      mediaOutP = round((mediaOutP / mediaFr))
                      print ('Media End position:',mediaOutP)
                    except:
                      mediaOutP = 0

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
                                      except:
                                        print ('Its file path is ', filePath)
                                        online = exists(filePath)
                                        mediaList[(len(mediaList) - 1)].online = online

                          except:
                            pass

                          #If Sequence
                          try:
                            for sequenceIDs in root.findall('.//SequenceSource/..[@ObjectID]'):
                              sequenceSourceID = sequenceIDs.get('ObjectID')
                              if sequenceSourceID == auvidMediaSourceRef:
                                sequenceRef = sequenceIDs.find('SequenceSource/Sequence').get('ObjectURef') #Link w/ Sequences Id

                                for sequences in root.findall('./Sequence'):
                                  sequenceID = sequences.get('ObjectUID')
                                  clipName = sequences.find('Name').text
                                  print ('Sequence Name', clipName)
                                  if sequenceID == sequenceRef:
                                    seqHeight = int(sequences.find('Node/Properties/MZ.Sequence.PreviewFrameSizeHeight').text)
                                    seqWidth = int(sequences.find('Node/Properties/MZ.Sequence.PreviewFrameSizeWidth').text)
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
                                          seqAudFrameRate = round((5292000 * 48000) / (seqAudFrameRate))
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
                            pass

                      except:
                        pass
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

print ('PRPROJ READER')
projectXml = OpenProj('test.prproj') #Your Project File Here
projectMediaList = getMediaList(projectXml)
projectSequences = openSequence(projectXml)
SaveProj (projectSequences,'proyectonuevo.prproj')
