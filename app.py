import streamlit as st
import requests
import random

# Настройка страницы
st.set_page_config(page_title="AI Песни в Подарок", page_icon="🎵", layout="centered")

# Получаем ключ из Secrets (спрятан от пользователей)
api_key = st.secrets["OPENROUTER_API_KEY"]

# Заголовок сайта
st.title("🎵 Генератор песен-подарков")
st.markdown("Создай уникальную песню для близких за пару кликов!")

# Основная форма
st.subheader("Расскажи о том, для кого песня:")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Имя:", "Андрей")
    occasion = st.text_input("Повод:", "День рождения")
with col2:
    interests = st.text_input("Интересы (через запятую):", "рыбалка, горы")

# Кнопка запуска
if st.button("✨ Создать шедевр", type="primary"):
    with st.spinner("🔮 Нейросеть подбирает рифмы..."):
        # ГЕНЕРАЦИЯ СТИХА
        try:
            models_response = requests.get(
                "https://openrouter.ai/api/v1/models", 
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            
            poem_text = ""
            if models_response.status_code == 200:
                free_models = [m["id"] for m in models_response.json()["data"] if ":free" in m["id"]]
                random.shuffle(free_models)
                
                for model in free_models[:10]:
                    try:
                        response = requests.post(
                            url="https://openrouter.ai/api/v1/chat/completions",
                            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                            json={
                                "model": model,
                                "messages": [
                                    {"role": "system", "content": "Ты — талантливый поэт-песенник. Пиши короткие душевные стихи из 2 куплетов по 4 строки. Избегай сложных метафор."},
                                    {"role": "user", "content": f"Напиши стих-поздравление с {occasion.lower()} для {name}, который любит {interests}."}
                                ]
                            },
                            timeout=30
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if "choices" in data and len(data["choices"]) > 0:
                                poem_text = data["choices"][0]["message"]["content"]
                                break
                    except:
                        continue
        except Exception as e:
            st.error(f"Ошибка подключения: {e}")
            poem_text = ""
        
        if poem_text:
            st.success("✅ Стих готов!")
            st.markdown(f"### {name}, с {occasion}!\n\n{poem_text}")
            st.info("💡 Генерация музыки с вокалом требует плат
