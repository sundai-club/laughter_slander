import numpy as np
import librosa

def extract_features(file):
    y, sr = librosa.load(file)
    rms = np.mean(librosa.feature.rms(y=y))
    duration = librosa.get_duration(y=y, sr=sr)
    pitches, magnitudes = librosa.core.pitch.piptrack(y=y, sr=sr)
    pitch = np.mean(pitches[magnitudes > np.median(magnitudes)])
    return rms, duration, pitch


def rerank_laughter(filepaths: list[str]) -> list[tuple[str, float]]:
    features = [extract_features(fn) for fn in filepaths]
    max_rms = max(features, key=lambda x: x[0])[0]
    max_duration = max(features, key=lambda x: x[1])[1]
    max_pitch = max(features, key=lambda x: x[2])[2]

    scores = []

    for fn, feature in zip(filepaths, features): 
        rms, duration, pitch = feature
        normalized_rms = rms / max_rms
        normalized_duration = duration / max_duration
        normalized_pitch = pitch / max_pitch
        
        composite_score = (0.4 * normalized_rms) + (0.3 * normalized_duration) + (0.3 * normalized_pitch)
        scores.append((fn, composite_score))

    # Rank files based on composite score
    ranked_files = sorted(scores, key=lambda x: x[1], reverse=True)
    return ranked_files


if __name__ == '__main__':
    DATA_DIR = './data/sample_wavs'
    filepaths = [f'{DATA_DIR}/laugh_{i}.wav' for i in range(9)]
    ranked_filepaths = rerank_laughter(filepaths)
    for fn in ranked_filepaths:
        print('File:', fn[0], '| Score:', fn[1])
