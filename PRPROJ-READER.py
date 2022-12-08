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
        self.timeline = []  # TrackID, file path, clip name, tape, timeline In, timeline Out,
        # media IN, media OUT, media Frame Rate
        self.inBin = 0


class MasterClip:
    def __init__(self):
        self.id = ''  # Id linking Bins and its instances in Sequences
        self.type = ''  # Audio, Video, Other
        self.name = ''
        self.filepath = ''
        self.online = True
        self.tapename = ''
        self.framerate = 0
        self.mediastart = 0
        self.mediaend = 0
        self.inbin = 0
        self.frameratefactor = 0


class Bin:
    def __init__(self, name, self_id, inbin):
        self.id = self_id
        self.name = name
        self.inbin = inbin  # Parent Bin Id
        self.contains = []  # of Clip Items contained.

    def ingest(self, clip_id):
        self.contains.append(clip_id)

    def contains(self, clip_id):
        if clip_id in self.contains:
            return True
        else:
            return False


class ClipInTimeline:
    def __init__(self, id_ref, kind, track, start_pos_timeline, end_pos_timeline, timecode_in, timecode_out, speed, ismuted):
        self.id = id_ref
        self.kind = kind  # Audio, Video, Text, etc.
        self.track_position = track  # Which track is it in
        self.pos_start = start_pos_timeline  # First Frame position in Timeline
        self.pos_end = end_pos_timeline  # Last Frame position in Timeline
        self.timecode_in = timecode_in  # Clip's First Frame's timecode reference (relative since first frame available)
        self.timecode_out = timecode_out  # Clip's Last Frame's timecode reference (relative since first frame available)
        self.ismuted = ismuted
        self.speed = speed

    def isvideo(self, scale, position, rotation, opacity, text):
        self.scale = scale
        self.position = position
        self.rotation = rotation
        self.opacity = opacity
        self.text = text

    def isaudio(self, level, balance):
        self.level = level # List containing [Level, Relative Position of KeyFrame since Clip's First Frame in Timeline]
        self.balance = balance

