"""
Homepage scraper using crawl4ai
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import re

class HomepageScraper:
    def __init__(self):
        self.data_dir = Path("data/companies")
        
    def clean_content(self, html_content):
        """Clean HTML content to extract meaningful text while preserving ALL essential information"""
        if not html_content:
            return ""
            
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove only truly non-content elements
        for element in soup(["script", "style", "noscript", "meta", "link"]):
            element.decompose()
        
        # Remove obvious navigation elements but be conservative
        # Only remove if they're clearly navigation with minimal content
        navigation_elements = soup.find_all(['nav', 'footer', 'header'])
        for element in navigation_elements:
            text_content = element.get_text(strip=True)
            # Only remove if it's clearly navigation (very short or mostly links)
            if len(text_content) < 100 and len(element.find_all('a')) > len(text_content.split()) * 0.5:
                element.decompose()
        
        # Remove elements with navigation-related classes/IDs but keep substantial content
        navigation_selectors = [
            '[class*="nav"]', '[class*="menu"]', '[class*="sidebar"]',
            '[class*="footer"]', '[class*="header"]',
            '[id*="nav"]', '[id*="menu"]', '[id*="sidebar"]',
            '[id*="footer"]', '[id*="header"]',
            '[class*="breadcrumb"]', '[class*="pagination"]',
            '[class*="social"]', '[class*="share"]',
            '[class*="cookie"]', '[class*="popup"]', '[class*="modal"]',
            '[class*="banner"]', '[class*="overlay"]'
        ]
        
        for selector in navigation_selectors:
            for element in soup.select(selector):
                if element:
                    text_content = element.get_text(strip=True)
                    # Only remove if it has minimal content (less than 30 chars)
                    if len(text_content) < 30:
                        element.decompose()
        
        # Remove empty elements
        for element in soup.find_all():
            if not element.get_text(strip=True) and not element.find(['img', 'svg']):
                element.decompose()
        
        # Extract all meaningful text content
        # Get text from all content elements
        text_parts = []
        
        # Process all content elements
        content_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span', 'li', 'td', 'th', 'article', 'section', 'main'])
        
        for element in content_elements:
            text = element.get_text(strip=True)
            if text and len(text) > 2:  # Include all meaningful text
                # Add structure markers for headings
                if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    text_parts.append(f"\n{text}\n")
                else:
                    text_parts.append(text)
        
        # If no structured content found, get all text
        if not text_parts:
            text_parts = [soup.get_text()]
        
        # Join all text
        text = ' '.join(text_parts)
        
        # Clean up whitespace but preserve content
        text = re.sub(r'\s+', ' ', text)  # Normalize all whitespace to single spaces
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Preserve paragraph breaks
        
        # Remove very short fragments that are likely navigation remnants
        # Split by common sentence endings and filter
        sentences = re.split(r'[.!?]+', text)
        cleaned_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Keep sentences longer than 10 characters
                cleaned_sentences.append(sentence)
        
        text = '. '.join(cleaned_sentences)
        
        # Final cleanup
        text = re.sub(r'\s+', ' ', text)  # Normalize spaces again
        text = re.sub(r'\.\s*\.', '.', text)  # Remove double periods
        
        return text.strip()
    
    async def scrape_homepage(self, company_name, url):
        """Scrape homepage content using crawl4ai"""
        try:
            print(f"🕷️ Starting to scrape: {url}")
            
            async with AsyncWebCrawler(verbose=True) as crawler:
                # Crawl the page
                result = await crawler.arun(
                    url=url,
                    word_count_threshold=10,
                    extraction_strategy="LLMExtractionStrategy",
                    chunking_strategy="RegexChunking",
                    bypass_cache=True
                )
                
                if not result.success:
                    print(f"❌ Failed to scrape {url}: {result.error_message}")
                    return None
                
                print(f"✅ Successfully scraped {url}")
                print(f"📊 Raw content length: {len(result.cleaned_html)} characters")
                
                # Clean the content
                clean_content = self.clean_content(result.cleaned_html)
                print(f"🧹 Cleaned content length: {len(clean_content)} characters")
                
                # Prepare homepage data
                homepage_data = {
                    "url": url,
                    "content": clean_content,
                    "scraped_at": datetime.now().isoformat(),
                    "raw_content_length": len(result.cleaned_html),
                    "clean_content_length": len(clean_content)
                }
                
                return homepage_data
                
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None
    
    def save_homepage_data(self, company_name, homepage_data):
        """Save homepage data to company JSON file"""
        try:
            company_file = self.data_dir / f"{company_name.lower().replace(' ', '_')}_data.json"
            
            if not company_file.exists():
                print(f"❌ Company file not found: {company_file}")
                return False
                
            # Load existing data
            with open(company_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update homepage data
            data["homepage"] = homepage_data
            data["last_updated"] = datetime.now().isoformat()
            
            # Save updated data
            with open(company_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Homepage data saved to: {company_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving homepage data: {e}")
            return False
    
    async def scrape_and_save(self, company_name, url):
        """Main method to scrape homepage and save data"""
        print(f"\n🚀 Scraping homepage for: {company_name}")
        print(f"🌐 URL: {url}")
        print("-" * 50)
        
        # Scrape the homepage
        homepage_data = await self.scrape_homepage(company_name, url)
        
        if not homepage_data:
            print("❌ Scraping failed. No data to save.")
            return False
        
        # Save the data
        success = self.save_homepage_data(company_name, homepage_data)
        
        if success:
            print(f"✅ Homepage scraping completed for {company_name}")
            print(f"📄 Content preview: {homepage_data['content'][:200]}...")
        else:
            print(f"❌ Failed to save data for {company_name}")
            
        return success

# Test function
async def test_scraper():
    """Test the scraper with Exa"""
    scraper = HomepageScraper()
    success = await scraper.scrape_and_save("Exa", "https://exa.ai/")
    return success

if __name__ == "__main__":
    asyncio.run(test_scraper())
