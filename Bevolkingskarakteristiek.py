import streamlit as st
# import cbsodata
import pandas as pd
import glob
import plotly.graph_objects as go

from utils import *


def filter_regio_df(region_df, query):
    '''Filtert df nadat een query is ingevuld in de zoekbalk'''
    mask = region_df.map(lambda x: query.lower() in str(x).lower()).any(axis=1)
    region_df = region_df[mask].reset_index(drop=True)
    return region_df

def load_table(jaar, folder='cbs_tabellen'):
    cbs_tabellen_fp = glob.glob(f'{folder}/*.parquet')
    tabel_fp = next((fp for fp in cbs_tabellen_fp if str(jaar) in fp), None)
    df = pd.read_parquet(tabel_fp)
    return df

# —————————— S I D E B A R ———————————————————————————————————————————————————————————————————————————

st.set_page_config(page_title="Bevolkingskarakteristiek")

st.title('Bevolkingskarakteristiek')
img = st.image('https://www.paradigmmarketinganddesign.com/wp-content/uploads/2022/02/How-to-use-demographics-in-digital-marketing-to-reach-your-target-audience.png')

with st.sidebar:
    st.header('**:rainbow[Opties]:**')

    with st.popover('Info', icon='ℹ️'):
        st.header('**Vink een locatie aan in de meest linker kolom zoals in het voorbeeld hieronder.**')
        st.image("selection_help.png")
    
    # Selecteer jaren
    jaar = st.pills('Jaren:', [2024, 2023, 2022, 2021], default=2024, selection_mode="single")

    # Importeer tabel
    df = load_table(jaar, folder='cbs_tabellen')

    # Selecteer regio
    query = st.text_input('Locatie:', placeholder='Zoeken', help='Vink een locatie aan in de meest linker kolom')
    region_df = df[['ID', 'WijkenEnBuurten', 'Gemeentenaam_1']][1:].copy()
    region_df = filter_regio_df(region_df, query)
    region_selection = st.dataframe(region_df, on_select='rerun', selection_mode='single-row', hide_index=True)

    run_button = False
    if region_selection.selection['rows']:
        selected_row_idx = region_selection.selection['rows'][0]
        cbs_id = region_df.loc[selected_row_idx]['ID']
        WeB = region_df.loc[selected_row_idx]['WijkenEnBuurten']

        st.session_state['cbs_id'] = cbs_id
        st.session_state['WeB'] = WeB

        run_button = st.button("Los geht's", type='primary', icon='🔥')

    


# ———————————— M A I N —————————————————————————————————————————————————————————————————————————



if run_button:
    img.empty()
    cbs_id = st.session_state['cbs_id']
    WeB = st.session_state['WeB']

    tab1, tab2 = st.tabs([f'{WeB} {jaar}', 'Radar chart'])

    with tab1: # Statistieken
    
        st.header(f'{WeB} {jaar}')

        # Processen van data (filteren, transponeren, percentages berekenen)
        processor = DataProcessing(df)
        df = processor.process_df(cbs_id=cbs_id)

        # df splitten in mini df'jes
        splitter = DataframeSplitter()
        minis = splitter.split_df(df)

        # Formatting van mini df's
        formatter = DataframeFormatter()
        minis = [formatter.format_df(mini) for mini in minis]

        for mini in minis:
            st.dataframe(mini, hide_index=True, use_container_width=True)

    with tab2: # Radar chart

        radar = RadarConstructor()
        radar_df = df.loc[radar.kenmerken_voor_radarchart]                 ; radar_df0 = radar_df.copy() # kopie zodat de df met formatting gepresenteerd kan worden.
        radar_df = formatter.format_kenmerken(radar_df)

        fig = radar.construct_radar(radar_df)
        st.plotly_chart(fig)

        st.dataframe(formatter.format_df(radar_df0))

