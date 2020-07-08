import pandas as pd
import requests
import time
import os
import xml.etree.ElementTree as ET

class SystemBolagetAPIClient:
    def __init__(self):
        self.url = 'https://www.systembolaget.se/api/assortment/products/xml'
        self._download_file()
        self._parse_downloaded_file()
        self._create_df()

    def _download_file(self):
        """Checks if a local xml file exists, if it does not it downloads from systembolaget.se"""
        print("[CHECK] - Checking if file exists locally.")
        with open('sortimentsfilen.xml', 'a', encoding='utf-8') as file:
            if os.stat('sortimentsfilen.xml').st_size > 0:
                print("[CHECK] - File exists, created: ", time.ctime(os.path.getmtime('sortimentsfilen.xml')))
                print("[INFO] - Reading from existing file")
                file.close()
            else:
                print("[CHECK] - File does not exist. Downloading new from systembolaget.se.")
                r = requests.get(self.url)
                #parse + unparse in order to "prettyprint" the file instead of one big chunk
                x = xmltodict.parse(r.text)
                file.write(xmltodict.unparse(x, pretty=True))
                file.close()

    def _parse_downloaded_file(self):
        tree = ET.parse('sortimentsfilen.xml')
        root = tree.getroot()

        columns = []
        for element in root:
            for subelement in element:
                if subelement.tag not in columns:
                    columns.append(subelement.tag)
            
        columns.remove('meddelande')

        artiklar = []
        for element in root:
            artikel = {}
            for subelement in element:
                artikel[subelement.tag] = subelement.text
            artiklar.append(artikel)

        artiklar.pop(0)
        artiklar.pop(0)

        #create missing keys to ensure they all have the same length (Otherwise, pandas gets cranky)
        for art in artiklar:
            missing_keys = list(set(columns) - set(art.keys()))
            for key in missing_keys:
                art[key] = None

        self.columns = columns
        self.artiklar = artiklar

    def _create_df(self):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        self.df = pd.DataFrame(self.artiklar, columns=self.columns)
        self.df.PrisPerLiter = self.df.PrisPerLiter.astype(float)

    def filter_varugrupp_prisperliter(self, varugrupp):
        return self.df.sort_values(by='PrisPerLiter', ascending=True)[['Namn', 'PrisPerLiter', 'Varugrupp', 'Typ', 'Stil']].loc[(self.df['Varugrupp'] == varugrupp)]
        


if __name__ == '__main__':
    sb = SystemBolagetAPIClient()
    #print(sb.filter_varugrupp_prisperliter('Öl'))
    print(sb.filter_varugrupp_prisperliter('Rött vin'))





