import streamlit as st
import requests
import os
import base64
from sentence_transformers import SentenceTransformer, util
import torch

# Load NLP model for semantic search
model = SentenceTransformer("all-MiniLM-L6-v2")

# Streamlit UI Setup
st.set_page_config(page_title="DrakonSearch - AI GitHub Finder", page_icon="🐉", layout="wide")
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
    .stApp {
        background: linear-gradient(to right, #1f4037, #99f2c8);
    }
    </style>
    <h1 class='glow-text'>⚡ DrakonSearch - The Mythical AI GitHub Finder</h1>
    """, unsafe_allow_html=True
)

st.markdown("### Find the most relevant GitHub project using AI-powered semantic search! 🚀")

# User input for GitHub API key
github_api_key = st.text_input("🔑 Enter your GitHub API Key (Optional for better rate limits)", type="password")
if github_api_key:
    headers = {"Authorization": f"token {github_api_key}"}
else:
    headers = {}

# Function to fetch repositories from GitHub API based on search
def search_github_repos(query, language=None, max_results=20):
    search_query = f"{query}"
    if language:
        search_query += f" language:{language}"
    url = f"https://api.github.com/search/repositories?q={search_query}&sort=stars&order=desc"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["items"][:max_results]
    return []

# Function to get README content for better context
def get_repo_readme(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json().get("content", "")
        return base64.b64decode(content).decode("utf-8", errors="ignore")
    return ""

# Function to rank results semantically
def rank_repositories(user_query, repos):
    query_embedding = model.encode(user_query, convert_to_tensor=True)
    repo_data = []
    
    for repo in repos:
        repo_owner, repo_name = repo["full_name"].split("/")
        readme_content = get_repo_readme(repo_owner, repo_name)
        text_content = (repo['description'] or "") + " " + readme_content
        repo_data.append((repo, text_content))
    
    repo_embeddings = model.encode([data[1] for data in repo_data], convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(query_embedding, repo_embeddings)[0]
    ranked_repos = sorted(zip([data[0] for data in repo_data], similarities), key=lambda x: x[1], reverse=True)
    return [repo[0] for repo in ranked_repos]

# Function to get top contributors
def get_top_contributors(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contributors"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        contributors = response.json()
        return [c["login"] for c in contributors[:3]] if contributors else ["No contributors found"]
    return ["No data available"]

# Function to check repository health
def get_repo_health(repo):
    last_update = repo.get("pushed_at", "Unknown")
    issues = repo.get("open_issues_count", 0)
    forks = repo.get("forks_count", 0)
    watchers = repo.get("watchers_count", 0)
    return f"🕒 Last Update: {last_update} | 🛠 Issues: {issues} | 🍴 Forks: {forks} | 👀 Watchers: {watchers}"

# User Input
user_query = st.text_input("🔍 Enter your project idea or keywords:")
language = st.selectbox("🌐 Filter by Programming Language (Optional)", ["Any", "Python", "JavaScript", "Java", "C++", "Go", "Rust"])
if language == "Any":
    language = None

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
                    st.markdown(f"### [{repo['name']}]({repo['html_url']}) ⭐ {repo['stargazers_count']}")
                    st.write(repo['description'])
                    st.markdown(f"🔗 [View Repository]({repo['html_url']})")
                    st.write(health_info)
                    st.markdown(f"👨‍💻 **Top Contributors:** {', '.join(contributors)}")
            else:
                st.warning("No relevant repositories found. Try modifying your query.")
    else:
        st.error("Please enter a search query.")