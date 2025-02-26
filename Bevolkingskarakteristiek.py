import streamlit as st
import cbsodata
import pandas as pd
import re

pd.set_option('display.max_rows', 100)

############################################################################

class CBSData:
    def __init__(self, jaar=2024):
        # self.table_column_ids = {
        #     2024: {'table_id': '85984NED'},
        #     2023: {'table_id': '85618NED'},
        #     2022: {'table_id': '85318NED'},
        #     2021: {'table_id': '85039NED'}
        # }

        self.table_column_ids = {
            2024: {'table_id': '85984NED', 'cols': ['ID', 'WijkenEnBuurten', 'Gemeentenaam_1', 'SoortRegio_2', 'AantalInwoners_5', 'k_0Tot15Jaar_8', 'k_15Tot25Jaar_9', 'k_25Tot45Jaar_10', 'k_45Tot65Jaar_11', 'k_65JaarOfOuder_12', 'HuishoudensTotaal_29', 'Eenpersoonshuishoudens_30', 'HuishoudensZonderKinderen_31', 'HuishoudensMetKinderen_32', 'GemiddeldeHuishoudensgrootte_33', 'Bevolkingsdichtheid_34', 'GemiddeldeWOZWaardeVanWoningen_39', 'Koopwoningen_47', 'HuurwoningenTotaal_48', 'AantalInkomensontvangers_81', 'GemiddeldInkomenPerInkomensontvanger_82', 'GemiddeldInkomenPerInwoner_83', 'HuishOnderOfRondSociaalMinimum_90', 'PersonenautoSPerHuishouden_114', 'AfstandTotGroteSupermarkt_118']}, 
            2023: {'table_id': '85618NED', 'cols': ['ID', 'WijkenEnBuurten', 'Gemeentenaam_1', 'SoortRegio_2', 'AantalInwoners_5', 'k_0Tot15Jaar_8', 'k_15Tot25Jaar_9', 'k_25Tot45Jaar_10', 'k_45Tot65Jaar_11', 'k_65JaarOfOuder_12', 'HuishoudensTotaal_29', 'Eenpersoonshuishoudens_30', 'HuishoudensZonderKinderen_31', 'HuishoudensMetKinderen_32', 'GemiddeldeHuishoudensgrootte_33', 'Bevolkingsdichtheid_34', 'GemiddeldeWOZWaardeVanWoningen_36', 'Koopwoningen_41', 'HuurwoningenTotaal_42', 'AantalInkomensontvangers_76', 'GemiddeldInkomenPerInkomensontvanger_77', 'GemiddeldInkomenPerInwoner_78', 'HuishOnderOfRondSociaalMinimum_85', 'PersonenautoSPerHuishouden_109', 'AfstandTotGroteSupermarkt_113']}, 
            2022: {'table_id': '85318NED', 'cols': ['ID', 'WijkenEnBuurten', 'Gemeentenaam_1', 'SoortRegio_2', 'AantalInwoners_5', 'k_0Tot15Jaar_8', 'k_15Tot25Jaar_9', 'k_25Tot45Jaar_10', 'k_45Tot65Jaar_11', 'k_65JaarOfOuder_12', 'HuishoudensTotaal_28', 'Eenpersoonshuishoudens_29', 'HuishoudensZonderKinderen_30', 'HuishoudensMetKinderen_31', 'GemiddeldeHuishoudensgrootte_32', 'Bevolkingsdichtheid_33', 'GemiddeldeWOZWaardeVanWoningen_35', 'Koopwoningen_40', 'HuurwoningenTotaal_41', 'AantalInkomensontvangers_70', 'GemiddeldInkomenPerInkomensontvanger_71', 'GemiddeldInkomenPerInwoner_72', 'HuishOnderOfRondSociaalMinimum_79', 'PersonenautoSPerHuishouden_103', 'AfstandTotGroteSupermarkt_107']}, 
            2021: {'table_id': '85039NED', 'cols': ['ID', 'WijkenEnBuurten', 'Gemeentenaam_1', 'SoortRegio_2', 'AantalInwoners_5', 'k_0Tot15Jaar_8', 'k_15Tot25Jaar_9', 'k_25Tot45Jaar_10', 'k_45Tot65Jaar_11', 'k_65JaarOfOuder_12', 'HuishoudensTotaal_28', 'Eenpersoonshuishoudens_29', 'HuishoudensZonderKinderen_30', 'HuishoudensMetKinderen_31', 'GemiddeldeHuishoudensgrootte_32', 'Bevolkingsdichtheid_33', 'GemiddeldeWOZWaardeVanWoningen_35', 'Koopwoningen_40', 'HuurwoningenTotaal_41', 'AantalInkomensontvangers_70', 'GemiddeldInkomenPerInkomensontvanger_71', 'GemiddeldInkomenPerInwoner_72', 'HuishOnderOfRondSociaalMinimum_79', 'PersonenautoSPerHuishouden_103', 'AfstandTotGroteSupermarkt_107']}
        }

        self.kenmerken = {
            'ID': {'nieuwe_naam': 'ID', 'value_type': 'abs', 'formatting': ''}, 
            'Gemeentenaam': {'nieuwe_naam': 'Gemeentenaam', 'value_type': 'abs', 'formatting': ''}, 
            'WijkenEnBuurten': {'nieuwe_naam': 'Wijken en Buurten', 'value_type': 'abs', 'formatting': ''}, 
            'SoortRegio': {'nieuwe_naam': 'Soort regio', 'value_type': 'abs', 'formatting': ''},
            
            'AantalInwoners': {'nieuwe_naam': 'Aantal inwoners', 'value_type': 'abs', 'formatting': '{:,.0f}'}, 
            'Bevolkingsdichtheid': {'nieuwe_naam': 'Bevolkingsdichtheid', 'value_type': 'abs', 'formatting': '{:,.0f}'}, 

            'HuishoudensTotaal': {'nieuwe_naam': 'Aantal huishoudens', 'value_type': 'abs', 'formatting': '{:,.0f}'}, 
            'GemiddeldeHuishoudensgrootte': {'nieuwe_naam': 'Gem. huishoudensgrootte', 'value_type': 'abs', 'formatting': '{:,.1f}'}, 
            'Eenpersoonshuishoudens': {'nieuwe_naam': '% Eenpersoonshuishoudens', 'value_type': '%', 'formatting': '{:.0%}'}, 
            'HuishoudensZonderKinderen': {'nieuwe_naam': '% Huishoudens zonder kinderen', 'value_type': '%', 'formatting': '{:.0%}'}, 
            'HuishoudensMetKinderen': {'nieuwe_naam': '% Huishoudens met kinderen', 'value_type': '%', 'formatting': '{:.0%}'}, 
            
            'k_0Tot15Jaar': {'nieuwe_naam': '% 0-14 jaar', 'value_type': '%', 'formatting': '{:.0%}'}, 
            'k_15Tot25Jaar': {'nieuwe_naam': '% 15-24 jaar', 'value_type': '%', 'formatting': '{:.0%}'}, 
            'k_25Tot45Jaar': {'nieuwe_naam': '% 25-44 jaar', 'value_type': '%', 'formatting': '{:.0%}'}, 
            'k_45Tot65Jaar': {'nieuwe_naam': '% 45-64 jaar', 'value_type': '%', 'formatting': '{:.0%}'}, 
            'k_65JaarOfOuder': {'nieuwe_naam': '% +65 jaar', 'value_type': '%', 'formatting': '{:.0%}'}, 

            'GemiddeldInkomenPerInwoner': {'nieuwe_naam': 'Gemiddeld inkomen per inwoner', 'value_type': 'abs', 'formatting': '{:,.2f}'}, 
            'AantalInkomensontvangers': {'nieuwe_naam': 'Aantal inkomensontvangers', 'value_type': '%', 'formatting': '{:.0%}'}, 
            'GemiddeldInkomenPerInkomensontvanger': {'nieuwe_naam': 'Gemiddeld inkomen per inkomensontvanger', 'value_type': 'abs', 'formatting': '€ {:.0f}X000'}, 
            'HuishOnderOfRondSociaalMinimum': {'nieuwe_naam': 'Huishoudens onder of rond sociaal minumum', 'value_type': 'abs', 'formatting': '{:.1f}%'},

            'GemiddeldeWOZWaardeVanWoningen': {'nieuwe_naam': 'Gemiddelde WOZ-waarde', 'value_type': 'abs', 'formatting': '€ {:.0f}X000'}, 
            'Koopwoningen': {'nieuwe_naam': '% Koopwoningen', 'value_type': 'abs', 'formatting': '{:.0f}%'}, 
            'HuurwoningenTotaal': {'nieuwe_naam': ' % Huurwoningen', 'value_type': 'abs', 'formatting': '{:.0f}%'}, 
            'PersonenautoSPerHuishouden': {'nieuwe_naam': "Gemiddeld aantal auto's per huishouden", 'value_type': 'abs', 'formatting': '{:,.2f}'}, 
            'AfstandTotGroteSupermarkt': {'nieuwe_naam': 'Gemiddelde afstand tot supermarkt', 'value_type': 'abs', 'formatting': '{:,.2f}'}
        }

        self.jaar = jaar
        self.df = self.load_table(jaar=jaar) # alle gemeenten
        self.df_regio = 'Je moet df nog filteren met <filter_regio(self, idx=None, formatted=True)>'
        self.df_regio_formatted = 'Leeg'

    def load_table(self, jaar=2024):
        # Data ophalen vanuit CBS API
        data0 = cbsodata.get_data(self.table_column_ids[jaar]['table_id'], select=self.table_column_ids[jaar]['cols'])
        df = pd.DataFrame(data0)

        df.columns = df.columns.str.replace(r'_\d+$', '', regex=True)   # suffix verwijderen
        df = df[self.kenmerken.keys()]                                  # Alleen benodigde kolommen selecteren
        return df
    
    def abs2perc(self, df):
        perc_kenmerken = [k for k, v in self.kenmerken.items() if v['value_type'] == '%']

        for col in df.columns:
            aantal_inwoners = df.at['AantalInwoners', col]

            for pk in perc_kenmerken:
                value = df.at[pk, col]
                if not pd.isna(value) and value is not None:
                    df.at[pk, col] = value / aantal_inwoners
                    
        return df

    def calculate_afwijking(self, A, B):
        try:
            afwijking = (B-A)/A
            # afwijking = f'{afwijking: .1%}'
            return afwijking
        except:
            return ''
        
    def format_cells(self, df):
        # NL en regio kolommen formatten
        for k, v in self.kenmerken.items():
            formatting_pattern = v['formatting']

            if formatting_pattern not in {'', None}:
                for col in df.columns[:2]:
                    try:
                        df.at[k, col] = formatting_pattern.format(df.at[k, col]).replace(',', 'X').replace('.', ',').replace('X', '.')
                    except:
                        pass
        
        # Afwijking kolom formatten
        formatted_afwijkingen = []
        
        for afwijking in df['Afwijking']:
            try:
                formatted_afwijking = '{:.1%}'.format(afwijking).replace(',', 'X').replace('.', ',').replace('X', '.')
                formatted_afwijkingen.append(formatted_afwijking)
            except:
                formatted_afwijkingen.append(afwijking)

        df['Afwijking'] = formatted_afwijkingen

        # Kenmerken formatten
        df.insert(0, 'Kenmerk', df.index)
        df = df.reset_index(drop=True)
        df['Kenmerk'] = df['Kenmerk'].replace({k:v['nieuwe_naam'] for k,v in self.kenmerken.items()})
        df = df.style.set_properties(subset=['Kenmerk'], **{'text-align': 'left'})

        return df

    def filter_regio(self, idx=None, formatted=True):
        # Filteren op regio
        df = self.df.loc[self.df['ID'].isin([0, idx])] # 0 == Nederland
        assert len(df) == 2, f"\nVerwachtte 2 rijen, vond {len(df)} rijen\n\n\n{df}"

        # Transpose
        df = df.T

        # Kolommen renamen 
        df.columns = [df.at['WijkenEnBuurten', c] for c in df.columns] # ([0, 1170] -> ['Nederland', 'Amsterdam'])
        
        # Absolute waarden naar percentages omrekenen voor geselecteerde kenmerken
        df = self.abs2perc(df)

        # Afwijking berekenen
        df['Afwijking'] = df.apply(lambda row: self.calculate_afwijking(row[df.columns[0]], row[df.columns[1]]), axis=1)

        # df toevoegen aan class
        self.df_regio = df
        
        # cellen formatten
        if formatted == True:
            df_formatted = self.format_cells(df.copy())
            self.df_regio_formatted = df_formatted

