"""
SMS-Activate API integratsiyasi uchun joy.
Hujjat: https://sms-activate.org/en/api2

Kerak bo'lganda shu yerga quyidagi funksiyalarni qo'shing:
  - get_number(service, country) -> (activation_id, phone_number)
  - get_status(activation_id) -> status
  - get_sms_code(activation_id) -> code
  - set_status(activation_id, status)

Hozircha bu — kengaytirish uchun tayyor stub.
"""

import aiohttp

API_URL = "https://sms-activate.org/stubs/handler_api.php"


async def get_balance(api_key: str) -> str:
    params = {"api_key": api_key, "action": "getBalance"}
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL, params=params) as resp:
            return await resp.text()
