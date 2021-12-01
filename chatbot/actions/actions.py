# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

import mysql.connector as mysql
import spacy
from typing import Any, Text, Dict, List

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

nlp = spacy.load('en_core_web_md')

class ActionDB(Action):

    def name(self) -> Text:
        return "action_recommend"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        all_stopwords = nlp.Defaults.stop_words

        des = tracker.get_slot("user_input")
        
        if not des:
            try:
                des = tracker.latest_message['entities'][0]['value']
            except:
                des = tracker.latest_message.get('text')
        
        db = mysql.connect(
        host="projectdb.cifjctjr38yf.us-east-1.rds.amazonaws.com",
        user="admin",
        passwd="tripad21",
        database="Project21"
        )

        cursor = db.cursor()
        
        if des == 'fun':
            query = '''select title, about, 
            website FROM df_general2 where category IN('Boat Tours & Water Sports', 'Fun Activities & Games') 
            and review_score >= 3 order by rand() limit 1;
            '''
        elif des == 'alcohol':
            query = '''select title, about, website FROM df_general2 
            where category_desc IN('Bars & Clubs') and category IN('Nightlife') order by rand() limit 1;
            '''
        elif des == 'relaxing':
            query = '''select title, about, website FROM df_general2 
            where category IN('Spas and Wellness', 'Nature & Parks') order by rand() limit 1;
            '''
        elif des == 'family':
            query = '''select title, about, website from df_general2 
            where category IN('Tours', 'Museums', 'Sights & Landmarks') order by rand() limit 1;
            '''
        elif des == 'surprise':
            query = '''select title, about, website from df_general2 
            order by rand() limit 1;
            '''
        else:
            doc = nlp(des)
            text_tokens = [token.text for token in doc]
            tokens_without_sw = [word for word in text_tokens if not word in all_stopwords]
            q_input = tokens_without_sw[-1]
            query = '''select distinct r.title, g.about, g.website 
            from df_reviews2 r inner join df_general2 g on g.id = r.item_id 
            where r.review_content LIKE "%{0}%" order by rand() limit 1;'''.format(q_input)
            
        cursor.execute(query)
        records = cursor.fetchall()
        for record in records:
            record = record
        output1 = '''How about {}?'''.format(record[0])
        output2 = '''{}'''.format(record[1])
        output3 = '''Check out their website: {}'''.format(record[2])
        output = '''{}\n\n{}\n{}'''.format(output1,output2,output3)
        dispatcher.utter_message(text=output)
        return []

class SaveDes(Action): 
    
    def name(self) -> Text: 
        return "action_save_input"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
            try:
                des = tracker.latest_message['entities'][0]['value']
            except: 
                des =  tracker.latest_message.get('text')
            
            return [SlotSet("user_input", des)]

