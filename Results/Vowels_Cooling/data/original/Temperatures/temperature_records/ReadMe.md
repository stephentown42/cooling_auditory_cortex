# Sample temperature records

The full dataset can be downloaded here: https://figshare.com/s/7f56f2198bfadc35efe9

### Original data format explained

The sample row below shows a single datapoint with probe (P) and ambient (A) temperature measures for left (1) and right (2) thermocouples. Probe temperatures were measured at the loop, ambient temperatures were measured outside the test chamber. Nonsense values (e.g. 5537°C) were recorded if a thermocouple was disconnected from the system. 

| DataPoint |  LogDate   |  LogTime |	1-P °C	| 1-A °C | 2-P °C | 2-A °C |
| --------- | ---------- | -------- |	------	| ------ | ------ | ------ |
|     0     | 06/18/2014 | 14:10:02 |	 25	    |  22.6	 |   34	  | 22.1   |

Towards the end of the study, one temperature recorder stopped working and was replaced by a manual temperature monitor that the experimenter checked throughout testing. It was not possible to record this temperature electronically and therefore we employed a strategy that the probe monitorred manually would always be cooler than the remaining functional recorder (usually by 1 to 2°C). Records for which this was relevant contain the suffix 'RACTL' (right always cooler than left). 


### Editted temperature records - correcting rounding bug
There was a minor bug in the way the original text files are recorded, where timestamps were not constrained to be unique. Such instances usually looked like a rounding error in which a timestamp has been rounded up rather than down. This results in a characteristic pattern where one second is missing and the next second is duplicated. Such instances are sufficiently rare (less than once per session) that the easiest fix was to manually correct the values back to the preceeding second. For auditing purposes, the changes from the original records can be identified easily using a simple text comparison program if required.
