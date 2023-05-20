import json

import constants
import pandas as pd
import streamlit as st
import pydeck as pdk
from langchain import OpenAI
from llama_index import (Document, GPTVectorStoreIndex, LLMPredictor,
                         PromptHelper, QuestionAnswerPrompt, ServiceContext,
                         StorageContext, load_index_from_storage)
from llama_index.node_parser import SimpleNodeParser
from prompts import get_prompt
from streamlit_lottie import st_lottie
import yaml

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
CATEGORIES = constants.CATEGORIES
REGIONS = constants.REGIONS
PLANTS_INFO = constants.PLANTS_INFO
RU_TO_EN = constants.RU_TO_EN
PLANTS = list(PLANTS_INFO.keys())


def clear_submit():
    st.session_state["submit"] = False


def get_data(disctrict=None, region=None):
    df = pd.DataFrame.from_dict({
        'Название растения': [
            'Одуванчик_0 обыкновенные', 'Одуванчик_1 обыкновенные',
            'Одуванчик_2 обыкновенные', 'Одуванчик_3 обыкновенные'
        ],
        'Краснокнижный': ['✅', '✅', '✅', '✅'],
        'Параметр 1': ['✅', '✅', '✅', '✅'],
        'Параметр 2': ['✅', '✅', '✅', '✅'],
        'Параметр 3': ['✅', '✅', '✅', '✅'],
        'Параметр 4': ['✅', '✅', '✅', '✅']
    })
    return df


def get_response_model(query_str, sel_plant):
    plant = sel_plant.replace(' ', '_')

    # service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)

    storage_context = StorageContext.from_defaults(
        persist_dir=f"../data/storage/{plant}")
    index = load_index_from_storage(storage_context)

    query_engine = index.as_query_engine(text_qa_template=get_prompt())
    response = query_engine.query(query_str)

    return response


def main_page():
    header_div = st.container()
    contetn_div = st.container()
    with header_div:
        col1, col2 = st.columns((1, 3))

        lottie_path_teeth = 'data\plant.json'
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
            ["Поиск по параметрам", "Информация о растении"])
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
                query = st.text_input(
                    "Спросить дополнительную информацию у ИИ помощника")
                if query:
                    st.markdown(f'Вы спросили: {query}')
                    response = get_response_model(query, sel_plant)
                    st.markdown(f'Ответ: {response}')

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
                    #MAP
                    with open("C:\\Users\\1bitt\\Documents\\projects\\MedPlantsGPT\\data\\name_to_coord.yml", "r", encoding='utf-8') as stream:
                        try:
                            name_to_coord = yaml.load(stream, Loader=yaml.Loader)
                        except yaml.YAMLError as exc:
                            print(exc)
                    right_name = sel_plant.upper()[0] + sel_plant.lower()[1:]
                    if right_name in list(RU_TO_EN.keys()):
                        coord = name_to_coord[RU_TO_EN[right_name]]
                        df = pd.DataFrame(coord, columns=['lat', 'lon'])
                        st.pydeck_chart(
                            pdk.Deck(
                                map_style='mapbox://styles/mapbox/light-v9',
                                initial_view_state=pdk.ViewState(
                                    latitude=61.160019,
                                    longitude=87.213516,
                                    zoom=3),
                                layers=[
                                    pdk.Layer('ScatterplotLayer',
                                              data=df,
                                              opacity=0.5,
                                              get_position='[lon, lat]',
                                              radius_scale=6,
                                              get_radius = 3000,
                                                auto_highlight = True,
                                              get_color=['255', '30', '30'])
                                ],
                            ))
                    else:
                        st.text('Данные по источникам произрастания еще не добавлены')

if __name__ == '__main__':
    st.set_page_config(page_title="MedPlantsGPT", page_icon="🌱", layout="wide")

    main_page()
