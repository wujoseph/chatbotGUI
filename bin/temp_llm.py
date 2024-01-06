import requests
import time
import json
import logging

def testing(input):
    time.sleep(3)
    return input + '喵'

def generate_output(input, character):
    #return testing(input)
    # just for test


    # api to llm
    # link will be dynamically generate
    # and need to manullay change

    if(character == "troll"):
        url = 'https://0f92-34-147-25-81.ngrok-free.app/v1/chat/completions'

        if(input[-1] != "?"):
            input = input + "?" # add questionmark at end of sentence, this can improve model performance

        myobj = {"messages": [{"role": "user","content": "扮演鄉民，以嘲諷而不實際的方式，回答以下句子，限二十字。" + input}], 
                "repetition_penalty": 1.0,
                'headers': {'Content-Type': 'application/json'}
        }

        t0 = time.time()
        x = requests.post(url, json = myobj)
        response = json.loads(x.text)
        sent = response["choices"][-1]["message"]["content"]
        print(response)
        time_interval = time.time() - t0
        logging.info(f'performance:{time_interval:.2f} sec, str length:{len(x.text)}')
        return sent

    if(character == "support"):
        url = 'https://9b45-35-229-222-199.ngrok-free.app/v1/chat/completions'

        myobj = {"messages": [{"role": "user","content": "你是一個正向溫和的心理治療師，回答以下問題，並且不可以用英文，限二百字。" + input}], 
                "repetition_penalty": 1.0,
                'headers': {'Content-Type': 'application/json'}
        }

        t0 = time.time()
        x = requests.post(url, json = myobj)
        response = json.loads(x.text)
        sent = response["choices"][-1]["message"]["content"]
        print(response)
        time_interval = time.time() - t0
        logging.info(f'performance:{time_interval:.2f} sec, str length:{len(x.text)}')
        return sent

