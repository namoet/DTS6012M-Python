This is a very basic python for communicating with the DTS5012M LIDAR Sensor via UART. It covers the basic usage as start/stopping the stream and reading values from it. More complex actions like writing registers are not implementet jet.

<h1>Usage</h1>
The module has one main class: **DTS6012M**

So import it with:
```python
from DTS6012M import DTS6012M
```

You can initialize your sensor with:
```python
ser = DTS6012M(PORT)
```

Befor reading data you have to send the start command with:
```python
ser.start_stream()
```

After that you can read values with the class attributes:
- ser.sec_distance
- ser.sec_correction
- ser.sec_intensity
- ser.distance
- ser.correction
- ser.intensity
- ser.sunlight_base

Dont forget to stop the stream with:
```python
ser.stop_stream()
```
Or just use:
```python
ser.close()
```
