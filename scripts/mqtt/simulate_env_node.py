#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import sys
import time

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print('paho-mqtt is required to run this simulator', file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Publish simple LabOS MQTT telemetry and node status messages.')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=1883)
    parser.add_argument('--prefix', default='labos')
    parser.add_argument('--node-id', default='sim-env-a1')
    parser.add_argument('--reactor-id', type=int, default=1)
    parser.add_argument('--interval', type=float, default=5.0)
    return parser.parse_args()


def publish_json(client: mqtt.Client, topic: str, payload: dict) -> None:
    client.publish(topic, json.dumps(payload), qos=0, retain=False)
    print(f'published {topic}: {payload}')


def main() -> int:
    args = parse_args()
    client = mqtt.Client(client_id=f'{args.node_id}-sim')
    client.connect(args.host, args.port, keepalive=30)
    client.loop_start()
    try:
        publish_json(
            client,
            f'{args.prefix}/node/{args.node_id}/status',
            {
                'name': f'Simulator {args.node_id}',
                'reactor_id': args.reactor_id,
                'node_type': 'env_control',
                'status': 'online',
                'firmware_version': 'sim-v1',
            },
        )
        started_at = time.time()
        while True:
            elapsed = time.time() - started_at
            temp_value = round(28.0 + math.sin(elapsed / 10.0) * 1.8, 2)
            ph_value = round(8.9 + math.cos(elapsed / 12.0) * 0.2, 2)
            publish_json(
                client,
                f'{args.prefix}/node/{args.node_id}/heartbeat',
                {
                    'reactor_id': args.reactor_id,
                    'node_type': 'env_control',
                    'firmware_version': 'sim-v1',
                },
            )
            publish_json(
                client,
                f'{args.prefix}/reactor/{args.reactor_id}/telemetry/temp',
                {
                    'value': temp_value,
                    'unit': 'degC',
                    'source': 'device',
                    'node_id': args.node_id,
                },
            )
            publish_json(
                client,
                f'{args.prefix}/reactor/{args.reactor_id}/telemetry/ph',
                {
                    'value': ph_value,
                    'unit': 'pH',
                    'source': 'device',
                    'node_id': args.node_id,
                },
            )
            time.sleep(args.interval)
    except KeyboardInterrupt:
        publish_json(
            client,
            f'{args.prefix}/node/{args.node_id}/status',
            {
                'name': f'Simulator {args.node_id}',
                'reactor_id': args.reactor_id,
                'node_type': 'env_control',
                'status': 'offline',
                'firmware_version': 'sim-v1',
            },
        )
        return 0
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    raise SystemExit(main())
