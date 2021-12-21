# -*- coding: UTF-8 -*-
import gzip, shutil, os
import xml.etree.ElementTree as ET

class Sequence:
  def __init__(self, id): #from Sequence Tab
    self.id = id
    self.name = ''
    self.height = ''
    self.width = ''
    self.vidframerate = 0
    self.audframerate = 0
    self.sequence = []

def OpenProj(filename):

  fileInside = filename.replace('.prproj', '')  # el archivo dentro del prproj se llama igual y no tiene extensión
  with gzip.open(filename, 'rb') as f_in, open(fileInside, 'wb') as f_out:
    shutil.copyfileobj(f_in, f_out)
    f_out.close()
    f_in.close()
    xml_file_handle = open(fileInside, 'rb')
    xml_as_string = xml_file_handle.read()
    xml_file_handle.close()
    #print (xml_as_string)
    #os.remove(fileInside)

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

def loadSequences(xml):

  root = ET.fromstring(xml)
  trackID = []

  seq =[]
  n = 0

  for sequences in root.findall('.//Name/..[@ClassID]'):
      if sequences.get('ClassID') == '6a15d903-8739-11d5-af2d-9b7855ad8974':

        #print (len(seq), n)
        seq.insert(n, Sequence(''))
        seq[n].id = sequences.get('ObjectUID')
        seq[n].name = sequences.find('Name').text
        seq[n].height = sequences.find('Node/Properties/MZ.Sequence.PreviewFrameSizeHeight').text
        seq[n].width = sequences.find('Node/Properties/MZ.Sequence.PreviewFrameSizeWidth').text

        #Find TrackGroup's ObjectRef

        #print ('Sequence ', seq[n].name, 'with ID ', seq[n].id)

        # First Check Video Tracks

        for trackGroupIDs in sequences.findall('TrackGroups/TrackGroup/Second/.[@ObjectRef]'):
          ObjectRef = trackGroupIDs.get('ObjectRef') #Referencia al ID de VideoTrackGroups

          for videoTrackGroup in root.findall('.//VideoTrackGroup'):
            if ObjectRef == videoTrackGroup.get('ObjectID'):

              #Frame Rate del Video TrackGroup
              seq[n].vidframerate = int(videoTrackGroup.find('TrackGroup/FrameRate').text)
              seq[n].vidframerate = round((10594584000*23.976)/ (seq[n].vidframerate),3)
              #print ('Video FrameRate: ', seq[n].vidframerate, 'fps')

              for tracksID in videoTrackGroup.findall('TrackGroup/Tracks/Track'):
                trackID = tracksID.get('ObjectURef')

                #Link between TrackGroups & ClipTrackItems via ClipTrack
                for videoClipTracks in root.findall('.//VideoClipTrack'):
                  videoClipTrackID = videoClipTracks.get('ObjectUID')
                  if videoClipTrackID == trackID:
                    videoClipTrackID = videoClipTracks.find('ClipTrack/Track/ID').text
                    for trackItems in videoClipTracks.findall('ClipTrack/ClipItems/TrackItems/TrackItem'):
                      trackItem = trackItems.get('ObjectRef')
                      #print ('Video Clip inside Track') #:', trackItem)

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
                                masterClipRef = subclips.find('MasterClip').get('ObjectURef')
                              else:
                                masterClipRef= None
                              clipName = subclips.find('Name').text
                              #print ('Clip Name is', clipName)

                              #Retrieving more information from VideoClip Objects
                              clipRef = subclips.find('Clip').get('ObjectRef')
                              for videoclips in root.findall('.//VideoClip'):
                                videoclip = videoclips.get('ObjectID')
                                if videoclip == clipRef:
                                  clipTimecodeIn = int(videoclips.find('Clip/InPoint').text)
                                  clipTimecodeIn = clipTimecodeIn/8441789933
                                  clipTimecodeOut = int(videoclips.find('Clip/OutPoint').text)
                                  clipTimecodeOut = (clipTimecodeOut/8441789933)-1
                                  #print ('Clip Start position Inner Timecode:', clipTimecodeIn) #Relative Amount of frames available since start of data
                                  #print ('Clip End position Inner Timecode:', clipTimecodeOut) #Relative Amount of frames available since start of data

                                  #Retrieve Timecode Start Value from Clip

                                  for masterclips in root.findall ('.//MasterClip'):
                                    masterclipID = masterclips.get('ObjectUID')
                                    if masterclipID == masterClipRef:
                                      if masterclips.find('LoggingInfo') != None:
                                        clipLoggingRef = masterclips.find('LoggingInfo').get('ObjectRef')
                                        for clipLoggings in root.findall('ClipLoggingInfo'):
                                          clipLoggingID = clipLoggings.get ('ObjectID')
                                          if clipLoggingID == clipLoggingRef:
                                            if clipLoggings.find('TapeName').text != None:
                                              tapeName = clipLoggings.find('TapeName').text
                                              #print ('TapeName:', tapeName)
                                            else:
                                              tapeName = 'Not Available'
                                            if clipLoggings.find('MediaInPoint').text != None:
                                              mediaInP = int(clipLoggings.find('MediaInPoint').text)
                                              mediaInP = (mediaInP / 8441789933)
                                              print ('Media Start position:',mediaInP)
                                              mediaOutP = int(clipLoggings.find('MediaOutPoint').text)
                                              mediaOutP = (mediaOutP / 8441789933)-1
                                              #print ('Media End position:',mediaOutP)
                                              mediaFrameR = int(clipLoggings.find('MediaFrameRate').text)
                                              mediaFrameR = round((10594584000*23.976)/ mediaFrameR,3)
                                              #print ('Medias Original Frame Rate :', mediaFrameR)

                                  # Retrieve file path information
                                  videoMedSrcRef = videoclips.find('Clip/Source').get('ObjectRef')
                                  for videoMediaSources in root.findall('.//VideoMediaSource'):
                                    videoMediaSource = videoMediaSources.get('ObjectID')
                                    if videoMediaSource == videoMedSrcRef:
                                      if videoMediaSources.find('MediaSource/Media').get(
                                              'ObjectURef') != None:
                                        mediaRef = videoMediaSources.find('MediaSource/Media').get(
                                          'ObjectURef')
                                        for medias in root.findall('.//Media'):
                                          mediaID = medias.get('ObjectUID')
                                          if mediaID == mediaRef:
                                            filePath = medias.find('FilePath').text
                                            #print ('Its file path is ', filePath)

                      # Add Info to the sequences' list.
                      seq[n].sequence.append([('SEQID'+str(n)),('V' + videoClipTrackID), filePath, tapeName, timecoder(start, seq[n].vidframerate),timecoder(end, seq[n].vidframerate),timecoder((mediaInP + clipTimecodeIn), seq[n].vidframerate),timecoder((mediaOutP + clipTimecodeOut), seq[n].vidframerate),mediaFrameR])  # TrackID, fpath, tape, timelineIn, timelineOut, mediaIN, mediaOUT

          #Now Check Audio Tracks
        for trackGroupIDs in sequences.findall('TrackGroups/TrackGroup/Second/.[@ObjectRef]'):
          ObjectRef = trackGroupIDs.get('ObjectRef')  # Referencia al ID de VideoTrackGroups

          for audioClipTrackID in root.findall('.//AudioTrackGroup'):
            if ObjectRef == audioClipTrackID.get('ObjectID'):

              #Frame Rate del Audio TrackGroup
              seq[n].audframerate = audioClipTrackID.find('TrackGroup/FrameRate').text
              seq[n].audframerate = int(seq[n].audframerate)
              seq[n].audframerate = (5292000*48000)/(seq[n].audframerate)
              #print ('Audio FrameRate: ', seq[n].audframerate, 'kHz')

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
                              clipName = subclips.find('Name').text
                              #print ('Clip Name is', clipName)

                              # Retrieving more information from AudioClip Objects
                              clipRef = subclips.find('Clip').get('ObjectRef')
                              for audioclips in root.findall('.//AudioClip'):
                                audioclip = audioclips.get('ObjectID')
                                if audioclip == clipRef:
                                  clipTimecodeIn = int(audioclips.find('Clip/InPoint').text)
                                  clipTimecodeIn = clipTimecodeIn / 8441789933
                                  clipTimecodeOut = int(audioclips.find('Clip/OutPoint').text)
                                  clipTimecodeOut = (clipTimecodeOut / 8441789933)-1
                                  #print ('Clip Start position Inner Timecode:', clipTimecodeIn) #Relative Amount of frames available since start of data
                                  #print ('Clip End position Inner Timecode:', clipTimecodeOut) #Relative Amount of frames available since start of data

                                  # Retrieve Timecode Start Value from Clip

                                  for masterclips in root.findall('.//MasterClip'):
                                    masterclipID = masterclips.get('ObjectUID')
                                    if masterclipID == masterClipRef:
                                      if masterclips.find('LoggingInfo') != None:
                                        clipLoggingRef = masterclips.find('LoggingInfo').get('ObjectRef')
                                        for clipLoggings in root.findall('ClipLoggingInfo'):
                                          clipLoggingID = clipLoggings.get('ObjectID')
                                          if clipLoggingID == clipLoggingRef:
                                            if clipLoggings.find('TapeName').text != None:
                                              tapeName = clipLoggings.find('TapeName').text
                                              #print ('TapeName:', tapeName)
                                            else:
                                              tapeName = 'Not Available'
                                            if clipLoggings.find('MediaInPoint').text != None:
                                              mediaInP = int(clipLoggings.find('MediaInPoint').text)
                                              mediaInP = (mediaInP / 8441789933)
                                              #print ('Media Start position :', mediaInP)
                                              mediaOutP = int(clipLoggings.find('MediaOutPoint').text)
                                              mediaOutP = (mediaOutP / 8441789933) - 1
                                              #print ('Media End position :', mediaOutP)
                                              if int(clipLoggings.find('TimecodeFormat').text) == 200:
                                                mediaFrameR = int(clipLoggings.find('MediaFrameRate').text)
                                                mediaFrameR = round(((5291994.71*48000) / mediaFrameR)) #improved ratio
                                              else:
                                                mediaFrameR = int(clipLoggings.find('MediaFrameRate').text)
                                                mediaFrameR = (10594584000 * 23.976) / mediaFrameR
                                              #print ('Medias Original Frame Rate :', mediaFrameR)

                                  #Retrieve file path information
                                  audioMedSrcRef = audioclips.find('Clip/Source').get('ObjectRef')
                                  for audioMediaSources in root.findall('.//AudioMediaSource'):
                                    audioMediaSource = audioMediaSources.get('ObjectID')
                                    if audioMediaSource == audioMedSrcRef:
                                      if audioMediaSources.find('MediaSource/Media').get('ObjectURef') !=None:
                                        mediaRef = audioMediaSources.find('MediaSource/Media').get('ObjectURef')
                                        for medias in root.findall('.//Media'):
                                          mediaID = medias.get('ObjectUID')
                                          if mediaID == mediaRef:
                                            filePath = medias.find('FilePath').text
                                            #print ('Its file path is ', filePath)

                      #Add Info to the sequences' list.
                      seq[n].sequence.append([('SEQID'+str(n)),('A'+audioClipTrackID),filePath, tapeName, timecoder(start,seq[n].vidframerate), timecoder (end, seq[n].vidframerate), timecoder((mediaInP+clipTimecodeIn),seq[n].vidframerate),timecoder((mediaOutP+clipTimecodeOut),seq[n].vidframerate),mediaFrameR]) #TrackID, fpath, tape, timelineIn, timelineOut, mediaIN, mediaOUT

        print (seq[n].name, seq[n].vidframerate)
        print (seq[n].sequence)
        n += 1

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


xml = OpenProj('popup2.prproj')
loadSequences(xml)
#save = SaveProj (xml,'proyectonuevo.prproj')

#Calculo para frames y frecuencias
#X=(10594584000*23,976)/framerate
#x = (5292000*48000)/freq
#1 frame = 8441789933 * dur / 8475666401,209865089699074