import openai
from config_data import load_config

openai.api_key = load_config().open_ai.token
response = openai.Image.create(
    prompt="a white siamese cat",
    n=1,
    size="1024x1024"
)
image_url = response['data'][0]['url']

response = openai.Image.create_edit(
    image=open("sunlit_lounge.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="A sunlit indoor lounge area with a pool containing a flamingo",
    n=1,
    size="1024x1024"
)

images_url = response['data'][0]['url']
