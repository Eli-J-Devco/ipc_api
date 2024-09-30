import base64
import datetime
import gzip
import json

def getUTC():
    now = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return now
def gzip_decompress(message):
    try:
        
        result_decode=base64.b64decode(message.decode('ascii'))
        result_decompress=gzip.decompress(result_decode)
        
    except Exception as err:
        print(f"gzip_decompress: '{err}'") 
        return []
    finally:
        return json.loads(result_decompress)
