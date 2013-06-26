#!/usr/bin/env python
import yaml
import argparse
import gdata.youtube
import gdata.youtube.service
import os
import subprocess

directoryBase = '/home/lotso/Desktop/Ben/'
def createYouJoVideo(directoryBase,filename, soundExt, imageExt):
    '''create a video from an image and a sound'''
    output='/tmp/video.mp4'
    soundPath = os.path.join(directoryBase, 'sound',filename+soundExt)
    imagePath = os.path.join(directoryBase, 'cover',filename+imageExt)
#    SCALE = "scale='max(sar,1)*iw':'max(1/sar,1)*ih'"
    args = ['avconv', '-y', '-i', soundPath, '-f', 'image2', '-loop', '1', '-r', '1', '-vf', 'scale=720:-1', '-i', imagePath, '-shortest', '-acodec', 'aac', '-strict', 'experimental', '-vcodec', 'libx264', '-crf', '23', '-preset', 'veryfast', output]
    proc = subprocess.Popen(args, shell=False) 
    outp, errors =  proc.communicate()
    if proc.returncode:
        raise Exception(errors)
    else:
        args2 = ['mv', output, os.path.join(directoryBase, 'toUpload', filename+'.mp4')]
        args3 = ['mv', soundPath, os.path.join(directoryBase, 'done')]
        args4 = ['mv', imagePath, os.path.join(directoryBase, 'done')]
        proc2= subprocess.Popen(args2, shell=False)
        proc3= subprocess.Popen(args3, shell=False)
        proc4= subprocess.Popen(args4, shell=False)


def uploadYouJoVideo(directoryBase, filename, uploadConfig):
    '''uploads a video to youtube, config.yaml holds the necessary config files'''
    # A complete client login request
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.email = uploadConfig['upload_config']['email']
    yt_service.password = uploadConfig['upload_config']['password'] 
    yt_service.source = uploadConfig['upload_config']['source']
    yt_service.developer_key = uploadConfig['upload_config']['developer_key']
    yt_service.client_id = uploadConfig['upload_config']['client_id']
    yt_service.ProgrammaticLogin()

    # prepare a media group object to hold our video's meta-data
    my_media_group = gdata.media.Group(\
            title=gdata.media.Title(text= filename),\
            description=gdata.media.Description(description_type='plain',text='No description'),\
            category=gdata.media.Category(text='Music',scheme='http://gdata.youtube.com/schemas/2007/categories.cat',label='Music'),\
            keywords=gdata.media.Keywords(text='reggae'),\
            player=None)
    # create the gdata.youtube.YouTubeVideoEntry to be uploaded
    video_entry = gdata.youtube.YouTubeVideoEntry(media=my_media_group)
    # set the path for the video file binary
    videoPath = os.path.join(directoryBase, 'toUpload', filename +'.mp4')
    print videoPath
    new_entry = yt_service.InsertVideoEntry(video_entry, videoPath)
    upload_status = yt_service.CheckUploadStatus(new_entry)
    print upload_status

def createTree(directoryBase):
    '''returns a dictionary of names / extensions of files to be transformed in a vider
    by browsing the sound/ directory and check if there are identical names in the
    cover/ directory'''
    treeList=[]
    for filesound in os.walk(os.path.join(directoryBase,'sound')):
#        print '---files----'
        print filesound[2]
        for i in filesound[2]:
            tmpfileS , tmpextS = os.path.splitext(i)
            tmp = {'name' : tmpfileS, 'soundext': tmpextS, 'imageext':None} 
            for fileimage in os.walk(os.path.join(directoryBase,'cover')):
#                print '---image--'
                if len(fileimage[2]) > 0:
                    for j in fileimage[2]:
                        tmpfileI, tmpextI = os.path.splitext(j)
                        if tmpfileI == tmpfileS:
                            tmp['imageext'] = tmpextI
                        else:
                            print 'NO IMAGE'
                        treeList.append(tmp)
                else:
                    print '>>> No image in folder /cover for ' + tmpfileS + tmpextS + ' <<<'
#                print treeList
    return treeList

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='mux sound and images files into a video and upload to youTube')
    parser.add_argument('-u', '--upload', help='upload to youTube', action='store_true')
    args = parser.parse_args()
    print args
    f = open(os.path.join(directoryBase,'config.yaml'))
    dataMap = yaml.safe_load(f)
    f.close()
    print dataMap
    toEncode = createTree(directoryBase)
    for items in toEncode:
        print items
        if items['imageext'] != None:
            createYouJoVideo(directoryBase,items['name'],items['soundext'],items['imageext'])
            videoToUpload = os.path.join(directoryBase, 'toUpload', items['name']+'mp4')
            print items['name']
            if args.upload :
                uploadYouJoVideo(directoryBase, items['name'], dataMap)

    
