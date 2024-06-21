## pre-requisites

1. You must have a functioning python environment for this to run. This version was tested on `Python 3.9.6`
2. You must have created an account on https://proxyscrape.com/
  - once you have an account and are signed in, go to https://dashboard.proxyscrape.com/other/freebies/scraperapi and accept all TOS to generate an API Key
  - the current "Freebeis" for this service is 1M credits per day. A single lookup costs 10 credits. This should allow for 100k lookups per day. 

## Install & run

```
pip install requirements.txt
python fast_people_search.py <INPUT>.xlsx <API_KEY>
```
