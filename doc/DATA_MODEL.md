# Data model

## Match

A Match consists of the following stages:

- qualification duels
- pre-finals
- finals

A Match might also be linked to a Practicarms event.

Before a Match is Frozen, new participants can be added.


### Match structure
```json
{
  "name": "",
  "date": "",
  "practicarmsEventLink": "",
  "participants": [],
  "duels": {
    "qualification": {
      "ranges": {
        "1": [
          // duels...
        ]
      }
    }
  },
  "events": {
    "dq": {
      
    }
  }
}
```

### Duel structure

```json
{
  "id": "",
  "leftId": "",
  "rightId": "",
  "clazz": "",
  "category": "",
  "result": {
    "date": "",
    "loggedByUserId": "",
    "winnerId": ""
  }
}
```

### Qualification

A list of Duels grouped by Range.