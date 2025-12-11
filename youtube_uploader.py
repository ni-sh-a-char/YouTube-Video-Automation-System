"""
YouTube Uploader - Automatically uploads videos to YouTube with metadata
Requires YouTube API setup (free tier available)
"""

import os
import json
import pickle
from typing import Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import mimetypes

class YouTubeUploader:
    """Upload videos to YouTube with full automation"""
    
    # YouTube API scopes
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.pickle'):
        """
        Initialize YouTube uploader
        
        credentials_file: OAuth 2.0 credentials from Google Cloud Console
        token_file: Cached token after first authentication
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.youtube = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with YouTube API using environment variables"""
        
        creds = None
        
        # Check if we have a cached token
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                print(f"⚠️ Could not load cached token: {e}")

        # If no valid credentials, create from environment variables
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"⚠️ Token refresh failed: {e}")
                    creds = None

            if not creds:
                # Load from environment variables
                client_id = os.getenv('YOUTUBE_CLIENT_ID')
                client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
                refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
                
                if client_id and client_secret and refresh_token:
                    print("🔄 Authenticating via Environment Variables...")
                    creds = Credentials(
                        token=None,
                        refresh_token=refresh_token,
                        token_uri="https://oauth2.googleapis.com/token",
                        client_id=client_id,
                        client_secret=client_secret,
                        scopes=self.SCOPES
                    )
                else:
                    # Fallback to file-based auth (legacy support or local dev without env vars)
                    if os.path.exists(self.credentials_file):
                         print("⚠️ Environment variables missing, falling back to file-based auth...")
                         flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, self.SCOPES)
                         creds = flow.run_local_server(port=0)
                    else:
                        print("❌ YouTube Authentication Failed: No environment variables or credentials file found.")
                        print("   Required ENV vars: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN")
                        return

            # Save token for next time
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"⚠️ Could not save token cache: {e}")
        
        self.youtube = build('youtube', 'v3', credentials=creds)
        print("✅ YouTube authentication successful")
    
    def upload_video(self,
                     video_path: str,
                     title: str,
                     description: str,
                     tags: list,
                     category_id: str = '28',  # Science & Tech category
                     is_public: bool = False,
                     is_premiere: bool = False) -> Optional[str]:
        """
        Upload video to YouTube
        
        Args:
            video_path: Path to the video file
            title: Video title (max 100 chars)
            description: Video description
            tags: List of tags
            category_id: YouTube category ID (28=Science & Tech)
            is_public: True=public, False=unlisted
            is_premiere: True=schedule as premiere
            
        Returns:
            Video ID if successful
        """
        
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return None
        
        if not self.youtube:
            print("❌ Not authenticated with YouTube")
            return None
        
        try:
            print(f"🚀 Uploading: {title}")
            
            # Prepare metadata
            body = {
                'snippet': {
                    'title': title[:100],
                    'description': description,
                    'tags': tags[:30],  # Max 30 tags
                    'categoryId': category_id,
                    'defaultLanguage': 'en',
                    'defaultAudioLanguage': 'en'
                },
                'status': {
                    'privacyStatus': 'public' if is_public else 'unlisted',
                    'madeForKids': False,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Add premiere scheduling if enabled
            if is_premiere:
                from datetime import datetime, timedelta
                premiere_time = datetime.utcnow() + timedelta(hours=24)
                body['liveDetails'] = {
                    'scheduledStartTime': premiere_time.isoformat() + 'Z'
                }
            
            # Prepare media upload
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True,
                chunksize=1024*1024  # 1MB chunks
            )
            
            # Create insert request
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media,
                notifySubscribers=True
            )
            
            # Execute with progress
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"   Upload progress: {progress}%")
            
            video_id = response['id']
            print(f"✅ Video uploaded successfully!")
            print(f"   Video ID: {video_id}")
            print(f"   URL: https://www.youtube.com/watch?v={video_id}")
            
            return video_id
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return None
    
    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Set custom thumbnail for video"""
        
        if not os.path.exists(thumbnail_path):
            print(f"❌ Thumbnail not found: {thumbnail_path}")
            return False
        
        try:
            media = MediaFileUpload(
                thumbnail_path,
                mimetype='image/jpeg',
                resumable=True
            )
            
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            )
            
            response = request.execute()
            print(f"✅ Thumbnail set for {video_id}")
            return True
            
        except Exception as e:
            print(f"❌ Thumbnail upload failed: {e}")
            return False
    
    def add_to_playlist(self, video_id: str, playlist_id: str) -> bool:
        """Add uploaded video to a playlist"""
        
        try:
            request = self.youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            )
            
            response = request.execute()
            print(f"✅ Video added to playlist {playlist_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add to playlist: {e}")
            return False
    
    def get_playlists(self) -> list:
        """Get all playlists for the authenticated channel"""
        
        try:
            request = self.youtube.playlists().list(
                part='snippet',
                mine=True,
                maxResults=50
            )
            
            playlists = []
            while request:
                response = request.execute()
                playlists.extend(response.get('items', []))
                request = self.youtube.playlists().list_next(request, response)
            
            return playlists
            
        except Exception as e:
            print(f"❌ Failed to get playlists: {e}")
            return []
    
    def update_video_metadata(self,
                             video_id: str,
                             title: Optional[str] = None,
                             description: Optional[str] = None,
                             tags: Optional[list] = None) -> bool:
        """Update video metadata after upload"""
        
        try:
            # Get current metadata
            request = self.youtube.videos().list(
                part='snippet',
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                print(f"❌ Video not found: {video_id}")
                return False
            
            snippet = response['items'][0]['snippet']
            
            # Update fields
            if title:
                snippet['title'] = title[:100]
            if description:
                snippet['description'] = description
            if tags:
                snippet['tags'] = tags[:30]
            
            # Send update
            update_request = self.youtube.videos().update(
                part='snippet',
                body={'id': video_id, 'snippet': snippet}
            )
            
            update_request.execute()
            print(f"✅ Video metadata updated: {video_id}")
            return True
            
        except Exception as e:
            print(f"❌ Update failed: {e}")
            return False


class YouTubeAnalytics:
    """Get video analytics and performance metrics"""
    
    def __init__(self, youtube_service):
        self.youtube = youtube_service
    
    def get_video_stats(self, video_id: str) -> Dict:
        """Get basic stats for a video"""
        
        try:
            request = self.youtube.videos().list(
                part='statistics,snippet,contentDetails',
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                return {}
            
            item = response['items'][0]
            stats = item['statistics']
            
            return {
                'title': item['snippet']['title'],
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
                'duration': item['contentDetails']['duration'],
                'thumbnail': item['snippet']['thumbnails']['high']['url']
            }
            
        except Exception as e:
            print(f"❌ Failed to get stats: {e}")
            return {}


if __name__ == "__main__":
    # Example usage
    uploader = YouTubeUploader()
    
    # Example video metadata
    metadata = {
        'title': 'The Top 10 Python Mistakes That Cost Companies Millions',
        'description': '''Learn the most critical Python mistakes that developers make daily.
This video covers real-world examples and how to avoid costly errors.

⏲️ Timestamps:
0:00 - Intro
0:30 - Mistake #1
...

👨‍💻 Topics Covered:
- Memory leaks
- Type errors
- Performance issues
- Security vulnerabilities

📚 Resources:
- GitHub: [link]
- Documentation: [link]

Thanks for watching! Don't forget to like and subscribe!
''',
        'tags': ['python', 'programming', 'mistakes', 'tutorial', 'coding', 'beginners', 'tech'],
    }
    
    # Upload video (uncomment when ready)
    # video_id = uploader.upload_video(
    #     video_path='video/final_video_with_subs.mp4',
    #     **metadata
    # )
