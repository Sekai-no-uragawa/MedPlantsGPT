from llama_index.prompts.prompts import QuestionAnswerPrompt

## Use a shorter template to reduce the number of tokens in the prompt
DEFAULT_PROMPT = """Создай финальный ответ на заданные вопросы, используя предоставленные выдержки из документов (в произвольном порядке) в качестве ссылок. ВСЕГДА включай в свой ответ раздел «ИСТОЧНИКИ», включая только минимальный набор источников, необходимых для ответа на вопрос. Если ты не можешь ответить на вопрос, просто скажи, что не знаешь ответа. Не пытайся выдумать ответ и оставь раздел ИСТОЧНИКИ пустым.

---------

ВОПРОС: Какие свойста есть у Хвоща полевого?
=========
Содержание: Хвощ полевой (Equisetum arvense L.) Морфологическое описание. Геофит, длиннокорневищный травянистый хвощ. Спороносные побеги появляются весной, они телесного цвета, сочные, 5–15 см высотой с 6–12 малозаметными ребрами и крупными темно-бурыми колокольчатыми влагалищами из 6–12 крупных зубцов, спаянных по 2–3.
Источник: 1-32
Содержание: Препараты хвоща назначают в качестве мочегонного и противовоспалительного средства при воспалительных заболеваниях почек, мочевого пузыря и мочевыводящих путей, при мочекаменной болезни, а также при застойных явлениях сердечного происхождения и отеках на фоне сердечной недостаточности. 
Источник: 1-33
Содержание: Сырье обладает кровоостанавливающими свойствами, используется при геморроидальных и маточных кровотечениях.
Источник: 1-30
=========
ОКОНЧАТЕЛЬНЫЙ ОТВЕТ: Хвощ полевой обладает мочегонным, кровоостанавливающим и противовоспалительным свойстами. Препараты хвоща могут быть использованы для лечения мочекаменной болезни. Хвощ полевой применяется при застойных явлениях сердечного происхождения и отеках, вызванных сердечной недостаточностью.

ИСТОЧНИКИ: 1-33, 1-30
---------

ВОПРОС: {question}
=========
{summaries}
=========
ОКОНЧАТЕЛЬНЫЙ ОТВЕТ: """

def get_prompt():
    return QuestionAnswerPrompt(DEFAULT_PROMPT)