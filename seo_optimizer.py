"""
SEO Optimizer - Optimizes titles, descriptions, and tags for YouTube virality
Uses keyword research and trending data
"""

import json
import re
from typing import Dict, List, Tuple
from collections import Counter

class SEOOptimizer:
    """Optimize video metadata for maximum reach and virality"""
    
    def __init__(self):
        """Initialize SEO optimizer with keyword databases"""
        
        # High-converting power words for titles
        self.power_words = [
            'incredible', 'amazing', 'shocking', 'unbelievable', 'mind-blowing',
            'the ultimate', 'secrets', 'hidden', 'finally revealed', 'exposed',
            'the truth about', 'why', 'how to', 'avoid', 'stop', 'never',
            'biggest', 'best', 'worst', 'crucial', 'critical', 'essential',
            'proven', 'official', 'real', 'honest', 'brutal', 'raw'
        ]
        
        # Viral keywords (tech/coding focused)
        self.viral_keywords = {
            'ai': {'difficulty': 'high', 'trend': 'rising', 'clicks': 8.5},
            'python': {'difficulty': 'medium', 'trend': 'stable', 'clicks': 7.2},
            'javascript': {'difficulty': 'medium', 'trend': 'stable', 'clicks': 6.8},
            'react': {'difficulty': 'medium', 'trend': 'stable', 'clicks': 6.5},
            'chatgpt': {'difficulty': 'low', 'trend': 'rising', 'clicks': 9.0},
            'machine learning': {'difficulty': 'high', 'trend': 'rising', 'clicks': 8.2},
            'web development': {'difficulty': 'low', 'trend': 'stable', 'clicks': 6.0},
            'devops': {'difficulty': 'high', 'trend': 'rising', 'clicks': 7.8},
            'kubernetes': {'difficulty': 'high', 'trend': 'rising', 'clicks': 7.5},
            'rust': {'difficulty': 'high', 'trend': 'rising', 'clicks': 7.9},
            'golang': {'difficulty': 'medium', 'trend': 'rising', 'clicks': 7.3},
            'typescript': {'difficulty': 'medium', 'trend': 'rising', 'clicks': 7.1},
            'nextjs': {'difficulty': 'medium', 'trend': 'rising', 'clicks': 6.9},
            'api': {'difficulty': 'low', 'trend': 'stable', 'clicks': 5.8},
            'database': {'difficulty': 'medium', 'trend': 'stable', 'clicks': 6.2},
        }
        
        self.engagement_triggers = [
            'TOP 10', 'STOP MAKING', 'WHY I', 'I BUILT', 'NOBODY TALKS ABOUT',
            'THE BIGGEST MISTAKE', 'RANKING', 'FINALLY REVEALED', 'THIS CHANGED EVERYTHING',
            'WARNING', 'EXPOSED', 'WATCH THIS', 'PROOF THAT'
        ]
        
        self.cta_hooks = [
            'If you find this helpful, smash the like button and subscribe',
            'Make sure to watch till the end for the bonus tip',
            'Drop a comment telling me what you think',
            'Subscribe to the channel for more advanced content',
            'Follow for weekly tutorials and coding tips',
            'Join our Discord community for daily challenges'
        ]

    def optimize_title(self, base_title: str, keyword: str = None,
                      video_type: str = 'general') -> str:
        """
        Optimize video title for clicks and virality
        
        Args:
            base_title: Original title
            keyword: Primary keyword to include
            video_type: 'ranking', 'tutorial', 'controversy', 'experiment'
        
        Returns:
            Optimized title
        """
        
        title_length = len(base_title)
        
        # Optimal length is 40-60 characters
        if title_length < 30:
            # Add power word prefix
            prefix = "Why " if video_type == 'tutorial' else "The Ultimate "
            base_title = prefix + base_title
        
        # Add emoji-like elements for visual interest
        if '|' not in base_title:
            base_title = base_title + " | Explained"
        
        # Ensure keyword is in title if provided
        if keyword and keyword.lower() not in base_title.lower():
            # Insert keyword naturally
            words = base_title.split()
            if len(words) > 3:
                insertion_point = len(words) // 2
                words.insert(insertion_point, keyword)
                base_title = ' '.join(words)
        
        # Capitalize for emphasis
        if video_type == 'controversy':
            base_title = base_title.upper()
        
        return base_title[:100]  # YouTube limit

    def generate_description(self, title: str, script: str, keywords: List[str],
                           video_duration: int = 480) -> str:
        """
        Generate SEO-optimized description
        
        Args:
            title: Video title
            script: Video script (for natural keyword inclusion)
            keywords: List of keywords to include
            video_duration: Duration in seconds
        
        Returns:
            Optimized description
        """
        
        # Extract key points from script
        sentences = script.split('.')
        key_points = [s.strip() for s in sentences[:5] if len(s.strip()) > 20]
        
        # Build description
        description = f"""📚 {title}

Learn everything you need to know about {keywords[0] if keywords else 'this topic'} in this comprehensive guide.

⏲️ TIMESTAMPS:
0:00 - Intro
1:00 - Key Concepts
3:00 - Practical Examples
5:00 - Advanced Tips
7:00 - Conclusion

🎯 WHAT YOU'LL LEARN:
"""
        
        # Add learning points
        for i, point in enumerate(key_points[:5], 1):
            description += f"✓ {point}\n"
        
        # Add keywords
        description += f"\n🔍 KEYWORDS: {', '.join(keywords[:8])}\n\n"
        
        # Add CTA
        description += """👍 HELP ME OUT:
- Like this video
- Subscribe to the channel
- Turn on notifications
- Drop a comment below

📱 CONNECT:
- Twitter: [Link]
- GitHub: [Link]
- Discord: [Link]

⚠️ DISCLAIMER:
This video is for educational purposes only.

#"""
        
        # Add hashtags
        description += ' #'.join(keywords[:5])
        
        return description[:5000]  # YouTube limit

    def generate_tags(self, title: str, keywords: List[str], category: str = 'Education') -> List[str]:
        """
        Generate SEO-optimized tags
        
        Args:
            title: Video title
            keywords: Primary keywords
            category: Video category
        
        Returns:
            List of tags
        """
        
        tags = []
        
        # Add primary keywords
        tags.extend([k.lower() for k in keywords[:5]])
        
        # Add variations
        for keyword in keywords[:3]:
            tags.append(f"{keyword.lower()} tutorial")
            tags.append(f"learn {keyword.lower()}")
        
        # Add category tags
        category_tags = {
            'Education': ['tutorial', 'learn', 'how to', 'guide', 'beginner'],
            'Technology': ['tech', 'software', 'programming', 'coding', 'development'],
            'Entertainment': ['viral', 'trending', 'reaction', 'funny', 'entertainment'],
        }
        
        tags.extend(category_tags.get(category, []))
        
        # Add trending tags
        tags.extend(['2025', category.lower(), 'explained', 'for beginners'])
        
        # Remove duplicates and limit to 30
        tags = list(dict.fromkeys(tags))[:30]
        
        return tags

    def calculate_seo_score(self, title: str, description: str,
                           tags: List[str]) -> Dict:
        """
        Calculate SEO score for content
        
        Returns:
            Score breakdown
        """
        
        score = {
            'title_score': 0,
            'description_score': 0,
            'tags_score': 0,
            'total_score': 0
        }
        
        # Title score
        title_length = len(title)
        if 40 <= title_length <= 60:
            score['title_score'] += 25
        elif 30 <= title_length <= 100:
            score['title_score'] += 15
        
        # Check for power words
        if any(word in title.lower() for word in self.power_words[:10]):
            score['title_score'] += 20
        
        # Check for keywords
        if any(word in title.lower() for word in self.viral_keywords.keys()):
            score['title_score'] += 25
        
        # Number in title
        if any(char.isdigit() for char in title):
            score['title_score'] += 15
        
        # Description score
        desc_length = len(description)
        if 200 <= desc_length <= 5000:
            score['description_score'] += 25
        
        # Keyword density
        keywords_found = sum(1 for keyword in self.viral_keywords.keys()
                            if keyword in description.lower())
        score['description_score'] += min(keywords_found * 10, 30)
        
        # Links and CTAs
        if 'http' in description or any(cta in description for cta in self.cta_hooks):
            score['description_score'] += 20
        
        # Tags score
        tag_count = len(tags)
        if 10 <= tag_count <= 30:
            score['tags_score'] = 30
        elif 5 <= tag_count < 10 or tag_count > 30:
            score['tags_score'] = 20
        
        # Calculate total
        score['total_score'] = int((score['title_score'] + score['description_score'] +
                                   score['tags_score']) / 3)
        
        return score

    def get_keyword_metrics(self, keyword: str) -> Dict:
        """Get metrics for a specific keyword"""
        return self.viral_keywords.get(keyword.lower(), {
            'difficulty': 'unknown',
            'trend': 'unknown',
            'clicks': 5.0
        })

    def suggest_improvements(self, title: str, description: str,
                            tags: List[str]) -> List[str]:
        """
        Suggest improvements for SEO
        
        Returns:
            List of improvement suggestions
        """
        
        suggestions = []
        
        # Title improvements
        if len(title) < 30:
            suggestions.append("✓ Extend title to 40-60 characters for better CTR")
        
        if not any(word in title.lower() for word in self.power_words[:10]):
            suggestions.append("✓ Add a power word to the title (e.g., 'Why', 'Stop', 'Avoid')")
        
        if not any(char.isdigit() for char in title):
            suggestions.append("✓ Add numbers to title (e.g., 'Top 10', 'In 30 Days')")
        
        # Description improvements
        if len(description) < 200:
            suggestions.append("✓ Expand description to 200+ characters for better SEO")
        
        if 'http' not in description:
            suggestions.append("✓ Add relevant links in description (GitHub, website, etc.)")
        
        # Tags improvements
        if len(tags) < 10:
            suggestions.append(f"✓ Add more tags (currently {len(tags)}, recommend 10-30)")
        
        return suggestions

    def batch_optimize(self, ideas: List[Dict]) -> List[Dict]:
        """Optimize multiple video ideas at once"""
        
        optimized = []
        
        for idea in ideas:
            optimized_idea = idea.copy()
            
            # Optimize title
            optimized_idea['optimized_title'] = self.optimize_title(
                idea['title'],
                keyword=idea.get('keyword'),
                video_type='ranking'
            )
            
            # Generate description
            optimized_idea['description'] = self.generate_description(
                optimized_idea['optimized_title'],
                idea.get('description', ''),
                idea.get('seo_tags', [idea.get('keyword', '')])
            )
            
            # Generate tags
            optimized_idea['tags'] = self.generate_tags(
                optimized_idea['optimized_title'],
                [idea.get('keyword', '')] + idea.get('seo_tags', [])
            )
            
            # Calculate score
            optimized_idea['seo_score'] = self.calculate_seo_score(
                optimized_idea['optimized_title'],
                optimized_idea['description'],
                optimized_idea['tags']
            )
            
            # Get suggestions
            optimized_idea['improvements'] = self.suggest_improvements(
                optimized_idea['optimized_title'],
                optimized_idea['description'],
                optimized_idea['tags']
            )
            
            optimized.append(optimized_idea)
        
        return optimized