############################################################################

# st.title('Bevolkingskarakteristiek')
# img = st.image('https://gmo-research.ai/en/application/files/5816/6011/7522/GettyImages-1150668297_1.jpg')

# with st.sidebar:
#     jaar = st.pills('Jaar', [2024, 2023, 2022, 2021], default=2024, selection_mode="single")

# # API
# api_button = st.button('Verbinden met CBS API')
# if api_button:
#     with st.spinner('Data ophalen vanuit CBS API (dit kan een paar minuten duren...)'):
#         data = CBSData(jaar=jaar)

#     st.success('Data opgehaald!', icon="✅")
#     st.session_state['data'] = data

# # Data verwerken
# if 'data' in st.session_state:
#     data = st.session_state['data']

#     with st.sidebar:
#         dropdown_values = [f'{id} - {WeB} ({gemeentenaam})' for id, WeB, gemeentenaam in zip(data.df['ID'], data.df['WijkenEnBuurten'], data.df['Gemeentenaam'])]

#         selection = st.selectbox(
#             "Regio",
#             dropdown_values,  # dropdown menu
#             placeholder="Selecteer een regio..."
#         )
#         selection_id = int(re.search(r'\d+', selection).group())

#     if st.button('Run', type='primary', icon='🏃‍♂️‍➡️'):
#         data.filter_regio(idx=selection_id, formatted=True)

