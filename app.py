import streamlit as st
import requests
import random

# Настройка страницы
st.set_page_config(page_title="AI Песни в Подарок", page_icon="🎵", layout="centered")

st.title("🎵 Генератор песен-подарков")
st.markdown("Создай уникальную песню для близких за пару кликов!")

# Боковая панель для настроек
st.sidebar.header("⚙️ Настройки")
api_key = st.sidebar.text_input("Вставь свой OpenRouter API Key:", type="password", help="Получи бесплатно на openrouter.ai/keys")

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
    if not api_key:
        st.error("Пожалуйста, введи API Key в боковой панели!")
    else:
        with st.spinner("🔮 Нейросеть подбирает рифмы..."):
            # ГЕНЕРАЦИЯ СТИХА
            models_response = requests.get(
                "https://openrouter.ai/api/v1/models", 
                headers={"Authorization": f"Bearer {api_key}"}
            )
            
            poem_text = "Не удалось сгенерировать стих."
            if models_response.status_code == 200:
                free_models = [m["id"] for m in models_response.json()["data"] if ":free" in m["id"]]
                random.shuffle(free_models)
                
                for model in free_models[:10]:
                    response = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json={
                            "model": model,
                            "messages": [
                                {"role": "system", "content": "Ты — поэт-песенник. Пиши короткие душевные стихи из 2 куплетов."},
                                {"role": "user", "content": f"Напиши стих-поздравление с {occasion.lower()} для {name}, который любит {interests}."}
                            ]
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if "choices" in data and len(data["choices"]) > 0:
                            poem_text = data["choices"][0]["message"]["content"]
                            break
            
            st.success("✅ Стих готов!")
            st.markdown(f"### {name}, с {occasion}!\n\n{poem_text}")
            
            st.info("💡 Генерация музыки требует мощного сервера. На бесплатном тарифе Streamlit это пока недоступно. Но стих отличный!")
