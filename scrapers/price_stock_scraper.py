"""
This finds prices and stock info on websites
Like checking if something is in stock or how much it costs
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

class PriceStockScraper:
    def __init__(self):
        self.data_dir = Path("data/companies")
        
    def extract_pricing_data(self, html_content, url):
        """Look for prices on the webpage"""
        if not html_content:
            return {}
            
        soup = BeautifulSoup(html_content, 'html.parser')
        pricing_data = {
            'prices': [],
            'plans': [],
            'currency': None,
            'currencies_found': [],  # Track all currencies found on the page
            'billing_periods': [],
            'discounts': [],
            'free_trials': []
        }
        
        # Look for prices in all major currencies
        price_patterns = [
            # Dollar formats
            r'\$(\d+(?:\.\d{2})?)',  # $99.99
            r'(\d+(?:\.\d{2})?)\s*(?:USD|dollars?)',  # 99.99 USD
            r'C\$(\d+(?:\.\d{2})?)',  # C$99.99 (Canadian)
            r'A\$(\d+(?:\.\d{2})?)',  # A$99.99 (Australian)
            
            # Euro formats
            r'€(\d+(?:\.\d{2})?)',  # €99.99
            r'(\d+(?:\.\d{2})?)\s*(?:EUR|euros?)',  # 99.99 EUR
            
            # Pound formats
            r'£(\d+(?:\.\d{2})?)',  # £99.99
            r'(\d+(?:\.\d{2})?)\s*(?:GBP|pounds?)',  # 99.99 GBP
            
            # Rupee formats
            r'₹(\d+(?:\.\d{2})?)',  # ₹99.99
            r'(\d+(?:\.\d{2})?)\s*(?:INR|rupees?)',  # 99.99 INR
            
            # Yen formats
            r'¥(\d+(?:\.\d{2})?)',  # ¥99.99
            r'(\d+(?:\.\d{2})?)\s*(?:JPY|yen)',  # 99.99 JPY
            
            # Won format
            r'₩(\d+(?:\.\d{2})?)',  # ₩99.99
            r'(\d+(?:\.\d{2})?)\s*(?:KRW|won)',  # 99.99 KRW
            
            # B2B-specific patterns
            r'(\d+(?:\.\d{2})?)\s*(?:per|/)\s*(?:month|year|mo|yr|user|seat|license)',  # 99.99 per user/month
            r'from\s*[€£₹¥₩\$]?(\d+(?:\.\d{2})?)',  # from $99.99, from €99.99, etc.
            r'starting\s*at\s*[€£₹¥₩\$]?(\d+(?:\.\d{2})?)',  # starting at $99.99
            r'(\d+(?:\.\d{2})?)\s*(?:monthly|yearly|per\s*month|per\s*year|per\s*user|per\s*seat)',  # 99.99 per user
            r'contact\s*sales|request\s*quote|custom\s*pricing|enterprise\s*pricing',  # B2B pricing models
        ]
        
        # Get all the text from the page
        text_content = soup.get_text()
        
        # Find all the prices with their currency context
        for pattern in price_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match)
                    if 0 < price < 10000:  # Only keep prices that make sense
                        # Try to determine currency from the pattern
                        currency = None
                        if '$' in pattern and 'C$' not in pattern and 'A$' not in pattern:
                            currency = 'USD'
                        elif 'C$' in pattern:
                            currency = 'CAD'
                        elif 'A$' in pattern:
                            currency = 'AUD'
                        elif '€' in pattern:
                            currency = 'EUR'
                        elif '£' in pattern:
                            currency = 'GBP'
                        elif '₹' in pattern:
                            currency = 'INR'
                        elif '¥' in pattern:
                            currency = 'JPY'
                        elif '₩' in pattern:
                            currency = 'KRW'
                        
                        # Store price with currency info
                        price_info = {
                            'amount': price,
                            'currency': currency,
                            'pattern_used': pattern
                        }
                        pricing_data['prices'].append(price_info)
                except ValueError:
                    continue
        
        # Look for plan names like "Basic Plan" or "Pro Package"
        plan_selectors = [
            '[class*="plan"]', '[class*="pricing"]', '[class*="tier"]',
            '[class*="package"]', '[class*="subscription"]'
        ]
        
        for selector in plan_selectors:
            elements = soup.select(selector)
            for element in elements:
                plan_text = element.get_text(strip=True)
                if plan_text and len(plan_text) > 10:
                    pricing_data['plans'].append(plan_text)
        
        # Check what currency they're using (USD, EUR, GBP, INR, JPY, etc.)
        currency_patterns = {
            'USD': [r'\$', r'USD', r'US\$', r'dollars?', r'US\s*dollars?'],
            'EUR': [r'€', r'EUR', r'euros?', r'euro'],
            'GBP': [r'£', r'GBP', r'pounds?', r'sterling', r'British\s*pounds?'],
            'INR': [r'₹', r'INR', r'rupees?', r'rupee', r'Indian\s*rupees?'],
            'JPY': [r'¥', r'JPY', r'yen', r'Japanese\s*yen'],
            'CAD': [r'C\$', r'CAD', r'Canadian\s*dollars?'],
            'AUD': [r'A\$', r'AUD', r'Australian\s*dollars?'],
            'CHF': [r'CHF', r'Swiss\s*francs?'],
            'CNY': [r'¥', r'CNY', r'Chinese\s*yuan', r'renminbi'],
            'KRW': [r'₩', r'KRW', r'Korean\s*won']
        }
        
        # Look for currency symbols and text
        for currency, patterns in currency_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_content, re.IGNORECASE):
                    if currency not in pricing_data['currencies_found']:
                        pricing_data['currencies_found'].append(currency)
                    if not pricing_data['currency']:  # Set primary currency to first found
                        pricing_data['currency'] = currency
                    break
        
        # Look for billing info like "per month" or "yearly"
        billing_patterns = [
            r'(?:per|/)\s*(month|year|mo|yr|annually|monthly)',
            r'(monthly|yearly|annual)',
            r'(billed\s+(?:monthly|yearly|annually))'
        ]
        
        for pattern in billing_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            pricing_data['billing_periods'].extend(matches)
        
        # Look for discounts like "20% off" or "save 15%"
        discount_patterns = [
            r'(\d+)%\s*(?:off|discount)',
            r'save\s*(\d+)%',
            r'(\d+)\s*(?:percent|%)\s*(?:off|discount)'
        ]
        
        for pattern in discount_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            pricing_data['discounts'].extend(matches)
        
        # Look for free trials like "14 day free trial"
        trial_patterns = [
            r'(\d+)\s*(?:day|week|month)s?\s*(?:free|trial)',
            r'free\s*(?:trial|for)\s*(\d+)\s*(?:day|week|month)s?',
            r'(\d+)\s*(?:day|week|month)s?\s*(?:trial|free)'
        ]
        
        for pattern in trial_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            pricing_data['free_trials'].extend(matches)
        
        # Get rid of duplicates and keep only the first 10 plans
        # Remove duplicate prices (based on amount and currency)
        unique_prices = []
        seen_prices = set()
        for price_info in pricing_data['prices']:
            price_key = (price_info['amount'], price_info['currency'])
            if price_key not in seen_prices:
                unique_prices.append(price_info)
                seen_prices.add(price_key)
        pricing_data['prices'] = unique_prices[:20]  # Keep up to 20 unique prices
        
        pricing_data['plans'] = list(set(pricing_data['plans']))[:10]  # Don't keep too many plans
        pricing_data['billing_periods'] = list(set(pricing_data['billing_periods']))
        pricing_data['discounts'] = list(set(pricing_data['discounts']))
        pricing_data['free_trials'] = list(set(pricing_data['free_trials']))
        
        return pricing_data
    
    def extract_availability_data(self, html_content, url):
        """Check B2B availability and service status"""
        if not html_content:
            return {}
            
        soup = BeautifulSoup(html_content, 'html.parser')
        availability_data = {
            'service_status': [],
            'availability_indicators': [],
            'deployment_options': [],
            'contact_requirements': []
        }
        
        # Look for B2B service availability patterns
        availability_patterns = [
            r'(?:available\s*now|ready\s*for\s*deployment|live\s*service)',
            r'(?:coming\s*soon|beta|preview|early\s*access)',
            r'(?:contact\s*sales|request\s*demo|schedule\s*call)',
            r'(?:enterprise\s*ready|production\s*ready|scalable)'
        ]
        
        text_content = soup.get_text()
        
        for pattern in availability_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            availability_data['service_status'].extend(matches)
        
        # Look for deployment and service options
        deployment_patterns = [
            r'(?:cloud|saas|on-premise|hybrid|self-hosted)',
            r'(?:api\s*access|sdk|integration|webhook)',
            r'(?:white-label|custom\s*deployment|dedicated)'
        ]
        
        for pattern in deployment_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            availability_data['deployment_options'].extend(matches)
        
        # Look for contact requirements (B2B sales process)
        contact_patterns = [
            r'(?:contact\s*sales|speak\s*to\s*sales|sales\s*team)',
            r'(?:request\s*quote|get\s*quote|custom\s*pricing)',
            r'(?:enterprise\s*contact|business\s*inquiry)'
        ]
        
        for pattern in contact_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            availability_data['contact_requirements'].extend(matches)
        
        # Get rid of duplicates
        availability_data['service_status'] = list(set(availability_data['service_status']))
        availability_data['deployment_options'] = list(set(availability_data['deployment_options']))
        availability_data['contact_requirements'] = list(set(availability_data['contact_requirements']))
        
        return availability_data
    
    async def scrape_pricing_page(self, company_name, url):
        """Go to a webpage and grab all the pricing info"""
        try:
            print(f"💰 Scraping pricing data from: {url}")
            
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
                
                print(f"✅ Successfully scraped pricing page")
                
                # Get the prices and availability info from the page
                pricing_data = self.extract_pricing_data(result.cleaned_html, url)
                availability_data = self.extract_availability_data(result.cleaned_html, url)
                
                # Put everything together
                page_data = {
                    "url": url,
                    "scraped_at": datetime.now().isoformat(),
                    "pricing": pricing_data,
                    "availability": availability_data,
                    "raw_content_length": len(result.cleaned_html)
                }
                
                return page_data
                
        except Exception as e:
            print(f"❌ Error scraping pricing page {url}: {e}")
            return None
    
    def save_pricing_data(self, company_name, pricing_data):
        """Save the pricing info to a file"""
        try:
            company_file = self.data_dir / f"{company_name.lower().replace(' ', '_')}_data.json"
            
            if not company_file.exists():
                print(f"❌ Company file not found: {company_file}")
                return False
                
            # Get the existing data
            with open(company_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Make sure we have a place to put pricing data
            if 'pricing_data' not in data:
                data['pricing_data'] = {}
            
            # Add the new pricing data
            data['pricing_data'].update(pricing_data)
            data['last_updated'] = datetime.now().isoformat()
            
            # Save it back to the file
            with open(company_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Pricing data saved to: {company_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving pricing data: {e}")
            return False
    
    async def scrape_and_save_pricing(self, company_name, url):
        """Do everything: scrape the page and save the data"""
        print(f"\n💰 Scraping pricing data for: {company_name}")
        print(f"🌐 URL: {url}")
        print("-" * 50)
        
        # Go get the pricing info
        page_data = await self.scrape_pricing_page(company_name, url)
        
        if not page_data:
            print("❌ Scraping failed. No data to save.")
            return False
        
        # Make a name for this page
        page_id = self.create_page_id(url)
        
        # Save everything
        pricing_data = {page_id: page_data}
        success = self.save_pricing_data(company_name, pricing_data)
        
        if success:
            print(f"✅ Pricing scraping completed for {company_name}")
            print(f"💰 Found {len(page_data['pricing']['prices'])} prices")
            print(f"💱 Currencies found: {', '.join(page_data['pricing']['currencies_found']) if page_data['pricing']['currencies_found'] else 'None detected'}")
            print(f"🚀 Found {len(page_data['availability']['service_status'])} service status indicators")
            print(f"📞 Found {len(page_data['availability']['contact_requirements'])} contact requirements")
        else:
            print(f"❌ Failed to save pricing data for {company_name}")
            
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
    
    def get_currency_info(self, currency_code):
        """Get information about a currency"""
        currency_info = {
            'USD': {'name': 'US Dollar', 'symbol': '$', 'region': 'United States'},
            'EUR': {'name': 'Euro', 'symbol': '€', 'region': 'European Union'},
            'GBP': {'name': 'British Pound', 'symbol': '£', 'region': 'United Kingdom'},
            'INR': {'name': 'Indian Rupee', 'symbol': '₹', 'region': 'India'},
            'JPY': {'name': 'Japanese Yen', 'symbol': '¥', 'region': 'Japan'},
            'CAD': {'name': 'Canadian Dollar', 'symbol': 'C$', 'region': 'Canada'},
            'AUD': {'name': 'Australian Dollar', 'symbol': 'A$', 'region': 'Australia'},
            'CHF': {'name': 'Swiss Franc', 'symbol': 'CHF', 'region': 'Switzerland'},
            'CNY': {'name': 'Chinese Yuan', 'symbol': '¥', 'region': 'China'},
            'KRW': {'name': 'Korean Won', 'symbol': '₩', 'region': 'South Korea'}
        }
        return currency_info.get(currency_code, {'name': 'Unknown', 'symbol': currency_code, 'region': 'Unknown'})
    
    def format_price_with_currency(self, price_info):
        """Format a price with proper currency symbol"""
        if isinstance(price_info, dict):
            amount = price_info.get('amount', 0)
            currency = price_info.get('currency', 'USD')
            currency_info = self.get_currency_info(currency)
            symbol = currency_info['symbol']
            return f"{symbol}{amount}"
        else:
            # Handle old format (just a number)
            return f"${price_info}"

# Test function
async def test_price_scraper():
    """Try it out with a test website"""
    scraper = PriceStockScraper()
    success = await scraper.scrape_and_save_pricing("TestCompany", "https://stripe.com/pricing")
    return success

if __name__ == "__main__":
    asyncio.run(test_price_scraper())
