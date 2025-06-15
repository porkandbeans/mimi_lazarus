from gradio_client import Client
import os
import discord
from dotenv import load_dotenv

load_dotenv()

# client declaration for image generation
# client = Client("deepseek-ai/Janus-Pro-7B", hf_token=os.getenv('GRADIO_TOKEN'))
#client = Client("deepseek-ai/Janus-Pro-7B")

async def test_command(message, args):
    await message.channel.send(f"Command receieved, arguments: {args}")

async def generate_image(message, args):
    await message.channel.send(f"image generation is currently down because amazon are stinky bitches")
    # _prompt = ' '.join(args) # reconstruct the array into a string
    # result = client.predict( # send generation request to DeepSeek
    #     prompt = _prompt,
    #     seed=1234,
    #     guidance=5,
    #     t2i_temperature=1,
    #     api_name="/generate_image"
    # )
    # # extract the first image path from the result
    # if result and isinstance(result, list) and len(result) > 0:
    #     first_image = result[0].get('image')
    #     if first_image:
    #         # construct the full file path or URL if needed
    #         image_link = f"{os.path.abspath(first_image)}" # Use the full file path

    #         # upload the image from filepath
    #         with open(image_link, 'rb') as file:
    #             discord_file = discord.File(file, filename="generated_image.png")
    #             await message.channel.send(file=discord_file)
    #     else:
    #         await message.channel.send("No image was generated.")
        
    # else:
    #     await message.channel.send("No response received from the API.")


commands = {
    "test": test_command,
    "generate": generate_image
}