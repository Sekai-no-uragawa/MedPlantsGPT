import streamlit as st
import constants
from streamlit_lottie import st_lottie
import json
import pandas as pd

CATEGORIES = constants.CATEGORIES
REGIONS = constants.REGIONS
PLANTS_INFO = constants.PLANTS_INFO
PLANTS = list(PLANTS_INFO.keys())


def clear_submit():
    st.session_state["submit"] = False


def get_data(disctrict=None, region=None):
    df = pd.DataFrame.from_dict({
        'Название растения': ['Одуванчик_0 обыкновенные', 'Одуванчик_1 обыкновенные', 'Одуванчик_2 обыкновенные', 'Одуванчик_3 обыкновенные'],
        'Краснокнижный': ['✅','✅','✅','✅'],
        'Параметр 1': ['✅','✅','✅','✅'],
        'Параметр 2': ['✅','✅','✅','✅'],
        'Параметр 3': ['✅','✅','✅','✅'],
        'Параметр 4': ['✅','✅','✅','✅']
    })
    return df


def main_page():
    header_div = st.container()
    contetn_div = st.container()
    with header_div:
        col1, col2 = st.columns((1,3))

        lottie_path_teeth = '../data/plant.json'
        with open(lottie_path_teeth, "r") as f:
            lottie_teeth = json.load(f)

        with col1:
            st_lottie(
                lottie_teeth,
                loop=True,
                quality='high',
                # height=300,
                # width=200,
            )
        with col2:
            st.title('🌱 Толковый растениевод')
            st.markdown(
                "Узнайте, как выращивать и ухаживать за растениями в вашем регионе\
                с помощью нашего инновационного сервиса! Мы предлагаем фермерам быстрый\
                и простой доступ к информации о растениях, которые можно успешно вырастить\
                в их конкретном местоположении. Наш сервис предоставляет подробные сведения о\
                различных растениях, включая сезоны посева, оптимальные условия выращивания и\
                полезные советы по уходу. Теперь у вас есть возможность получить всю необходимую\
                информацию о растениях, которые помогут вам повысить урожайность и успешно вести\
                свою фермерскую деятельность. Присоединяйтесь к нам и станьте экспертом в выращивании\
                растений в вашем регионе!")
    with contetn_div:
        enter_params, search_plant = st.tabs(
            ["Поиск по параметрам", "Информация про растение"])
        with enter_params:
            params, tabloid = st.columns((1, 3))
            with params:
                disctricts = [x for x in REGIONS.keys()]
                sel_district = st.selectbox('Выберете округ из списка',
                                            disctricts)

                regions = REGIONS[sel_district]
                sel_region = st.selectbox('Выберете область из списка',
                                          regions)

            with tabloid:
                table = get_data(sel_district, sel_region)
                st.dataframe(table)

        with search_plant:
            choose_plant, info = st.columns((1, 3))

            with choose_plant:
                sel_plant = st.selectbox('Выберете растение из списка', PLANTS)
                query = st.text_area(
                    "Спросить дополнительную информацию у ИИ помощника",
                    on_change=clear_submit)
                st.text(f'Вы спросили: {query}')
                st.text(f'Ответ: здесь будет мудрость от ИИ')

            with info:
                sel_plant = sel_plant.strip().upper()
                selected_plant = PLANTS_INFO[sel_plant]
                st.markdown(f'**{sel_plant}**')
                cats = selected_plant.keys()
                cats = [x for x in cats if len(selected_plant[x]) > 0]
                with info:
                    for cat in cats:
                        with st.expander(cat):
                            st.markdown(selected_plant[cat])
                    st.text('Карта распространения')
                    st.image('https://plant.depo.msu.ru/open/public/scan.jpg?pcode=MW0436310&fp-type=florus')


if __name__ == '__main__':
    st.set_page_config(page_title="MedPlantsGPT", page_icon="🌱", layout="wide")

    main_page()
