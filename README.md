# Real-Time Multilingual Sign Language Detection System

A real-time sign language detection system supporting multiple languages including American Sign Language (ASL), Indian Sign Language (ISL), and Tamil Sign Language (TSL).

## Project Structure

```
├── backend/          # Node.js/Express backend API
├── frontend/         # React frontend application
├── ml/               # Machine learning models and training code
└── dataset/          # Training datasets (not included in repo - too large)
```

## Features

- Real-time sign language detection
- Multi-language support (ASL, ISL, Tamil)
- LSTM-based hand gesture recognition
- Random Forest classification models
- Semantic correction for improved accuracy

## Tech Stack

- **Frontend**: React
- **Backend**: Node.js, Express, MongoDB
- **ML**: Python, TensorFlow/Keras, scikit-learn

## Getting Started

### Backend

```bash
cd backend
npm install
npm start
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### ML API

```bash
cd ml
pip install -r requirements.txt
python api.py
```

## Note

The dataset and large model files are excluded from this repository due to GitHub's file size limits. See the `dataset/` and `ml/` directories locally for training data and models.