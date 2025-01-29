import streamlit as st
import cbsodata
import pandas as pd
import re

pd.set_option('display.max_rows', 100)

########################################################################



########################################################################

def dict2dataframe(data0):
    df = pd.DataFrame(data0)
    df.columns = df.columns.str.replace(r'_\d+$', '', regex=True)
    return df

def filter_and_transpose_data(df, selection_id):
    # df = pd.DataFrame(data0)
    # df.columns = df.columns.str.replace(r'_\d+$', '', regex=True) # Verwijderen van "_72" suffix aan het einde van de kolomnaam

    # Filteren
    df = df.loc[
        ((df['SoortRegio'].str.strip() == 'Land')         & (df['WijkenEnBuurten'].str.strip() == 'Nederland'))
        | (df['ID'] == selection_id)
    ]
    assert len(df) == 2, f"\nVerwachtte 2 rijen, vond {len(df)} rijen\n\n\n{df}"

    # Transpose
    df = df.T
    df.insert(0, 'Kenmerk', df.index)
    df = df.reset_index(drop=True)

    return df

def rename_columns(df):
    # Convert column names to string and find numeric columns
    numeric_cols = [col for col in df.columns if str(col).isdigit()]

    # Ensure there are exactly two numeric columns
    if len(numeric_cols) == 2:
        # Sort the numeric columns to identify the smaller and larger values
        smaller, larger = sorted(numeric_cols, key=int)

        # Rename the columns
        df = df.rename(columns={smaller: 'Nederland', larger: 'Regionaal'})

    return df

def abs2perc(df, rows_to_transform):
    # Get the columns to process (excluding 'Kenmerk')
    data_columns = [col for col in df.columns if col != 'Kenmerk']

    # Get the values of 'AantalInwoners' for each column
    aantal_inwoners = {
        col: df.loc[df['Kenmerk'] == 'AantalInwoners', col].values[0] for col in data_columns
    }

    # Loop through the specified rows and convert the values to percentages
    for row in rows_to_transform:
        for col in data_columns:
            # Get the value for the row and column
            value = df.loc[df['Kenmerk'] == row, col].values[0]

            if not pd.isna(value) and value is not None:
                # Convert to percentage relative to AantalInwoners
                percentage = (value / aantal_inwoners[col]) * 100
                percentage = round(percentage, 1)

                # Update the DataFrame with the percentage value
                df.loc[df['Kenmerk'] == row, col] = percentage
                

    return df

# def format_numbers(df):
#     data_columns = [col for col in df.columns if col != 'Kenmerk']

#     def number2formattedstring(number):
#         if type(number) in [int, float]:
#             if number > 1000:
#                 # formatted = f"{number:,.2f}".replace(",", ".")
#                 formatted = f"{number:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
#             else:
#                 formatted = f"{number:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
#         else:
#             formatted = number
#         return formatted

#     for col in data_columns:
#         df[col] = df[col].apply(number2formattedstring)
#     return df

def calculate_afwijking(A, B):
    try:
        afwijking = (B-A)/A * 100
        afwijking = round(afwijking, 1)
    except:
        afwijking = ''
    return afwijking

# Format function
def format_value(row, column):
    if row['Kenmerk'] in percentage_rows:
        # Format as percentage
        return f"{row[column]:.1f}%" if pd.notnull(row[column]) else row[column]

    elif row['Kenmerk'] in ['GemiddeldInkomenPerInwoner', 'GemiddeldInkomenPerInkomensontvanger']:
        # Multiply by 1000 and format with thousands separator and euro sign
        if pd.notnull(row[column]) and isinstance(row[column], (int, float)):
            return f"€ {int(row[column] * 1000):,}".replace(",", ".")
        else:
            return f'{row[column]}'
    else:
        # Format with thousands separator if >= 1000
        if pd.notnull(row[column]) and isinstance(row[column], (int, float)) and row[column] >= 1000:
            return f"{int(row[column]):,}".replace(",", ".")
        else:
            return f'{row[column]}'

########################################################################

st.title('Bevolkingskarakteristiek')
st.image('https://digitaal.scp.nl/ssn2018/assets/img/uitsnede.jpg')

