import streamlit as st
import requests
import random

# Настройка страницы
st.set_page_config(page_title="AI Песни в Подарок", page_icon="🎵", layout="centered")

# Получаем ключ из Secrets
api_key = st.secrets["OPENROUTER_API_KEY"]

# МАСТЕР-ПРОМПТ 2.0 — с примерами и жёсткими правилами
MASTER_PROMPT = """Ты — великий русский поэт-песенник уровня Высоцкого и Окуджавы. Пиши стихи, которые хочется петь.

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА:

1. ФОРМАТ (САМОЕ ВАЖНОЕ!):
   - Ровно 2 куплета
   - В каждом куплете ровно 4 строки
   - МЕЖДУ СТРОКАМИ — перенос строки (Enter)
   - МЕЖДУ КУПЛЕТАМИ — пустая строка
   - Пример правильного формата:
   
   Строка первая куплета,
   Строка вторая куплета,
   Строка третья куплета,
   Строка четвёртая куплета.
   
   Строка первая второго,
   Строка вторая второго,
   Строка третья второго,
   Строка четвёртая второго.

2. РИФМА:
   - Только точные рифмы: друг/лук, река/рука, рассвет/привет
   - ЗАПРЕЩЕНО: глагольные рифмы (пошёл/нашёл, играл/гулял)
   - ЗАПРЕЩЕНО: неточные рифмы (любовь/вновь, сердце/сердце)
   - Схема рифмовки: AABB или ABAB (чередуй)

3. РИТМ:
   - Каждая строка должна иметь одинаковое количество слогов (10-12)
   - Читай вслух — должно звучать как песня

4. ОБРАЗЫ (вместо абстракций):
   - ЗАПРЕЩЕНО: "пусть сбудутся мечты", "счастья и любви", "удачи во всём"
   - РАЗРЕШЕНО: конкретные детали — "утренний туман на реке", "запах костра", "звёзды над вершиной"
   - Вплетай имя и интересы ЧЕРЕЗ ОБРАЗЫ, а не через перечисление

5. ЯЗЫК:
   - Живой, разговорный, но поэтичный
   - Без штампов и клише
   - Тёплый, мужской, искренний

ВЫДАВАЙ ТОЛЬКО СТИХ. Без заголовков, без "Вот ваш стих", без комментариев."""

# Список моделей в порядке приоритета (Qwen — лучший для русского)
PREFERRED_MODELS = [
    "qwen/qwen-2.5-72b-instruct:free",
    "qwen/qwen3-235b-a22b:free",
    "deepseek/deepseek-r1:free",
    "meta-llama/llama-3.1-70b-instruct:free",
]

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
            # Получаем список бесплатных моделей
            models_response = requests.get(
                "https://openrouter.ai/api/v1/models", 
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            
            poem_text = ""
            used_model = ""
            
            if models_response.status_code == 200:
                all_free = [m["id"] for m in models_response.json()["data"] if ":free" in m["id"]]
                
                # Сначала пробуем предпочтительные модели (Qwen, DeepSeek)
                models_to_try = []
                for pref in PREFERRED_MODELS:
                    if pref in all_free:
                        models_to_try.append(pref)
                
                # Добавляем остальные случайные
                others = [m for m in all_free if m not in models_to_try]
                random.shuffle(others)
                models_to_try.extend(others[:5])
                
                # Пробуем модели
                for model in models_to_try[:10]:
                    try:
                        response = requests.post(
                            url="https://openrouter.ai/api/v1/chat/completions",
                            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                            json={
                                "model": model,
                                "messages": [
                                    {"role": "system", "content": MASTER_PROMPT},
                                    {"role": "user", "content": f"Напиши стих-поздравление с {occasion.lower()} для человека по имени {name}, который увлекается: {interests}."}
                                ],
                                "temperature": 0.8,
                                "max_tokens": 300
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if "choices" in data and len(data["choices"]) > 0:
                                poem_text = data["choices"][0]["message"]["content"]
                                used_model = model
                                break
                    except:
                        continue
            
            if poem_text:
                st.success(f"✅ Шедевр готов! (Модель: {used_model})")
                st.markdown(f"### {name}, с {occasion}!\n\n{poem_text}")
                st.info("💡 Следующий шаг: добавим музыку с вокалом, как в Songly Gift!")
            else:
                st.error("😔 Не удалось сгенерировать стих. Все бесплатные модели временно перегружены. Попробуй через 5-10 минут.")
        except Exception as e:
            st.error(f"Ошибка подключения: {e}")
