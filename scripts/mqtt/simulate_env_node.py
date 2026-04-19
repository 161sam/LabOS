#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import datetime, timezone

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
    parser.add_argument('--ack-error-rate', type=float, default=0.0, help='0-1 fraction of commands to NACK for testing')
    return parser.parse_args()


def publish_json(client: mqtt.Client, topic: str, payload: dict) -> None:
    client.publish(topic, json.dumps(payload), qos=0, retain=False)
    print(f'published {topic}: {payload}')


def main() -> int:
    args = parse_args()
    client = mqtt.Client(client_id=f'{args.node_id}-sim')

    ack_topic = f'{args.prefix}/reactor/{args.reactor_id}/ack'
    control_topic_filter = f'{args.prefix}/reactor/{args.reactor_id}/control/#'

    command_counter = {'n': 0}

    def on_control(_client, _userdata, message):
        try:
            payload = json.loads(message.payload.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f'received invalid control payload on {message.topic}: {exc}', file=sys.stderr)
            return
        print(f'received control {message.topic}: {payload}')
        command_counter['n'] += 1
        nack = args.ack_error_rate > 0 and (command_counter['n'] % max(int(round(1 / args.ack_error_rate)), 1) == 0)
        ack_payload = {
            'command_id': payload.get('command_id'),
            'command_uid': payload.get('command_uid'),
            'status': 'error' if nack else 'ok',
            'received_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
        }
        if nack:
            ack_payload['error'] = 'simulated NACK'
        publish_json(_client, ack_topic, ack_payload)

    client.on_message = on_control
    client.connect(args.host, args.port, keepalive=30)
    client.subscribe(control_topic_filter)
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
