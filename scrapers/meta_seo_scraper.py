"""
This checks how good a website is for search engines
Like looking at the title, description, and other hidden info
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import requests

class MetaSEOScraper:
    def __init__(self):
        self.data_dir = Path("data/companies")
        
    def extract_meta_tags(self, html_content, url):
        """Find all the hidden info that search engines look at"""
        if not html_content:
            return {}
            
        soup = BeautifulSoup(html_content, 'html.parser')
        meta_data = {
            'title': '',
            'description': '',
            'keywords': '',
            'author': '',
            'viewport': '',
            'robots': '',
            'canonical': '',
            'og_tags': {},
            'twitter_tags': {},
            'schema_markup': [],
            'other_meta': {}
        }
        
        # Get the page title
        title_tag = soup.find('title')
        if title_tag:
            meta_data['title'] = title_tag.get_text(strip=True)
        
        # Look for all the meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name', '').lower()
            property_attr = meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                meta_data['description'] = content
            elif name == 'keywords':
                meta_data['keywords'] = content
            elif name == 'author':
                meta_data['author'] = content
            elif name == 'viewport':
                meta_data['viewport'] = content
            elif name == 'robots':
                meta_data['robots'] = content
            elif name == 'canonical':
                meta_data['canonical'] = content
            elif property_attr.startswith('og:'):
                # Facebook sharing tags
                og_property = property_attr.replace('og:', '')
                meta_data['og_tags'][og_property] = content
            elif name.startswith('twitter:'):
                # Twitter sharing tags
                twitter_property = name.replace('twitter:', '')
                meta_data['twitter_tags'][twitter_property] = content
            elif name and content:
                # Other meta tags
                meta_data['other_meta'][name] = content
        
        # Find the main URL for this page
        canonical_link = soup.find('link', rel='canonical')
        if canonical_link and canonical_link.get('href'):
            meta_data['canonical'] = canonical_link.get('href')
        
        # Look for structured data
        schema_scripts = soup.find_all('script', type='application/ld+json')
        for script in schema_scripts:
            try:
                schema_data = json.loads(script.string)
                meta_data['schema_markup'].append(schema_data)
            except (json.JSONDecodeError, TypeError):
                continue
        
        return meta_data
    
    def calculate_b2b_seo_score(self, meta_data, html_content, url):
        """Give the website a B2B-focused SEO score from 0-100"""
        score = 0
        max_score = 100
        seo_analysis = {
            'score': 0,
            'factors': {},
            'recommendations': [],
            'b2b_indicators': {}
        }
        
        # Check if they have a good title (25 points)
        title = meta_data.get('title', '')
        if title:
            score += 15
            seo_analysis['factors']['has_title'] = True
            seo_analysis['factors']['title_length'] = len(title)
            
            # Check for B2B keywords in title
            b2b_keywords = ['enterprise', 'business', 'professional', 'solution', 'platform', 'api', 'integration']
            title_lower = title.lower()
            b2b_keyword_count = sum(1 for keyword in b2b_keywords if keyword in title_lower)
            seo_analysis['b2b_indicators']['b2b_keywords_in_title'] = b2b_keyword_count
            
            if b2b_keyword_count > 0:
                score += 10
                seo_analysis['factors']['has_b2b_keywords'] = True
            else:
                seo_analysis['recommendations'].append("Consider adding B2B keywords to title (enterprise, business, solution, etc.)")
            
            if 30 <= len(title) <= 60:
                score += 5
                seo_analysis['factors']['title_length_optimal'] = True
            else:
                seo_analysis['recommendations'].append(f"Title length ({len(title)} chars) should be 30-60 characters")
        else:
            seo_analysis['factors']['has_title'] = False
            seo_analysis['recommendations'].append("Missing title tag")
        
        # Check if they have a good description (20 points)
        description = meta_data.get('description', '')
        if description:
            score += 15
            seo_analysis['factors']['has_description'] = True
            seo_analysis['factors']['description_length'] = len(description)
            
            # Check for B2B value propositions in description
            b2b_value_props = ['enterprise', 'scalable', 'secure', 'integration', 'api', 'automation', 'efficiency']
            desc_lower = description.lower()
            b2b_value_count = sum(1 for prop in b2b_value_props if prop in desc_lower)
            seo_analysis['b2b_indicators']['b2b_value_props_in_description'] = b2b_value_count
            
            if b2b_value_count > 0:
                score += 5
                seo_analysis['factors']['has_b2b_value_props'] = True
            else:
                seo_analysis['recommendations'].append("Consider adding B2B value propositions to description")
            
            if 120 <= len(description) <= 160:
                seo_analysis['factors']['description_length_optimal'] = True
            else:
                seo_analysis['recommendations'].append(f"Meta description length ({len(description)} chars) should be 120-160 characters")
        else:
            seo_analysis['factors']['has_description'] = False
            seo_analysis['recommendations'].append("Missing meta description")
        
        # Check B2B content structure (15 points)
        soup = BeautifulSoup(html_content, 'html.parser')
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        h1_count = len(soup.find_all('h1'))
        if h1_count == 1:
            score += 10
            seo_analysis['factors']['single_h1'] = True
        elif h1_count == 0:
            seo_analysis['recommendations'].append("Missing H1 tag")
        else:
            seo_analysis['recommendations'].append(f"Multiple H1 tags found ({h1_count})")
        
        # Check for B2B content sections
        b2b_sections = ['features', 'pricing', 'enterprise', 'api', 'integration', 'security', 'compliance']
        heading_text = ' '.join([h.get_text().lower() for h in headings])
        b2b_section_count = sum(1 for section in b2b_sections if section in heading_text)
        seo_analysis['b2b_indicators']['b2b_sections_found'] = b2b_section_count
        
        if b2b_section_count >= 3:
            score += 5
            seo_analysis['factors']['good_b2b_structure'] = True
        else:
            seo_analysis['recommendations'].append("Consider adding more B2B-focused content sections")
        
        seo_analysis['factors']['total_headings'] = len(headings)
        seo_analysis['factors']['h1_count'] = h1_count
        
        # Check for B2B trust signals (10 points)
        trust_signals = ['security', 'compliance', 'soc2', 'iso', 'gdpr', 'hipaa', 'enterprise', 'certified']
        page_text = soup.get_text().lower()
        trust_signal_count = sum(1 for signal in trust_signals if signal in page_text)
        seo_analysis['b2b_indicators']['trust_signals_found'] = trust_signal_count
        
        if trust_signal_count >= 2:
            score += 10
            seo_analysis['factors']['good_trust_signals'] = True
        else:
            seo_analysis['recommendations'].append("Consider adding more trust signals (security, compliance, certifications)")
        
        seo_analysis['factors']['trust_signals_count'] = trust_signal_count
        
        # Check if they link to other pages on their site (10 points)
        internal_links = []
        external_links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                if href.startswith('http'):
                    if urlparse(href).netloc == urlparse(url).netloc:
                        internal_links.append(href)
                    else:
                        external_links.append(href)
                elif href.startswith('/') or not href.startswith('#'):
                    internal_links.append(urljoin(url, href))
        
        seo_analysis['factors']['internal_links'] = len(internal_links)
        seo_analysis['factors']['external_links'] = len(external_links)
        
        if len(internal_links) >= 5:
            score += 5
            seo_analysis['factors']['good_internal_linking'] = True
        else:
            seo_analysis['recommendations'].append("Add more internal links")
        
        if len(external_links) >= 2:
            score += 5
            seo_analysis['factors']['good_external_linking'] = True
        else:
            seo_analysis['recommendations'].append("Add more external links for authority")
        
        # Check if they have Facebook sharing tags (10 points)
        og_tags = meta_data.get('og_tags', {})
        required_og_tags = ['title', 'description', 'image', 'url']
        
        og_score = 0
        for tag in required_og_tags:
            if tag in og_tags and og_tags[tag]:
                og_score += 2.5
        
        score += og_score
        seo_analysis['factors']['og_tags_score'] = og_score
        seo_analysis['factors']['og_tags_present'] = list(og_tags.keys())
        
        if og_score < 10:
            missing_og = [tag for tag in required_og_tags if tag not in og_tags or not og_tags[tag]]
            seo_analysis['recommendations'].append(f"Missing Open Graph tags: {', '.join(missing_og)}")
        
        # Check if they have Twitter sharing tags (5 points)
        twitter_tags = meta_data.get('twitter_tags', {})
        if twitter_tags:
            score += 5
            seo_analysis['factors']['has_twitter_cards'] = True
            seo_analysis['factors']['twitter_tags_present'] = list(twitter_tags.keys())
        else:
            seo_analysis['recommendations'].append("Add Twitter Card meta tags")
        
        # Check if they have structured data (5 points)
        schema_markup = meta_data.get('schema_markup', [])
        if schema_markup:
            score += 5
            seo_analysis['factors']['has_schema_markup'] = True
            seo_analysis['factors']['schema_types'] = [schema.get('@type', 'Unknown') for schema in schema_markup]
        else:
            seo_analysis['recommendations'].append("Add structured data (Schema.org markup)")
        
        # Check if the page is too big (5 points)
        # This is a basic check - in production, you'd use actual page speed APIs
        content_length = len(html_content)
        if content_length < 500000:  # Less than 500KB
            score += 5
            seo_analysis['factors']['reasonable_page_size'] = True
        else:
            seo_analysis['recommendations'].append("Page size is large, consider optimization")
        
        seo_analysis['factors']['page_size_bytes'] = content_length
        
        # Check if it works on phones (5 points)
        viewport = meta_data.get('viewport', '')
        if 'width=device-width' in viewport:
            score += 5
            seo_analysis['factors']['mobile_friendly'] = True
        else:
            seo_analysis['recommendations'].append("Add responsive viewport meta tag")
        
        # Add up the final score
        seo_analysis['score'] = min(score, max_score)
        seo_analysis['grade'] = self.get_seo_grade(seo_analysis['score'])
        
        return seo_analysis
    
    def get_seo_grade(self, score):
        """Turn the number score into a letter grade like A, B, C"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    async def scrape_seo_data(self, company_name, url):
        """Go to a webpage and check how good it is for search engines"""
        try:
            print(f"🔍 Scraping SEO data from: {url}")
            
            async with AsyncWebCrawler(verbose=True) as crawler:
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
                
                print(f"✅ Successfully scraped SEO data")
                
                # Get all the meta info and give it a B2B-focused score
                meta_data = self.extract_meta_tags(result.cleaned_html, url)
                seo_analysis = self.calculate_b2b_seo_score(meta_data, result.cleaned_html, url)
                
                # Put everything together
                page_data = {
                    "url": url,
                    "scraped_at": datetime.now().isoformat(),
                    "meta_tags": meta_data,
                    "seo_analysis": seo_analysis,
                    "raw_content_length": len(result.cleaned_html)
                }
                
                return page_data
                
        except Exception as e:
            print(f"❌ Error scraping SEO data {url}: {e}")
            return None
    
    def save_seo_data(self, company_name, seo_data):
        """Save the SEO info to a file"""
        try:
            company_file = self.data_dir / f"{company_name.lower().replace(' ', '_')}_data.json"
            
            if not company_file.exists():
                print(f"❌ Company file not found: {company_file}")
                return False
                
            # Get the existing data
            with open(company_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Make sure we have a place to put SEO data
            if 'seo_data' not in data:
                data['seo_data'] = {}
            
            # Add the new SEO data
            data['seo_data'].update(seo_data)
            data['last_updated'] = datetime.now().isoformat()
            
            # Save it back to the file
            with open(company_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 SEO data saved to: {company_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving SEO data: {e}")
            return False
    
    async def scrape_and_save_seo(self, company_name, url):
        """Do everything: check the SEO and save the results"""
        print(f"\n🔍 Scraping SEO data for: {company_name}")
        print(f"🌐 URL: {url}")
        print("-" * 50)
        
        # Go check the SEO
        page_data = await self.scrape_seo_data(company_name, url)
        
        if not page_data:
            print("❌ Scraping failed. No data to save.")
            return False
        
        # Make a name for this page
        page_id = self.create_page_id(url)
        
        # Save everything
        seo_data = {page_id: page_data}
        success = self.save_seo_data(company_name, seo_data)
        
        if success:
            seo_score = page_data['seo_analysis']['score']
            seo_grade = page_data['seo_analysis']['grade']
            print(f"✅ SEO data collected for {company_name}")
            print(f"📊 SEO Score: {seo_score}/100 (Grade: {seo_grade})")
            print(f"🔍 Found {len(page_data['meta_tags']['og_tags'])} Open Graph tags")
            print(f"🐦 Found {len(page_data['meta_tags']['twitter_tags'])} Twitter Card tags")
            print(f"\n💡 To analyze this SEO data, use 'Run analysis prompt' (option 4) and select 'seo_analysis' as data source")
        else:
            print(f"❌ Failed to collect SEO data for {company_name}")
            
        return success
    
    def create_page_id(self, url):
        """Make a simple name for the page from the URL"""
        path = urlparse(url).path
        # Take the URL and split it up
        path_parts = [part for part in path.strip('/').split('/') if part]
        
        if path_parts:
            # Use the last part of the URL as the name
            page_id = path_parts[-1].replace('-', '_').replace('.', '_')
        else:
            # If that doesn't work, use the website name
            domain = urlparse(url).netloc
            page_id = domain.replace('.', '_')
        
        return page_id

# Test function
async def test_seo_scraper():
    """Try it out with a test website"""
    scraper = MetaSEOScraper()
    success = await scraper.scrape_and_save_seo("TestCompany", "https://stripe.com")
    return success

if __name__ == "__main__":
    asyncio.run(test_seo_scraper())
