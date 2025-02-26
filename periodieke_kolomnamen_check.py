import cbsodata
import pandas as pd
import re

class CBS_Kolommen:
    def __init__(self):
        self.table_column_ids = {
            2024: {'table_id': '85984NED', 'cols': []},
            2023: {'table_id': '85618NED', 'cols': []},
            2022: {'table_id': '85318NED', 'cols': []},
            2021: {'table_id': '85039NED', 'cols': []}
        }

        self.kolomnamen_zonder_suffix = [
                'ID',
                'Gemeentenaam',
                'WijkenEnBuurten',
                'SoortRegio',

                'AantalInwoners',
                'Bevolkingsdichtheid',

                'HuishoudensTotaal',
                'GemiddeldeHuishoudensgrootte',
                'Eenpersoonshuishoudens',
                'HuishoudensZonderKinderen',
                'HuishoudensMetKinderen',

                'k_0Tot15Jaar',
                'k_15Tot25Jaar',
                'k_25Tot45Jaar',
                'k_45Tot65Jaar',
                'k_65JaarOfOuder',

                'GemiddeldInkomenPerInwoner',
                'GemiddeldInkomenPerInkomensontvanger',
                'AantalInkomensontvangers',
                'HuishOnderOfRondSociaalMinimum',

                'GemiddeldeWOZWaardeVanWoningen', 
                'Koopwoningen', 
                'HuurwoningenTotaal', 
                'PersonenautoSPerHuishouden', 
                'AfstandTotGroteSupermarkt'
            ]

        self.nieuwe_kolommen = self.check_nieuwe_kolomnamen()

    # def check_nieuwe_kolomnamen(self):
    #     nieuwe_kolommen = self.df.columns.tolist()

    #     result = []  # List to store matching items

    #     # Loop through each column in nieuwe_kolommen
    #     for nieuwe_col in nieuwe_kolommen:
    #         if re.sub(r'_\d+$', '', nieuwe_col) in self.cols:  
    #             result.append(nieuwe_col)
        
    #     assert len(cols) == len(result), f"\nVerwachtte kolommen: {len(cols)}\nGevonden kolommen: {len(result)}\n\n\n{result}"

    #     return result

    def check_nieuwe_kolomnamen(self):
        for jaar, table_info in self.table_column_ids.items():
            print(f"\n\n{jaar}: {table_info['table_id']}", end=' ')

            data0 = cbsodata.get_data(table_info['table_id'])
            df = pd.DataFrame(data0)

            kolomnamen = df.columns.tolist()

            results = []  # List to store matching items

            # Loop through each column in nieuwe_kolommen
            for kolomnaam in kolomnamen:
                if re.sub(r'_\d+$', '', kolomnaam) in self.kolomnamen_zonder_suffix:  
                    results.append(kolomnaam)
            
            
            assert len(self.kolomnamen_zonder_suffix) == len(results), f"\nVerwachtte kolommen: {len(self.kolomnamen_zonder_suffix)} \nGevonden kolommen: {len(results)}\n\n\n{results}"

            self.table_column_ids[jaar]['cols'] = results
            print('✅')
    
KOLOMMEN = CBS_Kolommen()

print(KOLOMMEN.table_column_ids)
