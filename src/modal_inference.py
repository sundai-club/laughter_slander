import models
import numpy as np
import torch

import modal
app = modal.App('laughter-slander-app')

def predict(features: np.ndarray) -> list[float]:
  MODEL_CKPT_PATH = './model_checkpoints/best.pth.tar'
  N_FRAMES = 44
  BATCH_SIZE = 128
  DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

  # set from here till probs on Modal
  model = models.ResNetBigger(
    dropout_rate=0.0,
    linear_layer_size=128,
    filter_sizes=[128, 64, 32, 32],
  )
  model.load_state_dict(torch.load(MODEL_CKPT_PATH, map_location='cpu')['state_dict'])
  model.to(DEVICE)
  model.eval()
  print('Model Loaded')

  probs = []
  for i in range(0, len(features) - N_FRAMES - 1, BATCH_SIZE):

    batch_inp = [features[j:j+N_FRAMES] for j in range(i, i+BATCH_SIZE) if (j+N_FRAMES) < len(features)]
    batch_inp = np.stack(batch_inp)
    batch_inp = torch.from_numpy(batch_inp).float().unsqueeze(1).to(DEVICE)

    with torch.no_grad(): preds = model(batch_inp).cpu().numpy().squeeze()
    preds = [float(preds)] if len(preds.shape) == 0 else list(preds)
    probs += preds

  return probs

