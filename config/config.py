import os
import json
from typing import Optional,Dict

def get_instagram_infos(key:str,default_value:Optional[str]=None)-> Dict[str,str]:
    FILE = '.insta/.insta.json'
    with open(FILE,'r') as fp:
        secrets : dict = json.loads(fp.read())
    
    try:
        return secrets[key]
    except:
        if default_value:
            return default_value
        raise EnvironmentError(f'Set The {key}')