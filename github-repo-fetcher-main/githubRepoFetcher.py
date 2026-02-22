import requests
import json
import os
from typing import Dict, List, Optional
import time   
import sys 
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime

class GitHubRepoFetcher:
    # Connection Through github API
    def __init__(self, token: str = None):
        """
        Initialize the GitHub repo fetcher with performance optimizations
        """
        # Base GitHub API URL used for all requests
        self.base_url = "https://api.github.com"

        # Default headers for GitHub API calls (required by GitHub)
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Repo-Fetcher"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
            
        # Created "github_exports" folder inside current working directory
        # This is where exported files will be saved later
        self.exports_dir = os.path.join(os.getcwd(), "github_exports")

         # Create the directory if it does not exist (avoid errors)
        os.makedirs(self.exports_dir, exist_ok=True)
        
        # Cache dictionary to store language results per repo
        # Prevents repeated API calls → faster performance
        self.language_cache = {}

        # Use a persistent session for faster HTTP requests
        # A session reuses the same TCP connection, reducing latency
        self.session = requests.Session()

        # Apply headers to ALL future requests made by this session
        self.session.headers.update(self.headers)
    
    def search_users(self, query: str) -> List[Dict]:
        """
        Fast user search with timeout
        """
        url = f"{self.base_url}/search/users"
        params = {"q": query, "per_page": 10}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except requests.exceptions.RequestException as e:
            print(f"❌ Error searching users: {e}")
            return []
    
    def get_user_repos_fast(self, username: str) -> List[Dict]:
        """
        Ultra-fast repository fetching with parallel requests
        """
        url = f"{self.base_url}/users/{username}/repos"
        all_repos = []
        
        # First request to get the first page and check rate limits
        try:
            response = self.session.get(url, params={"per_page": 100, "page": 1}, timeout=15)
            response.raise_for_status()
            
            # Check rate limits
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if remaining < 10:
                print(f"⚠️  Rate limit low: {remaining} requests remaining")
            
            first_page_repos = response.json()
            if not first_page_repos:
                return []
                
            all_repos.extend(first_page_repos)
            
            # Check if there are more pages
            if 'last' in response.links:
                last_page_url = response.links['last']['url']
                total_pages = int(last_page_url.split('page=')[-1])
                
                if total_pages > 1:
                    # Fetch remaining pages in parallel
                    def fetch_page(page):
                        try:
                            page_response = self.session.get(url, params={"per_page": 100, "page": page}, timeout=15)
                            page_response.raise_for_status()
                            return page_response.json()
                        except Exception as e:
                            print(f"❌ Error fetching page {page}: {e}")
                            return []
                    
                    # Limit concurrent requests to avoid rate limits
                    with ThreadPoolExecutor(max_workers=3) as executor:
                        future_to_page = {executor.submit(fetch_page, page): page 
                                       for page in range(2, min(total_pages + 1, 6))}  # Limit to 5 pages max
                        
                        for future in as_completed(future_to_page):
                            page_repos = future.result()
                            if page_repos:
                                all_repos.extend(page_repos)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching repositories: {e}")
        
        return all_repos
    
    def get_repo_languages_batch(self, repos: List[Dict], username: str) -> Dict[str, List[str]]:
        """
        Fetch languages for multiple repos in parallel
        """
        languages_map = {}
        
        def fetch_languages(repo):
            repo_name = repo['name']
            cache_key = f"{username}/{repo_name}"
            
            if cache_key in self.language_cache:
                return repo_name, self.language_cache[cache_key]
            
            url = f"{self.base_url}/repos/{username}/{repo_name}/languages"
            try:
                response = self.session.get(url, timeout=8)
                if response.status_code == 200:
                    languages = list(response.json().keys())
                    self.language_cache[cache_key] = languages
                    return repo_name, languages
                else:
                    return repo_name, []
            except Exception as e:
                print(f"❌ Error fetching languages for {repo_name}: {e}")
                return repo_name, []
        
        # Process languages in smaller batches to avoid rate limits
        batch_size = 10
        for i in range(0, len(repos), batch_size):
            batch = repos[i:i + batch_size]
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_repo = {executor.submit(fetch_languages, repo): repo for repo in batch}
                
                for future in as_completed(future_to_repo):
                    repo_name, languages = future.result()
                    languages_map[repo_name] = languages
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(repos):
                time.sleep(0.5)
        
        return languages_map
    
    def display_user_selection(self, users: List[Dict]) -> Optional[str]:
        """
        Display user search results and let user select one
        """
        if not users:
            print("❌ No users found!")
            return None
        
        print("\n🔍 Search Results:")
        print("=" * 60)
        for i, user in enumerate(users, 1):
            print(f"{i}. {user['login']}")
            if user.get('name'):
                print(f"   📛 Name: {user['name']}")
            if user.get('bio'):
                bio_preview = user['bio'][:100] + "..." if len(user['bio']) > 100 else user['bio']
                print(f"   📝 Bio: {bio_preview}")
            print(f"   👥 Followers: {user.get('followers', 0)} | 📂 Public Repos: {user.get('public_repos', 0)}")
            print("-" * 40)
        
        while True:
            try:
                choice = input("\n🎯 Select a user (number) or 'q' to quit: ").strip()
                if choice.lower() == 'q':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(users):
                    selected_user = users[choice_num - 1]
                    print(f"✅ Selected: {selected_user['login']}")
                    return selected_user['login']
                else:
                    print(f"❌ Please enter a number between 1 and {len(users)}")
            except ValueError:
                print("❌ Please enter a valid number or 'q' to quit")
    
    def display_repos_fast(self, repos: List[Dict], username: str):
        """
        Fast repository display with batch language fetching
        """
        if not repos:
            print(f"\n❌ No repositories found for user '{username}'")
            return
        
        print(f"\n📂 Repositories for {username} ({len(repos)} found)")
        print("=" * 80)
        
        # Get all languages in batches
        print("🔄 Fetching technology stacks...")
        languages_map = self.get_repo_languages_batch(repos, username)
        
        displayed_count = 0
        for i, repo in enumerate(repos, 1):
            # Limit display to first 20 repos to avoid overwhelming output
            if displayed_count >= 20 and len(repos) > 20:
                remaining = len(repos) - displayed_count
                print(f"\n... and {remaining} more repositories (see export for full list)")
                break
                
            print(f"\n{i}. {repo['name']}")
            print(f"   📖 {repo.get('description', 'No description')}")
            print(f"   ⭐ Stars: {repo.get('stargazers_count', 0)}")
            print(f"   🍴 Forks: {repo.get('forks_count', 0)}")
            print(f"   📅 Updated: {repo.get('updated_at', 'N/A')[:10]}")
            print(f"   🔗 {repo.get('html_url', 'N/A')}")
            
            # Display languages from batch
            repo_languages = languages_map.get(repo['name'], [])
            if repo_languages:
                print(f"   💻 Tech: {', '.join(repo_languages[:8])}{'...' if len(repo_languages) > 8 else ''}")
            elif repo.get('language'):
                print(f"   💻 Primary: {repo['language']}")
            
            if repo.get('has_issues') and repo.get('open_issues_count', 0) > 0:
                print(f"   🐛 Issues: {repo.get('open_issues_count', 0)} open")
            
            if repo.get('license'):
                print(f"   📜 License: {repo['license'].get('name', 'N/A')}")
            
            print("-" * 60)
            displayed_count += 1
    
    def export_to_json(self, repos: List[Dict], username: str, filename: str = None):
        """
        Export repository data to JSON file with proper path
        """
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{username}_repos_{timestamp}.json"
        
        # Ensure file is saved in exports directory
        filepath = os.path.join(self.exports_dir, filename)
        
        export_data = {
            "username": username,
            "fetched_at": datetime.datetime.now().isoformat(),
            "total_repositories": len(repos),
            "repositories": []
        }
        
        # Get languages in batch for export
        print("🔄 Gathering technology data for export...")
        languages_map = self.get_repo_languages_batch(repos, username)
        
        for repo in repos:
            repo_data = {
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "url": repo.get("html_url"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "watchers": repo.get("watchers_count"),
                "updated_at": repo.get("updated_at"),
                "created_at": repo.get("created_at"),
                "primary_language": repo.get("language"),
                "languages": languages_map.get(repo['name'], []),
                "has_issues": repo.get("has_issues"),
                "open_issues": repo.get("open_issues_count"),
                "license": repo.get("license", {}).get("name") if repo.get("license") else None,
                "size": repo.get("size"),
                "default_branch": repo.get("default_branch"),
                "archived": repo.get("archived"),
                "fork": repo.get("fork")
            }
            export_data["repositories"].append(repo_data)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Data exported to: {filepath}")
            print(f"📁 Full path: {os.path.abspath(filepath)}")
            
            # Show file size
            file_size = os.path.getsize(filepath)
            print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
    
    def show_export_directory(self):
        """Show the export directory and existing files"""
        print(f"\n📁 Export Directory: {os.path.abspath(self.exports_dir)}")
        
        if os.path.exists(self.exports_dir):
            files = [f for f in os.listdir(self.exports_dir) if f.endswith('.json')]
            if files:
                print(f"📂 Existing exports ({len(files)} files):")
                for file in sorted(files, reverse=True)[:10]:  # Show last 10 files
                    filepath = os.path.join(self.exports_dir, file)
                    size = os.path.getsize(filepath)
                    mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                    print(f"   • {file} ({size/1024:.1f} KB, {mod_time:%Y-%m-%d %H:%M})")
            else:
                print("   No export files yet")
        else:
            print("   Directory doesn't exist (will be created on first export)")
    
    def run(self):
        """
        Main program loop with performance optimizations
        """
        print("🚀 GitHub Repository Fetcher - ULTRA FAST")
        print("=" * 50)
        print("⚡ Parallel fetching enabled")
        print("💾 Export directory: ./github_exports/")
        
        # Show export directory info
        self.show_export_directory()
        
        while True:
            print("\n🎮 Options:")
            print("1. 🔍 Search for GitHub user")
            print("2. 📁 Show export directory")
            print("3. 🚪 Exit")
            
            choice = input("\n🎯 Enter your choice (1-3): ").strip()
            
            if choice == "1":
                self.search_and_display_fast()
            elif choice == "2":
                self.show_export_directory()
            elif choice == "3":
                print("👋 Goodbye!")
                if self.session:
                    self.session.close()
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def search_and_display_fast(self):
        """
        Optimized search and display flow
        """
        search_query = input("\n🔎 Enter GitHub username or name to search: ").strip()
        if not search_query:
            print("❌ Please enter a search query.")
            return
        
        print("🔄 Searching for users...")
        users = self.search_users(search_query)
        
        username = self.display_user_selection(users)
        if not username:
            return
        
        print(f"\n📥 Fetching repositories for {username} (fast mode)...")
        start_time = time.time()
        repos = self.get_user_repos_fast(username)
        fetch_time = time.time() - start_time
        
        if repos:
            print(f"✅ Found {len(repos)} repositories in {fetch_time:.2f} seconds")
            self.display_repos_fast(repos, username)
            
            # Export option
            export_choice = input("\n💾 Export to JSON file? (y/n): ").strip().lower()
            if export_choice in ['y', 'yes']:
                custom_name = input("Enter filename (or press Enter for auto-name): ").strip()
                self.export_to_json(repos, username, custom_name if custom_name else None)
        else:
            print(f"❌ No repositories found for user '{username}'")


def main():
    """
    Main function - Add your GitHub token here for better rate limits
    """
    # 🔑 ADD YOUR GITHUB TOKEN HERE (optional but recommended)
    token = None  # Replace with your actual token if you have one
    
    # Uncomment and add your token below for better performance:
    # token = "ghp_your_token_here"
    
    if not token:
        print("⚠️  Running without GitHub token (60 requests/hour limit)")
        print("   Add a token for 5000 requests/hour: https://github.com/settings/tokens")
        print("   (No special permissions needed)")
    
    fetcher = GitHubRepoFetcher(token=token)
    
    try:
        fetcher.run()
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted by user. Goodbye!")
        if fetcher.session:
            fetcher.session.close()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if fetcher.session:
            fetcher.session.close()


if __name__ == "__main__":
    main()
