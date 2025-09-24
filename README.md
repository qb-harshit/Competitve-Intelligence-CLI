<<<<<<< HEAD
---
Competitive Intelligence CLI which I use with QBack.AI
=======
# Competitive Intelligence CLI which I use with QBack.AI

>>>>>>> 540c3f6c5b789b8087286cd8333829f948826030
subscribe to my newsletter as I build apps like these for product marketing use cases: https://newsletter.qback.ai/

⚠️ IMPORTANT DISCLAIMER: This is a very simplified version of competitive intelligence tools. Please make your own version, edit your own prompts, and do your own setup as per whatever you want to do. This tool is provided as a starting point and should be customized for your specific needs and use cases.

<<<<<<< HEAD
A powerful command-line tool for scraping and analyzing competitor websites to gather competitive intelligence insights. I run this along side QBack.AI for both buyer + competitor analysis and create all sales and launch assets like battlecard, FAQs, sales objections, feature matrix, etc.
=======
A powerful command-line tool for scraping and analyzing competitor websites to gather competitive intelligence insights.
I run this along side [QBack.AI](https://www.qback.ai/) for both buyer + competitor analysis and create all sales and launch assets like battlecard, FAQs, sales objections, feature matrix, etc.
>>>>>>> 540c3f6c5b789b8087286cd8333829f948826030

## Features

### 📊 Basic Scraping
- 🕷️ **Web Scraping**: Extract clean content from homepages and feature pages
- 🗺️ **Sitemap Analysis**: Automatically find and scrape feature-related pages
- 🧹 **Content Cleaning**: Remove HTML/CSS clutter, keep only meaningful text
- 🔍 **Custom Analysis**: Run any analysis prompt on scraped data
- 📊 **Comprehensive Reports**: Generate markdown reports with all analysis results
- 💾 **Data Storage**: Organized JSON storage per company

### 💰 Additional Scraping Features
- 💰 **Pricing & Availability**: Extract pricing models and service availability
- 🔍 **SEO Analysis**: Focus on keywords, trust signals, and business value propositions

## Quick Start

1. **Run the CLI**:
   ```bash
   python main.py
   ```

2. **Follow the menu-driven interface** to add companies, scrape data, and run analysis.

## Step-by-Step User Guide

### Step 1: Add a Company
1. Choose option `1` from the main menu
2. Enter company name (e.g., "Stripe")
3. Company is added to the system

### Step 2: Scrape Homepage
1. Choose option `2` from the main menu
2. Enter company name
3. Enter homepage URL (e.g., "https://stripe.com")
4. System scrapes and cleans the content automatically

### Step 3: Analyze Sitemap (Optional)
1. Choose option `3` from the main menu
2. Enter company name
3. Enter sitemap URL (e.g., "https://stripe.com/sitemap.xml")
4. Enter keywords to filter pages (e.g., "features,api,pricing,customers,faq")
5. Choose which categories to scrape:
   - All categories
   - Features only
   - Products only
   - Pricing only
   - Customers only (case studies, testimonials, success stories)
   - FAQ only (frequently asked questions, support, help center)
   - API/Documentation only
   - Custom selection
6. System scrapes all selected pages

### Step 4: Run Analysis Prompts
1. Choose option `4` from the main menu
2. Enter company name
3. Select data source:
   - Individual pages (homepage, specific features)
   - All data combined
4. Enter your analysis prompt (see examples below)
5. Review the analysis result
6. Save with a descriptive name

### Step 5: Additional Features
1. **Pricing & Availability**: Choose option `5` to scrape pricing and service availability
2. **SEO Analysis**: Choose option `6` to analyze SEO and trust signals

### Step 6: View Results
1. Choose option `7` to view company data
2. See all scraped content and analysis results
3. Check the markdown reports in `data/companies/[company]/` folder
4. Choose option `8` to list all tracked companies

## Analysis Prompt Examples

Copy and paste these prompts from `prompts/prompt_library.md`:

### Feature Analysis
```
Extract all features and their descriptions from the content
```

### Pricing Analysis
```
Find pricing information and plans
```

### Competitive Analysis
```
Identify strengths and weaknesses
```

### Technical Analysis
```
List all API endpoints mentioned
```

### Business Analysis
```
Find funding and investment information
```

### Customer Analysis
```
Extract customer success stories and case studies
```

### FAQ Analysis
```
Extract frequently asked questions and common concerns
```

## Additional Features Guide

### B2B Pricing & Availability Monitoring
- **Enterprise Price Extraction**: Automatically finds B2B pricing using multiple patterns ($123.45/user, €123.45/seat, etc.)
- **Service Availability**: Detects B2B service status (available now, contact sales, enterprise ready, etc.)
- **Deployment Options**: Identifies cloud, SaaS, on-premise, hybrid deployment models
- **Contact Requirements**: Tracks B2B sales processes (contact sales, request demo, custom pricing)
- **Price Tracking**: Monitors B2B pricing changes over time with percentage calculations
- **Alerts**: Get notified when enterprise pricing changes by specified thresholds

### B2B SEO Analysis
- **Enterprise Meta Tags**: Extracts B2B-focused meta tags including Open Graph, Twitter Cards
- **B2B Keywords Detection**: Identifies enterprise, business, professional, solution keywords in titles
- **Trust Signals**: Detects security, compliance, certifications (SOC2, ISO, GDPR, HIPAA)
- **B2B Value Propositions**: Analyzes enterprise, scalable, secure, integration keywords in descriptions
- **Business Content Structure**: Evaluates B2B content sections (features, pricing, enterprise, API, security)
- **Technical Analysis**: Analyzes viewport, robots, canonical, and other technical tags


## File Structure

```
comp_intel/
├── data/
│   └── companies/
│       ├── [company_name]/
│       │   ├── [analysis_name].md (custom analysis files)
│       └── [company_name]_data.json
├── prompts/
│   └── prompt_library.md
├── scrapers/
│   ├── homepage_scraper.py
│   ├── sitemap_analyzer.py
│   ├── price_stock_scraper.py
│   └── meta_seo_scraper.py
├── utils/
│   └── prompt_executor.py
├── main.py
└── requirements.txt
```

## Data Storage

### JSON Files
- **Location**: `data/companies/[company_name]_data.json`
- **Contains**: All scraped content, metadata, pricing data, SEO data
- **Format**: Consolidated JSON per company

### Markdown Reports
- **Location**: `data/companies/[company_name]/[analysis_name].md`
- **Contains**: Individual analysis results saved with custom names
- **Format**: Professional markdown with timestamps
- **Multiple Files**: Each analysis is saved as a separate file for better organization


## URL Categorization

The system automatically categorizes URLs based on keywords with **full plural form support**:

### Sitemap Analyzer Categories
- **Features**: `feature`, `features`, `capability`, `capabilities`, `function`, `functions`
- **Products**: `product`, `products`, `service`, `services`, `solution`, `solutions`, `tool`, `tools`, `platform`, `platforms`, `software`, `app`, `apps`
- **Pricing**: `pricing`, `price`, `prices`, `cost`, `costs`, `plan`, `plans`, `subscription`, `subscriptions`
- **Customers**: `customer`, `customers`, `case-study`, `case-studies`, `success-story`, `success-stories`, `testimonial`, `testimonials`, `review`, `reviews`, `client`, `clients`
- **FAQ**: `faq`, `frequently-asked-questions`, `frequently-asked`, `questions`, `help`, `support`
- **API**: `api`, `apis`, `developer`, `developers`, `sdk`, `sdks`, `integration`, `integrations`
- **Documentation**: `doc`, `docs`, `documentation`, `documentations`, `guide`, `guides`, `tutorial`, `tutorials`, `manual`, `manuals`, `wiki`, `wikis`


## Content Quality

The system automatically:
- ✅ Removes HTML/CSS clutter
- ✅ Preserves all essential content
- ✅ Maintains text structure
- ✅ Filters out navigation elements
- ✅ Keeps meaningful sentences

**Typical content extraction**: 70,000+ characters of clean text per homepage

## Recent Improvements

### 🎯 Enhanced Analysis System
- **Multiple Data Source Selection**: Select multiple data sources for analysis (comma-separated numbers)
- **Custom Analysis File Names**: Save analyses with custom names instead of hardcoded filenames
- **Individual Analysis Files**: Each analysis is saved as a separate markdown file for better organization
- **SEO Analysis Integration**: SEO data is now available as an analysis source alongside homepage and features

### 🔍 Improved Data Management
- **Session Management**: CLI remembers the current company until you exit or switch
- **Better Input Handling**: Fixed CLI flow to wait for user input and prevent jumping ahead
- **Cleaner Menu Structure**: Simplified menu with 9 options (removed redundant features)
- **Honest Feature Claims**: Removed misleading automation claims - all features are manual/on-demand

### 🗑️ Removed Features (For Honesty & Simplicity)
- **Link Collection**: Removed redundant link collection feature (option 7)
- **Price Tracking**: Removed automated price tracking claims
- **Automated Scheduling**: Removed misleading automation features
- **Alert System**: Removed automated alert system
- **Monitoring Dashboard**: Removed automated monitoring claims

### 📁 File Organization Improvements
- **Individual Analysis Files**: Each analysis is saved as a separate markdown file
- **Custom File Names**: Users can name their analysis files (e.g., "seo_insights.md", "pricing_analysis.md")
- **Better Organization**: No more single large analysis file - each analysis is independent

## Menu Options

1. **Add new company** - Add a competitor to track
2. **Scrape homepage** - Extract homepage content
3. **Analyze sitemap** - Find and scrape feature pages
4. **Run analysis prompt** - Analyze data with custom prompts (supports multiple data sources)
5. **Scrape pricing & availability data** - Extract pricing and availability information
6. **Analyze SEO & meta tags** - Extract meta tags and SEO information
7. **View company data** - See all scraped data and results
8. **List all companies** - View all tracked companies
9. **Exit** - Close the application

## Tips for Best Results

### Sitemap Analysis
- Use specific keywords: "api", "features", "pricing", "products", "customers", "faq"
- **Smart keyword matching**: When you search for "customers", it automatically finds:
  - `customers`, `customer`
  - `case-studies`, `case-studies` 
  - `success-stories`, `testimonials`
  - `reviews`, `clients`, `stories`
- **Plural forms supported**: The system automatically detects both "feature" and "features", "product" and "products", etc.
- Choose "API/Documentation only" for technical analysis
- Choose "Customers only" for customer success stories, case studies, and testimonials
- Choose "FAQ only" for frequently asked questions and support content
- Choose "All categories" for comprehensive analysis

### Analysis Prompts
- Be specific: "Extract all pricing plans and their costs"
- Use action words: "Find", "List", "Identify", "Extract"
- Combine multiple aspects: "Find pricing and feature limitations"

### Data Sources
- **Homepage only**: For general company overview
- **Specific features**: For detailed feature analysis
- **SEO analysis**: For SEO and meta tag analysis
- **Multiple sources**: Select multiple sources with comma-separated numbers (e.g., 1,3,5)
- **All data**: For comprehensive competitive intelligence

## Example Workflow

### Basic Workflow
1. **Add Company**: "Stripe"
2. **Scrape Homepage**: "https://stripe.com"
3. **Analyze Sitemap**: "https://stripe.com/sitemap.xml" with keywords "api,features,pricing,customers,faq"
4. **Run Analysis**:
   - "Extract all features and their descriptions"
   - "Find pricing information and plans"
   - "Extract customer success stories and case studies"
   - "Extract frequently asked questions and common concerns"
   - "Identify competitive advantages"
5. **Review Reports**: Check individual analysis files in `data/companies/stripe/` folder

### Additional Features Workflow
6. **Price Monitoring**: Scrape "https://stripe.com/pricing" for pricing and availability data
7. **SEO Analysis**: Analyze "https://stripe.com" for meta tags and SEO scoring
8. **View Results**: Check all collected data and analysis results

## Troubleshooting

### Common Issues
- **Company not found**: Make sure to add the company first
- **No data available**: Scrape homepage or sitemap first
- **Scraping fails**: Check URL format and internet connection

### File Locations
- **Company data**: `data/companies/[company_name]_data.json`
- **Analysis reports**: `data/companies/[company_name]/[analysis_name].md`
- **Prompt library**: `prompts/prompt_library.md`

## Support

For issues or questions:
1. Check the file structure matches the expected format
2. Verify all dependencies are installed
3. Ensure URLs are accessible and properly formatted

---

**Ready to start competitive intelligence gathering!** 🚀
