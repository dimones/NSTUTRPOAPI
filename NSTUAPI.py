import requests.exceptions, requests,datetime
from enum import Enum
from dateutil import parser
#Auth states
class OperationResult(Enum):
    SUCCESSFUL = 1
    UNSUCCESSFUL = 2
    NETERROR = 3
    WTFERROR = 4

class Utils:
    #get week number
    @staticmethod
    def get_week_number(start_date):
        now = datetime.date.today()
        d = start_date.split('.')
        start = datetime.date(int(d[2]), int(d[1]), int(d[0]))
        delta = now - start
        weekday = start.weekday()
        return (delta.days + weekday) // 7 + 1
    #Check time for pair
    @staticmethod
    def is_between(time, time_range):
        if time_range[1] < time_range[0]:
            return time >= time_range[0] or time <= time_range[1]
        return time_range[0] <= time <= time_range[1]

# API for CIU NSTU
class NSTUAPI:
    def __init__(self):
        pass

    def get_persons_current_pair(self, person_id):
        #TODO!!!!! Еще в процессе
        try:
            r = requests.get('https://api_my.nstu.ru/2/getPossibleScheduleForDay',params={"faculty": "АВТФ", "day": "Среда", "pair":3, "odd": 1 },)
            if r.status_code == 200:
                print(r.json())
                # resp = r.json()[0]
                # return OperationResult.SUCCESSFUL,{"group": resp["STUDY_GROUP"],
                #      "FIO": "%s %s %s" %(resp["FAMILY_NAME"], resp["NAME"], resp["PATRONYMIC_NAME"])}
            else:
                return OperationResult.UNSUCCESSFUL, str()
        except requests.exceptions.ConnectionError as e:
            print(e)
            return OperationResult.NETERROR, str()
        except Exception as e:
            print(e)
            return OperationResult.WTFERROR, str()
    def get_current_pair(self, token, date = None) -> (OperationResult,str):
        try:
            stud_info = self.get_student_info(token)
            if stud_info[0] is OperationResult.SUCCESSFUL:
                r = requests.get("https://api_my.nstu.ru/2/get_schedule/%s" % (stud_info[1]["group"]))
                week_number = Utils.get_week_number(r.json()["semester_begin"])
                if date == None:
                    cur_date = datetime.datetime.now()
                else:
                    cur_date = parser.parse(date)
                cur_day_of_week = cur_date.weekday()
                # cur_day_of_week = 1 # for test
                cur_time_str = cur_date.strftime("%H:%M")
                pair_number = -1
                if Utils.is_between(cur_time_str, ("08:30", "09:55")):
                    pair_number = 1
                elif Utils.is_between(cur_time_str, ("10:10", "11:35")):
                    pair_number = 2
                elif Utils.is_between(cur_time_str, ("11:50", "13:15")):
                    pair_number = 3
                elif Utils.is_between(cur_time_str, ("13:45", "15:10")):
                    pair_number = 4
                elif Utils.is_between(cur_time_str, ("15:25", "16:50")):
                    pair_number = 5
                elif Utils.is_between(cur_time_str, ("17:05", "18:30")):
                    pair_number = 6
                elif Utils.is_between(cur_time_str, ("18:40", "20:00")):
                    pair_number = 7
                has_pair = False
                temp_pair = None
                for pair in r.json()["data"][cur_day_of_week]:
                    if pair["pair_number"] == pair_number:
                        if pair["weeks"][week_number-1] == 1:
                            has_pair = True
                            temp_pair = pair
                            break
                        else:
                            has_pair = False
                        # break
                if has_pair:
                    return (OperationResult.SUCCESSFUL, temp_pair)
                else:
                    return (OperationResult.UNSUCCESSFUL, None)
        except requests.exceptions.ConnectionError as e:
            print(e)
            return OperationResult.NETERROR, str()
        except Exception as e:
            print(e)
            return OperationResult.WTFERROR, str()
            # print(r.json())

    def get_student_info(self, token) -> (OperationResult,str):
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
    auth_result = napi.auth_user("avgustan.2016@stud.nstu.ru", "0123456789a!")
    if auth_result[0] is OperationResult.SUCCESSFUL:
        info_result = napi.get_student_info(auth_result[1])
        # Время в запросе ниже, вовсе не обязательно. Но нужно также в API конечном его предусмотреть как опциональный параметр
        cur_pair = napi.get_current_pair(auth_result[1], "2018-05-29 11:59:35")
        print(napi.get_persons_current_pair("91252"))