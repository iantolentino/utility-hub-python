# GitHub Repository Fetcher

A high-performance Python tool for fetching and analyzing GitHub user repositories with parallel processing and batch operations.

![GitHub](https://img.shields.io/badge/GitHub-API-blue?logo=github) 
![Python](https://img.shields.io/badge/Python-3.7+-green?logo=python) 
![Performance](https://img.shields.io/badge/Performance-⚡_Parallel-yellow)

## Features
  
### Performance Optimized  
- **Parallel repository fetching** with ThreadPoolExecutor  
- **Batch language detection** (processes 10 repos simultaneously)
- **Connection pooling** with persistent sessions
- **Smart caching** to avoid duplicate API calls
- **Rate limit aware** with automatic throttling  
 
### Comprehensive Data 
- **User search** with detailed profiles
- **Repository metadata** (stars, forks, descriptions) 
- **Technology stack analysis** with language detection  
- **Export to JSON** with full repository details
- **File size tracking** and timestamps

### User-Friendly
- **Interactive CLI** with emoji-rich interface
- **Smart pagination** with automatic page detection
- **Export directory management**
- **Progress indicators** for long operations
- **Keyboard interrupt support** (Ctrl+C)

## Export System

All exports are automatically saved to: `./github_exports/`

**Example export path:**
```
C:\Projects\github_exports\octocat_repos_20231201_143022.json
```

Files include:
- ✅ Repository metadata
- ✅ Technology stacks
- ✅ Star and fork counts
- ✅ License information
- ✅ Timestamp of fetch

## Quick Start

### Installation

1. **Clone or download** the script
2. **No dependencies needed!** Uses only Python standard libraries

```bash
# Just download and run!
python github_repo_fetcher.py
```

### Basic Usage

```python
# Run without token (60 requests/hour)
python github_repo_fetcher.py

# Or add your token for better limits
# Edit the script and set: token = "your_github_token"
```

### Getting a GitHub Token (Optional but Recommended)

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token"
3. **No special permissions needed** - just leave all boxes unchecked
4. Copy the token and add it to the script

**Benefits with token:**
- 5000 requests/hour vs 60 requests/hour
- Faster, more reliable API access
- Higher rate limits for large accounts

## How to Use

### 1. Search for Users
```
🎮 Options:
1. 🔍 Search for GitHub user
2. 📁 Show export directory
3. 🚪 Exit

Enter your choice (1-3): 1

🔎 Enter GitHub username or name to search: torvalds
```

### 2. Select User
```
🔍 Search Results:
============================================================
1. torvalds
   📛 Name: Linus Torvalds
   👥 Followers: 220750 | 📂 Public Repos: 7
--------------------------------------------------------
```

### 3. View Repositories
```
📂 Repositories for torvalds (7 found)
================================================================================

1. linux
   📖 Linux kernel source tree
   ⭐ Stars: 159950
   🍴 Forks: 50936
   📅 Updated: 2023-12-01
   🔗 https://github.com/torvalds/linux
   💻 Tech: C, Assembly, Python, Perl, Makefile, Shell, HTML...
------------------------------------------------------------
```

### 4. Export Data
```
💾 Export to JSON file? (y/n): y
Enter filename (or press Enter for auto-name): 

🔄 Gathering technology data for export...

💾 Data exported to: ./github_exports/torvalds_repos_20231201_143022.json
📁 Full path: C:\Projects\github_exports\torvalds_repos_20231201_143022.json
📊 File size: 15,234 bytes (14.9 KB)
```

## Performance Metrics

| Operation | Without Token | With Token |
|-----------|---------------|------------|
| User Search | ~1-2 seconds | ~1 second |
| Fetch 50 Repos | ~10-15 seconds | ~5-8 seconds |
| Language Detection | ~20-30 seconds | ~10-15 seconds |
| Full Export | ~30-45 seconds | ~15-25 seconds |

## 🛠️ Technical Details

### Architecture
- **Multi-threaded** with ThreadPoolExecutor
- **Batch processing** for language detection
- **Connection reuse** with requests.Session
- **Memory efficient** streaming
- **Rate limit compliant** with smart delays

### API Endpoints Used
- `GET /search/users` - User search
- `GET /users/{username}/repos` - Repository list
- `GET /repos/{owner}/{repo}/languages` - Technology stack

### Error Handling
- ✅ Network timeouts
- ✅ Rate limit detection
- ✅ Invalid user handling
- ✅ File system errors
- ✅ Keyboard interrupts

## Example Export Format

```json
{
  "username": "torvalds",
  "fetched_at": "2023-12-01T14:30:22.123456",
  "total_repositories": 7,
  "repositories": [
    {
      "name": "linux",
      "full_name": "torvalds/linux",
      "description": "Linux kernel source tree",
      "url": "https://github.com/torvalds/linux",
      "stars": 159950,
      "forks": 50936,
      "primary_language": "C",
      "languages": ["C", "Assembly", "Python", "Perl", "Makefile"],
      "license": "GPL-2.0",
      "size": 123456789
    }
  ]
}
```

## Advanced Usage

### Customizing Export Location
Modify this line in the code:
```python
self.exports_dir = os.path.join(os.getcwd(), "github_exports")
```

### Adjusting Performance Settings
```python
# In get_user_repos_fast method:
with ThreadPoolExecutor(max_workers=3)  # Adjust concurrency

# In get_repo_languages_batch method:
batch_size = 10  # Repos processed simultaneously
max_workers = 5  # Language fetch threads
```

## Troubleshooting

### Common Issues

**"Rate limit exceeded"**
- Add a GitHub token to the script
- Wait until your rate limit resets (usually 1 hour)

**"User not found"**
- Check the username spelling
- User might have changed username

**"No repositories found"**
- User might have no public repositories
- Organization accounts work differently

**Network errors**
- Check your internet connection
- Corporate firewalls might block GitHub API

### Performance Tips

1. **Use a GitHub token** for 83x higher rate limits
2. **Search by exact username** for faster results
3. **Export only when needed** to save API calls
4. **Close other GitHub applications** during large fetches

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the [MIT License](LICENSE).

---

**Pro Tip:** For analyzing organizations with hundreds of repositories, consider using a GitHub token and running during off-peak hours for best performance!

---

<div align="center">

*Fast, reliable, and dependency-free GitHub data extraction*

</div>
