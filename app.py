import streamlit as st
import pandas as pd
import ast
import ollama

st.set_page_config(page_title="Recipe Recommender", page_icon="🍳", layout="centered")
st.title("🍳 Recipe Recommender Chatbot")
st.caption("Tell me what you're craving and I'll find recipes for you!")

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_recipes.csv")
    df["tags"] = df["tags"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df["ingredients"] = df["ingredients"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    return df

df = load_data()

def find_recipes(user_query, df, n=5):
    query = user_query.lower()
    keywords = query.split()

    def score(row):
        s = 0
        tag_str = " ".join(row["tags"]).lower()
        ing_str = " ".join(row["ingredients"]).lower()
        name_str = str(row["name"]).lower()
        for kw in keywords:
            if kw in tag_str: s += 2
            if kw in ing_str: s += 1
            if kw in name_str: s += 3
        # bonus for quick recipes if user mentions time
        if any(w in query for w in ["quick", "fast", "easy", "30", "15"]):
            if row["minutes"] <= 30:
                s += 2
        return s

    df["score"] = df.apply(score, axis=1)
    top = df[df["score"] > 0].nlargest(n, "score")
    return top[["name", "minutes", "ingredients", "tags"]].to_dict("records")

def format_recipes(recipes):
    if not recipes:
        return "No recipes found matching that description."
    lines = []
    for i, r in enumerate(recipes, 1):
        ings = ", ".join(r["ingredients"][:5])
        if len(r["ingredients"]) > 5:
            ings += f" + {len(r['ingredients'])-5} more"
        lines.append(f"{i}. **{r['name'].title()}** — {r['minutes']} mins | Ingredients: {ings}")
    return "\n".join(lines)

def chat(messages, user_query, recipes_text):
    system_prompt = f"""You are a friendly recipe recommender chatbot. 
The user is looking for recipes. Here are the top matches from the database:

{recipes_text}

Recommend these recipes conversationally. Mention cooking time and key ingredients. 
Be warm, helpful, and concise. If no recipes matched, suggest the user try different keywords."""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "system", "content": system_prompt}] + messages
    )
    return response["message"]["content"]

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("e.g. something spicy and vegetarian under 30 minutes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Finding recipes..."):
            recipes = find_recipes(prompt, df)
            recipes_text = format_recipes(recipes)
            response = chat(st.session_state.messages, prompt, recipes_text)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
