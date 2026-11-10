# Pilot report

The design's usable sample is 80 trader-meetings.

```count
name: usable_units
unit: trader-meetings
value: 80
source: pilot_data.py
expression: len(set(zip(df.taker, df.meeting)))
terminal: true
expression_b: len(set(df.taker)) * len(set(df.meeting))
```
