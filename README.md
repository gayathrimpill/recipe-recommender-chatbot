# recipe-recommender-chatbot
A conversational recipe recommender built on 200k+ recipes, powered by a local LLM.

## How it works
- User describes what they're craving in plain language
- App matches recipes by name, ingredients, and tags
- Llama3 (via Ollama) responds conversationally with recommendations

## Tech stack
Python, Streamlit, Ollama (Llama3), Pandas

## Run locally
pip3 install streamlit ollama pandas


python3 -m streamlit run app.py
![Recipe Chatbot Demo](chatbot.png)
