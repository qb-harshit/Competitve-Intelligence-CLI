#!/usr/bin/env python3
"""
Competitive Intelligence CLI
A command-line tool for scraping and analyzing competitor websites
"""

import os
import json
import sys
import asyncio
from datetime import datetime
from pathlib import Path
from scrapers.homepage_scraper import HomepageScraper
from scrapers.sitemap_analyzer import SitemapAnalyzer
from scrapers.price_stock_scraper import PriceStockScraper
from scrapers.meta_seo_scraper import MetaSEOScraper
from utils.prompt_executor import PromptExecutor

class CompetitiveIntelligenceCLI:
    def __init__(self):
        self.data_dir = Path("data/companies")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.current_company = None  # Track current company session
        
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "="*60)
        print("🏢 B2B Competitive Intelligence CLI")
        if self.current_company:
            print(f"📊 Current Company: {self.current_company}")
        else:
            print("📊 No company selected")
        print("="*60)
        print("1. Add new company")
        print("2. Scrape homepage")
        print("3. Analyze sitemap")
        print("4. Run analysis prompt")
        print("5. Scrape pricing & availability data")
        print("6. Analyze SEO & meta tags")
        print("7. View company data")
        print("8. List all companies")
        print("9. Exit")
        print("="*60)
        
    def safe_input(self, prompt):
        """Safely get user input with proper error handling"""
        try:
            return input(prompt).strip()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        except EOFError:
            print("\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Input error: {e}")
            return None
    
    def get_user_choice(self):
        """Get user menu choice"""
        while True:
            choice = self.safe_input("\nChoose option (1-9): ")
            if choice is None:
                return None
            if choice in [str(i) for i in range(1, 10)]:
                return int(choice)
            else:
                print("❌ Invalid choice. Please enter a number between 1-9.")
                # Don't continue the loop immediately, let user see the error
                continue
    
    def get_current_company(self):
        """Get current company or ask user to select one"""
        if self.current_company:
            return self.current_company
        
        # If no current company, ask user to select one
        print("\n📋 No company selected. Please choose:")
        print("1. Add new company")
        print("2. Select existing company")
        
        choice = self.safe_input("Choose option (1-2): ")
        if choice == "1":
            return self.add_company()
        elif choice == "2":
            return self.select_existing_company()
        else:
            print("❌ Invalid choice.")
            return None
    
    def select_existing_company(self):
        """Select from existing companies"""
        company_files = list(self.data_dir.glob("*_data.json"))
        
        if not company_files:
            print("📭 No companies found. Please add a company first.")
            return None
        
        print("\n📋 Available companies:")
        companies = []
        for i, company_file in enumerate(company_files, 1):
            try:
                with open(company_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                company_name = data.get('company_name', 'Unknown')
                companies.append(company_name)
                print(f"{i}. {company_name}")
            except Exception as e:
                print(f"❌ Error reading {company_file}: {e}")
        
        if not companies:
            print("📭 No valid companies found.")
            return None
        
        try:
            choice = self.safe_input(f"\nSelect company (1-{len(companies)}): ")
            if choice and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(companies):
                    self.current_company = companies[idx]
                    print(f"✅ Selected company: {self.current_company}")
                    return self.current_company
        except Exception as e:
            print(f"❌ Error selecting company: {e}")
        
        print("❌ Invalid selection.")
        return None
    
    def add_company(self):
        """Add a new company to track"""
        print("\n📝 Add New Company")
        print("-" * 30)
        
        company_name = self.safe_input("Enter company name: ")
        if not company_name:
            print("❌ Company name cannot be empty.")
            return None
            
        # Check if company already exists
        company_file = self.data_dir / f"{company_name.lower().replace(' ', '_')}_data.json"
        if company_file.exists():
            print(f"✅ Company '{company_name}' already exists. Setting as current company.")
            self.current_company = company_name
            return company_name
            
        # Create initial company data structure
        company_data = {
            "company_name": company_name,
            "created_at": datetime.now().isoformat(),
            "last_updated": None,
            "homepage": None,
            "features": {},
            "analysis_results": {}
        }
        
        # Save company data
        try:
            with open(company_file, 'w', encoding='utf-8') as f:
                json.dump(company_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Company '{company_name}' added successfully!")
            print(f"📁 Data saved to: {company_file}")
            self.current_company = company_name
            return company_name
        except Exception as e:
            print(f"❌ Error saving company data: {e}")
            return None
    
    def list_companies(self):
        """List all tracked companies"""
        print("\n📋 Tracked Companies")
        print("-" * 30)
        
        company_files = list(self.data_dir.glob("*_data.json"))
        
        if not company_files:
            print("📭 No companies found. Add a company first!")
            return
            
        for i, company_file in enumerate(company_files, 1):
            try:
                with open(company_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                company_name = data.get('company_name', 'Unknown')
                last_updated = data.get('last_updated', 'Never')
                homepage_status = "✅" if data.get('homepage') else "❌"
                features_count = len(data.get('features', {}))
                
                print(f"{i}. {company_name}")
                print(f"   📅 Last updated: {last_updated}")
                print(f"   🏠 Homepage: {homepage_status}")
                print(f"   🔧 Features: {features_count}")
                print()
                
            except Exception as e:
                print(f"❌ Error reading {company_file}: {e}")
    
    def scrape_homepage(self):
        """Scrape homepage for a company"""
        print("\n🕷️ Scrape Homepage")
        print("-" * 30)
        
        company_name = self.get_current_company()
        if not company_name:
            return
            
        url = self.safe_input("Enter homepage URL: ")
        if not url:
            print("❌ URL cannot be empty.")
            return
            
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Run the scraper
        try:
            scraper = HomepageScraper()
            success = asyncio.run(scraper.scrape_and_save(company_name, url))
            
            if success:
                print(f"\n✅ Homepage scraping completed for {company_name}")
            else:
                print(f"\n❌ Homepage scraping failed for {company_name}")
                
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
        
        # Always wait for user to press Enter before returning to menu
        self.safe_input("\nPress Enter to continue...")

    def analyze_sitemap(self):
        """Analyze sitemap and scrape feature pages"""
        print("\n🗺️ Analyze Sitemap")
        print("-" * 30)
        
        company_name = self.get_current_company()
        if not company_name:
            return
            
        sitemap_url = self.safe_input("Enter sitemap URL: ")
        if not sitemap_url:
            print("❌ Sitemap URL cannot be empty.")
            return
            
        # Validate URL format
        if not sitemap_url.startswith(('http://', 'https://')):
            sitemap_url = 'https://' + sitemap_url
            
        # Get keywords
        keywords_input = self.safe_input("Enter keywords to filter URLs (comma-separated, or press Enter for all): ")
        keywords = [kw.strip() for kw in keywords_input.split(',')] if keywords_input else None
        
        # Run the sitemap analyzer
        try:
            analyzer = SitemapAnalyzer()
            success = asyncio.run(analyzer.analyze_and_scrape_sitemap(company_name, sitemap_url, keywords))
            
            if success:
                print(f"\n✅ Sitemap analysis completed for {company_name}")
            else:
                print(f"\n❌ Sitemap analysis failed for {company_name}")
                
        except Exception as e:
            print(f"❌ Error during sitemap analysis: {e}")
        
        # Always wait for user to press Enter before returning to menu
        self.safe_input("\nPress Enter to continue...")

    def run_analysis_prompt(self):
        """Run analysis prompt on company data"""
        print("\n🔍 Run Analysis Prompt")
        print("-" * 30)
        
        company_name = self.get_current_company()
        if not company_name:
            return
        
        # Get available data sources
        executor = PromptExecutor()
        company_data = executor.load_company_data(company_name)
        if not company_data:
            return
        
        available_sources = executor.get_available_data_sources(company_data)
        if not available_sources:
            print("❌ No data available for analysis. Scrape some data first.")
            return
        
        print(f"\n📊 Available data sources:")
        for i, source in enumerate(available_sources, 1):
            print(f"{i}. {source}")
        print(f"{len(available_sources) + 1}. all (combine all data)")
        
        # Get data source selection (multiple selection support)
        print(f"\n💡 You can select multiple sources by separating numbers with commas (e.g., 1,3,5)")
        print(f"💡 Or select 'all' by entering: {len(available_sources) + 1}")
        
        try:
            choice_input = self.safe_input(f"\nSelect data source(s) (1-{len(available_sources) + 1}): ")
            if not choice_input:
                print("❌ No input provided.")
                return
            
            # Handle multiple selections
            if ',' in choice_input:
                # Multiple selections
                choices = [int(x.strip()) for x in choice_input.split(',')]
                if all(1 <= choice <= len(available_sources) for choice in choices):
                    data_sources = [available_sources[choice - 1] for choice in choices]
                    data_source = data_sources  # List of selected sources
                else:
                    print("❌ Invalid choice(s). All selections must be between 1 and", len(available_sources))
                    return
            else:
                # Single selection
            choice = int(choice_input)
            if 1 <= choice <= len(available_sources):
                data_source = available_sources[choice - 1]
            elif choice == len(available_sources) + 1:
                data_source = 'all'
            else:
                print("❌ Invalid choice.")
                return
        except ValueError:
            print("❌ Invalid input. Please enter numbers separated by commas.")
            return
        
        # Get analysis prompt
        print(f"\n💭 Enter your analysis prompt:")
        print("Examples:")
        print("- Extract all features and their descriptions")
        print("- Find pricing information and plans")
        print("- Identify strengths and weaknesses")
        print("- List all API endpoints mentioned")
        
        prompt = self.safe_input("\nPrompt: ")
        if not prompt:
            print("❌ Prompt cannot be empty.")
            return
        
        # Run the analysis
        try:
            result = executor.run_analysis_prompt(company_name, prompt, data_source)
            
            print(f"\n📋 Analysis Result:")
            print("=" * 50)
            print(result)
            print("=" * 50)
            
            # Ask if user wants to save the result
            save_choice = self.safe_input("\n💾 Save this analysis result? (y/n): ")
            if save_choice and save_choice.lower() in ['y', 'yes']:
                analysis_name = self.safe_input("Enter analysis name: ")
                if analysis_name:
                    success = executor.save_analysis_result(company_name, analysis_name, result)
                    if success:
                        print(f"✅ Analysis saved as: {analysis_name}")
                    else:
                        print("❌ Failed to save analysis result")
                else:
                    print("❌ Analysis name cannot be empty")
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
        
        # Always wait for user to press Enter before returning to menu
        self.safe_input("\nPress Enter to continue...")

    def view_company_data(self):
        """View detailed company data"""
        print("\n👁️ View Company Data")
        print("-" * 30)
        
        company_name = self.get_current_company()
        if not company_name:
            return
            
        company_file = self.data_dir / f"{company_name.lower().replace(' ', '_')}_data.json"
        
        if not company_file.exists():
            print(f"❌ Company '{company_name}' not found.")
            return
            
        try:
            with open(company_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"\n📊 Company: {data.get('company_name', 'Unknown')}")
            print(f"📅 Created: {data.get('created_at', 'Unknown')}")
            print(f"🔄 Last updated: {data.get('last_updated', 'Never')}")
            
            # Homepage info
            homepage = data.get('homepage')
            if homepage:
                print(f"\n🏠 Homepage:")
                print(f"   URL: {homepage.get('url', 'Unknown')}")
                print(f"   Scraped: {homepage.get('scraped_at', 'Unknown')}")
                content_length = len(homepage.get('content', ''))
                print(f"   Content: {content_length} characters")
                print(f"   Preview: {homepage.get('content', '')[:200]}...")
            else:
                print(f"\n🏠 Homepage: Not scraped yet")
            
            # Features info
            features = data.get('features', {})
            print(f"\n🔧 Features: {len(features)} pages")
            for feature_name, feature_data in features.items():
                print(f"   • {feature_name}: {feature_data.get('url', 'Unknown')}")
            
            # Analysis results
            analysis = data.get('analysis_results', {})
            print(f"\n📈 Analysis Results: {len(analysis)} completed")
            for analysis_name in analysis.keys():
                print(f"   • {analysis_name}")
                
        except Exception as e:
            print(f"❌ Error reading company data: {e}")
    
    def scrape_pricing_data(self):
        """Scrape pricing and availability data for a company"""
        print("\n💰 Scrape Pricing & Availability Data")
        print("-" * 30)
        
        company_name = self.get_current_company()
        if not company_name:
            return
            
        url = self.safe_input("Enter pricing page URL: ")
        if not url:
            print("❌ URL cannot be empty.")
            return
            
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Run the price scraper
        try:
            scraper = PriceStockScraper()
            success = asyncio.run(scraper.scrape_and_save_pricing(company_name, url))
            
            if success:
                print(f"\n✅ Pricing data scraping completed for {company_name}")
            else:
                print(f"\n❌ Pricing data scraping failed for {company_name}")
                
        except Exception as e:
            print(f"❌ Error during pricing scraping: {e}")
        
        # Always wait for user to press Enter before returning to menu
        self.safe_input("\nPress Enter to continue...")
    
    def scrape_seo_data(self):
        """Scrape SEO and meta tag data for a company"""
        print("\n🔍 Analyze SEO & Meta Tags")
        print("-" * 30)
        
        company_name = self.get_current_company()
        if not company_name:
            return
            
        url = self.safe_input("Enter page URL to analyze: ")
        if not url:
            print("❌ URL cannot be empty.")
            return
            
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Run the SEO scraper
        try:
            scraper = MetaSEOScraper()
            success = asyncio.run(scraper.scrape_and_save_seo(company_name, url))
            
            if success:
                print(f"\n✅ SEO analysis completed for {company_name}")
            else:
                print(f"\n❌ SEO analysis failed for {company_name}")
                
        except Exception as e:
            print(f"❌ Error during SEO analysis: {e}")
    
        # Always wait for user to press Enter before returning to menu
        self.safe_input("\nPress Enter to continue...")
    
    def run(self):
        """Main CLI loop"""
        print("🚀 Starting B2B Competitive Intelligence CLI...")
        
        while True:
            try:
                self.display_menu()
                choice = self.get_user_choice()
                
                if choice is None:
                    break
                elif choice == 1:
                    self.add_company()
                elif choice == 2:
                    self.scrape_homepage()
                elif choice == 3:
                    self.analyze_sitemap()
                elif choice == 4:
                    self.run_analysis_prompt()
                elif choice == 5:
                    self.scrape_pricing_data()
                elif choice == 6:
                    self.scrape_seo_data()
                elif choice == 7:
                    self.view_company_data()
                elif choice == 8:
                    self.list_companies()
                elif choice == 9:
                    print("👋 Goodbye!")
                    self.current_company = None  # Clear session
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                self.current_company = None  # Clear session
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    cli = CompetitiveIntelligenceCLI()
    cli.run()