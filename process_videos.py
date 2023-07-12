import os
import cv2
import moviepy.editor as mp
import wave
import numpy as np
import pandas as pd
import csv
import glob
import shutil
from pydub import AudioSegment
import subprocess
import whisper
model = whisper.load_model("base")


dir_path=os.getcwd()
ISL_path=os.path.join(dir_path,"ISLRTC_DATA")
input_path=os.path.join(ISL_path,"input")
output_path=os.path.join(ISL_path,"output")
inputaud_path=os.path.join(ISL_path,"AudioIN")

if not os.path.exists(input_path):
    os.mkdir(input_path)
if not os.path.exists(output_path):
    os.mkdir(output_path)

if not os.path.exists(inputaud_path):
    os.mkdir(inputaud_path)



for filename in os.listdir(input_path):
    try:    
        f = os.path.join(input_path, filename)
        vid_path=os.path.join(output_path,filename.replace(".mp4",""))

        if not os.path.exists(vid_path):
            os.mkdir(vid_path)
        audio_path=os.path.join(vid_path,"audio.wav")

        

        out_path=vid_path
        #frames_path=os.path.join(out_path,"Frames")
        #f=os.path.join(input_path, filename)
        myaudio=os.path.join(inputaud_path,filename.replace(".mp4",".wav"))


        my_clip=mp.VideoFileClip(f)
        rate=my_clip.fps

        wav_obj=wave.open(myaudio,'rb')

        sample_freq = wav_obj.getframerate()
        n_samples = wav_obj.getnframes()
        t_audio = n_samples/sample_freq
        n_channels = wav_obj.getnchannels()
        signal_wave = wav_obj.readframes(n_samples)


        signal_array = np.frombuffer(signal_wave, dtype=np.int16)

        l_channel = signal_array[0::2]
        r_channel = signal_array[1::2]
        times = np.linspace(0, n_samples/sample_freq, num=n_samples)




        times = times[::4410]
        l_channel = l_channel[::4410]

        data = {'Time': times, 'L_channel': l_channel}

        df = pd.DataFrame(data)
        df.to_csv(os.path.join(out_path,'l_channel.csv'),  index=False)

        cut = []

        l = len(l_channel)
        i = 0

        while i<l-1:
            if l_channel[i] == 0 and l_channel[i+1] != 0:
                cut.append(times[i])
            i = i+1

        cut.insert(0,0.0)
        cut.append(t_audio)

        i = len(cut)-1

        while i>0:
            if cut[i] - cut[i-1] < 2.5:
                cut.pop(i-1)
            i = i-1


        i = 0
        l = len(cut)

        #frames = []
        times = []

        while i<l-1:
            times.append([(cut[i]),(cut[i+1])])
            i = i +1

        i = 0

        
        timestamps_path=os.path.join(out_path,"time_stamps.csv")
        with open(timestamps_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(times)

        wav_obj.close()

        #df=pd.read_csv(framestamps_path,header=None)
        df=pd.read_csv(timestamps_path,header=None)

        l=df.shape[0]
        j=0

        newpath=os.path.join(out_path,"clipped_videos")

        if not os.path.exists(newpath):
            os.mkdir(newpath)

        f = os.path.join(input_path, filename)
        myclip=mp.VideoFileClip(f)

    except:
        with open(os.path.join(output_path,"wasted_videos.csv"),mode='a',newline='') as file:
                csvwriter=csv.writer(file)
                csvwriter.writerow([filename.replace(".mp4","")])
        continue
            


    while j<l:

        try:
            x = round(df[0].iloc[j],2)
            y = round(df[1].iloc[j],2)
            sub_path=os.path.join(newpath,str(j)+".mp4")
            cmd = f"ffmpeg -i {f} -ss {x} -t {round(y-x,2)} -c copy {sub_path}" 

            #subclip=myclip.subclip(x,y)
            #subclip.write_videofile(os.path.join(newpath,str(j)+".mp4"))
            os.system(cmd)
            j=j+1
        
        except:
            with open(os.path.join(out_path,"errors.csv"),mode='a',newline='') as file:
                csvwriter=csv.writer(file)
                csvwriter.writerow([j,x,y,"video"])
            
            j=j+1
            
            continue
        

        



    df=pd.read_csv(timestamps_path,header=None)
    l=df.shape[0]
    j=0

    newpath=os.path.join(out_path,"clipped_audios")

    if not os.path.exists(newpath):
        os.makedirs(newpath)

    while j<l:
        x = round(df[0].iloc[j] * 1000)
        y = round(df[1].iloc[j] * 1000)


        try:
            newAudio = AudioSegment.from_wav(myaudio)
            newAudio = newAudio[x:y]
            newAudio.export(os.path.join(newpath,str(j)+'.wav'), format="wav")

            j=j+1
        except:
            x=round(df[0].iloc[j],2)
            y=round(df[1].iloc[j],2)

            with open(os.path.join(out_path,"errors.csv"),mode='a',newline='') as file:
                csvwriter=csv.writer(file)
                csvwriter.writerow([j,x,y,"audio"])

            j=j+1
            
            continue

    j=0
    while j<l:
        try:
            x=round(df[0].iloc[j],2)
            y=round(df[1].iloc[j],2)
            subaudio_path=os.path.join(newpath,str(j)+'.wav')
            result=model.transcribe(subaudio_path,fp16=False)
            transcript=result['text']

        
            with open(os.path.join(out_path,"transcripts.csv"),mode='a',newline='') as file:
                csvwriter=csv.writer(file)
                csvwriter.writerow([j,x,y,transcript])

            j=j+1
        except:
            x=round(df[0].iloc[j],2)
            y=round(df[1].iloc[j],2)
            with open(os.path.join(out_path,"errors.csv"),mode='a',newline='') as file:
                csvwriter=csv.writer(file)
                csvwriter.writerow([j,x,y,"transcript"])

            j=j+1
        
            continue

       


    my_clip.reader.close()
    del my_clip.reader
    #os.remove(timestamps_path)
    #os.remove(framestamps_path)
    os.remove(os.path.join(out_path,"l_channel.csv"))
    os.remove(f)
    os.remove(myaudio)
    #shutil.rmtree(frames_path)
