import pandas as pd
import re
import numpy as np

class DataProcessing:
    '''Processen van CBS data (filteren, transponeren, percentages berekenen)'''
    def __init__(self, df):
        self.df = df

        self.percentage_rows = [
            'Eenpersoonshuishoudens',
            'HuishoudensZonderKinderen',
            'HuishoudensMetKinderen',
            'Buiten Europa (herkomstland)',
            'Buiten Europa (geboren in Nederland)',
            'Buiten Europa (geboren buiten Nederland)',
            'k_0Tot15Jaar',
            'k_15Tot25Jaar',
            'k_25Tot45Jaar',
            'k_45Tot65Jaar',
            'k_65JaarOfOuder',
            'AantalInkomensontvangers'
        ]

    def process_df(self, cbs_id=None):
        '''Main function (filteren, transponeren, percentages berekenen)'''
        df = self.df
        df = self.preprocess(df)
        df = self.filter_regio(df, cbs_id)
        df = self.abs2perc(df)
        df = self.calculate_afwijking(df)

        self.df = df
        return df
    
    def preprocess(self, df):
        '''Renamen van kenmerken zoals suffixes verwijderen'''
        # 'BuitenEuropa_19', 'BuitenEuropa_22', 'BuitenEuropa_24' kolommen renamen, omdat in de volgende coderegel de suffixen worden verwijderd
        df = df.rename(columns={'BuitenEuropa_19': 'Buiten Europa (herkomstland)', 'BuitenEuropa_22': 'Buiten Europa (geboren in Nederland)', 'BuitenEuropa_24': 'Buiten Europa (geboren buiten Nederland)'})
        
        # Suffix verijderen
        df.columns = df.columns.str.replace(r'_\d+$', '', regex=True)

        return df

    def filter_regio(self, df, cbs_id):
        '''Dataframe filteren op basis van regio ID'''
        df = df.loc[df['ID'].isin([0, cbs_id])] # 0 == Nederland

        # Transpose & rename columns
        df = df.T
        df.columns = [df.at['WijkenEnBuurten', c] for c in df.columns] # ([0, 1170] -> ['Nederland', 'Amsterdam'])
        return df
    
    def abs2perc(self, df):
        '''Absolute waarden (subset van kenmerken) omzetten naar percentage van totale bevolking'''
        # perc_kenmerken = [k for k, v in self.config.items() if v['value_type'] == '%']
        perc_kenmerken = self.percentage_rows

        for col in df.columns:
            aantal_inwoners = df.at['AantalInwoners', col]

            for kenmerk in perc_kenmerken:
                if kenmerk in df.index:
                    value = df.at[kenmerk, col]

                    if not pd.isna(value) and value is not None:
                        df.at[kenmerk, col] = value / aantal_inwoners
        return df

    def calculate_afwijking(self, df):
        '''Afwijking berekenen tussen regio en Nederland'''
        A = df.iloc[:, 0]
        B = df.iloc[:, 1]

        afwijkingen = []
        for a, b in zip(A, B):
            # Check for NaN values or other invalid conditions
            if any([pd.isna(a), pd.isna(b),  # Check for NaN using pd.isna()
                    a == 0, b == 0, 
                    not isinstance(a, (int, float)), not isinstance(b, (int, float))]):

                afwijking = None
            else:
                afwijking = (b - a) / a
            afwijkingen.append(afwijking)

        df['Afwijking'] = afwijkingen
        return df
    
