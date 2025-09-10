# Competitive Intelligence CLI which I use with QBack.AI

> ⚠️ **IMPORTANT DISCLAIMER**: This is a very simplified version of competitive intelligence tools. Please make your own version, edit your own prompts, and do your own setup as per whatever you want to do. This tool is provided as a starting point and should be customized for your specific needs and use cases.

A powerful command-line tool for scraping and analyzing competitor websites to gather competitive intelligence insights.
I run this along side [QBack.AI](https://www.qback.ai/) for both buyer + competitor analysis and create all sales and launch assets like battlecard, FAQs, sales objections, feature matrix, etc.

## Features

- 🕷️ **Web Scraping**: Extract clean content from homepages and feature pages
- 🗺️ **Sitemap Analysis**: Automatically find and scrape feature-related pages
- 🧹 **Content Cleaning**: Remove HTML/CSS clutter, keep only meaningful text
- 🔍 **Custom Analysis**: Run any analysis prompt on scraped data
- 📊 **Comprehensive Reports**: Generate markdown reports with all analysis results
- 💾 **Data Storage**: Organized JSON storage per company

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

### Step 5: View Results
1. Choose option `6` to view company data
2. See all scraped content and analysis results
3. Check the markdown report in `data/companies/[company]/detailed_competitive_analysis.md`

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

## File Structure

```
comp_intel/
├── data/
│   └── companies/
│       ├── [company_name]/
│       │   └── detailed_competitive_analysis.md
│       └── [company_name]_data.json
├── prompts/
│   └── prompt_library.md
├── scrapers/
│   ├── homepage_scraper.py
│   └── sitemap_analyzer.py
├── utils/
│   └── prompt_executor.py
├── main.py
└── requirements.txt
```

## Data Storage

### JSON Files
- **Location**: `data/companies/[company_name]_data.json`
- **Contains**: All scraped content, metadata, analysis results
- **Format**: Consolidated JSON per company

### Markdown Reports
- **Location**: `data/companies/[company_name]/detailed_comparative_analysis.md`
- **Contains**: All analysis results in chronological order
- **Format**: Professional markdown with timestamps

## URL Categorization

The system automatically categorizes URLs based on keywords:

- **Features**: `feature`, `capability`, `function`
- **Products**: `product`, `service`, `solution`
- **Pricing**: `pricing`, `price`, `cost`, `plan`
- **Customers**: `customer`, `customers`, `case-study`, `case-studies`, `success-story`, `success-stories`, `testimonial`, `testimonials`, `client`, `clients`
- **FAQ**: `faq`, `frequently-asked-questions`, `frequently-asked`, `questions`, `support`, `help-center`, `knowledge-base`, `kb`
- **API**: `api`, `developer`, `docs`, `documentation`
- **Documentation**: `doc`, `guide`, `tutorial`, `help`
- **Other**: Everything else

## Content Quality

The system automatically:
- ✅ Removes HTML/CSS clutter
- ✅ Preserves all essential content
- ✅ Maintains text structure
- ✅ Filters out navigation elements
- ✅ Keeps meaningful sentences

**Typical content extraction**: 70,000+ characters of clean text per homepage

## Menu Options

1. **Add new company** - Add a competitor to track
2. **Scrape homepage** - Extract homepage content
3. **Analyze sitemap** - Find and scrape feature pages
4. **Run analysis prompt** - Analyze data with custom prompts
5. **Check for updates** - (Coming soon)
6. **View company data** - See all scraped data and results
7. **List all companies** - View all tracked companies
8. **Exit** - Close the application

## Tips for Best Results

### Sitemap Analysis
- Use specific keywords: "api", "features", "pricing", "products", "customers", "faq"
- Choose "API/Documentation only" for technical analysis
- Choose "Customers only" for customer success stories and case studies
- Choose "FAQ only" for frequently asked questions and support content
- Choose "All categories" for comprehensive analysis

### Analysis Prompts
- Be specific: "Extract all pricing plans and their costs"
- Use action words: "Find", "List", "Identify", "Extract"
- Combine multiple aspects: "Find pricing and feature limitations"

### Data Sources
- **Homepage only**: For general company overview
- **Specific features**: For detailed feature analysis
- **All data**: For comprehensive competitive intelligence

## Example Workflow

1. **Add Company**: "Stripe"
2. **Scrape Homepage**: "https://stripe.com"
3. **Analyze Sitemap**: "https://stripe.com/sitemap.xml" with keywords "api,features,pricing,customers,faq"
4. **Run Analysis**:
   - "Extract all features and their descriptions"
   - "Find pricing information and plans"
   - "Extract customer success stories and case studies"
   - "Extract frequently asked questions and common concerns"
   - "Identify competitive advantages"
5. **Review Report**: Check `data/companies/stripe/detailed_competitive_analysis.md`

## Troubleshooting

### Common Issues
- **Company not found**: Make sure to add the company first
- **No data available**: Scrape homepage or sitemap first
- **Scraping fails**: Check URL format and internet connection

### File Locations
- **Company data**: `data/companies/[company_name]_data.json`
- **Analysis reports**: `data/companies/[company_name]/detailed_competitive_analysis.md`
- **Prompt library**: `prompts/prompt_library.md`

## Support

For issues or questions:
1. Check the file structure matches the expected format
2. Verify all dependencies are installed
3. Ensure URLs are accessible and properly formatted

---

**Ready to start competitive intelligence gathering!** 🚀
