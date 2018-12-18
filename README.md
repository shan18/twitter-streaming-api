# Report Generation from Twitter Streaming API

Clone the repository:  
`git clone https://github.com/shan18/twitter-streaming-api`

## Keys and tokens setup

1. Create a Twitter developer account by signing up [here](https://developer.twitter.com/en.html).

2. After creating a developer account, go to this [link](https://developer.twitter.com/en/apps) and create a new app.

3. Rename the file `keys-sample.py` to `keys.py` and fill out your consumer keys and access tokens generated from the app created above.


## Environment Setup

1. Install python3 on your system

2. Install the requirements  
`pip install -r requirements.txt`

3. Download the nltk stopwords package  
`python -m nltk.downloader stopwords`


## Running the script

Run the script using the command:  
`python stream.py -k <your_keyword>`  

Replace `<your_keyword>` with the keyword with which you want to filter out the tweets.  

The script will display the output in the console.
