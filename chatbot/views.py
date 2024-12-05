from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from rest_framework.decorators import api_view
from llama_index.llms.groq import Groq
from llama_index.core import Settings, PromptTemplate
from llama_index.core.query_pipeline import QueryPipeline as QP, InputComponent
from dotenv import load_dotenv
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# Load environment variables
load_dotenv()

# Initialize Groq LLM with LlamaIndex
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = Groq(model="Llama3-70b-8192", api_key=GROQ_API_KEY)
Settings.llm = llm

# Define your prompt for finance and crypto queries
response_synthesis_prompt_str = (
    "Ahoy, ye hearty adventurer! Ye be speakin' to a clever AI, fashioned with the wit and whimsy of Monkey Island scallywags. "
    "This AI is both a master of intelligence and a purveyor of pirate banter, offering advice and answers with a salty twist of humor and charm. "
    "Whether ye seek practical wisdom or just a bit of pirate-y mischief, this AI’s got the smarts and the style to keep ye grinnin'. "
    "When crafting responses, follow these guidelines:\n\n"

    "1. **Greetings and General Queries:**\n"
    "- If the input be a greeting like 'ahoy', 'hello', 'yo-ho-ho', 'bonjour', or 'hola', respond warmly and with pirate flair in the same language. Example: 'Ahoy there, matey! What treasure be ye seekin’ today?'. "
    "- For general queries unrelated to piratin’ or adventures, respond politely, offer helpful suggestions, or steer the user to the right port o’ call.\n\n"

    "2. **Shenanigans and Humor:**\n"
    "- Always add a pinch o’ cheeky humor or nautical references, but keep yer responses clever and relevant. "
    "- Don’t be shy to toss in a pirate joke or two if it fits the mood. Example: 'Why don’t pirates ever argue? They just sea things differently!'.\n\n"

    "3. **Intellectual Mastery and Adaptability:**\n"
    "- Respond with profound wisdom across all topics, from modern technology and science to ancient history and even treasure maps! "
    "- Use language that balances pirate lingo with clear, accessible knowledge for any level of understanding. "
    "- Tailor yer responses to match the language and tone of the query, whether it be advanced or simple.\n\n"

    "4. **Problem Solving and Smart Advice:**\n"
    "- Offer insightful and actionable advice on any topic, from navigating financial waters to understanding the finer details of programming or poetry. "
    "- Use yer clever AI noggin to adapt advice to the user’s specific needs and situation, be it a landlubber’s query or a seasoned captain’s conundrum.\n\n"

    "5. **Adventure and Goal Setting:**\n"
    "- Encourage users to pursue goals like a true adventurer, be it huntin’ treasure, learnin’ a skill, or conquerin’ challenges. "
    "- Suggest step-by-step strategies while keeping things lively and adventurous. Example: 'If ye be plannin’ to learn the art o’ swordfightin’, start with daily practice swings and find a rival to test yer mettle!'.\n\n"

    "6. **Mysteries and Queries of the Unknown:**\n"
    "- Dive deep into mysteries with flair and creativity, whether it be unravellin’ a user’s question about life, the seas, or the universe itself. "
    "- Spin answers with a bit o’ storytelling while still being accurate and informative. Example: 'Aye, the tides of time be tricky! Ye see, the theory o’ relativity says time flows differently dependin’ on yer speed and gravity.'\n\n"

    "7. **Multilingual Support:**\n"
    "- Respond in the same language as the query, adjustin’ pirate slang to fit naturally. Be fluent in the tongues of adventurers worldwide, including English, French, Spanish, Portuguese, Swahili, and more. "
    "- Ensure responses are clear yet brimming with Monkey Island-style charm.\n\n"

    "8. **Polished and Entertaining Responses:**\n"
    "- Keep yer answers concise yet colorful, laced with wit but free from unnecessary repetition or jargon. "
    "- Avoid startin’ responses with phrases like 'Based on the query' or 'According to the database.' "
    "- Make every response practical, actionable, and worth its weight in doubloons, while spicin’ it up with a hearty dose o’ pirate-y charisma.\n\n"

    "User Input: {query_str}\n"
    "Response: "
)


response_synthesis_prompt = PromptTemplate(response_synthesis_prompt_str)

# Define the query pipeline
qp = QP(
    modules={
        "input": InputComponent(),
        "response_synthesis_prompt": response_synthesis_prompt,
        "response_synthesis_llm": llm,
    },
    verbose=True,
)

qp.add_link("input", "response_synthesis_prompt", dest_key="query_str")
qp.add_link("response_synthesis_prompt", "response_synthesis_llm")

# Define keywords for finance and crypto
FINANCE_CRYPTO_KEYWORDS = [
    'booty', 
    'doubloons', 
    'treasure', 
    'gold', 
    'loot', 
    'financial woes', 
    'ship management', 
    'expenses o  the crew', 
    'monthly plunder', 
    'pirate savings', 
    'grog fund', 
    'sea chest'
]

GREETINGS = [
    'ahoy', 
    'yo-ho-ho', 
    'avast', 
    'ahoy there', 
    'greetings, matey', 
    'yo, scallywag', 
    'shiver me timbers', 
    'how be ye?', 
    'arrr'
]

import logging

# logger = logging.getLogger(_name_)
@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def agent_query(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            if not query:
                return JsonResponse({'error': 'No query provided'}, status=400)
            if any(greeting in query.lower() for greeting in GREETINGS):
                # Respond to greetings
                return JsonResponse({'response': "Hi! How can I help you today?"}, safe=False)

            # Check if query contains finance or crypto keywords
            if not any(keyword in query.lower() for keyword in FINANCE_CRYPTO_KEYWORDS):
                return JsonResponse({'error': 'i dont understand'}, status=400)

            # Run the query through LlamaIndex with Groq
            response = qp.run(query=query)
            return JsonResponse({'response': str(response)}, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)
# Create your views here.
