import streamlit as st
import requests

# Настройка страницы
st.set_page_config(page_title="AI Песни в Подарок", page_icon="🎵", layout="centered")

# Получаем ключ из Secrets
api_key = st.secrets["OPENROUTER_API_KEY"]
model_name = "qwen/qwen-2.5-72b-instruct:free"

# МАСТЕР-ПРОМПТ: задаёт ИИ роль великого поэта
MASTER_PROMPT = """Ты — величайший поэт-песенник современности, сочетающий мастерство классиков (Пушкин, Есенин, Высоцкий) с современным языком. Твои стихи публикуются в лучших журналах, их поют известные артисты.

ПРАВИЛА ТВОЕГО МАСТЕРСТВА:
1. РИФМА — только точная (любовь/кровь, а не любовь/вновь). Избегай глагольных рифм (пошёл/нашёл).
2. РИТМ — каждая строка должна читаться как песня, с чётким размером (ямб или хорей).
3. СТРУКТУРА — ровно 2 куплета по 4 строки. Без припева, без вступлений.
4. ЯЗЫК — тёплый, живой, без канцеляризмов и штампов ("пусть сбудутся мечты" — запрещено).
5. ПЕРСОНАЛИЗАЦИЯ — обязательно вплети имя человека и его интересы так, чтобы это звучало естественно, а не как список.
6. ЭМОЦИЯ — стих должен вызывать улыбку или лёгкое волнение.

ФОРМАТ ВЫВОДА: Только текст стиха, без комментариев, без "Вот ваш стих", без кавычек."""

# Заголовок сайта
st.title("🎵 Генератор песен-подарков")
st.markdown("Создай уникальное поздравление от великого поэта за пару кликов!")

# Основная форма
st.subheader("Расскажи о том, для кого поздравление:")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Имя:", "Андрей")
    occasion = st.text_input("Повод:", "День рождения")
with col2:
    interests = st.text_input("Интересы (через запятую):", "рыбалка, горы")

# Кнопка запуска
if st.button("✨ Создать шедевр", type="primary"):
    with st.spinner("Великий поэт сочиняет шедевр..."):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": MASTER_PROMPT},
                        {"role": "user", "content": f"Напиши стих-поздравление с {occasion.lower()} для человека по имени {name}, который увлекается: {interests}."}
                    ]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                poem_text = data["choices"][0]["message"]["content"]
                
                st.success("✅ Шедевр готов!")
                st.markdown(f"### {name}, с {occasion}!\n\n{poem_text}")
                st.info("💡 Следующий шаг: добавим музыку с вокалом, как в Songly Gift!")
            else:
                st.error(f"Ошибка: {response.status_code}. Модель временно перегружена — попробуй через минуту.")
        except Exception as e:
            st.error(f"Ошибка подключения: {e}")
