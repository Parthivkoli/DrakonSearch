import streamlit as st
import requests
import base64
from sentence_transformers import SentenceTransformer, util
import torch

# Load NLP model for semantic search
device = torch.device("cpu")  # Ensure CPU usage for compatibility
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

# Streamlit UI Setup
st.set_page_config(page_title="DrakonSearch - AI GitHub Finder", page_icon="🐉", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    @keyframes glow {
        0% { text-shadow: 0 0 5px #33ff33, 0 0 10px #33ff33, 0 0 20px #33ff33; }
        50% { text-shadow: 0 0 20px #00ff00, 0 0 30px #00ff00, 0 0 40px #00ff00; }
        100% { text-shadow: 0 0 5px #33ff33, 0 0 10px #33ff33, 0 0 20px #33ff33; }
    }
    .glow-text {
        font-size: 48px;
        font-weight: bold;
        color: #ffffff;
        text-align: center;
        animation: glow 1.5s infinite alternate;
    }
    body {
        background-color: #0e1117;
        color: white;
    }
    </style>
    <h1 class='glow-text'>⚡ DrakonSearch - The Mythical AI GitHub Finder</h1>
    """, unsafe_allow_html=True
)

st.markdown("### Find the most relevant GitHub project using AI-powered semantic search! 🚀")

# User input for GitHub API key
github_api_key = st.text_input("🔑 Enter your GitHub API Key (Optional)", type="password")
headers = {"Authorization": f"token {github_api_key}"} if github_api_key else {}

# Function to fetch repositories from GitHub API based on search
@st.cache_data(ttl=300)  # Cache results for 5 minutes
def search_github_repos(query, language=None, max_results=20):
    search_query = f"{query} language:{language}" if language else query
    url = f"https://api.github.com/search/repositories?q={search_query}&sort=stars&order=desc"
    response = requests.get(url, headers=headers)
    return response.json().get("items", [])[:max_results] if response.status_code == 200 else []

# Function to get README content for better context
@st.cache_data(ttl=600)  # Cache results for 10 minutes
def get_repo_readme(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            return base64.b64decode(response.json().get("content", "")).decode("utf-8", errors="ignore")
        except Exception:
            return ""
    return ""

# Function to rank results using NLP-based similarity
def rank_repositories(user_query, repos):
    query_embedding = model.encode(user_query, convert_to_tensor=True)

    repo_texts = []
    repo_objects = []

    for repo in repos:
        repo_owner, repo_name = repo["full_name"].split("/")
        readme_content = get_repo_readme(repo_owner, repo_name)
        text_content = (repo.get("description") or "") + " " + readme_content
        repo_texts.append(text_content)
        repo_objects.append(repo)

    if repo_texts:
        repo_embeddings = model.encode(repo_texts, convert_to_tensor=True)
        similarities = util.pytorch_cos_sim(query_embedding, repo_embeddings)[0]
        ranked_repos = sorted(zip(repo_objects, similarities), key=lambda x: x[1], reverse=True)
        return [repo[0] for repo in ranked_repos]
    
    return repos

# Function to get top contributors
@st.cache_data(ttl=600)
def get_top_contributors(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contributors"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [c["login"] for c in response.json()[:3]] if response.json() else ["No contributors found"]
    return ["No data available"]

# Function to check repository health
def get_repo_health(repo):
    return f"🕒 Last Update: {repo.get('pushed_at', 'Unknown')} | 🛠 Issues: {repo.get('open_issues_count', 0)} | 🍴 Forks: {repo.get('forks_count', 0)} | 👀 Watchers: {repo.get('watchers_count', 0)}"

# User Input Section
user_query = st.text_input("🔍 Enter your project idea or keywords:")
language_options = ["Any", "Python", "JavaScript", "Java", "C++", "Go", "Rust"]
language = st.selectbox("🌐 Filter by Programming Language (Optional)", language_options)
language = None if language == "Any" else language

# Search Button
if st.button("🚀 Search GitHub Projects"):
    if user_query:
        st.write(f"### Searching for: **{user_query}**")
        with st.spinner("🔄 Fetching and analyzing projects..."):
            results = search_github_repos(user_query, language)
            if results:
                ranked_results = rank_repositories(user_query, results)
                for repo in ranked_results:
                    repo_owner, repo_name = repo["full_name"].split("/")
                    contributors = get_top_contributors(repo_owner, repo_name)
                    health_info = get_repo_health(repo)

                    # Display repository details
                    st.markdown(f"### [{repo['name']}]({repo['html_url']}) ⭐ {repo['stargazers_count']}")
                    st.write(repo['description'] or "No description available.")
                    st.markdown(f"🔗 [View Repository]({repo['html_url']})")
                    st.write(health_info)
                    st.markdown(f"👨‍💻 **Top Contributors:** {', '.join(contributors)}")
            else:
                st.warning("No relevant repositories found. Try modifying your query.")
    else:
        st.error("Please enter a search query.")
