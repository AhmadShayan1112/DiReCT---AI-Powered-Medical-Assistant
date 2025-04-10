from google import genai

client = genai.Client(api_key="AIzaSyBN6BqOHbtBVqA9NkeU12M6oVwr5FcHG7Q")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)
print(response.text)
