#!/usr/bin/env python3
"""
Script pour vérifier la connexion Kafka et les topics
"""

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
import json
import time

def check_kafka_connection():
    """Vérifier la connexion à Kafka"""
    try:
        # Test de connexion avec un producer
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1)
        )
        
        # Test d'envoi d'un message
        test_message = {"test": "connection", "timestamp": time.time()}
        future = producer.send('test-topic', test_message)
        record_metadata = future.get(timeout=10)
        
        producer.close()
        
        print("✅ Kafka connection successful!")
        print(f"   Topic: {record_metadata.topic}")
        print(f"   Partition: {record_metadata.partition}")
        print(f"   Offset: {record_metadata.offset}")
        
        return True
        
    except Exception as e:
        print(f"❌ Kafka connection failed: {e}")
        return False

def list_topics():
    """Lister les topics Kafka"""
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers='localhost:9092',
            api_version=(0, 10, 1)
        )
        
        metadata = admin_client.describe_topics()
        topics = list(metadata.keys())
        
        print(f"\n📋 Available Kafka topics ({len(topics)}):")
        for topic in topics:
            print(f"   - {topic}")
            
        return topics
        
    except Exception as e:
        print(f"❌ Failed to list topics: {e}")
        return []

def create_machine_events_topic():
    """Créer le topic machine-events s'il n'existe pas"""
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers='localhost:9092',
            api_version=(0, 10, 1)
        )
        
        topic = NewTopic(
            name='machine-events',
            num_partitions=1,
            replication_factor=1
        )
        
        admin_client.create_topics([topic])
        print("✅ Topic 'machine-events' created successfully!")
        
    except Exception as e:
        if "TopicExistsException" in str(e):
            print("ℹ️ Topic 'machine-events' already exists")
        else:
            print(f"❌ Failed to create topic: {e}")

def test_consumer():
    """Tester la consommation de messages"""
    try:
        consumer = KafkaConsumer(
            'machine-events',
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='test-consumer-group',
            api_version=(0, 10, 1),
            consumer_timeout_ms=5000
        )
        
        print("\n🔍 Testing consumer (waiting 5 seconds for messages)...")
        message_count = 0
        
        for message in consumer:
            print(f"📨 Received: {message.value}")
            message_count += 1
            if message_count >= 3:  # Limiter à 3 messages
                break
        
        consumer.close()
        
        if message_count == 0:
            print("ℹ️ No messages received (this is normal if no events were sent recently)")
        else:
            print(f"✅ Consumer test successful! Received {message_count} messages")
            
    except Exception as e:
        print(f"❌ Consumer test failed: {e}")

def main():
    print("🔧 Kafka Connection Checker")
    print("=" * 40)
    
    # 1. Vérifier la connexion
    if not check_kafka_connection():
        print("\n❌ Cannot connect to Kafka. Make sure Kafka is running on localhost:9092")
        return
    
    # 2. Lister les topics
    topics = list_topics()
    
    # 3. Créer le topic machine-events si nécessaire
    print("\n🔨 Ensuring 'machine-events' topic exists...")
    create_machine_events_topic()
    
    # 4. Tester le consumer
    test_consumer()
    
    print("\n✅ Kafka check completed!")

if __name__ == "__main__":
    main()