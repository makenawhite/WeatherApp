#pip install --upgrade langchain
#pip install openai
#pip install flask

# For Models
from langchain_community.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# For Agent and Tools
from langchain.agents import AgentType
from langchain.agents import initialize_agent, Tool
from langchain.tools import BaseTool, format_tool_to_openai_function
from pydantic import BaseModel, Field
from typing import Optional, Type
from flask import Flask, request, jsonify
from flask_cors import CORS 
import requests, json, os
# For Message schemas, 
from langchain.schema import HumanMessage, AIMessage, ChatMessage, FunctionMessage


app = Flask(__name__)
CORS(app)



#class for model to verify the input of the query is correct 
class GetCurrentWeatherCheckInput(BaseModel):
    # Check the input for Weather
    location: str = Field(..., description = "The name of the location name for which we need to find the weather")
    unit: str = Field(..., description = "The unit for the temperature value")

#class that is a toll that will call get weather function 
class GetCurrentWeatherTool(BaseTool):
    name: str = "get_current_weather"
    description: str = "Used to find the weather for a given location in said unit"
    
    def _run(self, location: str, unit: str):
       
        weather_response = get_current_weather(location, unit)
        return weather_response
    
    def _arun(self, location: str, unit:str):
        raise NotImplementedError("This tool does not support async")
   
    args_schema: Optional[Type[BaseModel]] = GetCurrentWeatherCheckInput

#using the open weather map api to get the weather data 
def get_current_weather(location, unit):
    apiKey = ""
    forecastURL = "http://api.openweathermap.org/data/2.5/weather?appid=" + apiKey + "&q=" + location + "&units=" + unit
    response = requests.get(forecastURL)
    response = response.json()
   
    return response


   

#create route that will take in the query from front end and pass it to the model and return the response 
@app.route('/query', methods=['POST'])
def query():
     
    #define the functions the bot will use 
    function_definitions = [
            {
                "name": "get_current_weather",
                                "description": "Get the current weather in a given location",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "location": {
                                            "type": "string",
                                            "description": "The city and state, e.g. San Francisco, CA",
                                        },
                                        "unit": {
                                            "type": "string",
                                            "description": "The temperature unit to use. Infer this from the users location.",
                                            "enum": ["celsius", "fahrenheit"]
                                        },
                                    },
                                    "required": ["location", "unit"],
                        },
            }

        ]

    # Import OpenAI key
    os.environ["OPENAI_API_KEY"] = ""
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

    model_name = "gpt-3.5-turbo"
    client = OpenAI(organization='')

    #define the tools and functions for the model
    tools = [GetCurrentWeatherTool()]
    functions = [format_tool_to_openai_function(tool_name) for tool_name in tools]
    model = ChatOpenAI(model=model_name, temperature=0, max_retries=2, max_tokens=100, n=1, streaming=False)

    #get the text from the front end
    data = request.get_json()  # Get JSON data from JavaScript
    query_text = data.get('query')
    
    # Use the query_text with  model and get a prediction from model
    response_ai_message = model.predict_messages([HumanMessage(content=query_text)], functions=functions)
    
    _args = json.loads(response_ai_message.additional_kwargs['function_call'].get('arguments'))
    tool_result = tools[0](_args)
    FunctionMessage(name = "get_current_weather", content=str(tool_result))

    #convert the model response to a humanlike response
    response_final = model.predict_messages(
                    [
                        HumanMessage(content= query_text),
                        response_ai_message,
                        FunctionMessage(name='get_current_weather',content=str(tool_result)),
                    ], 
                    functions=functions
                )
    print(response_final)

    #return the final response 
    return jsonify({"response": response_final.content})


if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=3001)


