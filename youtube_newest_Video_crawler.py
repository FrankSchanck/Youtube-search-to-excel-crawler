# -*- coding: utf-8 -*-

import os
import sys
import pandas
import json
from youtubesearchpython import *
import time

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from googleapiclient.discovery import build

def list_newest_videos(searchName, pages):
    # First Page
    custom_search = CustomSearch(searchName, VideoSortOrder.uploadDate, limit = 30)
    result_cache = custom_search.result() # returns dic
    print('Videos from page 1: ' +str(len(result_cache['result'])))

    video_count=len(result_cache['result'])
    # Iterate over the next x pages
    for page_number in range(pages-1):
        custom_search.next()
        videos_per_page = len(custom_search.result()['result'])
        video_count= video_count+videosPerPage
        print('Videos from page '+str(page_number+2)+ ': '+ str(videos_per_page))
        videos = custom_search.result()['result'] # List of all videos
        for video in videos:
            result_cache['result'].append(video)
    print("Total amount of videos found: "+ str(video_count))

    # Get video Informations and add to resultCache 
    videos = result_cache['result']
    for video in range(len(videos)):
        # Get video information
        info = Video.get(videos[video]['link'], mode = ResultMode.dict)
        print('Get Video Nr:' + str(video))
            
        channel = info['channel']
        videos[video]['channel'] = channel # returns a dict

        # Delete accessibility
        del videos[video]['accessibility']
        del videos[video]['shelfTitle']
        del videos[video]['type']

        keywords = info['keywords']
        videos[video]['keywords'] = keywords

        # Multiple streaming data available --> Remove because unnecessary?
        try:
            for formats in range(len(info['streamingData']['formats'])):
                quality = info['streamingData']['formats'][formats]['quality'] 
                videos[video]['quality-'+str(formats)] = quality

                streaming_data = info['streamingData']['formats'][formats]['audioQuality'] 
                videos[video]['audioQuality-'+str(formats)] = streaming_data 

                streaming_data = info['streamingData']['formats'][formats]['qualityLabel'] 
                videos[video]['qualityLabel-'+str(formats)] = streaming_data

                streaming_data = info['streamingData']['formats'][formats]['fps'] 
                videos[video]['fps-'+str(formats)] = streaming_data
        except KeyError:
            print("Keyerror: No streaming format available for video "+str(video))
        except TypeError:
            print("Typerror: No streaming format available for video "+str(video))
            
    return videos


def connect_to_youtube():
    # Enter your API key from GCP
    api_key = "**********"
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)

    return youtube

def search_for_term(search_name, initial_search, next_page_token):
    youtube = connect_to_youtube()
    if( initial_search ):
        request = youtube.search().list(
                part="snippet",
                maxResults=50,
                q=search_name,
                type="video",
                order="date",
                # Trier Uni
                # location="49.7457817,6.6862555",
                # locationRadius="1000km",
                relevanceLanguage="en",
                regionCode="DE",
                videoCategoryId=27
        )
    else:
        request = youtube.search().list(
            part="snippet",
            maxResults=50,
            q=search_name,
            type="video",
            order="date",
            pageToken= next_page_token,
            # location="49.7457817,6.6862555",
            # locationRadius="1000km",
            relevanceLanguage="en",
            regionCode="DE",
            videoCategoryId=27
        )
    response = None
    try:
        response = request.execute()
    except:
        global quota_not_exceeded 
        quota_not_exceeded = False
        print( "The request cannot be completed because you have exceeded your quota ")
    return response  

def list_videos(search_result):
    videos= [dict() for x in range(len(search_result['items']))]
    #   [ "1": {"videoID": "bbkjh", " ": ""}, "2": { "videoId": }]
    print("\n length: "+ str(len(search_result['items'])))
    next_page_token = None
    try:
        next_page_token = search_result['nextPageToken']
    except KeyError:
        print( 'No more pages found')

    for video in range(len(search_result['items'])):
            videos[video]['id'] = search_result['items'][video]['id']['videoId']
            videos[video]['url'] = "https://www.youtube.com/watch?v="+ search_result['items'][video]['id']['videoId']
            videos[video]['Title'] = search_result['items'][video]['snippet']['title']
            videos[video]['channelTitle'] = search_result['items'][video]['snippet']['channelTitle']

    return videos, next_page_token

