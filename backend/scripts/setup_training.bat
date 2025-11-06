@echo off
REM Setup script for model training environment (Windows)

echo Setting up training environment...

REM Create directories
mkdir data\ner 2>nul
mkdir data\summarization 2>nul
mkdir data\qa 2>nul
mkdir models\base_models 2>nul
mkdir models\ner_model 2>nul
mkdir models\summarization_model 2>nul
mkdir models\qa_model 2>nul

REM Download base models
echo Downloading base models...
cd models\training
python download_models.py --model all

REM Create sample data
echo Creating sample training data...
python train_all.py --create-samples --data-dir ..\..\data

echo Setup complete!
echo Next steps:
echo 1. Add your training data to data\ner\, data\summarization\, data\qa\
echo 2. Run: python models\training\train_all.py --data-dir data --output-dir models

