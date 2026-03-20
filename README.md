# Discusso ML Services

This repository contains the machine learning microservices for **Discusso**,
a discussion platform focused on semantic understanding and content discovery.

![Coverage](https://img.shields.io/badge/Coverage-82%25-brightgreen?style=flat-square&logo=pytest)
## 🚀 Current Feature
### Auto Tag Generator
Generates up to 3 semantic tags for a post asynchronously after it is saved.

## 🧠 Design Philosophy
- ML is **non-blocking**
- App works even if ML fails
- Intelligence is modular and replaceable
- System design > model complexity

## 🏗 Architecture
- FastAPI-based microservice
- Async background processing
- Fake ML logic (rule-based) for early integration
- Real ML models will replace logic incrementally

## 📦 API
### Health Check
