"""
Sitemap analyzer to identify feature-related pages
"""

import asyncio
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from scrapers.homepage_scraper import HomepageScraper

class SitemapAnalyzer:
    def __init__(self):
        self.data_dir = Path("data/companies")
        self.scraper = HomepageScraper()
        
    def fetch_sitemap(self, sitemap_url):
        """Fetch sitemap content"""
        try:
            print(f"📥 Fetching sitemap: {sitemap_url}")
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            print(f"✅ Sitemap fetched successfully ({len(response.content)} bytes)")
            return response.content
            
        except Exception as e:
            print(f"❌ Error fetching sitemap: {e}")
            return None
    
    def parse_sitemap(self, sitemap_content):
        """Parse XML sitemap and extract URLs"""
        try:
            root = ET.fromstring(sitemap_content)
            urls = []
            
            # Handle different sitemap formats
            # Standard sitemap format
            for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None:
                    urls.append(loc_elem.text)
            
            # Sitemap index format (contains other sitemaps)
            for sitemap_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                loc_elem = sitemap_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None:
                    # Recursively fetch nested sitemaps
                    nested_content = self.fetch_sitemap(loc_elem.text)
                    if nested_content:
                        nested_urls = self.parse_sitemap(nested_content)
                        urls.extend(nested_urls)
            
            print(f"📊 Found {len(urls)} URLs in sitemap")
            return urls
            
        except ET.ParseError as e:
            print(f"❌ Error parsing XML sitemap: {e}")
            return []
        except Exception as e:
            print(f"❌ Error parsing sitemap: {e}")
            return []
    
    def filter_urls_by_keywords(self, urls, keywords):
        """Filter URLs based on keywords"""
        if not keywords:
            return urls
            
        filtered_urls = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        print(f"🔍 Filtering URLs with keywords: {keywords}")
        
        for url in urls:
            url_lower = url.lower()
            path = urlparse(url).path.lower()
            
            # Check if any keyword matches the URL or path
            for keyword in keywords_lower:
                if keyword in url_lower or keyword in path:
                    filtered_urls.append(url)
                    print(f"   ✅ Match: {url} (keyword: {keyword})")
                    break
        
        print(f"📊 Filtered to {len(filtered_urls)} URLs matching keywords")
        return filtered_urls
    
    def categorize_urls(self, urls):
        """Categorize URLs by type"""
        categories = {
            'features': [],
            'products': [],
            'pricing': [],
            'customers': [],
            'faq': [],
            'api': [],
            'documentation': [],
            'other': []
        }
        
        for url in urls:
            url_lower = url.lower()
            path = urlparse(url).path.lower()
            
            # Categorize based on URL patterns
            if any(word in url_lower for word in ['feature', 'capability', 'function']):
                categories['features'].append(url)
            elif any(word in url_lower for word in ['product', 'service', 'solution']):
                categories['products'].append(url)
            elif any(word in url_lower for word in ['pricing', 'price', 'cost', 'plan']):
                categories['pricing'].append(url)
            elif any(word in url_lower for word in ['customer', 'customers', 'case-study', 'case-studies', 'success-story', 'success-stories', 'testimonial', 'testimonials', 'stories', 'client', 'clients']):
                categories['customers'].append(url)
            elif any(word in url_lower for word in ['faq', 'frequently-asked-questions', 'frequently-asked', 'questions']):
                categories['faq'].append(url)
            elif any(word in url_lower for word in ['api', 'developer', 'docs', 'documentation']):
                categories['api'].append(url)
            elif any(word in url_lower for word in ['doc', 'guide', 'tutorial', 'help']):
                categories['documentation'].append(url)
            else:
                categories['other'].append(url)
        
        return categories
    
    async def scrape_feature_pages(self, company_name, urls):
        """Scrape multiple feature pages"""
        print(f"\n🕷️ Scraping {len(urls)} feature pages for {company_name}")
        print("-" * 50)
        
        scraped_data = {}
        successful_scrapes = 0
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Scraping: {url}")
            
            try:
                # Scrape the page
                homepage_data = await self.scraper.scrape_homepage(company_name, url)
                
                if homepage_data:
                    # Create a feature name from the URL
                    feature_name = self.create_feature_name(url)
                    scraped_data[feature_name] = {
                        "url": url,
                        "content": homepage_data["content"],
                        "scraped_at": homepage_data["scraped_at"],
                        "content_length": homepage_data["clean_content_length"]
                    }
                    successful_scrapes += 1
                    print(f"   ✅ Success: {homepage_data['clean_content_length']} characters")
                else:
                    print(f"   ❌ Failed to scrape")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n📊 Scraping Summary:")
        print(f"   ✅ Successful: {successful_scrapes}/{len(urls)}")
        print(f"   ❌ Failed: {len(urls) - successful_scrapes}/{len(urls)}")
        
        return scraped_data
    
    def create_feature_name(self, url):
        """Create a feature name from URL"""
        path = urlparse(url).path
        # Remove leading/trailing slashes and split by slashes
        path_parts = [part for part in path.strip('/').split('/') if part]
        
        if path_parts:
            # Use the last meaningful part of the path
            feature_name = path_parts[-1].replace('-', '_').replace('.', '_')
        else:
            # Fallback to domain-based name
            domain = urlparse(url).netloc
            feature_name = domain.replace('.', '_')
        
        return feature_name
    
    def save_feature_data(self, company_name, feature_data):
        """Save feature data to company JSON file"""
        try:
            company_file = self.data_dir / f"{company_name.lower().replace(' ', '_')}_data.json"
            
            if not company_file.exists():
                print(f"❌ Company file not found: {company_file}")
                return False
                
            # Load existing data
            with open(company_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update features data
            if 'features' not in data:
                data['features'] = {}
            
            data['features'].update(feature_data)
            data['last_updated'] = datetime.now().isoformat()
            
            # Save updated data
            with open(company_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Feature data saved to: {company_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving feature data: {e}")
            return False
    
    async def analyze_and_scrape_sitemap(self, company_name, sitemap_url, keywords=None):
        """Main method to analyze sitemap and scrape feature pages"""
        print(f"\n🗺️ Analyzing sitemap for: {company_name}")
        print(f"🌐 Sitemap URL: {sitemap_url}")
        if keywords:
            print(f"🔍 Keywords: {keywords}")
        print("-" * 50)
        
        # Fetch sitemap
        sitemap_content = self.fetch_sitemap(sitemap_url)
        if not sitemap_content:
            return False
        
        # Parse sitemap
        all_urls = self.parse_sitemap(sitemap_content)
        if not all_urls:
            print("❌ No URLs found in sitemap")
            return False
        
        # Filter URLs by keywords
        if keywords:
            filtered_urls = self.filter_urls_by_keywords(all_urls, keywords)
        else:
            filtered_urls = all_urls
        
        if not filtered_urls:
            print("❌ No URLs match the provided keywords")
            return False
        
        # Categorize URLs
        categories = self.categorize_urls(filtered_urls)
        
        print(f"\n📊 URL Categories:")
        for category, urls in categories.items():
            if urls:
                print(f"   {category}: {len(urls)} URLs")
        
        # Ask user which categories to scrape
        print(f"\n🎯 Which categories would you like to scrape?")
        print("1. All categories")
        print("2. Features only")
        print("3. Products only")
        print("4. Pricing only")
        print("5. Customers only")
        print("6. FAQ only")
        print("7. API/Documentation only")
        print("8. Custom selection")
        
        choice = input("Choose option (1-8): ").strip()
        
        urls_to_scrape = []
        if choice == "1":
            urls_to_scrape = filtered_urls
        elif choice == "2":
            urls_to_scrape = categories['features']
        elif choice == "3":
            urls_to_scrape = categories['products']
        elif choice == "4":
            urls_to_scrape = categories['pricing']
        elif choice == "5":
            urls_to_scrape = categories['customers']
        elif choice == "6":
            urls_to_scrape = categories['faq']
        elif choice == "7":
            urls_to_scrape = categories['api'] + categories['documentation']
        elif choice == "8":
            print("\nAvailable categories:")
            for i, (category, urls) in enumerate(categories.items(), 1):
                if urls:
                    print(f"{i}. {category} ({len(urls)} URLs)")
            
            selected = input("Enter category numbers (comma-separated): ").strip()
            try:
                indices = [int(x.strip()) - 1 for x in selected.split(',')]
                category_list = list(categories.keys())
                for idx in indices:
                    if 0 <= idx < len(category_list):
                        urls_to_scrape.extend(categories[category_list[idx]])
            except:
                print("❌ Invalid selection, scraping all URLs")
                urls_to_scrape = filtered_urls
        else:
            print("❌ Invalid choice, scraping all URLs")
            urls_to_scrape = filtered_urls
        
        if not urls_to_scrape:
            print("❌ No URLs selected for scraping")
            return False
        
        print(f"\n🚀 Scraping {len(urls_to_scrape)} selected URLs...")
        
        # Scrape the selected URLs
        feature_data = await self.scrape_feature_pages(company_name, urls_to_scrape)
        
        if feature_data:
            # Save the data
            success = self.save_feature_data(company_name, feature_data)
            if success:
                print(f"✅ Sitemap analysis completed for {company_name}")
                print(f"📄 Scraped {len(feature_data)} feature pages")
            else:
                print(f"❌ Failed to save feature data for {company_name}")
            return success
        else:
            print(f"❌ No feature data scraped for {company_name}")
            return False

# Test function
async def test_sitemap_analyzer():
    """Test the sitemap analyzer"""
    analyzer = SitemapAnalyzer()
    success = await analyzer.analyze_and_scrape_sitemap("Exa", "https://exa.ai/sitemap.xml", ["api", "features"])
    return success

if __name__ == "__main__":
    asyncio.run(test_sitemap_analyzer())