if st.button('Verbinden met CBS API'):
    # Ruwe CBS data ophalen
    with st.spinner('Data verzamelen uit CBS API... (dit kan een paar minuten duren)'):
        cols2024 = ['ID', 'WijkenEnBuurten', 'Gemeentenaam_1', 'SoortRegio_2', 'AantalInwoners_5', 'k_0Tot15Jaar_8', 'k_15Tot25Jaar_9', 'k_25Tot45Jaar_10', 'k_45Tot65Jaar_11', 'k_65JaarOfOuder_12', 'HuishoudensTotaal_29', 'Eenpersoonshuishoudens_30', 'HuishoudensZonderKinderen_31', 'HuishoudensMetKinderen_32', 'GemiddeldeHuishoudensgrootte_33', 'Bevolkingsdichtheid_34', 'AantalInkomensontvangers_81', 'GemiddeldInkomenPerInkomensontvanger_82', 'GemiddeldInkomenPerInwoner_83', 'HuishOnderOfRondSociaalMinimum_90']
        cols2022 = ['ID', 'Gemeentenaam_1', 'WijkenEnBuurten', 'SoortRegio_2', 'AantalInwoners_5', 'Bevolkingsdichtheid_33', 'HuishoudensTotaal_28', 'GemiddeldeHuishoudensgrootte_32', 'Eenpersoonshuishoudens_29', 'HuishoudensZonderKinderen_30', 'HuishoudensMetKinderen_31', 'k_0Tot15Jaar_8', 'k_15Tot25Jaar_9', 'k_25Tot45Jaar_10', 'k_45Tot65Jaar_11', 'k_65JaarOfOuder_12', 'GemiddeldInkomenPerInwoner_72', 'GemiddeldInkomenPerInkomensontvanger_71', 'AantalInkomensontvangers_70', 'HuishOnderOfRondSociaalMinimum_79']

        table_column_ids = {
            2024: {'table_id': '85984NED', 'cols': cols2024},
            2023: {'table_id': '85618NED', 'cols': []},
            2022: {'table_id': '85318NED', 'cols': cols2022},
        }
    
        data0 = cbsodata.get_data(table_column_ids[2024]['table_id'], select=table_column_ids[2024]['cols'])
        df = dict2dataframe(data0)

        st.session_state['df'] = df
    
if 'df' in st.session_state:
    df = st.session_state['df']

    dropdown_values = [f'{id} - {WeB}' for id, WeB in zip(df['ID'], df['WijkenEnBuurten'])]
    selection = st.selectbox(
        "Regio",
        dropdown_values,  # dropdown menu
        placeholder="Selecteer een regio..."
    )

    selection_id = int(re.search(r'\d+', selection).group())

    if st.button('Run'):
        # List of rows to convert to percentages
        percentage_rows = [
            'Eenpersoonshuishoudens', 'HuishoudensZonderKinderen', 'HuishoudensMetKinderen',
            'k_0Tot15Jaar', 'k_15Tot25Jaar', 'k_25Tot45Jaar', 'k_45Tot65Jaar', 'k_65JaarOfOuder',
            'AantalInkomensontvangers'
        ]

        # Data filteren en processen
        df = filter_and_transpose_data(df, selection_id)
        df = rename_columns(df)
        df = abs2perc(df, percentage_rows)
        df['Afwijking'] = df.apply(lambda row: calculate_afwijking(row['Nederland'], row['Regionaal']), axis=1)

        nieuw_rijnamen = {
            'ID': 'ID',
            'Gemeentenaam': 'Gemeentenaam',
            'WijkenEnBuurten': 'Wijken en Buurten',
            'SoortRegio': 'Soort regio',

            'AantalInwoners': 'Aantal inwoners',
            'Bevolkingsdichtheid': 'Bevolkingsdichtheid',

            'HuishoudensTotaal': 'Aantal huishoudens',
            'GemiddeldeHuishoudensgrootte': 'Gem. huishoudensgrootte',
            'Eenpersoonshuishoudens': '% Eenpersoonshuishoudens',
            'HuishoudensZonderKinderen': '% Huishoudens zonder kinderen',
            'HuishoudensMetKinderen': '% Huishoudens zonder kinderen',

            'k_0Tot15Jaar': '% 0-14 jaar',
            'k_15Tot25Jaar': '% 15-24 jaar',
            'k_25Tot45Jaar': '% 25-44 jaar',
            'k_45Tot65Jaar': '% 45-64 jaar',
            'k_65JaarOfOuder': '% +65 jaar',

            'GemiddeldInkomenPerInwoner': 'Gemiddeld inkomen per inwoner',
            'AantalInkomensontvangers': 'Aantal inkomensontvangers',
            'GemiddeldInkomenPerInkomensontvanger': 'Gemiddeld inkomen per inkomensontvanger',
            'HuishOnderOfRondSociaalMinimum': 'Huishoudens onder of rond sociaal minumum'
        }

        # Apply formatting
        df['Nederland'] = df.apply(lambda row: format_value(row, 'Nederland'), axis=1)
        df['Regionaal'] = df.apply(lambda row: format_value(row, 'Regionaal'), axis=1)
        df['Afwijking'] = df['Afwijking'].apply(lambda x: f"{float(x):.1f}%" if pd.notnull(x) and str(x).replace('.', '', 1).lstrip('-').isdigit() else x)
        df['Kenmerk'] = df['Kenmerk'].replace(nieuw_rijnamen)

        # # Apply left-alignment to the 'Kenmerk' column
        # df = df.style.set_properties(subset=['Kenmerk'], **{'text-align': 'left'})
        # df.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])

        # dfA = df.loc[df['Kenmerk'].isin()]

        st.dataframe(df, height=800, hide_index=True)
