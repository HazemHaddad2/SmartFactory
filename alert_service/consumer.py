#!/usr/bin/env python
"""
Script pour démarrer le consommateur Kafka de l'Alert Service
Exécutez ce script dans un terminal séparé pour traiter les événements
"""

import logging
from kafka_consumer import AlertConsumer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    consumer = AlertConsumer(
        bootstrap_servers='localhost:9092',
        topic='machine-events'
    )
    consumer.start_consuming()