def open_proj(filename):
    try:
        file_inside = filename.replace('.prproj', '')  # file inside prprojfiles have same name and no extension
        with gzip.open(filename, 'rb') as f_in, open(file_inside, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            f_out.close()
            f_in.close()
            xml_file_handle = open(file_inside, 'rb')
            xml_as_string = xml_file_handle.read()
            xml_file_handle.close()
            # os.remove(file_inside) #Interine File
        print('Retrieved data from File')
        return xml_as_string
    except:
        print('Could not retrieve data from .prpoj')


def save_proj(xml, out_file):
    file_inside = out_file.replace('.prproj', '')
    f = open(file_inside, "wb")  # temporal file to be ingested in gzip
    f.write(xml)
    f.close()

    with open(file_inside, 'rb') as f_in:
        with gzip.open(out_file, 'w') as f_out:
            f_out.writelines(f_in)
            f_out.close()
            f_in.close()
    os.remove(file_inside)  # deletes temporal file


def open_sequence(xml):
    root = ET.fromstring(xml)
    n = 0
    for sequences in root.findall('./Sequence'):
        sequence_id = sequences.get('ObjectUID')

        print('')
        print('Reading Sequence')

        # First Check Video Tracks

        for trackgroups in sequences.findall('TrackGroups/TrackGroup/Second/.[@ObjectRef]'):
            trackgroup_object_ref = trackgroups.get('ObjectRef')  # Referencia al ID de VideoTrackGroups

            for video_trackgroups in root.findall('.//VideoTrackGroup'):
                if trackgroup_object_ref == video_trackgroups.get('ObjectID'):
                    frame_rate_factor = int(video_trackgroups.find('TrackGroup/FrameRate').text)  # For frame rate calculus
                    for tracks in video_trackgroups.findall('TrackGroup/Tracks/Track'):
                        track_ref = tracks.get('ObjectURef')

                        # Link between TrackGroups & ClipTrackItems via ClipTrack
                        for video_clip_tracks in root.findall('.//VideoClipTrack'):
                            video_clip_track_id = video_clip_tracks.get('ObjectUID')
                            if video_clip_track_id == track_ref:
                                video_clip_track_id = video_clip_tracks.find('ClipTrack/Track/ID').text
                                for track_items in video_clip_tracks.findall('ClipTrack/ClipItems/TrackItems/TrackItem'):
                                    trackitem_ref = track_items.get('ObjectRef')

                                    # Retrieving more information from each VideoClipTrackItem

                                    for video_clip_track_items in root.findall('.//VideoClipTrackItem'):
                                        video_clip_track_item_id = video_clip_track_items.get('ObjectID')
                                        if video_clip_track_item_id == trackitem_ref:
                                            print('')
                                            print('Video Clip in Sequence.')
                                            try:
                                                mute = video_clip_track_items.find('ClipTrackItem/IsMuted').text
                                                print('Clip is Muted')
                                            except:
                                                mute = False
                                            start = int(video_clip_track_items.find('ClipTrackItem/TrackItem/Start').text)
                                            start = round(start / frame_rate_factor)
                                            # print('Clip Start position in Timeline: ', start)
                                            end = int(video_clip_track_items.find('ClipTrackItem/TrackItem/End').text)
                                            end = round((end / frame_rate_factor)-1)
                                            # print('Clip End position in Timeline: ', end)

                                            # To search Text content / Scale Info / Motion Attributes.

                                            scale = None
                                            rotation = None
                                            opacity = None
                                            text = None
                                            position = None

                                            try:
                                                cliptrackitem_component_ref = video_clip_track_items.find('ClipTrackItem/ComponentOwner/Components').get('ObjectRef')
                                                for component_chains in root.findall('./VideoComponentChain'):
                                                    component_chain_id = component_chains.get('ObjectID')
                                                    for video_components in component_chains.findall('ComponentChain/Components/Component'):
                                                        video_components_ref = video_components.get('ObjectRef')
                                                        if component_chain_id == cliptrackitem_component_ref:

                                                            for filters in root.findall('VideoFilterComponent'):
                                                                filter_id = filters.get('ObjectID')
                                                                if filter_id == video_components_ref:
                                                                    # print('Accessing attributes')

                                                                    # Text Clip?
                                                                    try:
                                                                        text = filters.find('Component/InstanceName').text
                                                                        print('Text Found:', text)
                                                                    except:
                                                                        text = None
                                                                    try:
                                                                        for filters_refs in filters.findall('Component/Params/Param'):
                                                                            filter_ref = filters_refs.get('ObjectRef')

                                                                            # Position
                                                                            try:
                                                                                for atts2IDs in root.findall('PointComponentParam'):
                                                                                    att2ID = atts2IDs.get('ObjectID')
                                                                                    if att2ID == filter_ref:
                                                                                        filter_name = atts2IDs.find('Name').text
                                                                                        print('Filter found:', filter_name)

                                                                                        if filter_name == 'Position':

                                                                                            pos_start = atts2IDs.find('StartKeyframe').text
                                                                                            # Position has 14 values. Second matters and includes x & y multiplied by sequence's width and height respectively
                                                                                            # print(pos_start)
                                                                                            pos_start = pos_start.split(',')
                                                                                            position = pos_start[1].split(':')
                                                                                            position = position + ['None']  # Third Value is 'Time'

                                                                                            # If Position is Keyframed
                                                                                            try:
                                                                                                position = keyframer(atts2IDs.find('Keyframes').text, frame_rate_factor)
                                                                                            except:
                                                                                                pass
                                                                                            print('Position:', position)
                                                                            except:
                                                                                position = None

                                                                            # Attributes

                                                                            for attsIDs in root.findall('VideoComponentParam'):
                                                                                attID = attsIDs.get('ObjectID')
                                                                                if attID == filter_ref:
                                                                                    filter_name = attsIDs.find('Name').text
                                                                                    print('Filter found:', filter_name)

                                                                                    if filter_name == 'Scale':
                                                                                        scale = attsIDs.find('StartKeyframe').text
                                                                                        scale = scale.split(',')
                                                                                        l = len(scale[1])
                                                                                        scale[1] = scale[1][:l - 1]  # deletes last character '.'
                                                                                        scale = int(scale[1])

                                                                                        # If Keyframed attribute
                                                                                        try:
                                                                                            scale = keyframer(attsIDs.find('Keyframes').text, frame_rate_factor)
                                                                                        except:
                                                                                            pass

                                                                                        print('Scale:', scale)

                                                                                    if filter_name == 'Rotation':
                                                                                        rot_start = attsIDs.find('StartKeyframe').text
                                                                                        rot_start = rot_start.split(',')
                                                                                        rotation = rot_start[1].split('.')
                                                                                        rotation = int(rotation[0])

                                                                                        # If Keyframed attribute
                                                                                        try:
                                                                                            rotation = keyframer(attsIDs.find('Keyframes').text, frame_rate_factor)
                                                                                        except:
                                                                                            pass
                                                                                        print('Rotation', rotation)

                                                                                    if filter_name == 'Opacity':
                                                                                        opacity = attsIDs.find('StartKeyframe').text
                                                                                        opacity = opacity.split(',')
                                                                                        opacity = opacity[1].split('.')
                                                                                        opacity = int(opacity[0])

                                                                                        # If Keyframed attribute
                                                                                        try:
                                                                                            opacity = keyframer(attsIDs.find('Keyframes').text, frame_rate_factor)
                                                                                        except:
                                                                                            pass
                                                                                        print('Opacity', opacity)
                                                                    except:
                                                                        pass
                                            except:
                                                # When Project has no modification in this parameters, gives this values None
                                                try:
                                                    opacity
                                                except NameError:
                                                    opacity = None
                                                    print('Default Opacity Value')
                                                try:
                                                    position
                                                except NameError:
                                                    position = None
                                                    print('Default Position Value')
                                                try:
                                                    scale
                                                except NameError:
                                                    scale = None
                                                    print('Default Scale Value')
                                                try:
                                                    rotation
                                                except NameError:
                                                    rotation = None
                                                    print('Default Rotation Value')
                                                try:
                                                    text
                                                except NameError:
                                                    text = None

                                            # Now Retrieving more information from each SubClip Linked

                                            subclip_ref = video_clip_track_items.find('ClipTrackItem/SubClip').get('ObjectRef')  # SubClip's Ref links with SubCLips
                                            for subclips in root.findall('.//SubClip'):
                                                subclip_id = subclips.get('ObjectID')
                                                if subclip_id == subclip_ref:
                                                    if subclips.find('MasterClip') is not None:
                                                        masterclip_ref = subclips.find('MasterClip').get('ObjectURef')  # This must be linked with clips' ID
                                                    else:
                                                        masterclip_ref = None

                                                    # Retrieving Relative Amount of frames available since start of MasterClip
                                                    clip_ref = subclips.find('Clip').get('ObjectRef')
                                                    for videoclips in root.findall('.//VideoClip'):
                                                        videoclip_id = videoclips.get('ObjectID')
                                                        if videoclip_id == clip_ref:
                                                            for objects in projectMediaList:
                                                                if type(objects) is MasterClip:
                                                                    if objects.id == masterclip_ref:
                                                                        cframerate = objects.framerate
                                                                        cinpoint = objects.mediastart
                                                                        coutpoint = objects.mediaend - 1

                                                            clip_timecode_in = int(videoclips.find('Clip/InPoint').text)
                                                            clip_timecode_out = int(videoclips.find('Clip/OutPoint').text)
                                                            clip_speed = 1
                                                            try:
                                                                clip_speed = round(int(videoclips.find('Clip/PlaybackSpeed').text),2)
                                                            except:
                                                                pass
                                                            try:
                                                                if videoclips.find('Clip/PlayBackwards').text == 'true':
                                                                    clip_speed = clip_speed * (-1)
                                                            except:
                                                                pass
                                                            try:
                                                                if clip_speed > 0:
                                                                    clip_timecode_in = round(clip_timecode_in / cframerate) + cinpoint
                                                                    clip_timecode_out = round(clip_timecode_out / cframerate) + cinpoint - 1
                                                                if clip_speed < 0:
                                                                    clip_timecode_in = coutpoint - round((clip_timecode_in / cframerate)) - 1
                                                                    clip_timecode_out = coutpoint - round((clip_timecode_out - 1) / cframerate)
                                                            except:
                                                                pass

                                    # Add Attributes to Sequence in ProjectMediaList
                                    for objects in projectMediaList:
                                        if type(objects) is Sequence:
                                            if objects.id == sequence_id:
                                                objects.timeline.append(ClipInTimeline(masterclip_ref, 'video', ('V' + str(video_clip_track_id)), start, end, clip_timecode_in, clip_timecode_out, clip_speed, mute))
                                                objects.timeline[-1].isvideo(scale, position, rotation, opacity, text)

        # Now Check Audio Tracks

        for trackgroups in sequences.findall('TrackGroups/TrackGroup/Second/.[@ObjectRef]'):
            trackgroup_object_ref = trackgroups.get('ObjectRef')  # Referencia al ID de VideoTrackGroups

            for audio_trackgroups in root.findall('.//AudioTrackGroup'):
                if trackgroup_object_ref == audio_trackgroups.get('ObjectID'):
                    #frame_rate_factor = int(audio_trackgroups.find('TrackGroup/FrameRate').text)
                    # print('Audio Frame Rate', audRateFactor)
                    for audio_tracks in audio_trackgroups.findall('TrackGroup/Tracks/Track'):
                        track_ref = audio_tracks.get('ObjectURef')

                        # Link between TrackGroups & ClipTrackItems via ClipTrack
                        for audio_clip_tracks in root.findall('.//AudioClipTrack'):
                            audio_clip_track_id = audio_clip_tracks.get('ObjectUID')
                            if audio_clip_track_id == track_ref:
                                track_id = int(audio_clip_tracks.find('ClipTrack/Track/ID').text) - 1
                                for track_items in audio_clip_tracks.findall('ClipTrack/ClipItems/TrackItems/TrackItem'):
                                    trackitem_ref = track_items.get('ObjectRef')
                                    print('')
                                    print('Audio Clip in Sequence')  # :', trackItem)

                                    # Retrieving more information from each AudioClipTrackItem
                                    for audio_clip_track_items in root.findall('.//AudioClipTrackItem'):
                                        audio_clip_track_item_id = audio_clip_track_items.get('ObjectID')
                                        if audio_clip_track_item_id == trackitem_ref:
                                            try:
                                                mute = audio_clip_track_items.find('ClipTrackItem/IsMuted').text
                                                print('Clip is Muted')
                                            except:
                                                mute = False
                                            start = int(audio_clip_track_items.find('ClipTrackItem/TrackItem/Start').text)
                                            start = round(start / frame_rate_factor)
                                            # print('Clip Start position in Timeline: ', start)
                                            end = int(audio_clip_track_items.find('ClipTrackItem/TrackItem/End').text)
                                            end = round((end / frame_rate_factor)-1)
                                            # print('Clip End position in Timeline: ', end)

                                            # Audio Attributes.

                                            level = None
                                            balance = None

                                            try:
                                                cliptrackitem_component_ref = audio_clip_track_items.find('ClipTrackItem/ComponentOwner/Components').get('ObjectRef')
                                                for component_chains in root.findall('./AudioComponentChain'):
                                                    component_chain_id = component_chains.get('ObjectID')
                                                    for audio_components in component_chains.findall('ComponentChain/Components/Component'):
                                                        audio_components_ref = audio_components.get('ObjectRef')
                                                        if component_chain_id == cliptrackitem_component_ref:
                                                            # print('Audio Clip in Sequence.')
                                                            for filters in root.findall('AudioFilterComponent'):
                                                                filter_id = filters.get('ObjectID')
                                                                if filter_id == audio_components_ref:
                                                                    # print('Accessing attributes')
                                                                    try:
                                                                        for filters_refs in filters.findall('AudioComponent/Component/Params/Param'):
                                                                            filter_ref = filters_refs.get('ObjectRef')

                                                                            # Attributes
                                                                            for attsIDs in root.findall('AudioComponentParam'):
                                                                                attID = attsIDs.get('ObjectID')

                                                                                # For Balance Only
                                                                                if balance is None:
                                                                                    try:
                                                                                        panner_ref = audio_clip_track_items.find('Panner').get('ObjectRef')
                                                                                        for panner_processors in root.findall('StereoToStereoPanProcessor'):
                                                                                            panner_proc_id = panner_processors.get('ObjectID')
                                                                                            if panner_proc_id == panner_ref:
                                                                                                param_ref = panner_processors.find('PanProcessor/AudioComponent/Component/Params/Param').get('ObjectRef')
                                                                                                if attID == param_ref:
                                                                                                    filter_name = attsIDs.find('Name').text
                                                                                                    print('Filter found:', filter_name)

                                                                                                    if filter_name == 'Balance':
                                                                                                        balance = attsIDs.find('StartKeyframe').text
                                                                                                        balance = balance.split(',')
                                                                                                        balance = balance[1].split('.')
                                                                                                        balance = int(balance[0])

                                                                                                        # If Keyframed attribute
                                                                                                        try:
                                                                                                            balance = keyframer(attsIDs.find('Keyframes').text, frame_rate_factor)
                                                                                                        except:
                                                                                                            pass
                                                                                                        print('Balance',
                                                                                                              balance)
                                                                                    except:
                                                                                        pass

                                                                                # For Other Attributes (Level)
                                                                                if attID == filter_ref:
                                                                                    filter_name = attsIDs.find('Name').text
                                                                                    print('Filter found:', filter_name)

                                                                                    if filter_name == 'Level':
                                                                                        level = attsIDs.find('StartKeyframe').text
                                                                                        level = level.split(',')
                                                                                        level = level[1].split('.')
                                                                                        level = int(level[0])

                                                                                        # If Keyframed attribute
                                                                                        try:
                                                                                            level = keyframer(attsIDs.find('Keyframes').text, frame_rate_factor)
                                                                                        except:
                                                                                            pass
                                                                                        print('Level', level)
                                                                    except:
                                                                        pass
                                            except:
                                                pass

                                            # Now Retrieving more information from each SubClip Linked
                                            subclip_ref = audio_clip_track_items.find('ClipTrackItem/SubClip').get('ObjectRef')  # SubClip's Ref links with SubCLips
                                            for subclips in root.findall('.//SubClip'):
                                                subclip_id = subclips.get('ObjectID')
                                                if subclip_id == subclip_ref:
                                                    if subclips.find('MasterClip') is not None:
                                                        masterclip_ref = subclips.find('MasterClip').get('ObjectURef')
                                                    else:
                                                        masterclip_ref = None

                                                    # Retrieving Relative Amount of frames available since start of MasterClip
                                                    clip_ref = subclips.find('Clip').get('ObjectRef')
                                                    for audioclips in root.findall('.//AudioClip'):
                                                        audioclip_id = audioclips.get('ObjectID')
                                                        if audioclip_id == clip_ref:
                                                            for objects in projectMediaList:
                                                                if type(objects) is MasterClip:
                                                                    if objects.id == masterclip_ref:
                                                                        cframerate = objects.framerate
                                                                        cinpoint = objects.mediastart
                                                                        coutpoint = objects.mediaend
                                                            clip_speed = 1
                                                            clip_timecode_in = int(audioclips.find('Clip/InPoint').text)
                                                            clip_timecode_out = int(audioclips.find('Clip/OutPoint').text)
                                                            try:
                                                                clip_speed = round(int(audioclips.find('Clip/PlaybackSpeed').text),2)
                                                            except:
                                                                pass
                                                            try:
                                                                if audioclips.find('Clip/PlayBackwards').text == 'true':
                                                                    clip_speed = clip_speed * (-1)
                                                            except:
                                                                pass
                                                            try:
                                                                # Timecode Notation depends on Clip being natively a video or just audio
                                                                for objects in projectMediaList:
                                                                    if type(objects) is MasterClip:
                                                                        if objects.id == masterclip_ref:
                                                                            ctype = objects.type
                                                                            # If this audio is video based (CHECKED)
                                                                            if ctype == 'Video':
                                                                                if clip_speed > 0:
                                                                                    cframerate = objects.framerate
                                                                                    clip_timecode_in = round((clip_timecode_in / cframerate)) + cinpoint  # Seems to be linked to Project's VideoSetting's FrameRate, Why???
                                                                                    clip_timecode_out = round((clip_timecode_out - 1) / cframerate) + cinpoint - 1
                                                                                if clip_speed < 0:
                                                                                    cframerate = objects.framerate
                                                                                    clip_timecode_in = coutpoint - round((clip_timecode_in / cframerate)) - 1  # Seems to be linked to Project's VideoSetting's FrameRate, Why???
                                                                                    clip_timecode_out = coutpoint - round((clip_timecode_out - 1) / cframerate)
                                                                            if ctype == 'Audio':
                                                                                # I assume this different treatment for audio lenghts depends on format
                                                                                file_extension = (objects.filepath[len(objects.filepath) - 3:]).lower()
                                                                                if file_extension == 'mp3':
                                                                                    # KIND ONE: MP3 (CHECKED)
                                                                                    cinpoint = objects.mediastart
                                                                                    coutpoint = objects.mediaend
                                                                                    proj_fr_ref = root.find('ProjectSettings/VideoSettings').get('ObjectRef')
                                                                                    for proj_frs in root.findall ('VideoSettings'):
                                                                                        if proj_frs.get('ObjectID') == proj_fr_ref:
                                                                                            if clip_speed > 0:
                                                                                                cframerate = int(proj_frs.find('FrameRate').text)
                                                                                                clip_timecode_in = round((clip_timecode_in) / cframerate) + cinpoint # Seems to be linked to Project's VideoSetting's FrameRate, Why???
                                                                                                clip_timecode_out = round((clip_timecode_out - 1)/ cframerate) + cinpoint - 1
                                                                                            if clip_speed < 0:
                                                                                                coutpoint = round(objects.mediaend * cframerate / int(proj_frs.find('FrameRate').text)) - 1
                                                                                                cframerate = int(proj_frs.find('FrameRate').text)
                                                                                                clip_timecode_in = coutpoint - round((clip_timecode_in) / cframerate)  # Seems to be linked to Project's VideoSetting's FrameRate, Why???
                                                                                                clip_timecode_out = coutpoint - round((clip_timecode_out - 1) / cframerate) + 1
                                                                                if file_extension == 'wav':
                                                                                    # KIND WAV TIMECODED
                                                                                    cframerate = objects.framerate
                                                                                    cinpoint = round(objects.mediastart / 2000)  # Originally cinpoint already divided by MediaFrameRate
                                                                                    coutpoint = round(objects.mediaend / 2000) - 1
                                                                                    if clip_speed > 0:
                                                                                        clip_timecode_in = round((clip_timecode_in / cframerate / 2000)) + cinpoint  # Seems to be linked to Project's VideoSetting's FrameRate, Why???
                                                                                        clip_timecode_out = round((clip_timecode_out - 1) / cframerate / 2000) + cinpoint - 1
                                                                                    if clip_speed < 0:
                                                                                        clip_timecode_in = coutpoint - round((clip_timecode_in / cframerate / 2000))  # Seems to be linked to Project's VideoSetting's FrameRate, Why???
                                                                                        clip_timecode_out = coutpoint - round((clip_timecode_out - 1) / cframerate / 2000) + 1
                                                                                if file_extension == 'aif' or file_extension == 'iff':
                                                                                    cframerate = objects.framerate
                                                                                    cinpoint = round(objects.mediastart / 2002)  # Originally cinpoint already divided by MediaFrameRate
                                                                                    coutpoint = round(objects.mediaend / 2002) - 1
                                                                                    if clip_speed > 0:
                                                                                        clip_timecode_in = round((clip_timecode_in / cframerate / 2002)) + cinpoint - 1  # Seems to be linked to Project's VideoSetting's FrameRate, Why???
                                                                                        clip_timecode_out = round((clip_timecode_out - 1) / cframerate / 2002) + cinpoint - 1
                                                                                    if clip_speed < 0:
                                                                                        clip_timecode_in = coutpoint - round((clip_timecode_in / cframerate / 2002))  # Seems to be linked to Project's VideoSetting's FrameRate, Why???
                                                                                        clip_timecode_out = coutpoint - round((clip_timecode_out - 1) / cframerate / 2002) + 1


                                                            except:
                                                                pass

                                    # Add Attributes to Sequence in ProjectMediaList
                                    for objects in projectMediaList:
                                        if type(objects) is Sequence:
                                            if objects.id == sequence_id:
                                                objects.timeline.append(ClipInTimeline(masterclip_ref, 'audio', ('A' + str(track_id)), start, end, clip_timecode_in, clip_timecode_out, clip_speed, mute))
                                                objects.timeline[-1].isaudio(level, balance)

        n += 1
    xml = ET.tostring(root, encoding='UTF-8')
    return xml


def get_media_list(xml):
    print('Getting File Structure')

    root = ET.fromstring(xml)
    nbin = 0
    media_list = []

    # Find ProjectItem list of Bins and its content's ObjectURefs)

    for bins in root.findall('.//ProjectItemContainer/..[@ObjectUID]'):
        try:
            bin_name = (bins.find('ProjectItem/Name')).text
            bin_id = bins.get('ObjectUID')
            matches = 0  # check for matchs in mediaList

            # if not duplicated
            for instance in media_list:
                if isinstance(instance, Bin):
                    if instance.id == bin_id:
                        matches += 1
            if matches == 0:
                media_list.append(Bin(bin_name, bin_id, None))
                bin_pos = len(media_list) - 1
        except:
            pass

        # Get ObjectURefs to later match with Masterclips' IDs
        for items in bins.findall('ProjectItemContainer/Items/Item'):
            itemID = items.get('ObjectURef')

            # If it's a Bin
            try:
                for all_bins in root.findall('./BinProjectItem'):
                    bin_id2 = all_bins.get('ObjectUID')
                    if bin_id2 == itemID:
                        bin_name2 = all_bins.find('ProjectItem/Name').text
                        print('')
                        print('Bin', bin_name2, 'inside Bin', bin_name)
                        nbin += 1
                        media_list.append(Bin(bin_name2, bin_id2, bin_id))
                        bin_pos = len(media_list) - 1
                        media_list[bin_pos].inbin = bin_id

            except:
                pass

            # Find Ref in ClipProjectItems' matching ObjectsIDs
            for clip_project_items in root.findall('.//MasterClip/..[@ObjectUID]'):
                clip_project_item_id = clip_project_items.get('ObjectUID')
                if clip_project_item_id == itemID:
                    masterclip_ref = clip_project_items.find('MasterClip').get('ObjectURef')
                    # print ('Match', masterIdRef)
                    for masterclips in root.findall('./MasterClip'):
                        masterclip_id = masterclips.get('ObjectUID')  # This is The global ID to link with project's bin
                        auvid_ref = (masterclips.find('Clips/Clip')).get('ObjectRef')
                        if masterclip_id == masterclip_ref:
                            if masterclips.find('LoggingInfo') is not None:
                                clip_logging_ref = masterclips.find('LoggingInfo').get('ObjectRef')

                                # Search for ClipLoggingInfo with matching ObjectRef
                                for clip_loggings in root.findall('ClipLoggingInfo'):
                                    clip_logging_id = clip_loggings.get('ObjectID')
                                    if clip_logging_id == clip_logging_ref:
                                        try:
                                            clip_frame_rate_factor = int(clip_loggings.find('MediaFrameRate').text)
                                        except:
                                            clip_frame_rate_factor = None
                                        try:
                                            clip_name = clip_loggings.find('ClipName').text
                                            if clip_name is None:
                                                clip_name = clip_loggings.find('Name').text
                                            print('')
                                            print('In Bin', bin_name, 'element named', clip_name, 'found')
                                        except:
                                            clip_name = 'Pending'
                                            print('')
                                            print('In Bin', bin_name, 'Non Clip Element found')

                                        try:
                                            tape_name = clip_loggings.find('TapeName').text
                                            print('TapeName:', tape_name)
                                        except:
                                            tape_name = 'Not Available'
                                            print('TapeName:', tape_name)
                                        try:
                                            media_framerate = int(clip_loggings.find('MediaFrameRate').text)
                                            media_framerate = round((10594584000 * 23.976) / media_framerate, 3)
                                            if media_framerate == 0.0:
                                                media_framerate = None
                                            print('Medias Original Frame Rate:', media_framerate)
                                        except:
                                            media_framerate = None
                                        try:
                                            media_inpoint = int(clip_loggings.find('MediaInPoint').text)
                                            media_framerate = int(clip_loggings.find('MediaFrameRate').text)
                                            media_inpoint = round((media_inpoint / media_framerate))
                                            print('Media Start position:', media_inpoint)
                                        except:
                                            media_inpoint = 0
                                        try:
                                            media_outpoint = int(clip_loggings.find('MediaOutPoint').text)
                                            media_framerate = int(clip_loggings.find('MediaFrameRate').text)
                                            media_outpoint = round((media_outpoint / media_framerate))
                                            print('Media End position:', media_outpoint)
                                        except:
                                            media_outpoint = 0

                                        # Find AudioClip and VideoClip link with MasterClip
                                        for auvid_ids in root.findall('.//Clip/..[@ObjectID]'):
                                            try:
                                                auvidMediaSourceRef = auvid_ids.find('Clip/Source').get('ObjectRef')
                                                auvid_id = auvid_ids.get('ObjectID')
                                                if auvid_id == auvid_ref:
                                                    class_id = auvid_ids.get('ClassID')
                                                    if class_id == '9308dbef-2440-4acb-9ab2-953b9a4e82ec':
                                                        class_id = 'Video'
                                                    if class_id == 'b8830d03-de02-41ee-84ec-fe566dc70cd9':
                                                        class_id = 'Audio'

                                                    # If it's Media
                                                    try:
                                                        for media_sources in root.findall('.//MediaSource/..[@ObjectID]'):
                                                            media_source = media_sources.get('ObjectID')
                                                            if media_source == auvidMediaSourceRef:  # A clip is found

                                                                # Create Instance of Clip
                                                                media_list.append(MasterClip())
                                                                media_list[(len(media_list) - 1)].id = masterclip_id  # Id linking Bins and its instances in Sequences
                                                                media_list[(len(media_list) - 1)].name = clip_name
                                                                media_list[(len(media_list) - 1)].type = class_id
                                                                media_list[(len(media_list) - 1)].tapename = tape_name
                                                                media_list[(len(media_list) - 1)].framerate = media_framerate
                                                                media_list[(len(media_list) - 1)].frameratefactor = clip_frame_rate_factor
                                                                media_list[(len(media_list) - 1)].mediastart = media_inpoint  # Media's start timecode
                                                                media_list[(len(media_list) - 1)].mediaend = media_outpoint
                                                                media_list[(len(media_list) - 1)].inbin = bin_id
                                                                media_list[bin_pos].ingest(masterclip_id)

                                                                if media_sources.find('MediaSource/Media').get('ObjectURef') is not None:
                                                                    media_source_ref = media_sources.find('MediaSource/Media').get('ObjectURef')
                                                                    for medias in root.findall('.//Media'):
                                                                        media_id = medias.get('ObjectUID')
                                                                        if media_id == media_source_ref:
                                                                            file_path = medias.find('FilePath').text
                                                                            media_list[(len(media_list) - 1)].filepath = file_path
                                                                            try:  # Internal Premiere's clips have non-valid a numeric reference for file path
                                                                                file_path = int(file_path)
                                                                                file_path = 'Not Available'
                                                                                media_list[(len(media_list) - 1)].filepath = file_path
                                                                            except:
                                                                                print('Its file path is ', file_path)
                                                                                online = exists(file_path)
                                                                                media_list[(len(media_list) - 1)].online = online
                                                    except:
                                                        pass

                                                    # If Sequence
                                                    try:
                                                        for sequence_ids in root.findall('.//SequenceSource/..[@ObjectID]'):
                                                            sequence_source_id = sequence_ids.get('ObjectID')
                                                            if sequence_source_id == auvidMediaSourceRef:
                                                                sequence_ref = sequence_ids.find('SequenceSource/Sequence').get('ObjectURef')  # Link w/ Sequences Id

                                                                for sequences in root.findall('./Sequence'):
                                                                    sequence_id = sequences.get('ObjectUID')
                                                                    clip_name = sequences.find('Name').text
                                                                    print('Sequence Name', clip_name)
                                                                    if sequence_id == sequence_ref:
                                                                        seq_height = int(sequences.find('Node/Properties/MZ.Sequence.PreviewFrameSizeHeight').text)
                                                                        seq_width = int(sequences.find('Node/Properties/MZ.Sequence.PreviewFrameSizeWidth').text)
                                                                        print('Sequence is', seq_width, 'x', seq_height)

                                                                        # Now FrameRates
                                                                        for trackgroups_refs in sequences.findall('TrackGroups/TrackGroup/Second/.[@ObjectRef]'):
                                                                            trackgroup_ref = trackgroups_refs.get('ObjectRef')  # Referred to VideoTrackGroups' ID

                                                                            for video_track_group in root.findall('.//VideoTrackGroup'):
                                                                                if trackgroup_ref == video_track_group.get('ObjectID'):
                                                                                    # Frame Rate del Video TrackGroup
                                                                                    seq_vid_frame_rate = int(video_track_group.find('TrackGroup/FrameRate').text)
                                                                                    seq_vid_frame_rate = round((10594584000 * 23.976) / seq_vid_frame_rate, 3)
                                                                                    print('Video FrameRate:', seq_vid_frame_rate, 'fps')

                                                                            for audio_track_group in root.findall('.//AudioTrackGroup'):
                                                                                if trackgroup_ref == audio_track_group.get('ObjectID'):
                                                                                    # AudioTrackGroup's FrameRate
                                                                                    seq_aud_frame_rate = audio_track_group.find('TrackGroup/FrameRate').text
                                                                                    seq_aud_frame_rate = int(seq_aud_frame_rate)
                                                                                    seq_aud_frame_rate = round((5292000 * 48000) / seq_aud_frame_rate)
                                                                                    print('Audio FrameRate:', seq_aud_frame_rate, 'kHz')

                                                                        # Create Instance of Sequence
                                                                        media_list.append(Sequence())
                                                                        media_list[(len(media_list) - 1)].id = sequence_id
                                                                        media_list[(len(media_list) - 1)].name = clip_name
                                                                        media_list[(len(media_list) - 1)].height = seq_height
                                                                        media_list[(len(media_list) - 1)].width = seq_width
                                                                        media_list[(len(media_list) - 1)].vidframerate = seq_vid_frame_rate
                                                                        media_list[(len(media_list) - 1)].audframerate = seq_aud_frame_rate
                                                                        media_list[(len(media_list) - 1)].inbin = bin_id
                                                                        media_list[bin_pos].ingest(sequence_id)
                                                    except:
                                                        pass

                                            except:
                                                pass
    nbin += 1
    return media_list


def timecoder(frames, timebase):
    if timebase < 1000:
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


def keyframer(string, frame_rate_factor):  # Returns Keyframe Value + Time Value
    keyframes = string.split(';')
    n = 0
    for keyframe in keyframes:
        try:
            kf = keyframe.split(',')
            kf_time = round(int(kf[0]) / frame_rate_factor)
            # print('KeyF Time', kf_time)
            try:
                keyframes[n] = kf[1].split(':')
                if keyframes[n][0][-1] == '.':
                    keyframes[n][0] = keyframes[n][0].rstrip(keyframes[n][0][-1])
                    keyframes[n][0] = int(keyframes[n][0])
                try:
                    if keyframes[n][1][-1] == '.':
                        keyframes[n][1] = keyframes[n][1].rstrip(keyframes[n][1][-1])
                        keyframes[n][1] = int(keyframes[n][1])
                except:
                    pass
            except:
                if kf[1][-1] == '.':
                    kf[1] = kf[1].rstrip(kf[1][-1])
                keyframes[n] = int(kf[1])
                print('Only One Value for Keyframe')
            keyframes[n].append(kf_time)
            # print(keyframes[n])
        except:
            del keyframes[n]  # Deletes non valid keyframes
        n += 1
    print(len(keyframes), 'keyframes')
    return keyframes


print('PRPROJ READER')
projectXml = open_proj('test.prproj')  # Your Project File Here
projectMediaList = get_media_list(projectXml)
projectSequences = open_sequence(projectXml)
save_proj(projectSequences, 'proyectonuevo.prproj')
