# MQTT fuzzer

This is the source code for the MQTT fuzzer that we used in our paper *Di Paolo, E., Bassetti, E., & Spognardi, A. (2021). Security assessment of common open source MQTT brokers and clients.*

## Requirements

This code was tested with Python 3.7. Libraries needed are specified in the `requirements.txt` file.

### Use in a venv

We suggest to setup a virtual environment to avoid conflicts and mismatched libraries:

```shell
python3 -m venv venv
. venv/bin/activate
pip install -r requirements
```

For more information about virtual envs please refer to the official documentation.

## Usage

| File | Description |
|-------|-----------------|
|  [mqttprotocol.py](./fuzz/mqttprotocol.py)    | This file contains the MQTT protocol implementation. Packets implemented: _connect, connack, publish, puback, pubrec, pubrel,, pubcomp, subscribe, suback, unsubscribe, unsuback,, pingreq, pingresp, disconnect_. |
|  [client.py](./fuzz/client.py) |  MQTT Client implementation for testing purpose. |
|  [publisher.py](./fuzz/publisher.py) | MQTT Publisher implementation with Twisted and radamsa (payload fuzzing test). |
|  [tester.py](./fuzz/tester.py)      |  With this script you can run the experiments. Example: `./tester.py --host %host --port %port --packets %packets_file`. By default _host_ is _localhost_, _port_ is _1883_, _packets_file_ represents a path to a _json_ file and it has not a default value. |
|  [packets.json](./fuzz/packets.json) | Example of packets that can be passed to the tester. | 
|  packets_generated | This folder contains all the experiments, which are reported in the paper. |


## License

This code is licensed under GPLv3. See [LICENSE](LICENSE) for more information.

If you use this code in your research you can cite our paper: *Di Paolo, E., Bassetti, E., & Spognardi, A. (2021). Security assessment of common open source MQTT brokers and clients.*