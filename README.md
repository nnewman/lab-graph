# lab-graph

This project is a thought model for representing experiment-process relational 
data in a graph database.

## Usage

### Requirements:

- Docker
- Docker-Compose
- Python3

### Getting Started

1. `$ git clone git@github.com:nnewman/lab-graph.git`
2. `$ cd lab-graph`
3. `$ docker-compose up -d`
4. `$ pip3 install -r requirements.txt`
5. `$ python3 app.py`

### Endpoints

POST `/samples` - Create a sample

_Request_
```json
{}
```
_Response_ - UUID of sample
```json
{
    "uid": "671403ec-b27a-45ac-b6a7-2488fdbe7221"
}
```

GET `/samples` - Get a list of samples

_Response_
```json
[
  {
    "uid": "671403ec-b27a-45ac-b6a7-2488fdbe7221"
  }
]
```

POST `/processes` - Create an experiment using a sample

_Request_
```json
{
  "samples": [
    {
      "uid": "671403ec-b27a-45ac-b6a7-2488fdbe7221"
    }
  ]
}
```
_Response_ - UUID of process and list of samples
```json
{
    "samples": [
        {
            "uid": "671403ec-b27a-45ac-b6a7-2488fdbe7221"
        }
    ],
    "uid": "45e6b4b5-06b8-411d-aec5-016d661b4cf9"
}
```

GET `processes` - Get a list of processes

_Response_
```json
[
  {
    "samples": [
      {
        "uid": "671403ec-b27a-45ac-b6a7-2488fdbe7221"
      }
    ],
    "uid": "45e6b4b5-06b8-411d-aec5-016d661b4cf9"
  }
]
```

POST `/split` - Break a sample into several pieces and apply previous 
experiments to split samples

_Request_
```json
{
  "original_sample": {
    "uid": "671403ec-b27a-45ac-b6a7-2488fdbe7221",
  },
  "target_count": 2
}
```
_Response_ - Includes UUID of new sample
```json
{
  "original_sample": {
    "uid": "671403ec-b27a-45ac-b6a7-2488fdbe7221"
  },
  "target_samples": [
    {
      "uid": "c24615a9-b839-4d92-9cce-7a005f2a118f"
    }
  ],
  "timestamp": "2019-02-18T17:23:25+00:00",
  "uid": "937dc0fe-2257-4574-b849-787faad0ea5c"
}
```

## What this is, what this isn't

- This is a model for a future software project that I or someone else 
  might undertake
- This is not a full usable software, and does not contain things like 
  permissions or experimental parameters
  - For something more complete that does this, take a look at 
    [Emergence Lab](https://github.com/emergence-lab/emergence-lab)
- This does not contain a frontend; my focus right now is the data
- This is not intended for any production usage
