import requests


def get_weather(latitude: float, longitude: float) -> str:
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude="
        f"{longitude}&hourly=temperature_2m,precipitation_probability,precipitation,"
        f"cloudcover,windspeed_10m,windgusts_10m&daily=sunrise,sunset&"
        f"current_weather=true&forecast_days=3&timezone=auto").json()

    return _parse_weather(response)


def _parse_weather(response):
    res = response["hourly"]
    sunset_sunrise = response["daily"]
    messages = []
    date = sun = 0
    for (time,
         temp,
         probability,
         precipitation,
         windspeed,
         windgusts,
         cloud,) in zip(res['time'],
                        res["temperature_2m"],
                        res["precipitation_probability"],
                        res["precipitation"],
                        res["windspeed_10m"],
                        res["windgusts_10m"],
                        res['cloudcover']):
        if int(time[8:10]) > date:
            messages.append(f"\n_______{time[8:10]}.{time[5:7]}.{time[:4]}. "
                            f"день {sunset_sunrise['sunrise'][sun][-5:]}-"
                            f"{sunset_sunrise['sunset'][sun][-5:]}_______")
            sun += 1
            date = int(time[8:10])
        if int(time[-5:-3]) % 3 == 0:
            messages.append(f"\n{time[-5:]}: {temp}°C, "
                            f"осадки: {probability}%, {precipitation}mm, "
                            f"Ветер: {round(windspeed / 3.6, 2)}m/c, "
                            f"порывы {round(windgusts / 3.6, 2)}m/c "
                            f"облака: {cloud}%")
    message_text = "\n".join(messages)
    return message_text



