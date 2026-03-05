from app.services.ner_ar import extract_places_ner

text = "أعلنت وزارة الدفاع في طهران عن انفجار قرب أصفهان، وقالت مصادر في إيران إن الوضع متوتر."
print(extract_places_ner(text))