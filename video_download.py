from pytube import YouTube
from pytube import Playlist
import os



ISL_path=os.path.join(os.getcwd(),"ISLRTC_DATA")
if os.path.exists(ISL_path)==False:
    os.mkdir(ISL_path)
playlist_path=os.path.join(ISL_path,"Playlist4")
if os.path.exists(playlist_path)==False:
    os.mkdir(playlist_path)
print("RUNNING")
def give_title(yt):
    '''given a Youtube object returns the title in right format'''
    
    title = yt.title.replace("|", "")
    return title
def give_paths(playlist_path,i):
    '''return paths of temp video, temp audio and subclip folder in the video directory in the playlist directory'''
    
    vid_path=os.path.join(playlist_path,"video"+str(i))
    temp_path=os.path.join(vid_path,"temp")
    tempvid_path=os.path.join(vid_path,"video")
    subclip_path=os.path.join(vid_path,"Subclips")
    
    return vid_path,temp_path,tempvid_path,subclip_path

def create_directories(vid_path,temp_path,tempvid_path,subclip_path):
    ''' Creating the directories'''

    if os.path.exists(vid_path)!=True:
        os.mkdir(vid_path)
    if os.path.exists(temp_path)!=True:
        os.mkdir(temp_path)
    if os.path.exists(tempvid_path)!=True:
        os.mkdir(tempvid_path)
    if os.path.exists(subclip_path)!=True:
        os.mkdir(subclip_path)

def get_audio_webm(video):
    '''Given a Youtube object return audio in .webm format'''

    audio_streams = video.streams.filter(only_audio=True,file_extension="webm").order_by("abr").desc()
    
    audio_streams = video.streams.filter(only_audio=True, file_extension="webm").order_by("abr").desc()
    for t in audio_streams:
        if(t.abr=="160kbps"):
            audio=t
            break
    return audio

def get_720p_video(yt):
    '''given an object of the class Youtube, return the video with 720p in mp3 format'''

    video_streams = yt.streams.filter(only_video=True, file_extension="mp4", progressive=False).order_by('resolution').desc()
    for t in video_streams:
        if(t.resolution == "720p"):
            video = t
            break

    return video


playlist_url="https://www.youtube.com/playlist?list=PLFjydPMg4DaoJzTOrougHhfZIXWy907xw"
playlist = Playlist(playlist_url)

print_progress=True

unable_to_download=[]
unable_to_convert=[]
unable_to_get_stamps=[]
unable_to_clip=[]

for i,link in enumerate(playlist):
    
    
    '''Setting paths and link for the yt video'''
    Data_path,temp_path,tempvid_path,subclip_path=give_paths(playlist_path,i)
    create_directories(Data_path,temp_path,tempvid_path,subclip_path)
    yt=YouTube(link)
    #file_name=give_title(yt)
    #print(file_name)

    try:                                                                 
        
        video=get_720p_video(yt)
        video.download(tempvid_path)
        audio=get_audio_webm(yt)
        audio.download(temp_path)
        audio_path=os.path.join(temp_path,os.listdir(temp_path)[0])
        video_path=os.path.join(tempvid_path,os.listdir(tempvid_path)[0])
        
        if print_progress==True:
            print("Download Succesful for video "+str(i)+" \nDownload Succesful for audio "+str(i))
        
    except Exception as e:
        #print("Failed to download %s. Reason: %s"%(file_name,e))
        #unable_to_download.append((i,file_name))
        continue
