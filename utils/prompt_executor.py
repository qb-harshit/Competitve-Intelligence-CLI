"""
Prompt executor for running analysis prompts on company data
"""

import json
import os
from openai import OpenAI
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class PromptExecutor:
    def __init__(self):
        self.data_dir = Path("data/companies")
        # Initialize OpenAI client (you'll need to set OPENAI_API_KEY environment variable)
        self.openai_client = None
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
        except Exception as e:
            print(f"⚠️ OpenAI not configured: {e}")
            print("💡 Set OPENAI_API_KEY environment variable to enable AI analysis with GPT-5-mini")
        
    def load_company_data(self, company_name: str) -> Optional[Dict]:
        """Load company data from JSON file"""
        try:
            company_file = self.data_dir / f"{company_name.lower().replace(' ', '_')}_data.json"
            
            if not company_file.exists():
                print(f"❌ Company file not found: {company_file}")
                return None
                
            with open(company_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
            
        except Exception as e:
            print(f"❌ Error loading company data: {e}")
            return None
    
    def save_analysis_result(self, company_name: str, analysis_name: str, result: str) -> bool:
        """Save analysis result to company data and markdown file"""
        try:
            company_file = self.data_dir / f"{company_name.lower().replace(' ', '_')}_data.json"
            
            # Load existing data
            with open(company_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add analysis result
            if 'analysis_results' not in data:
                data['analysis_results'] = {}
            
            data['analysis_results'][analysis_name] = {
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save updated data
            with open(company_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Save to markdown file
            self.save_to_markdown_report(company_name, analysis_name, result)
            
            print(f"💾 Analysis result saved: {analysis_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving analysis result: {e}")
            return False
    
    def save_to_markdown_report(self, company_name: str, analysis_name: str, result: str) -> bool:
        """Save analysis result to markdown report file"""
        try:
            # Create company directory if it doesn't exist
            company_dir = self.data_dir / company_name.lower().replace(' ', '_')
            company_dir.mkdir(exist_ok=True)
            
            # Markdown file path
            markdown_file = company_dir / "detailed_competitive_analysis.md"
            
            # Check if file exists to determine if we need to create header
            file_exists = markdown_file.exists()
            
            # Prepare the analysis content
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            analysis_content = f"""
## {analysis_name}
**Date:** {timestamp}

{result}

---

"""
            
            # Append to markdown file
            with open(markdown_file, 'a', encoding='utf-8') as f:
                if not file_exists:
                    # Create header for new file
                    header = f"""# {company_name} - Detailed Competitive Analysis

This document contains all competitive intelligence analysis results for {company_name}.

---
"""
                    f.write(header)
                
                f.write(analysis_content)
            
            print(f"📄 Analysis added to markdown report: {markdown_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving to markdown report: {e}")
            return False
    
    def get_available_data_sources(self, company_data: Dict) -> List[str]:
        """Get list of available data sources for analysis"""
        sources = []
        
        if company_data.get('homepage'):
            sources.append('homepage')
        
        if company_data.get('features'):
            for feature_name in company_data['features'].keys():
                sources.append(f'feature:{feature_name}')
        
        return sources
    
    def extract_content_for_analysis(self, company_data: Dict, data_source: str) -> str:
        """Extract content from specified data source"""
        if data_source == 'homepage':
            homepage = company_data.get('homepage')
            if homepage:
                return homepage.get('content', '')
            return ''
        
        elif data_source.startswith('feature:'):
            feature_name = data_source.replace('feature:', '')
            features = company_data.get('features', {})
            if feature_name in features:
                return features[feature_name].get('content', '')
            return ''
        
        elif data_source == 'all':
            # Combine all content
            all_content = []
            
            # Add homepage content
            homepage = company_data.get('homepage')
            if homepage and homepage.get('content'):
                all_content.append(f"HOMEPAGE CONTENT:\n{homepage['content']}\n")
            
            # Add feature content
            features = company_data.get('features', {})
            for feature_name, feature_data in features.items():
                if feature_data.get('content'):
                    all_content.append(f"FEATURE: {feature_name}\nURL: {feature_data.get('url', 'Unknown')}\nCONTENT:\n{feature_data['content']}\n")
            
            return '\n'.join(all_content)
        
        return ''
    
    def run_analysis_prompt(self, company_name: str, prompt: str, data_source: str = 'all') -> str:
        """Run analysis prompt on company data"""
        print(f"\n🔍 Running Analysis Prompt")
        print(f"Company: {company_name}")
        print(f"Data Source: {data_source}")
        print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        print("-" * 50)
        
        # Load company data
        company_data = self.load_company_data(company_name)
        if not company_data:
            return "❌ Failed to load company data"
        
        # Get available data sources
        available_sources = self.get_available_data_sources(company_data)
        if not available_sources:
            return "❌ No data available for analysis"
        
        # Validate data source
        if data_source != 'all' and data_source not in available_sources:
            print(f"❌ Invalid data source: {data_source}")
            print(f"Available sources: {', '.join(available_sources)}")
            return "❌ Invalid data source specified"
        
        # Extract content
        content = self.extract_content_for_analysis(company_data, data_source)
        if not content:
            return "❌ No content found in specified data source"
        
        print(f"📊 Content length: {len(content)} characters")
        
        # Run AI analysis
        if not self.openai_client:
            return "❌ OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        
        result = self.run_ai_analysis(prompt, content, data_source)
        
        return result
    
    def estimate_tokens(self, text: str) -> int:
        """Rough estimate of token count (1 token ≈ 4 characters)"""
        return len(text) // 4
    
    def chunk_content(self, content: str, max_chunk_size: int) -> List[str]:
        """Split content into chunks for processing (if needed in future)"""
        chunks = []
        for i in range(0, len(content), max_chunk_size):
            chunk = content[i:i + max_chunk_size]
            chunks.append(chunk)
        return chunks
    
    def run_ai_analysis(self, prompt: str, content: str, data_source: str) -> str:
        """Run actual AI analysis using OpenAI GPT-5-mini with large context window"""
        try:
            print("🤖 Running AI analysis with OpenAI GPT-5-mini (400K context window)...")
            
            # GPT-5-mini has 400,000 context window
            # We'll reserve space for prompt and response, allowing ~350K tokens for content
            max_content_tokens = 350000  # Reserve 50K tokens for prompt and response
            max_content_length = max_content_tokens * 4  # Convert to character estimate
            
            original_content_length = len(content)
            estimated_tokens = self.estimate_tokens(content)
            
            print(f"📊 Content: {len(content):,} characters (~{estimated_tokens:,} tokens)")
            
            if estimated_tokens > max_content_tokens:
                print(f"⚠️ Content exceeds token limit ({estimated_tokens:,} > {max_content_tokens:,} tokens)")
                print(f"📝 Truncating content to fit within context window")
                content = content[:max_content_length] + f"\n\n[Content truncated for analysis - original length: {original_content_length:,} characters (~{estimated_tokens:,} tokens)]"
                print(f"📊 Final content: {len(content):,} characters (~{self.estimate_tokens(content):,} tokens)")
            else:
                print(f"✅ Content fits within context window")
            
            # Create the analysis prompt
            system_prompt = """You are a competitive intelligence analyst with access to a large context window. Analyze the provided content thoroughly and respond to the user's prompt with detailed, actionable insights. Be comprehensive and specific in your analysis. Structure your response clearly with headings, bullet points, and detailed explanations. Take advantage of the large context to provide in-depth analysis."""
            
            final_token_count = self.estimate_tokens(content)
            user_prompt = f"""Data Source: {data_source}
Content Length: {len(content):,} characters (~{final_token_count:,} tokens)
Original Content Length: {original_content_length:,} characters (~{estimated_tokens:,} tokens)

User Analysis Request: {prompt}

Content to Analyze:
{content}

Please provide a comprehensive, detailed analysis based on the user's request. Use the full context available to provide thorough insights. You have access to a large context window, so be as detailed and comprehensive as possible."""

            # Call OpenAI API with GPT-5-mini and large output tokens
            response = self.openai_client.chat.completions.create(
                model="gpt-5-mini-2025-08-07",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=128000  # Use the full 128K output tokens
                # Note: GPT-5-mini only supports default temperature (1)
            )
            
            analysis_result = response.choices[0].message.content.strip()
            
            # Format the result
            formatted_result = f"ANALYSIS RESULT\n"
            formatted_result += f"Data Source: {data_source}\n"
            formatted_result += f"Content Length: {len(content):,} characters (~{final_token_count:,} tokens)\n"
            formatted_result += f"Original Content Length: {original_content_length:,} characters (~{estimated_tokens:,} tokens)\n"
            formatted_result += f"Analysis Prompt: {prompt}\n"
            formatted_result += f"Model: GPT-5-mini-2025-08-07 (400K context window, 128K max output tokens)\n"
            formatted_result += f"Output Tokens Used: ~{self.estimate_tokens(analysis_result):,} tokens\n\n"
            formatted_result += f"{analysis_result}\n"
            
            return formatted_result
            
        except Exception as e:
            print(f"❌ Error running AI analysis: {e}")
            return f"❌ Failed to run AI analysis: {str(e)}"
    
    
    def list_analysis_results(self, company_name: str) -> List[str]:
        """List all analysis results for a company"""
        company_data = self.load_company_data(company_name)
        if not company_data:
            return []
        
        analysis_results = company_data.get('analysis_results', {})
        return list(analysis_results.keys())
    
    def get_analysis_result(self, company_name: str, analysis_name: str) -> Optional[str]:
        """Get specific analysis result"""
        company_data = self.load_company_data(company_name)
        if not company_data:
            return None
        
        analysis_results = company_data.get('analysis_results', {})
        if analysis_name in analysis_results:
            return analysis_results[analysis_name].get('result', '')
        
        return None

# Test function
def test_prompt_executor():
    """Test the prompt executor"""
    executor = PromptExecutor()
    
    # Test with a company (you would need to have scraped data first)
    company_name = "Exa"
    prompt = "Extract all features and their descriptions from the content"
    data_source = "all"
    
    result = executor.run_analysis_prompt(company_name, prompt, data_source)
    print(f"Analysis Result:\n{result}")

if __name__ == "__main__":
    test_prompt_executor()
