import json

user = {}
user['name'] = "方方土"
user['url'] = "http://facebook.com"
user['likes'] = [{'club_name':'粉絲團A','club_type':'sport'},{'club_name':'粉絲團B','club_type':'music'}]
user_dump = json.dumps(user,ensure_ascii=False)

# print(type(user_dump))
# user_load = json.loads(user_dump)
# print(type(user_load))

string = ""
string += user_dump + "\n"
string += user_dump + "\n"
string += user_dump + "\n"

for s in string.split("\n"):
    print(s)

