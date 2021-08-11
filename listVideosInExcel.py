from youtubesearchpython import *
import json
import pandas
import time

# Depreceated without youtube api
def list_videos_in_excel(searchName, pages):
    # First Page
    customSearch = CustomSearch(searchName, VideoSortOrder.uploadDate, limit = 20)
    resultCache = customSearch.result() # returns dic
    print('Videos from page 1: ' +str(len(resultCache['result'])))

    videoCount=len(resultCache['result'])
    # Iterate over the next x pages
    for pageNumber in range(pages-1):
        time.sleep(1.0)
        customSearch.next()
        videosPerPage = len(customSearch.result()['result'])
        videoCount= videoCount+videosPerPage
        print('Videos from page '+str(pageNumber+2)+ ': '+ str(videosPerPage))
        videos = customSearch.result()['result'] # List of all videos
        for video in videos:
            resultCache['result'].append(video)
    print("Total amount of videos found: "+ str(videoCount))

    # Get video Informations and add to resultCache 
    videos = resultCache['result']
    for video in range(len(videos)):
        info = Video.get(videos[video]['link'], mode = ResultMode.dict)
        print('Get Video Nr:' + str(video))
        try:
            channel = info['channel']
            resultCache['result'][video]['channel'] = channel # returns a dict
        except TypeError:
            resultCache['result'][video]['channel'] = 'Not available'

        try:
            keywords = info['keywords']
            resultCache['result'][video]['keywords'] = keywords
        except TypeError:
            resultCache['result'][video]['keywords'] = 'Not available'

        try:
            streamingData = info['streamingData']
            resultCache['result'][video]['AllstreamingData'] = streamingData
        except TypeError:
            resultCache['result'][video]['AllstreamingData'] = 'Not available'
        

    # Save as json
    with open('customSearch.json', 'w') as outfile:
        json.dump(resultCache['result'], outfile)

    # Convert to XLSX
    pandas.read_json("customSearch.json").to_excel(str(searchName)+".xlsx")

try:
    list_videos_in_excel('Mathematics',20)
except TypeError:
    print('Error')


