# Copyright 2016 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
    The v1 Speech to Text service
    (https://www.ibm.com/watson/developercloud/speech-to-text.html)
    """
from __future__ import print_function

import json
from watson_developer_cloud import ToneAnalyzerV3

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
        }
        },
    'shouldEndSession': should_end_session
}


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
}


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
        add those here
        """
    
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the EloquenC helper," \
        "Say a phrase for me to analyze it and I will tell you the emotions I sense in it," \
            "For example, How does this sound, Hey bob, I do not like that idea"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Say a phrase for me to analyze it and tell you the emotions I sense in it"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
        "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
                                                       card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}




def analyze(intent, session):
    tone_analyzer = ToneAnalyzerV3(
                                   username = '4f73cf28-2a4c-4d5a-94e9-a955608af68f',
                                   password = 'pF6tsaTMIEES',
                                   version = '2016-05-19')
    session_attributes = {}
    reprompt_text = None
                                   
    s = intent['slots']['Text']['value']
                                   
    evaluation = json.dumps(tone_analyzer.tone(text=s), indent=2)
                                   
    data = evaluation.split()
                                   
    ans = []
                                   
    for temp in data:
        if(temp[0] == '0'):
            ans.append(temp[0:len(temp)-1])


    values = ["Anger","Disgust","Fear","Joy","Sadness"];
    nums = []
    i = 0
    output = ""
    
    print(len(ans))
    for thing in values:
        x = ans.pop(0);
        nums.append(x);
        #if emotion is >.40, it is counted as strong
        if(float(x) > 0.4):
            output += thing + ", "
            i += 1
    
    
    if(i > 1):
        speech_output = "Here are the emotions it sounds like you feel, " + output
    elif(i > 0):
        speech_output = "Here is the emotion it sounds like you feel, " + output
    else:
        speech_output = "Cannot identify any strong emotions"

    reprompt_text = ""
    
    speech_output += ", Here are the detailed results, "
    for things in values:
        speech_output += str(round((float(nums.pop(0)) * 100),2)) + " percent " + things + ","

    should_end_session = True
    
    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    
    print("on_session_started requestId=" + session_started_request['requestId'] + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
        want
        """
    
    print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    
    print("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])
    
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    
    # Dispatch to your skill's intent handlers
    if intent_name == "getResponse":
        return analyze(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
        
        Is not called when the skill returns should_end_session=true
        """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
# add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
        etc.) The JSON body of the request is provided in the event parameter.
        """
    print("event.session.application.applicationId=" + event['session']['application']['applicationId'])
    
    """
        Uncomment this if statement and populate with your skill's application ID to
        prevent someone else from configuring a skill that sends requests to this
        function.
        """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")
    
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])
    
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
