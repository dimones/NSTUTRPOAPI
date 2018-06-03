import requests.exceptions, requests
from enum import Enum

#Auth states
class OperationResult(Enum):
    SUCCESSFUL = 1
    UNSUCCESSFUL = 2
    NETERROR = 3
    WTFERROR = 4
# API for CIU NSTU
class NSTUAPI:
    def __init__(self):
        pass
    def get_student_info(self, token):
        try:
            r = requests.get('https://api.ciu.nstu.ru/v1.0/data/simple/student',
                                      cookies={'NstuSsoToken': token})
            if r.status_code == 200:
                resp = r.json()[0]
                return OperationResult.SUCCESSFUL,{"group": resp["STUDY_GROUP"],
                     "FIO": "%s %s %s" %(resp["FAMILY_NAME"], resp["NAME"], resp["PATRONYMIC_NAME"])}
            else:
                return OperationResult.UNSUCCESSFUL, str()
        except requests.exceptions.ConnectionError as e:
            print(e)
            return OperationResult.NETERROR, str()
        except Exception as e:
            print(e)
            return OperationResult.WTFERROR, str()
    def auth_user(self, username, password) -> (OperationResult,str):
        headers = {'Content-Type': 'application/json',
                   'X-OpenAM-Username': username,
                   'X-OpenAM-Password': password}
        try:
            r = requests.post('https://login.nstu.ru/ssoservice/json/authenticate', headers=headers)
            if r.status_code == 200:
                resp = r.json()
                return OperationResult.SUCCESSFUL, resp["tokenId"]
            else:
                return OperationResult.UNSUCCESSFUL, str()
        except requests.exceptions.ConnectionError as e:
            print(e)
            return OperationResult.NETERROR, str()
        except Exception as e:
            print(e)
            return OperationResult.WTFERROR, str()



#for testing
if __name__ == '__main__':
    napi = NSTUAPI()
    auth_result = napi.auth_user("d.bogomolov@corp.nstu.ru", "jmXQF97J")
    if auth_result[0] is OperationResult.SUCCESSFUL:
        info_result = napi.get_student_info(auth_result[1])
        print(info_result)