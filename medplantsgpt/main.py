import json

import constants
from file import find_plants_in_region
import pickle
import pandas as pd
import streamlit as st
import pydeck as pdk
from llama_index import (
                         StorageContext, load_index_from_storage)
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
EN_TO_RU = constants.EN_TO_RU
PLANTS = list(PLANTS_INFO.keys())
DATA_PATH = constants.DATA_PATH
HARVESTING_INFO = constants.HARVESTING_INFO

def clear_submit():
    st.session_state["submit"] = False


def get_data(disctrict=None, region=None, name_to_region=None):
    plants = find_plants_in_region(region, name_to_region)
    ru_planst = []
    if plants:
        for plant in plants:
            if plant in EN_TO_RU.keys():
                ru_planst.append(EN_TO_RU[plant])

        with open(DATA_PATH / 'redbook.pickle', 'rb') as file_pickle:
            redbook_dict = pickle.load(file_pickle, encoding='utf-8')

        plants_rb = []
        for plant in ru_planst:
            if plant in redbook_dict.keys():
                rb_regions = [x[0] for x in redbook_dict[plant]]
                if region in rb_regions:
                    plants_rb.append('Да')
                else:
                    plants_rb.append('Нет')
            else:
                    plants_rb.append('Нет')

        plants_farm = []
        farma_df = pd.read_csv(DATA_PATH / 'farma.csv')
        for plant in ru_planst:
            if plant in farma_df['Наименование раздела на русском языке'].to_list():
                plants_farm.append('Да')
            else:
                plants_farm.append('Нет')

#Аир обыкновенный

        plant_seed = []
        plant_harv = []
        for plant in ru_planst:
            plant = plant.upper()
            if plant in HARVESTING_INFO.keys():
                plant_seed.append(HARVESTING_INFO[plant]['Период посева'])
                plant_harv.append(HARVESTING_INFO[plant]['Период сбора урожая, мес'])
            else:
                plant_seed.append('---')
                plant_harv.append('---')

        df = pd.DataFrame.from_dict({
            'Название растения': ru_planst,
            'Культура в Красной книге?': plants_rb,
            'Культура в гос.  фармакопейи?': plants_farm,
            'Период посева': plant_seed,
            'Период сбора урожая': plant_harv,
        })
        return df
    else:
        return None





def get_response_model(query_str, sel_plant):
    plant = sel_plant.replace(' ', '_')

    # service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)

    storage_context = StorageContext.from_defaults(
        persist_dir= (DATA_PATH / 'storage' / plant).as_posix())
    index = load_index_from_storage(storage_context)

    query_engine = index.as_query_engine(text_qa_template=get_prompt())
    response = query_engine.query(query_str)

    return response


def main_page():
    header_div = st.container()
    contetn_div = st.container()
    with header_div:
        col1, col2 = st.columns((1, 3))

        lottie_path_teeth = DATA_PATH / 'plant.json'
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
            st.title('🌱 Толковый фермер')

            st.markdown("""
<style>
.big-font {
    font-size:20px !important;
}
</style>
""", unsafe_allow_html=True)
            text1 = 'Узнайте, как выращивать и ухаживать за растениями в вашем регионе с помощью нашего инновационного сервиса!'
        
            text2 = 'Мы предлагаем фермерам быстрый и простой доступ к информации о растениях, которые можно успешно вырастить в их конкретном местоположении.'

            text3 = 'Теперь у вас есть возможность получить всю необходимую информацию о растениях, которые помогут вам повысить урожайность и успешно вести свою фермерскую деятельность.'

            text4 = 'Присоединяйтесь к нам и станьте экспертом в выращивании растений в вашем регионе!'
            st.markdown(f'<p class="big-font">{text1}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-font">{text2}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-font">{text3}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-font">{text4}</p>', unsafe_allow_html=True)

            
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

            with open(DATA_PATH / "name_to_region.yml", "r", encoding='utf-8') as stream:
                try:
                    name_to_region = yaml.load(stream, Loader=yaml.Loader)
                except yaml.YAMLError as exc:
                    print(exc)

            with tabloid:
                table = get_data(sel_district, sel_region, name_to_region)
                if table is not None:
                    st.dataframe(table)
                else:
                    st.text('Данные по растениям в базе не найдены')

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
                    with open(DATA_PATH / "name_to_coord.yml", "r", encoding='utf-8') as stream:
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
                                    pdk.Layer('HeatmapLayer',
                                              data=df,
                                              opacity=0.5,
                                              get_position='[lon, lat]',
                                              aggregation=pdk.types.String("SUM"),
                                              radiusPixels = 30,
                                              weightsTextureSize = 256,
                                              get_color=['255', '30', '30'])]
                            ))
                    else:
                        st.text('Данные по источникам произрастания еще не добавлены')

if __name__ == '__main__':
    st.set_page_config(page_title="MedPlantsGPT", page_icon="🌱", layout="wide")

    main_page()
