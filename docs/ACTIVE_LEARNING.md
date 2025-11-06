# Active Learning & Self-Training System

The AI Document Analysis System includes an active learning feature that automatically improves models based on user interactions and document uploads.

## How It Works

### 1. Automatic Data Collection

When users upload and analyze documents:

- **After Document Analysis**: 
  - OCR text and extracted summary are saved as training data
  - Entity extraction results are collected
  - Data is stored in `models/training_data/` directory

- **After Chat Interactions**:
  - Question-answer pairs are extracted from chat history
  - Answer spans are identified in the document context
  - QA training data is automatically generated

### 2. Incremental Training

The system automatically triggers training when:

- **Minimum samples collected**: At least 10 new samples per model type
- **Batch size reached**: Every 50 new samples (configurable)
- **Background process**: Checks hourly for new training data

### 3. Training Process

1. **Data Preparation**: Collected data is automatically formatted
2. **Incremental Training**: Models are fine-tuned with:
   - Lower learning rate (1e-5) for stability
   - Fewer epochs (1) for faster training
   - Existing model weights as starting point

3. **Model Updates**: New models replace old ones automatically

## User Feedback

Users can provide feedback to improve model accuracy:

### Summary Feedback
- Rate summary quality (1-5 stars)
- Mark as correct/incorrect
- Provide corrected summary

### Entity Feedback
- Correct entity extractions
- Add missing entities
- Fix entity types

### QA Feedback
- Rate answer quality
- Provide corrected answers
- Mark answers as correct/incorrect

## API Endpoints

### POST /feedback/summary
Submit summary feedback

### POST /feedback/entities/{job_id}
Submit entity corrections

### POST /feedback/qa
Submit QA feedback

## Configuration

Training thresholds can be adjusted in `services/incremental_trainer.py`:

```python
min_samples_for_training = 10  # Minimum samples before training
batch_train_size = 50          # Train after N new samples
```

## Benefits

1. **Continuous Improvement**: Models get better with usage
2. **Domain Adaptation**: Models adapt to your specific document types
3. **User-Driven**: Improvements based on actual user needs
4. **Automatic**: No manual intervention required

## Monitoring

Check training data collection:
```bash
ls -la backend/models/training_data/
```

View training logs:
```bash
tail -f backend/models/training/app.log
```

## Manual Training Trigger

Admins can manually trigger training:

```bash
cd backend/models/training
python incremental_train.py --model all
```

