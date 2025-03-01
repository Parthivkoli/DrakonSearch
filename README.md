# DrakonSearch 🐉

DrakonSearch is an AI-powered GitHub project search tool that leverages NLP and semantic search to find the most relevant repositories based on user queries. It ranks repositories not just by keywords but by actual project relevance, using advanced NLP techniques.

## 🚀 Features
- **AI-Powered Search**: Uses NLP and semantic ranking to find projects based on meaning, not just keywords.
- **GitHub API Integration**: Searches GitHub repositories with optional filtering by language and stars.
- **Repository Insights**: Displays top contributors, project health, last updated status, forks, and issues.
- **Customizable API Key**: Users can input their own GitHub API key for better rate limits.
- **Themed UI**: Modern interface with an animated glowing app title.

## 🛠 Installation

### Prerequisites
- Python 3.8+
- Streamlit
- Sentence-Transformers
- Requests

### Setup
```bash
git clone https://github.com/Parthivkoli/DrakonSearch.git
cd DrakonSearch
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 🎯 Usage
1. Run the app and enter a project idea or keywords.
2. (Optional) Select a programming language filter.
3. Click "Search GitHub Projects."
4. Browse ranked results with insights.

## 🧠 How It Works
1. Fetches GitHub repositories matching the query.
2. Retrieves README contents for better context.
3. Uses **Sentence Transformers** to rank repositories based on semantic similarity.
4. Displays ranked results with contributors and project health insights.

## UI
![image](https://github.com/user-attachments/assets/07732b81-cfc4-4ae9-8f26-e4fa205a8935)

## 🌟 Demo
[![Hugging Face Space](https://img.shields.io/badge/HuggingFace-DrakonSearch-yellow)](https://huggingface.co/spaces/ParthivKoli/DrakonSearch)

## 🤝 Contributing
Feel free to fork the repo, create pull requests, or submit issues!

## 📜 License
This project is licensed under the MIT License.
