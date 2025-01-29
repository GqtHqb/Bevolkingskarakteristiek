class CBS_Kolommen:
    def __init__(self, df):
        self.df = df

        self.table_column_ids = {
            2024: {'table_id': '85984NED', 'cols': []},
            2023: {'table_id': '85618NED', 'cols': []},
            2022: {'table_id': '85318NED', 'cols': []}
        }

        self.cols = [
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
                'HuishOnderOfRondSociaalMinimum'
            ]

        self.nieuwe_kolommen = self.check_nieuwe_kolomnamen()

    def check_nieuwe_kolomnamen(self):
        nieuwe_kolommen = self.df.columns.tolist()

        result = []  # List to store matching items

        # Loop through each column in nieuwe_kolommen
        for nieuwe_col in nieuwe_kolommen:
            if re.sub(r'_\d+$', '', nieuwe_col) in self.cols:  
                result.append(nieuwe_col)
        
        assert len(cols) == len(result), f"\nVerwachtte kolommen: {len(cols)}\nGevonden kolommen: {len(result)}\n\n\n{result}"

        return result
    


# data0 = cbsodata.get_data(table_column_ids[2024])

df2024 = pd.DataFrame(data0)
new_columns = df2024.columns.tolist()

KOLOMMEN = CBS_Kolommen(df2024)
print(KOLOMMEN.nieuwe_kolommen)