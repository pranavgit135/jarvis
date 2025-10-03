from frontend.Gui import(
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextTscreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifire,
    QueryModifire,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from backend.Model import FirstLeyerDMM
from backend.RealtimeSearchEngine import RealTimeSearchEngine
from backend.Automation import Automation
from backend.SpeachToText import SpeachRecognition
from backend.Chatbot import ChatBot
from backend.TextToSpeach import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get('Assistantname')
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing wel. How may i help you?'''
subProcess = []
Functions = ["open", "close","play", "system","content", "google search","youtube search"]

def ShowDefaultChatIfNoChats():
    File = open(r"Data\ChatLog.json","r", encoding='utf-8')
    if len(File.read())<5:
        with open(TempDirectoryPath('Database.data'),"w",encoding='utf-8') as file:
            file.write("")

        with open(TempDirectoryPath('Responses.data'),"w",encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadchatLogJson():
    with open(r"Data\ChatLog.json","r",encoding='utf-8') as file:
            chatlog_data = json.load(file)

    return chatlog_data

def ChatLogIntegration():
     json_data = ReadchatLogJson()
     formatted_chatlog = ""
     for entry in json_data:
          if entry['role']=='user':
               formatted_chatlog +=f"User:{entry['content']}\n"
          elif entry['role']=="assistant":
               formatted_chatlog +=f"Assistant:{entry['content']}\n"

     formatted_chatlog = formatted_chatlog.replace('User', Username + " ")
     formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

     with open(TempDirectoryPath('Database.data'),"w",encoding='utf-8') as file:
            file.write(AnswerModifire(formatted_chatlog))

def showChatsOnGuI():
     File = open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8')
     Data = File.read()
     if len(str(Data))>0:
          lines = Data.split('\n')
          result = '\n'.join(lines)
          File.close()
          File = open(TempDirectoryPath('Responses.data'),"w", encoding='utf-8')
          File.write(result)
          File.close()

def InitialExecution():
     Answer = "Hii am jarvis"
     TextToSpeech(Answer)
     SetMicrophoneStatus("False")
     ShowTextTscreen("")
     ShowDefaultChatIfNoChats()
     ChatLogIntegration()
     showChatsOnGuI()

InitialExecution()

def MainExecution():
     TaskExecution = False
     ImageExecution = False
     ImageGenerationQuery = ""

     SetAssistantStatus("Listerning...")
     Query = SpeachRecognition()
     ShowTextTscreen(f"{Username}:{Query}")
     SetAssistantStatus("Thinking...")
     Decision = FirstLeyerDMM(Query)

     print('')
     print(f"Decision: {Decision}")
     print("")

     G = any([i for i  in Decision if i.startswith("general")])
     R  = any([i for i in Decision if i.startswith("realtime")])

     Mearged_query = " and ".join(
          [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]

     )

     for queries in Decision:
          if "generate " in queries:
               ImageGenerationQuery = str(queries)
               ImageExecution = True

     for queries in Decision:
          if TaskExecution == False:
               if any(queries.startswith(func) for func in Functions):
                    run(Automation(list(Decision)))
                    TaskExecution = True

     if ImageExecution == True:
          
          with open(r"frontend\Files\ImageGenaration.data", "w") as file:
               file.write(f"{ImageGenerationQuery},True")

          try:
               p1 = subprocess.Popen(['python', r"backend\ImageGenaration.py"],
                                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                     stdin=subprocess.PIPE,shell=False)
               subProcess.append(p1)

          except Exception as e:
               print(f"Error starting ImageGeneration.py: {e}")

     if G and R :

          SetAssistantStatus("Searching...")
          Answer = RealTimeSearchEngine(QueryModifire(QueryModifire(Mearged_query)))
          ShowTextTscreen(f'{Assistantname} : {Answer}')
          SetAssistantStatus("Answering...")
          TextToSpeech(Answer)
          return True
     else:
          for Queries in Decision:
               if 'general' in Queries:
                    SetAssistantStatus("Thinking...")
                    QueryFinal = Queries.replace("general ","")
                    Answer = ChatBot(QueryModifire(QueryFinal))
                    ShowTextTscreen(f"{Assistantname}:{Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True

               elif "realtime" in Queries:
                    SetAssistantStatus("Searching...")
                    QueryFinal = Queries.replace("realtime ","") 
                    Answer = RealTimeSearchEngine(QueryModifire(QueryFinal))
                    ShowTextTscreen(f"{Assistantname}:{Answer}") 
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True

               elif "exit" in Queries:
                    QueryFinal = "Okay, Bye!"
                    Answer = ChatBot(QueryModifire(QueryFinal))
                    ShowTextTscreen(f"{Assistantname}:{Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    SetAssistantStatus("Answering...")
                    os._exit(1)

def FirstThread():

     while True:

          currentStatus = GetMicrophoneStatus()
         
          if currentStatus =="True":
               MainExecution()

          else:
               AIStatus = GetAssistantStatus()

               if "Available..." in AIStatus:
                    sleep(0.1)

               else:
                    SetAssistantStatus("Available...")

def SecondThread():

     GraphicalUserInterface()

if __name__ =="__main__":
     thread2 = threading.Thread(target=FirstThread,daemon=True)
     thread2.start()
     SecondThread()                                                      


