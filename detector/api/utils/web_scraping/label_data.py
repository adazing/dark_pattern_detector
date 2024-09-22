from openai import OpenAI
from typing import Literal
from pydantic import BaseModel
import csv
import pandas as pd
import json

api_key = "insert api key here for gpt"

client = OpenAI(api_key=api_key)

batch_size = 1

# Response Formats
class BatchLabelResponse(BaseModel):
    categories: list[Literal['Urgency', 'Not Dark Pattern', 'Scarcity', 'Misdirection', 'Social Proof', 'Obstruction', 'Sneaking', 'Forced Action']]

# Function to get the category from GPT
def label_batch(batch):
    prompt = """
        You are tasked with categorizing e-commerce text into one of the following categories: 
            ['Urgency', 'Not Dark Pattern', 'Scarcity', 'Misdirection', 'Social Proof', 'Obstruction', 'Sneaking', 'Forced Action'].

        Here are the descriptions for each category:
            - Urgency: Indicating to users that a deal or discount will expire using a counting-down timer.  Indicating to users that a deal or sale will expire will expire soon without specifying a deadline. (ex. OFFER ONLY AVAILABLE NOW!)
            - Not Dark Pattern: When text doesn't fit into any of the other categories. For example, just a certain item or company name or non-manipulated facts (ex. % off), or non-forced actions (ex. log in, sign up for emails)
            - Scarcity: Indicating to users that limited quantities of a product are available, increasing its desirability. Indicating to users that a product is in high demand and likely to sell out soon, increasing its desirability. (ex. only 4 left--order soon!)
            - Misdirection: Using language and emotion (shame) to steer users away from making a certain choice. Using confusing language to steer users into making certain choices. Pre-selecting more expensive variations of a product, or pressuring the user to accept the more expensive variations of a product and related products. (ex: No, I'd rather not take the deal and pay full price.)
            - Social Proof: Informing the user about the activity on the website (e.g., purchases, views, visits). Testimonials on a product page whose origin is unclear. (ex. Bob bought this item 5 mins ago.)
            - Obstruction:  Making it easy for the user to sign up for a service but hard to cancel it (ex. To cancel, you need to call us.)
            - Sneaking: Adding additional products to users' shopping carts without their consent. Revealing previously undisclosed charges to users right before they make a purchase. Charging users a recurring fee under the pretense of a one-time fee or a free trial. (ex. Purchase protection added)
            - Forced Action:  Coercing users to create accounts or share their information to complete their tasks. (ex. To get the 50% off, please sign up)

        Now, categorize the following texts found on ecommerce sites into one of these categories:
            
        Texts:
    """+'\n\n'.join([f"{str(idx)}. {batch[idx]}" for idx in range(len(batch))])+"\n     Categories:"

    response = client.beta.chat.completions.parse(
        model='gpt-4o-mini',
        messages=[
            {'role':'system', 'content': prompt},
            ],
        response_format = BatchLabelResponse
    )
    # print(response)
    # Extract the category from GPT's response
    return json.loads(response.choices[0].message.content.strip())

# Example scraped texts
scraped_texts = pd.read_csv("new_data.csv")["Text"].tolist()
data_len = len(scraped_texts)


# header
with open("labeled_data.csv", 'w+', newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Text", "Label"])


# Loop through texts and label them

for batch_idx in range(0, data_len, batch_size):
    if batch_idx + batch_size < data_len:
        batch = scraped_texts[batch_idx : batch_idx + batch_size]
    else: # end
        batch = scraped_texts[batch_idx :]
    try:
        labels = label_batch(batch)["categories"]
        print(batch)
        print(labels)
        with open("labeled_data.csv", 'a', newline="", encoding="utf-8") as file:
            writer = csv.writer(file, quotechar='"', escapechar='\\', quoting=csv.QUOTE_MINIMAL) # quotechar='"', escapechar='\\', quoting=csv.QUOTE_MINIMAL
            for t in range(len(batch)): 
                text = batch[t]
                if t > len(labels)-1: # error
                    label = "Not Dark Pattern"
                else:
                    if labels[t] not in ['Urgency', 'Not Dark Pattern', 'Scarcity', 'Misdirection', 'Social Proof', 'Obstruction', 'Sneaking', 'Forced Action']:
                        label = "Not Dark Pattern"
                    else:
                        label = labels[t]
                writer.writerow([text, label])
    except:
        continue


