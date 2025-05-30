# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount

import requests



class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.

    
    def __init__(self):
        
        # Create a session here
        self.cso_session_active = False
        self.base_url = "http://127.0.0.1:8000"
        self.agent = "agent"
        self.user_id = "u_123"
        self.session_id = "s_123"

        super().__init__()

    
    async def on_message_activity(self, turn_context: TurnContext):

        if not self.cso_session_active:
            await self.create_session()
                
            response = await self.prompt_agent(turn_context.activity.text)

            last_resp = response[-1]
            message = last_resp['content']['parts'][0]['text']
            print("*"*50, "\n", message, "\n", "*"*50)
            
    
            # print(response)                                
        
        await turn_context.send_activity(message)

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")

    async def prompt_agent(self, prompt):
        url = "http://localhost:8000/run"
        
        payload = {
            "appName": "agent",
            "userId": "u_123",
            "sessionId": "s_123",
            "newMessage": {
                "role": "user",
                "parts": [{
                    "text": prompt
                }]
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Error: {response.status_code}")
            error_text = response.text
            print(error_text)
            return None

    async def create_session(self):
        """Create a new session with the API"""
        url = f"{self.base_url}/apps/{self.agent}/users/{self.user_id}/sessions/{self.session_id}"
        
        response = requests.post(url, headers={"Content-Type": "application/json"})
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"✓ Session created successfully")
            
        else:
            print(f"✗ Failed to create session: {response.status_code}")
            error_text = response.text
            print(f"Error details: {error_text}")
            return False

        self.cso_session_active = True
