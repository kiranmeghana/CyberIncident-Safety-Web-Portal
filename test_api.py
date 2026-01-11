import google.generativeai as genai

genai.configure(api_key="AIzaSyA1XC2smURg6PX8LVboTssMV2zYPvILKCk") 

model = genai.GenerativeModel("gemini-pro")
response = model.generate_content("Test message")

print(response.text)