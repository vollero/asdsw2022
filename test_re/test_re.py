import re

regex = r"\{\"topic\":[\ ]\"([a-zA-Z0-9]+)\"\}"

matches = re.findall(regex, "{\"topic\": \"casa1\"}")

print(matches)

