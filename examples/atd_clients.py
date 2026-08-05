import os

from dotenv import load_dotenv

import judge0

load_dotenv()

api_key = os.getenv("JUDGE0_ATD_API_KEY")

client_ce = judge0.ATDJudge0CE(api_key=api_key)
print(client_ce.get_about())
print(client_ce.get_config_info())
print(client_ce.get_statuses())
print(client_ce.get_languages())
print(client_ce.get_language(language_id=42))

client_extra_ce = judge0.ATDJudge0ExtraCE(api_key=api_key)
print(client_extra_ce.get_about())
print(client_extra_ce.get_config_info())
print(client_extra_ce.get_statuses())
print(client_extra_ce.get_languages())
print(client_extra_ce.get_language(language_id=24))
