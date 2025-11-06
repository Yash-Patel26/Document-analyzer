#!/bin/bash
# Setup script for model training environment

echo "Setting up training environment..."

# Create directories
mkdir -p data/ner
mkdir -p data/summarization
mkdir -p data/qa
mkdir -p models/base_models
mkdir -p models/ner_model
mkdir -p models/summarization_model
mkdir -p models/qa_model

# Download base models
echo "Downloading base models..."
cd models/training
python download_models.py --model all

# Create sample data
echo "Creating sample training data..."
python train_all.py --create-samples --data-dir ../../data

echo "Setup complete!"
echo "Next steps:"
echo "1. Add your training data to data/ner/, data/summarization/, data/qa/"
echo "2. Run: python models/training/train_all.py --data-dir data --output-dir models"