#         img.empty()

#         st.dataframe(data.df_regio_formatted, height=1000, use_container_width=True, hide_index=True)

st.title('Bevolkingskarakteristiek')
img = st.image('https://gmo-research.ai/en/application/files/5816/6011/7522/GettyImages-1150668297_1.jpg')

with st.sidebar:
    st.header('**:rainbow[Opties]:**')
    st.text('Kies hieronder welke jaren je wilt meenemen. Klik daarna op verbinden. \n\nLet wel: hoe meer jaren, hoe langer het laden. \n\nAls je na het runnen de jaren wilt veranderen, moet je opnieuw op de verbinden-knop klikken. Als je een nieuwe regio wilt kiezen, hoef je niet opnieuwe te verbinden.')

    jaren = st.pills('Jaar', [2024, 2023, 2022, 2021], default=[2024, 2023], selection_mode="multi")

    # API
    api_button = st.button('Verbinden met CBS API')
    if api_button:
        with st.spinner('Data ophalen vanuit CBS API (dit kan een paar minuten duren...)'):

            meerjarendata = {}
            for jaar in jaren:
                data = CBSData(jaar=jaar)
                meerjarendata[jaar] = data
                st.success(f'Data {jaar} opgehaald!', icon="✅")

            st.session_state['meerjarendata'] = meerjarendata
            

