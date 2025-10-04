#!/usr/bin/env python3
"""
Test script for Lua TTS System API
"""
import requests
import json
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data['status']}")
            print(f"   Services: {data['services']}")
            return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    return False

def test_voices():
    """Test voices endpoint"""
    print("\nTesting /api/voice/voices endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/voice/voices")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['count']} voices:")
            for voice_id, name in data['voices'].items():
                print(f"   - {voice_id}: {name}")
            return True
    except Exception as e:
        print(f"❌ Voices test failed: {e}")
    return False

def test_tts():
    """Test TTS endpoint"""
    print("\nTesting /api/voice/speak endpoint...")
    try:
        payload = {
            "text": "Olá! Este é um teste do sistema de síntese de voz.",
            "voice": "luna",
            "speed": 1.0
        }
        response = requests.post(
            f"{BASE_URL}/api/voice/speak",
            json=payload
        )
        if response.status_code == 200:
            # Save audio file
            with open("test_output.wav", "wb") as f:
                f.write(response.content)
            print(f"✅ TTS successful! Audio saved to test_output.wav")
            print(f"   File size: {len(response.content)} bytes")
            return True
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
    return False

def test_chat():
    """Test chat endpoint"""
    print("\nTesting /api/chat endpoint...")
    try:
        payload = {
            "message": "Olá Lua, como você está?",
            "user_id": "test_user"
        }
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response received:")
            print(f"   Lua: {data['response']}")
            return True
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
    return False

def main():
    print("=" * 50)
    print("   Lua TTS System API Test Suite")
    print("=" * 50)
    
    # Wait for server to be ready
    print("\nChecking if server is running...")
    retries = 5
    while retries > 0:
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            print("✅ Server is running!")
            break
        except:
            print(f"⏳ Waiting for server... ({retries} retries left)")
            time.sleep(2)
            retries -= 1
    
    if retries == 0:
        print("❌ Server is not responding. Please start it first.")
        sys.exit(1)
    
    # Run tests
    tests = [
        test_health,
        test_voices,
        test_tts,
        test_chat
    ]
    
    results = []
    for test in tests:
        results.append(test())
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total - passed} tests failed")
    
    print("=" * 50)

if __name__ == "__main__":
    main()