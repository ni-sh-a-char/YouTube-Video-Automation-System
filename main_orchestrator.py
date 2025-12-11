"""
Main Orchestrator - Fully automated YouTube automation pipeline
Handles: Idea Generation → Script Writing → Video Creation → Upload

Uses credentials from:
- .env file (environment variables)
- credentials.json (YouTube OAuth tokens)
- client_secrets.json (Google OAuth config)
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("[!] python-dotenv not installed. Install with: pip install python-dotenv")

from ai.gen_ideas import ViralIdeaGenerator
from ai.gen_script import ScriptGenerator
from ai.gen_image import gen_image, gen_thumbnail
from ai.gen_voice import gen_voice
from ai.gen_subs import gen_subs
from seo_optimizer import SEOOptimizer
from thumbnail_generator import ThumbnailGenerator
from youtube_uploader import YouTubeUploader

# Configure logging
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutomationConfig:
    """Configuration for automation pipeline
    
    Loads credentials from:
    - .env file (main configuration)
    - credentials.json (YouTube OAuth tokens)
    - client_secrets.json (Google OAuth)
    - config.json (system configuration)
    """
    
    def __init__(self):
        self.config = self.get_default_config()
        self.env_vars = self.load_env_vars()
        self.update_config_from_env()
    
    def load_env_vars(self) -> Dict:
        """Load environment variables from .env file"""
        return {
            'groq_api_key': os.getenv('GROQ_API_KEY'),
            'groq_model': os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b'),
            'youtube_client_id': os.getenv('YOUTUBE_CLIENT_ID'),
            'youtube_client_secret': os.getenv('YOUTUBE_CLIENT_SECRET'),
            'youtube_refresh_token': os.getenv('YOUTUBE_REFRESH_TOKEN'),
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'pexels_api_key': os.getenv('PEXELS_API_KEY'),
            'pixabay_api_key': os.getenv('PIXABAY_API_KEY'),
            'video_resolution': os.getenv('VIDEO_RESOLUTION', '1920x1080'),
            'video_fps': int(os.getenv('VIDEO_FPS', '24')),
            'target_duration': int(os.getenv('TARGET_VIDEO_DURATION', '30')),
            'output_format': os.getenv('OUTPUT_FORMAT', 'longform'),
            'batch_size': int(os.getenv('BATCH_SIZE', '1')),
            'upload_schedule_hours': int(os.getenv('UPLOAD_SCHEDULE_HOURS', '12')),
            'local_timezone': os.getenv('LOCAL_TIMEZONE', 'UTC'),
            'dry_run': os.getenv('DRY_RUN', 'false').lower() == 'true',
            'cleanup_temp': os.getenv('CLEANUP_TEMP', 'true').lower() == 'true',
            'auto_upload': os.getenv('AUTO_UPLOAD', 'false').lower() == 'true',
            'youtube_privacy_status': os.getenv('YOUTUBE_PRIVACY_STATUS', 'private'),
        }
    
    def update_config_from_env(self):
        """Override default config with environment variables"""
        if self.env_vars.get('upload_schedule_hours'):
             self.config['upload_schedule'] = 'custom'
        
        # Override auto_upload from env
        self.config['auto_upload'] = self.env_vars['auto_upload']
        
        # Override privacy status
        if self.env_vars['youtube_privacy_status'].lower() == 'public':
            self.config['upload_as_public'] = True
    
    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'channel_name': 'TechAutomation',
            'upload_schedule': 'weekly',  # daily, weekly, custom
            'video_format': 'video',  # video or reel
            'audio_language': 'english',  # english, hindi, etc
            'subtitles': True,
            'auto_upload': False,  # Set to True once credentials configured
            'upload_as_public': False,  # Start as unlisted by default
            'generate_thumbnail': True,
            'enable_premiere': False,
            'ideal_upload_time': '18:00',  # UTC time
            'keywords_focus': ['python', 'javascript', 'ai', 'machine learning'],
            'video_duration_target': 480,  # 8 minutes
        }
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        logger.info(f"Configuration saved to {self.config_file}")


class YouTubeAutomationPipeline:
    """Main automation pipeline"""
    
    def __init__(self):
        """Initialize automation pipeline with credentials from .env"""
        
        self.config_handler = AutomationConfig()
        self.config = self.config_handler.config
        self.env_vars = self.config_handler.env_vars
        
        logger.info("="*80)
        logger.info("YOUTUBE AUTOMATION PIPELINE INITIALIZING")
        logger.info("="*80)
        logger.info(f"LLM Provider: {os.getenv('LLM_PROVIDER', 'groq')}")
        logger.info(f"Groq Model: {self.env_vars['groq_model']}")
        logger.info(f"Video Resolution: {self.env_vars['video_resolution']}")
        logger.info(f"Batch Size: {self.env_vars['batch_size']}")
        logger.info(f"Dry Run Mode: {self.env_vars['dry_run']}")
        logger.info("="*80)
        
        # Initialize components with environment variables
        self.idea_generator = ViralIdeaGenerator(groq_api_key=self.env_vars['groq_api_key'])
        self.script_generator = ScriptGenerator(api_key=self.env_vars['groq_api_key'])
        self.seo_optimizer = SEOOptimizer()
        self.thumbnail_generator = ThumbnailGenerator()
        self.youtube_uploader = None
        
        # Initialize YouTube uploader with environment variables
        self.youtube_uploader = YouTubeUploader()
        logger.info("[OK] YouTube uploader initialized (using env vars)")
        
        # Setup directories
        self.setup_directories()
        
        logger.info("✅ Automation pipeline initialized")
    
    def setup_directories(self):
        """Create necessary directories"""
        dirs = ['videos', 'scripts', 'thumbnails', 'logs', 'metadata']
        for dir_name in dirs:
            os.makedirs(dir_name, exist_ok=True)
    
    def generate_video_idea(self) -> Dict:
        """Step 1: Generate viral video idea"""
        logger.info("🔍 Step 1: Generating viral video idea...")
        
        ideas = self.idea_generator.generate_ideas(count=1)
        idea = ideas[0]
        
        logger.info(f"✅ Generated idea: {idea['title']}")
        logger.info(f"   Viral Score: {idea['viral_score']}/100")
        
        return idea
    
    def generate_script(self, idea: Dict) -> Dict:
        """Step 2: Generate video script from idea"""
        logger.info("📝 Step 2: Generating video script...")
        
        script = self.script_generator.generate_from_idea(idea)
        
        logger.info(f"✅ Generated script with {len(script['scene'])} scenes")
        
        return script
    
    def optimize_metadata(self, idea: Dict, script: Dict) -> Dict:
        """Step 3: Optimize title, description, tags"""
        logger.info("🎯 Step 3: Optimizing metadata for SEO...")
        
        # Extract full script text for analysis to avoid dumping raw JSON
        script_text = ""
        if isinstance(script, dict):
            if 'scenes' in script:
                # Handle both list and dict scene formats
                scenes = script['scenes']
                if isinstance(scenes, dict):
                    for scene in scenes.values():
                        script_text += scene.get('narration', '') + " "
                elif isinstance(scenes, list):
                    for scene in scenes:
                        script_text += scene.get('narration', '') + " "
            elif 'script' in script:
                script_text = script['script']
        
        if not script_text:
            script_text = idea.get('description', '')

        optimized = {
            'title': self.seo_optimizer.optimize_title(
                idea['title'],
                keyword=idea.get('keyword'),
                video_type='ranking'
            ),
            'description': self.seo_optimizer.generate_description(
                idea['title'],
                script_text,
                [idea.get('keyword', '')] + idea.get('seo_tags', [])
            ),
            'tags': self.seo_optimizer.generate_tags(
                idea['title'],
                [idea.get('keyword', '')] + idea.get('seo_tags', [])
            ),
            'seo_score': self.seo_optimizer.calculate_seo_score(
                idea['title'],
                self.seo_optimizer.generate_description(
                    idea['title'],
                    script_text,
                    [idea.get('keyword', '')] + idea.get('seo_tags', [])
                ),
                self.seo_optimizer.generate_tags(
                    idea['title'],
                    [idea.get('keyword', '')] + idea.get('seo_tags', [])
                )
            )
        }
        
        logger.info(f"✅ SEO Score: {optimized['seo_score']['total_score']}/100")
        
        return optimized
    
    def create_video(self, script: Dict) -> str:
        """Step 4: Create video from script"""
        logger.info("🎬 Step 4: Creating video (images + audio + subtitles)...")
        
        try:
            os.makedirs("images", exist_ok=True)
            os.makedirs("audio", exist_ok=True)
            os.makedirs("video", exist_ok=True)
            
            from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
            
            clips = []
            
            for scene_key, scene_data in script['scene'].items():
                scene_num = scene_key.split('-')[1]
                image_path = f"images/image_{scene_num}.png"
                audio_path = f"audio/voice_{scene_num}.wav"
                
                # Generate image
                if not os.path.exists(image_path):
                    logger.info(f"   Generating image {scene_num}...")
                    gen_image(scene_data['image-prompt'], image_path)
                
                # Generate audio
                if not os.path.exists(audio_path):
                    logger.info(f"   Generating audio {scene_num}...")
                    gen_voice(scene_data['narration'], audio_path)
                
                # Create clip
                audio_clip = AudioFileClip(audio_path)
                image_clip = ImageClip(image_path, duration=audio_clip.duration)
                image_clip = image_clip.with_audio(audio_clip)
                clips.append(image_clip)
            
            # Concatenate clips
            logger.info("   Concatenating clips...")
            final_clip = concatenate_videoclips(clips)
            
            # Write video
            # Write final video
            logger.info("   Writing video file...")
            video_path = "video/final_video.mp4"
            final_clip.write_videofile(video_path, fps=24, codec="libx264",
                                     audio_codec="aac", threads=4,
                                     logger="bar")
            
            # Cleanup clips
            final_clip.close()
            for clip in clips:
                clip.close()
                
            logger.info(f"✅ Video created successfully: {video_path}")
            
            # Add subtitles if enabled
            if self.config.get('subtitles'):
                logger.info("   Adding subtitles...")
                gen_subs(output_srt_path='subtitles.srt',
                        input_video_path=video_path,
                        output_video_path='video/final_video_with_subs.mp4',
                        video_format=self.config.get('video_format'))
                video_path = 'video/final_video_with_subs.mp4'
                logger.info(f"✅ Subtitles added: {video_path}")
            
            return video_path
            
        except Exception as e:
            logger.error(f"❌ Video creation failed: {e}")
            raise
    
    def generate_thumbnail(self, idea: Dict) -> str:
        """Step 5: Generate thumbnail"""
        logger.info("🖼️  Step 5: Generating thumbnail...")
        
        try:
            os.makedirs("thumbnails", exist_ok=True)
            thumbnail_path = f"thumbnails/{idea['keyword']}_thumb.jpg"
            
            # Use the new stunning thumbnail generator
            # Use title as text overlay, but keep it short if possible
            title = idea['title']
            # Limit text length for visual appeal if needed, but gen_thumbnail handles wrapping
            
            gen_thumbnail(prompt=title, image_path=thumbnail_path, text_overlay=title)
            
            if os.path.exists(thumbnail_path):
                logger.info(f"✅ Thumbnail generated: {thumbnail_path}")
                return thumbnail_path
            else:
                logger.warning("⚠️  Thumbnail file not found after generation.")
                return None
            
        except Exception as e:
            logger.error(f"⚠️  Thumbnail generation failed: {e}")
            return None
    
    def upload_to_youtube(self, video_path: str, metadata: Dict) -> Optional[str]:
        """Step 6: Upload video to YouTube"""
        logger.info("📤 Step 6: Uploading to YouTube...")
        
        if not self.youtube_uploader:
            logger.warning("⚠️  YouTube uploader not configured. Skipping upload.")
            logger.info("   To enable uploads, configure YouTube API credentials")
            return None
        
        if not self.config.get('auto_upload'):
            logger.info("   Auto-upload disabled. Video ready for manual review.")
            return None
        
        try:
            video_id = self.youtube_uploader.upload_video(
                video_path=video_path,
                title=metadata['title'],
                description=metadata['description'],
                tags=metadata['tags'],
                category_id='28',  # Science & Tech
                is_public=self.config.get('upload_as_public', False),
                is_premiere=self.config.get('enable_premiere', False)
            )
            
            if video_id:
                # Set thumbnail if available
                if os.path.exists("thumbnails/thumb.jpg"):
                    self.youtube_uploader.set_thumbnail(video_id, "thumbnails/thumb.jpg")
                
                logger.info(f"✅ Video uploaded! ID: {video_id}")
                return video_id
            
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
        
        return None
    
    def cleanup_temporary_files(self, keep_final_video: bool = False):
        """Step 7: Clean up temporary files to prevent storage bloat
        
        This is critical for GitHub Actions to avoid storage quota issues.
        Removes intermediate files while keeping metadata for records.
        
        Args:
            keep_final_video: If True, keep the final video file (default False for GitHub Actions)
        """
        logger.info("🧹 Step 7: Cleaning up temporary files...")
        
        try:
            cleanup_dirs = ['images', 'audio', 'video']
            
            if keep_final_video:
                # Move final video to safe location before cleanup
                if os.path.exists('video/final_video_with_subs.mp4'):
                    os.rename('video/final_video_with_subs.mp4', 'output/final_video_archived.mp4')
                elif os.path.exists('video/final_video.mp4'):
                    os.rename('video/final_video.mp4', 'output/final_video_archived.mp4')
            
            # Remove temporary directories
            import shutil
            for dir_name in cleanup_dirs:
                if os.path.exists(dir_name):
                    shutil.rmtree(dir_name)
                    logger.info(f"   ✓ Deleted {dir_name}/")
            
            # Clean up individual temp files
            temp_files = [
                'subtitles.srt',
                'temp.txt',
                '.tmp',
                '*.tmp'
            ]
            
            for pattern in temp_files:
                if '*' in pattern:
                    import glob
                    for file in glob.glob(pattern):
                        try:
                            os.remove(file)
                            logger.info(f"   ✓ Deleted {file}")
                        except:
                            pass
                elif os.path.exists(pattern):
                    os.remove(pattern)
                    logger.info(f"   ✓ Deleted {pattern}")
            
            logger.info("✅ Cleanup completed successfully")
            
            # Log storage status
            import shutil as shell
            total, used, free = shell.disk_usage("/")
            logger.info(f"   Storage status: {free / (1024**3):.2f} GB free")
            
        except Exception as e:
            logger.error(f"⚠️  Cleanup error: {e}")
            # Don't fail the entire pipeline due to cleanup errors
    
    def run_full_pipeline(self, manual_upload: bool = False) -> Dict:
        """
        Run complete pipeline from idea to upload
        
        Args:
            manual_upload: If True, save metadata for manual review before upload
        
        Returns:
            Pipeline result with all generated data
        """
        
        start_time = time.time()
        
        logger.info("\n" + "="*80)
        logger.info("🚀 STARTING FULL YOUTUBE AUTOMATION PIPELINE")
        logger.info("="*80)
        
        try:
            # Step 1: Generate idea
            idea = self.generate_video_idea()
            
            # Step 2: Generate script
            script = self.generate_script(idea)
            
            # Step 3: Optimize metadata
            metadata = self.optimize_metadata(idea, script)
            
            # Step 4: Create video
            video_path = self.create_video(script)
            
            # Step 5: Generate thumbnail
            thumbnail_path = self.generate_thumbnail(idea)
            
            # Step 6: Upload to YouTube (or save for manual review)
            video_id = None
            if not manual_upload:
                video_id = self.upload_to_youtube(video_path, metadata)
            else:
                logger.info("📋 Saving metadata for manual review...")
            
            # Save metadata
            metadata_file = f"metadata/{idea['keyword']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.save_metadata(idea, script, metadata, video_path, thumbnail_path, video_id, metadata_file)
            
            # Step 7: Cleanup temporary files (CRITICAL for GitHub Actions)
            # Auto-cleanup is enabled by default to prevent storage bloat
            if self.env_vars.get('cleanup_temp', True):
                self.cleanup_temporary_files(keep_final_video=False)
            
            # Calculate statistics
            elapsed_time = time.time() - start_time
            
            result = {
                'success': True,
                'idea': idea,
                'script': script,
                'metadata': metadata,
                'video_path': video_path,
                'thumbnail_path': thumbnail_path,
                'video_id': video_id,
                'metadata_file': metadata_file,
                'elapsed_time': elapsed_time,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("\n" + "="*80)
            logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("="*80)
            logger.info(f"⏱️  Time taken: {elapsed_time:.2f} seconds")
            logger.info(f"📝 Metadata saved: {metadata_file}")
            if video_id:
                logger.info(f"📺 YouTube URL: https://www.youtube.com/watch?v={video_id}")
            logger.info("="*80 + "\n")
            
            return result
            
        except Exception as e:
            logger.error(f"\n❌ PIPELINE FAILED: {e}")
            logger.error("="*80)
            raise
    
    def save_metadata(self, idea: Dict, script: Dict, metadata: Dict,
                     video_path: str, thumbnail_path: str, video_id: str,
                     output_file: str):
        """Save all metadata for record keeping"""
        
        data = {
            'idea': idea,
            'script': script,
            'metadata': metadata,
            'files': {
                'video': video_path,
                'thumbnail': thumbnail_path
            },
            'youtube': {
                'video_id': video_id,
                'url': f"https://www.youtube.com/watch?v={video_id}" if video_id else None
            },
            'timestamp': datetime.now().isoformat(),
            'config': self.config
        }
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def schedule_pipeline(self, interval_hours: int = 24):
        """Schedule pipeline to run periodically"""
        
        logger.info(f"📅 Scheduling pipeline to run every {interval_hours} hours")
        
        import schedule
        
        def job():
            try:
                self.run_full_pipeline()
            except Exception as e:
                logger.error(f"Scheduled job failed: {e}")
        
        schedule.every(interval_hours).hours.do(job)
        
        logger.info("Starting scheduler... (press Ctrl+C to stop)")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped")


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Automation Pipeline")
    parser.add_argument('--run', action='store_true', help='Run full pipeline once')
    parser.add_argument('--schedule', action='store_true', help='Schedule pipeline to run periodically')
    parser.add_argument('--hours', type=int, default=24, help='Hours between runs (with --schedule)')
    parser.add_argument('--manual', action='store_true', help='Save metadata for manual review')

    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = YouTubeAutomationPipeline()
    
    if args.run:
        # Run once
        pipeline.run_full_pipeline(manual_upload=args.manual)
    
    elif args.schedule:
        # Schedule periodic runs
        pipeline.schedule_pipeline(interval_hours=args.hours)
    
    else:
        # Show help
        parser.print_help()
        print("\n📖 QUICK START:")
        print("  python main_orchestrator.py --run          # Run once")
        print("  python main_orchestrator.py --schedule --hours 24  # Run daily")
        print("  python main_orchestrator.py --run --manual # Save for review before upload")


if __name__ == "__main__":
    main()
