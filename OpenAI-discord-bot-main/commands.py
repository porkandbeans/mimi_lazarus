import os
import discord
import requests
from dotenv import load_dotenv

load_dotenv()

# Set this to an image-generation model (not a text model!)
HF_MODEL_ID = "stabilityai/stable-diffusion-2"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('GRADIO_TOKEN')}"
}

async def test_command(message, args):
    await message.channel.send(f"Command received, arguments: {args}")

async def generate_image(message, args):
    prompt = " ".join(args)
    payload = {"inputs": prompt}

    await message.channel.send("Generating image, please wait...")

    try:
        response = requests.post(HF_API_URL, headers=HEADERS, json=payload)

        if response.status_code == 200 and response.headers["content-type"] == "image/png":
            with open("generated.png", "wb") as f:
                f.write(response.content)

            await message.channel.send(file=discord.File("generated.png"))
        else:
            await message.channel.send(f"Failed to generate image. Status code: {response.status_code}")
    except Exception as e:
        await message.channel.send(f"Error: {e}")


# from gradio_client import Client
# import os
# import discord
# from dotenv import load_dotenv

# load_dotenv()

# # client declaration for image generation
# client = Client("deepseek-ai/Janus-Pro-7B", hf_token=os.getenv('GRADIO_TOKEN'))
# #client = Client("deepseek-ai/Janus-Pro-7B")

# async def test_command(message, args):
#     await message.channel.send(f"Command receieved, arguments: {args}")

# async def generate_image(message, args):
#     _prompt = ' '.join(args) # reconstruct the array into a string
#     result = client.predict( # send generation request to DeepSeek
#         prompt = _prompt,
#         seed=1234,
#         guidance=5,
#         t2i_temperature=1,
#         api_name="/generate_image"
#     )
#     # extract the first image path from the result
#     if result and isinstance(result, list) and len(result) > 0:
#         first_image = result[0].get('image')
#         if first_image:
#             # construct the full file path or URL if needed
#             image_link = f"{os.path.abspath(first_image)}" # Use the full file path

#             # upload the image from filepath
#             with open(image_link, 'rb') as file:
#                 discord_file = discord.File(file, filename="generated_image.png")
#                 await message.channel.send(file=discord_file)
#         else:
#             await message.channel.send("No image was generated.")
        
#     else:
#         await message.channel.send("No response received from the API.")


commands = {
    "test": test_command,
    "generate": generate_image
}