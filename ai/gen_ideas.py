"""
Viral Idea Generator for Coding/Tech Videos
Fetches ideas from multiple web sources and optimizes them through AI
100% Dynamic - Ideas from web trends, not hardcoded

Credentials loaded from:
- .env file (GROQ_API_KEY)
- Environment variables (LLM_PROVIDER, GROQ_MODEL)
"""

import os
import requests
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import time
import re

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Graceful fallback if dotenv not installed

class ViralIdeaGenerator:
    """Generate viral coding/tech video ideas from web sources + AI optimization"""
    
    def __init__(self, groq_api_key: str = None):
        # Use provided key or load from environment
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        self.groq_model = os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')
        self.use_ai = self.groq_api_key is not None
        
        if self.use_ai:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.groq_api_key)
                print(f"[OK] Groq AI initialized with model: {self.groq_model}")
            except ImportError:
                print("[!] Groq not installed. Install with: pip install groq")
                self.use_ai = False
        else:
            print("[!] GROQ_API_KEY not found in .env. Set it to enable AI optimization.")
        
        # Expanded list of web sources to fetch from
        self.web_sources = {
            'github': 'GitHub Trending',
            'hackernews': 'HackerNews',
            'devto': 'Dev.to',
            'reddit': 'Reddit r/programming',
            'stackoverflow': 'Stack Overflow',
            'techcrunch': 'Tech News Trends'
        }

    def fetch_github_trends(self) -> List[Dict]:
        """Fetch trending repositories from GitHub with details"""
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                'q': 'language:python OR language:javascript OR language:rust OR language:go sort:stars',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 15
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                repos = response.json()['items']
                return [
                    {
                        'title': f"{repo['name']} - GitHub Trending",
                        'source': 'GitHub',
                        'keywords': repo['language'] or 'Open Source',
                        'description': repo['description'] or repo['name'],
                        'url': repo['html_url'],
                        'stars': repo['stargazers_count']
                    }
                    for repo in repos[:8]
                ]
            return []
        except Exception as e:
            print(f"[!] Error fetching GitHub trends: {e}")
            return []

    def fetch_hackernews_trends(self) -> List[Dict]:
        """Fetch trending topics from HackerNews with details"""
        try:
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                story_ids = response.json()[:20]
                trends = []
                
                for story_id in story_ids[:8]:
                    try:
                        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                        story_response = requests.get(story_url, timeout=5)
                        if story_response.status_code == 200:
                            story = story_response.json()
                            if 'title' in story and story.get('type') == 'story':
                                trends.append({
                                    'title': story['title'],
                                    'source': 'HackerNews',
                                    'keywords': 'Tech News',
                                    'description': story['title'],
                                    'url': story.get('url', ''),
                                    'score': story.get('score', 0)
                                })
                    except:
                        continue
                
                return trends
            return []
        except Exception as e:
            print(f"[!] Error fetching HackerNews trends: {e}")
            return []

    def fetch_devto_trends(self) -> List[Dict]:
        """Fetch trending articles from Dev.to with details"""
        try:
            url = "https://dev.to/api/articles"
            params = {
                'per_page': 15,
                'tag': 'coding,javascript,python,webdev,productivity,tutorial'
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                articles = response.json()
                return [
                    {
                        'title': article['title'],
                        'source': 'Dev.to',
                        'keywords': ','.join(article.get('tag_list', ['coding'])),
                        'description': article.get('description', article['title']),
                        'url': article['url'],
                        'reactions': article.get('public_reactions_count', 0)
                    }
                    for article in articles[:8]
                ]
            return []
        except Exception as e:
            print(f"[!] Error fetching Dev.to trends: {e}")
            return []

    def fetch_reddit_trends(self) -> List[Dict]:
        """Fetch trending posts from Reddit r/programming"""
        try:
            url = "https://www.reddit.com/r/programming/top.json"
            headers = {'User-Agent': 'YouTube-Automation/1.0'}
            params = {'t': 'week', 'limit': 10}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                posts = response.json()['data']['children']
                return [
                    {
                        'title': post['data']['title'],
                        'source': 'Reddit',
                        'keywords': 'Programming',
                        'description': post['data']['title'],
                        'url': f"https://reddit.com{post['data']['permalink']}",
                        'score': post['data']['score']
                    }
                    for post in posts[:8] if post['data'].get('is_self') or post['data'].get('url')
                ]
            return []
        except Exception as e:
            print(f"[!] Error fetching Reddit trends: {e}")
            return []

    def fetch_stackoverflow_trends(self) -> List[Dict]:
        """Fetch trending tags and questions from Stack Overflow"""
        try:
            url = "https://api.stackexchange.com/2.3/tags"
            params = {
                'site': 'stackoverflow',
                'sort': 'popular',
                'order': 'desc',
                'pagesize': 10
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                tags = response.json()['items']
                return [
                    {
                        'title': f"Mastering {tag['name']} on Stack Overflow",
                        'source': 'Stack Overflow',
                        'keywords': tag['name'],
                        'description': f"{tag['count']} questions about {tag['name']}",
                        'url': f"https://stackoverflow.com/questions/tagged/{tag['name']}",
                        'count': tag['count']
                    }
                    for tag in tags[:8] if tag.get('has_synonyms') or tag['count'] > 50000
                ]
            return []
        except Exception as e:
            print(f"[!] Error fetching Stack Overflow trends: {e}")
            return []

    def optimize_idea_with_ai(self, raw_idea: Dict) -> Dict:
        """Pass raw web-fetched idea through AI for viral optimization"""
        if not self.use_ai:
            # Fallback: rule-based optimization
            return {
                'title': raw_idea.get('title', 'New Trend'),
                'hook': f"Breaking: {raw_idea.get('title', 'New Trend')} is changing everything...",
                'keyword': raw_idea.get('keywords', 'coding'),
                'viral_score': min(98, raw_idea.get('score', raw_idea.get('stars', raw_idea.get('count', 50))) // 100 + 70)
            }
        
        try:
            # Create a viral optimization prompt
            prompt = f"""You are a YouTube video strategist for coding/tech content. 
Optimize this web-sourced idea into a viral video concept:

Source: {raw_idea.get('source', 'Web')}
Title: {raw_idea.get('title')}
Description: {raw_idea.get('description', '')}
Keywords: {raw_idea.get('keywords', 'coding')}

Return ONLY a JSON response (no markdown, no extra text) with:
{{
    "title": "Compelling 50-60 char video title",
    "hook": "Attention-grabbing opening hook (100 chars max)",
    "keyword": "Primary keyword for SEO",
    "viral_elements": ["element1", "element2", "element3"],
    "viral_score": <85-99>
}}"""

            chat_completion = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
                optimized = json.loads(response_text)
                return {
                    'title': optimized.get('title', raw_idea.get('title')),
                    'hook': optimized.get('hook', f"Breaking: {raw_idea.get('title')}..."),
                    'keyword': optimized.get('keyword', raw_idea.get('keywords', 'coding')),
                    'viral_score': optimized.get('viral_score', 85),
                    'viral_elements': optimized.get('viral_elements', [])
                }
            except:
                # If JSON parsing fails, extract manually
                return {
                    'title': raw_idea.get('title'),
                    'hook': f"{response_text[:100]}...",
                    'keyword': raw_idea.get('keywords', 'coding'),
                    'viral_score': 85
                }
        
        except Exception as e:
            print(f"[!] Error optimizing idea with AI: {e}")
            # Fallback to rule-based optimization
            return {
                'title': raw_idea.get('title', 'New Trend'),
                'hook': f"Breaking: {raw_idea.get('title', 'New Trend')} is changing everything...",
                'keyword': raw_idea.get('keywords', 'coding'),
                'viral_score': 80
            }

    def generate_ideas(self, count: int = 3) -> List[Dict]:
        """Generate viral coding/tech ideas from web sources, optimized by AI"""
        try:
            raw_ideas = []
            
            print("[*] Fetching viral ideas from web sources...")
            
            # Fetch from all available sources
            raw_ideas.extend(self.fetch_github_trends())
            raw_ideas.extend(self.fetch_hackernews_trends())
            raw_ideas.extend(self.fetch_devto_trends())
            raw_ideas.extend(self.fetch_reddit_trends())
            raw_ideas.extend(self.fetch_stackoverflow_trends())
            
            if raw_ideas:
                sources_count = len(set(i.get('source') for i in raw_ideas))
                print(f"[OK] Found {len(raw_ideas)} trending topics from {sources_count} sources")
                
                # Select random ideas from all sources
                selected = random.sample(raw_ideas, min(count, len(raw_ideas)))
                
                # Optimize each idea through AI
                ideas = []
                for raw_idea in selected:
                    optimized = self.optimize_idea_with_ai(raw_idea)
                    ideas.append(optimized)
                
                return ideas
            else:
                print("[!] No web sources available, using fallback ideas")
                return self._fallback_ideas(count)
        
        except Exception as e:
            print(f"[!] Error generating ideas: {e}")
            return self._fallback_ideas(count)

    def _fallback_ideas(self, count: int = 3) -> List[Dict]:
        """Fallback ideas if web sources are unavailable"""
        fallback_topics = [
            {
                'title': 'The Hidden Power of Async/Await in JavaScript',
                'hook': 'Most developers miss this async trick...',
                'keyword': 'JavaScript',
                'viral_score': 87
            },
            {
                'title': 'Why Your API Design is Wrong',
                'hook': 'APIs should be designed differently...',
                'keyword': 'API Design',
                'viral_score': 85
            },
            {
                'title': 'Database Optimization Will Change Everything',
                'hook': 'This database trick saved us $100k...',
                'keyword': 'Database Optimization',
                'viral_score': 90
            }
        ]
        return fallback_topics[:count]

    def save_ideas(self, ideas: List[Dict], filename: str = 'generated_ideas.json'):
        """Save generated ideas to JSON file"""
        with open(filename, 'w') as f:
            json.dump(ideas, f, indent=2)
        print(f"[OK] Ideas saved to {filename}")
        return filename


if __name__ == "__main__":
    import os
    groq_key = os.environ.get('GROQ_API_KEY')
    
    generator = ViralIdeaGenerator(groq_api_key=groq_key)
    ideas = generator.generate_ideas(count=3)
    
    print("\n" + "="*80)
    print("TOP VIRAL VIDEO IDEAS")
    print("="*80)
    
    for i, idea in enumerate(ideas, 1):
        print(f"\n#{i} - Viral Score: {idea.get('viral_score', 0)}/100")
        print(f"   Title: {idea.get('title', 'N/A')}")
        print(f"   Hook: {idea.get('hook', 'N/A')}")
        print(f"   Keyword: {idea.get('keyword', 'N/A')}")
    
    generator.save_ideas(ideas)