# Data verwerken
if 'meerjarendata' in st.session_state:
    meerjarendata = st.session_state['meerjarendata']
    img.empty()

    with st.sidebar:
        dropdown_values = [f'{id} - {WeB} ({gemeentenaam})' for id, WeB, gemeentenaam in zip(meerjarendata[jaren[0]].df['ID'], meerjarendata[jaren[0]].df['WijkenEnBuurten'], meerjarendata[jaren[0]].df['Gemeentenaam'])]

        selection = st.selectbox(
            "Regio",
            dropdown_values,  # dropdown menu
            placeholder="Selecteer een regio..."
        )
        selection_id = int(re.search(r'\d+', selection).group())

    if st.button('Run', type='primary', icon='🏃‍♂️‍➡️'):

        # Dynamically create tabs based on the list
        tabs = st.tabs([str(year) for year in meerjarendata.keys()])

        # Iterate through each tab and display content
        for tab, year in zip(tabs, meerjarendata.keys()):
            with tab:
                st.header(f"{year}")

                meerjarendata[year].filter_regio(idx=selection_id, formatted=True)
                st.dataframe(meerjarendata[year].df_regio_formatted, height=1000, use_container_width=True, hide_index=True)
                

# streamlit run /Users/quincyliem/My\ Drive/Projects/Kardol/Bevolkingskarakteristiek/bevolkingskarakterstiek2.py
