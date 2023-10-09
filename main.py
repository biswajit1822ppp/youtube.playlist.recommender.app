from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from googleapiclient.discovery import build
from pydantic import BaseModel

api_key = 'AIzaSyBuzXtmvgUzIyH05dKi77wUyzIw6QDyGKc'

class Query(BaseModel):
    query: str

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_most_popular_playlist(api_key, query, max_results=5, sort_by='viewCount'):
    # Build the YouTube Data API client
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Search for playlists based on the query
    search_response = youtube.search().list(
        part='snippet',
        q=query,
        type='playlist',
        maxResults=max_results
    ).execute()

    playlist_info = []
    if 'items' in search_response:
        for item in search_response['items']:
            playlist_id = item['id']['playlistId']

            # Get playlist item details to count the number of videos in the playlist
            playlist_item_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50  # Assuming a maximum of 50 videos in the playlist (can be adjusted as needed)
            ).execute()

            # Count the number of videos in the playlist
            playlist_item_count = len(playlist_item_response['items'])

            # Check if the playlist has at least 50 videos
            if playlist_item_count >= 10:
                channel_name = item['snippet']['channelTitle']

                # Fetch video statistics for each video in the playlist
                video_ids = [video['snippet']['resourceId']['videoId'] for video in playlist_item_response['items']]
                videos_response = youtube.videos().list(
                    part='statistics',
                    id=','.join(video_ids)
                ).execute()

                # Calculate the total view count for all videos in the playlist
                total_view_count = 0
                for video in videos_response['items']:
                    total_view_count += int(video['statistics']['viewCount'])

                playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                playlist_info.append((channel_name, playlist_url, total_view_count))

    # Sort the playlist_info based on the maximum number of subscribers
    if sort_by == 'subscriberCount':
        playlist_info.sort(key=lambda x: get_channel_subscriber_count(api_key, x[0]), reverse=True)
    # Sort the playlist_info based on the total view count (default sorting)
    else:
        playlist_info.sort(key=lambda x: x[2], reverse=True)

    return playlist_info

@app.get('/', response_class=FileResponse)
async def index():
    return './index.html'

@app.post('/getPlaylist/')
async def getPlaylist(input: Query):
    print(input)
    if api_key == 'YOUR_API_KEY':
        print("Please replace 'YOUR_API_KEY' with your actual API key.")
    else:
        search_query = input.query
        playlist_list = get_most_popular_playlist(api_key, search_query)
        response = []

        if playlist_list:
            for i, (channel_name, playlist_url, total_view_count) in enumerate(playlist_list):
                response.append({
                    'channel_name': channel_name,
                    'playlist_url': playlist_url,
                    'total_view_count': total_view_count
                })
        else:
            return {"error": "No playlist found"}
        
        return response

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=3000)