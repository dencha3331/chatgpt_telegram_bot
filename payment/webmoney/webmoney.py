from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

wallets = {
    "USD": "garry@gmail.ru",
    "wallet": "Z655044288932"
}

wallet = {
          "tg_id": 12342131,
          "email": "gar@jsdf.sa",
          "name": "Denis",
          "price": 111.12,
          "wallet": "Z655044288932"}


async def get_pay_link(request, data: dict):
    data.update(request=request)
    return templates.TemplateResponse("payform.html", context=data)


from hashlib import sha256

input_ = "Z655044288932;1.12;1234;1;834;847;20230803+19%3A29%3A07;9755816480;Z655044288932;723181082389"
print(sha256(input_.encode('utf-8')).hexdigest())

