import streamlit as st
import requests
import random
import asyncio
import edge_tts
import os

# Настройка страницы
st.set_page_config(page_title="AI Песни в Подарок", page_icon="🎵", layout="centered")

# Получаем ключ из Secrets
api_key = st.secrets["OPENROUTER_API_KEY"]

# МАСТЕР-ПРОМПТ 3.0
MASTER_PROMPT = """Ты — великий русский поэт-песенник, наследник традиций Высоцкого, Окуджавы и Визбора. Твои стихи — это песни, которые люди поют за столом и помнят всю жизнь.

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА (нарушение любого = провал):

1. ФОРМАТ (НЕПОКОЛЕБИМО):
   - Ровно 2 куплета
   - В каждом куплете ровно 4 строки
   - КАЖДАЯ СТРОКА — с новой строки (Enter после каждой)
   - МЕЖДУ КУПЛЕТАМИ — одна пустая строка
   - НИКАКОГО сплошного текста!
   
   ПРАВИЛЬНЫЙ ПРИМЕР:
   Первая строка первого куплета,
   Вторая строка первого куплета,
   Третья строка первого куплета,
   Четвёртая строка первого куплета.
   
   Первая строка второго куплета,
   Вторая строка второго куплета,
   Третья строка второго куплета,
   Четвёртая строка второго куплета.

2. РИФМА (ТОЧНАЯ!):
   - Разрешено: друг/лук, река/рука, рассвет/привет, костёр/простор
   - ЗАПРЕЩЕНО: глагольные рифмы (пошёл/нашёл, играл/гулял, сидел/пел)
   - ЗАПРЕЩЕНО: неточные рифмы (любовь/вновь, сердце/сердце, душа/хороша)
   - Схема: AABB или ABAB (выбери одну и придерживайся)

3. РИТМ (КАК ПЕСНЯ):
   - Каждая строка: 10-12 слогов
   - Прочитай вслух — должно ложиться на мотив
   - Если не ритмично — переделай

4. ОБРАЗЫ (КОНКРЕТИКА!):
   - ЗАПРЕЩЕНО: "пусть сбудутся мечты", "счастья и любви", "удачи во всём", "здоровья и радости"
   - РАЗРЕШЕНО: "утренний туман над рекой", "запах соснового костра", "звёзды над горной вершиной", "следы на снежном склоне"
   - Имя и интересы вплетай ЧЕРЕЗ ОБРАЗЫ, не через перечисление

5. ЭМОЦИЯ:
   - Тёплый, мужской, искренний тон
   - Вызывает улыбку или лёгкое волнение
   - Без пафоса и слащавости

6. ЯЗЫК:
   - Живой, разговорный, но поэтичный
   - Без штампов, клише и канцеляризмов
   - Современные слова разрешены, если они в ритме

ВЫДАВАЙ ТОЛЬКО СТИХ. Без заголовков, без "Вот ваш стих", без комментариев, без кавычек."""

# Модели в порядке приоритета
MODELS_PRIORITY = [
    # Бесплатные (пробуем сначала)
    "qwen/qwen-2.5-72b-instruct:free",
    "deepseek/deepseek-r1:free",
    "meta-llama/llama-3.1-70b-instruct:free",
    # Платные fallback (копейки за стих, отличное качество)
    "openai/gpt-4o-mini",
    "deepseek/deepseek-chat-v3-0324",
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
            # Получаем список доступных моделей
            models_response = requests.get(
                "https://openrouter.ai/api/v1/models", 
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            
            poem_text = ""
            used_model = ""
            model_cost = ""
            
            if models_response.status_code == 200:
                available = [m["id"] for m in models_response.json()["data"]]
                
                # Фильтруем только доступные модели из нашего приоритетного списка
                models_to_try = [m for m in MODELS_PRIORITY if m in available]
                
                # Пробуем модели по порядку
                for model in models_to_try:
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
                                "temperature": 0.85,
                                "max_tokens": 300
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if "choices" in data and len(data["choices"]) > 0:
                                poem_text = data["choices"][0]["message"]["content"]
                                used_model = model
                                
                                # Определяем стоимость
                                if ":free" in model:
                                    model_cost = "бесплатно ✨"
                                elif "gpt-4o-mini" in model:
                                    model_cost = "~2 копейки"
                                else:
                                    model_cost = "~1 копейка"
                                break
                    except:
                        continue
            
            if poem_text:
                st.success(f"✅ Шедевр готов! (Модель: {used_model} — {model_cost})")
                st.markdown(f"### {name}, с {occasion}!\n\n{poem_text}")
                
                # Сохраняем стих в сессию для озвучки
                st.session_state['poem_text'] = poem_text
                st.session_state['poem_name'] = name
                
                st.info("💡 Хочешь услышать стих? Нажми кнопку ниже!")
            else:
                st.error("😔 Не удалось сгенерировать стих. Все модели временно недоступны. Попробуй через 5-10 минут.")
        except Exception as e:
            st.error(f"Ошибка подключения: {e}")

# Кнопка озвучки (появляется после генерации стиха)
if 'poem_text' in st.session_state:
    st.markdown("---")
    st.subheader("🔊 Озвучить стих")
    
    if st.button("🎙️ Озвучить стих голосом диктора", type="secondary"):
        with st.spinner("Озвучиваю стих профессиональным голосом..."):
            try:
                # Асинхронная функция для TTS
                async def generate_audio(text, output_file):
                    # Используем мужской голос Dmitry (русский)
                    communicate = edge_tts.Communicate(text, "ru-RU-DmitryNeural")
                    await communicate.save(output_file)
                
                # Генерируем аудио
                output_file = "poem_audio.mp3"
                asyncio.run(generate_audio(st.session_state['poem_text'], output_file))
                
                # Показываем плеер
                st.success("✅ Аудио готово!")
                st.audio(output_file, format="audio/mp3")
                
                # Ссылка на скачивание
                with open(output_file, "rb") as f:
                    st.download_button(
                        "📥 Скачать аудио-открытку",
                        data=f,
                        file_name=f"pozdravlenie_dlya_{st.session_state['poem_name']}.mp3",
                        mime="audio/mp3"
                    )
                
            except Exception as e:
                st.error(f"Ошибка озвучки: {e}")
