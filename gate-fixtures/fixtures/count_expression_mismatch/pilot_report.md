# Pilot report

The design's usable sample is 97 trader-meetings.

```count
name: usable_units
unit: trader-meetings
value: 97
source: pilot_data.py
expression: len(set(zip(df.taker, df.meeting)))
```
