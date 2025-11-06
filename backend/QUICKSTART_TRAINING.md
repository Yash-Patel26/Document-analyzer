# Quick Start: Model Training

This guide will help you quickly set up and train the AI models for the document analysis system.

## Prerequisites

1. **Python Environment**: Python 3.8+
2. **GPU** (recommended): CUDA-compatible GPU for faster training
3. **Dependencies**: Install from `requirements.txt`

```bash
pip install -r requirements.txt
```

## Step 1: Download Base Models

Download pre-trained models that will be fine-tuned:

```bash
cd backend/models/training
python download_models.py --model all
```

This downloads:
- BERT model for NER (Named Entity Recognition)
- BART model for Summarization
- RoBERTa model for Question Answering

**Time**: ~5-10 minutes (depending on internet speed)

## Step 2: Create Sample Training Data

Generate sample data to test the training pipeline:

```bash
python train_all.py --create-samples --data-dir ../../data
```

This creates sample JSON files in `backend/data/samples/`:
- `ner_sample.json` - Example NER training data
- `summarization_sample.json` - Example summarization data
- `qa_sample.json` - Example QA data

## Step 3: Prepare Your Training Data

### Option A: Use Sample Data (Testing)

Copy sample data to training directories:

```bash
# Windows
mkdir data\ner data\summarization data\qa
copy data\samples\ner_sample.json data\ner\
copy data\samples\summarization_sample.json data\summarization\
copy data\samples\qa_sample.json data\qa\
```

```bash
# Linux/Mac
mkdir -p data/ner data/summarization data/qa
cp data/samples/ner_sample.json data/ner/
cp data/samples/summarization_sample.json data/summarization/
cp data/samples/qa_sample.json data/qa/
```

### Option B: Use Your Own Data

Create JSON files in the following format:

**NER Data** (`data/ner/*.json`):
```json
{
  "text": "John Smith works at Microsoft in Seattle.",
  "entities": [
    {"text": "John Smith", "type": "PER", "start": 0},
    {"text": "Microsoft", "type": "ORG", "start": 20},
    {"text": "Seattle", "type": "LOC", "start": 33}
  ]
}
```

**Summarization Data** (`data/summarization/*.json`):
```json
{
  "text": "Long document text here...",
  "summary": "Short summary here."
}
```

**QA Data** (`data/qa/*.json`):
```json
{
  "context": "Document text that contains the answer...",
  "qa_pairs": [
    {
      "question": "What is this about?",
      "answer": "The answer text"
    }
  ]
}
```

## Step 4: Train Models

### Train All Models

```bash
python train_all.py --data-dir ../../data --output-dir ../../models --epochs 3
```

### Train Individual Models

```bash
# Train NER model only
python train_all.py --model ner --data-dir ../../data --output-dir ../../models

# Train Summarization model only
python train_all.py --model summarization --data-dir ../../data --output-dir ../../models

# Train QA model only
python train_all.py --model qa --data-dir ../../data --output-dir ../../models
```

### Training Parameters

- `--epochs`: Number of training epochs (default: 3)
- `--batch-size`: Batch size (default: 16)
- `--learning-rate`: Learning rate (default: 2e-5)
- `--data-dir`: Directory containing training data
- `--output-dir`: Where to save trained models

Example with custom parameters:

```bash
python train_all.py --data-dir ../../data --output-dir ../../models \
  --epochs 5 --batch-size 8 --learning-rate 3e-5
```

## Step 5: Verify Training

After training, check that models are saved:

```bash
# Check model directories
ls models/ner_model/
ls models/summarization_model/
ls models/qa_model/
```

Each directory should contain:
- `config.json` - Model configuration
- `pytorch_model.bin` or `model.safetensors` - Model weights
- `tokenizer_config.json` - Tokenizer configuration
- `vocab.txt` or `vocab.json` - Vocabulary

## Step 6: Use Trained Models

The models will be automatically loaded by the inference service. Update the model paths in your model service if needed:

```python
# In models/entity_extraction_model.py
self.model_name_or_path = "./models/ner_model"  # Use local model

# In models/summarization_model.py
self.model_name_or_path = "./models/summarization_model"

# In models/qa_model.py
self.model_name_or_path = "./models/qa_model"
```

## Troubleshooting

### Out of Memory Errors

Reduce batch size:
```bash
python train_all.py --batch-size 4 --data-dir ../../data
```

### Training Too Slow

1. Use GPU: Ensure CUDA is available
2. Reduce max_length in datasets
3. Use smaller models (e.g., `bert-base-cased` instead of `bert-large-cased`)

### No Training Data Found

Ensure your data files are in the correct format and location:
- `data/ner/*.json`
- `data/summarization/*.json`
- `data/qa/*.json`

## Next Steps

1. **Collect More Data**: More training data = better models
2. **Fine-tune Hyperparameters**: Experiment with learning rates, batch sizes
3. **Evaluate Models**: Test on validation set
4. **Deploy**: Use trained models in production

For detailed information, see [models/training/README.md](models/training/README.md)