if __name__ == "__main__":
    optimizer = SEOOptimizer()
    
    # Example optimization
    title = "Python Tutorial"
    description = "Learn Python programming basics"
    tags = ["python", "tutorial"]
    
    optimized_title = optimizer.optimize_title(title, keyword="Python")
    optimized_description = optimizer.generate_description(
        optimized_title,
        description,
        ["Python", "Programming", "Beginner"]
    )
    optimized_tags = optimizer.generate_tags(
        optimized_title,
        ["Python", "Programming"]
    )
    
    score = optimizer.calculate_seo_score(
        optimized_title,
        optimized_description,
        optimized_tags
    )
    
    print("="*80)
    print("ORIGINAL vs OPTIMIZED")
    print("="*80)
    print(f"\n📝 TITLE:")
    print(f"  Before: {title}")
    print(f"  After:  {optimized_title}")
    print(f"\n📄 DESCRIPTION (first 200 chars):")
    print(f"  After:  {optimized_description[:200]}...")
    print(f"\n🏷️  TAGS:")
    print(f"  {', '.join(optimized_tags)}")
    print(f"\n📊 SEO SCORE: {score['total_score']}/100")
    print(f"  Title: {score['title_score']}/100")
    print(f"  Description: {score['description_score']}/100")
    print(f"  Tags: {score['tags_score']}/100")