def list_video(id_name):
    youtube = connect_to_youtube()
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics,status",
        id=id_name,
    )
    response = None
    try:
        response = request.execute()
    except:
        global quota_not_exceeded 
        quota_not_exceeded = False
        print( "The request cannot be completed because you have exceeded your quota ")

    return response

def get_coment(video_id):
    youtube = connect_to_youtube()
    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id
    )
    try:
        response = request.execute()
        return response
    except e:
        print("Comments disabled")

def get_top_level_comment(comments):
    try:
        top_level_comment = comments['items'][0]['snippet']['topLevelComment']['snippet']['textDisplay']
    except KeyError:
        print("Keyerror: No comment on video "+ videoId) 
    except IndexError:
        print("Indexerror: No comment on video "+ videoId) 
    except TypeError:
        print("TypeError: No comment on video "+ videoId) 

    return top_level_comment
    
def get_video_info(videos, video, list_info, video_id , paramter1, paramter2):
    try:
        videos[video][paramter2] = list_info['items'][0][paramter1][paramter2]
    except KeyError:
        print("No " + paramter2 +" on video "+ video_id)

def add_videoinfo(videos):

    for video in range(len(videos)):
        try:
            video_id = videos[video]['id']
            list_info = list_video(video_id)
            # comments = getComment(videoId)

            get_video_info(videos, video, list_info, video_id, 'statistics', 'viewCount')
            get_video_info(videos, video, list_info, video_id, 'statistics', 'likeCount')
            get_video_info(videos, video, list_info, video_id, 'statistics', 'dislikeCount')
            get_video_info(videos, video, list_info, video_id, 'statistics', 'commentCount')
            get_video_info(videos, video, list_info, video_id, 'statistics', 'favoriteCount')

            get_video_info(videos, video, list_info, video_id, 'snippet', 'categoryId')
            get_video_info(videos, video, list_info, video_id, 'snippet', 'publishedAt')
            get_video_info(videos, video, list_info, video_id, 'snippet', 'defaultLanguage')
            get_video_info(videos, video, list_info, video_id, 'snippet', 'description')

            # get_video_info(videos, video, list_info, video_id, 'status', 'madeForKids')

        except KeyError:
            print("Keyerror: No id  "+ str(videos[video]))  

    return videos
        

def dict_to_csv(name, dicti):
    directory = 'results'
    if not os.path.exists(directory):
        os.makedirs(directory)

    named_tuple = time.localtime() # get struct_time
    time_string = time.strftime("_%m-%d-%Y_%H-%M-%S", named_tuple)

    # Convert to XLSX
    file_name = name+time_string+".xlsx"
    data_frame = pandas.DataFrame.from_dict(dicti)
    data_frame.to_excel(os.path.join(directory, file_name))


if __name__ == "__main__":
   
    # Prefill List with youtubesearchpython according uploadDate
    
        searchName = sys.argv[1]
        # Old version with youtubesearchpython
        if(False):
            newestVideoList = list_newest_videos(searchName, 1)
            completVideoList = add_videoinfo(newestVideoList)
            dictToCSV(searchName,completVideoList)
        
        # New Version with Youtube V3
        if(True):
            pages_to_crawl = 50
            videos= [dict() for x in range(pages_to_crawl*50)]

            nextPage = "InitialPage"
            initialCall = True
            videoCount = 0
            page_counter = 0
            quota_not_exceeded = True

            if ( quota_not_exceeded ):
                if ( nextPage != None ):
                    for page_nr in range(pages_to_crawl):
                        
                        if(page_nr>0):
                            initialCall = False
                        
                        search = search_for_term(searchName,initialCall, nextPage)
                        if( search != None ):
                            videoList, nextPage = list_videos(search)
                            print("nextPage "+str(page_nr)+" :"+str(nextPage)+"\n")
                            print("videolist "+str(page_nr)+" :"+str(videoList)+"\n")
                            
                            if(page_nr == 0):
                                for page_nr in range(0,len(videoList)):
                                    videos[page_nr]=videoList[page_nr]
                                videoCount = videoCount+len(videoList) 
                            else:
                                for page_nr in range(0,len(videoList)):
                                    videos[videoCount+page_nr]=videoList[page_nr] 
                                videoCount = videoCount+len(videoList) 
                            print("VideoCount "+str(videoCount))
                            page_counter += 1

                completVideoList = add_videoinfo(videos)
            dict_to_csv(searchName,completVideoList)
            print(str(page_counter) + "pages found with "+str(videoCount)+" videos")
            
    
    