class DataframeFormatter:
    def __init__(self):
        self.config = {
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

            'Buiten Europa (herkomstland)': {'nieuwe_naam': 'Buiten Europa (herkomstland)', 'value_type': '%', 'formatting': '{:.0%}'},
            'Buiten Europa (geboren in Nederland)': {'nieuwe_naam': 'Buiten Europa (geboren in Nederland)', 'value_type': '%', 'formatting': '{:.0%}'},
            'Buiten Europa (geboren buiten Nederland)': {'nieuwe_naam': 'Buiten Europa (geboren buiten Nederland)', 'value_type': '%', 'formatting': '{:.0%}'},
            
            'k_0Tot15Jaar': {'nieuwe_naam': '% 0-14 jaar', 'value_type': '%', 'formatting': '{:.0%}'}, 
            'k_15Tot25Jaar': {'nieuwe_naam': '% 15-24 jaar', 'value_type': '%', 'formatting': '{:.0%}'}, 
            'k_25Tot45Jaar': {'nieuwe_naam': '% 25-44 jaar', 'value_type': '%', 'formatting': '{:.0%}'}, 
            'k_45Tot65Jaar': {'nieuwe_naam': '% 45-64 jaar', 'value_type': '%', 'formatting': '{:.0%}'}, 
            'k_65JaarOfOuder': {'nieuwe_naam': '% +65 jaar', 'value_type': '%', 'formatting': '{:.0%}'}, 

            'GemiddeldInkomenPerInwoner': {'nieuwe_naam': 'Gemiddeld inkomen per inwoner', 'value_type': 'abs', 'formatting': '€ {:,.0f}'},                      # 
            'AantalInkomensontvangers': {'nieuwe_naam': 'Aantal inkomensontvangers', 'value_type': '%', 'formatting': '{:.0%}'}, 
            'GemiddeldInkomenPerInkomensontvanger': {'nieuwe_naam': 'Gemiddeld inkomen per inkomensontvanger', 'value_type': 'abs', 'formatting': '€ {:,.0f}'},  # 
            'HuishOnderOfRondSociaalMinimum': {'nieuwe_naam': 'Huishoudens onder of rond sociaal minumum', 'value_type': 'abs', 'formatting': '{:.1f}%'},

            'GemiddeldeWOZWaardeVanWoningen': {'nieuwe_naam': 'Gemiddelde WOZ-waarde', 'value_type': 'abs', 'formatting': '€ {:,.0f}'},                          # 
            'Koopwoningen': {'nieuwe_naam': '% Koopwoningen', 'value_type': 'abs', 'formatting': '{:.0f}%'}, 
            'HuurwoningenTotaal': {'nieuwe_naam': ' % Huurwoningen', 'value_type': 'abs', 'formatting': '{:.0f}%'}, 
            'PersonenautoSPerHuishouden': {'nieuwe_naam': "Gemiddeld aantal auto's per huishouden", 'value_type': 'abs', 'formatting': '{:,.2f}'}, 
            'AfstandTotGroteSupermarkt': {'nieuwe_naam': 'Gemiddelde afstand tot supermarkt', 'value_type': 'abs', 'formatting': '{:,.2f}'}
        }

        def format_df(self, df):
            pass

        def format_column(self):
            pass

        def format_afwijking(self):
            pass

        def format_kenmerken(self):
            pass


        def format_cells(self, df):
            # Kolommen Nederland en [regio]
            for k, v in self.kenmerken.items(): # data -> self
                formatting_pattern = v['formatting']

                if formatting_pattern != '': 

                    for col in df.columns[:2]:
                        cell_value = df.at[k, col]

                        if pd.isna(cell_value) == False:

                            if k in ['GemiddeldInkomenPerInwoner', 'GemiddeldInkomenPerInkomensontvanger', 'GemiddeldeWOZWaardeVanWoningen']:
                                cell_value = cell_value * 1000

                            df.at[k, col] = formatting_pattern.format(cell_value).replace(',', 'X').replace('.', ',').replace('X', '.')

            # Kolom afwijking
            formatted_afwijkingen = []
            for afwijking in df['Afwijking']:
                if pd.isna(afwijking) == False:
                    afwijking = '{:.1%}'.format(afwijking).replace(',', 'X').replace('.', ',').replace('X', '.')
                
                formatted_afwijkingen.append(afwijking)
            
            df['Afwijking'] = formatted_afwijkingen

            # Kenmerken formatten
            df.insert(0, 'Kenmerk', df.index)
            df = df.reset_index(drop=True)
            df['Kenmerk'] = df['Kenmerk'].replace({k:v['nieuwe_naam'] for k,v in self.kenmerken.items()})
            # df = df.style.set_properties(subset=['Kenmerk'], **{'text-align': 'left'})

            return df

