from fastapi import FastAPI, Body, Form, Request
import pydantic
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from payment.webmoney.webmoney import get_pay_link


app = FastAPI()
# templates = Jinja2Templates(directory="payment.webmoney.templates")

# async def some(request):
#     return templates.TemplateResponse("payform.html", {"request": request})
@app.get("/", response_class=HTMLResponse)
async def handle_payment(request: Request):
    sad = await get_pay_link(request)
    return sad

from fastapi.responses import HTMLResponse
from fastapi import Response
import aiohttp


# @app.get("/", response_class=HTMLResponse)
# async def handle_payment(request: Request):
#     # return templates.TemplateResponse("payform.html", {"request": request, "tg_id": 12342131})
#     url = "https://merchant.webmoney.com/lmi/payment_utf.asp"
#     data = {'LMI_PAYMENT_AMOUNT': '111.12',
#             'LMI_PAYMENT_DESC': 'платежka',
#             'LMI_PAYMENT_NO': '1234112',
#             'LMI_PAYEE_PURSE': 'Z655044288932',
#             'LMI_SIM_MODE': '1',
#             }
#     headers = {"Content-Type": "application/x-www-form-urlencoded"}
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, data=data, headers=headers) as response:
#             print(response.url)
#             sed = await response.text()
#             # return Response(sed)
#             return session.get(response.url)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
