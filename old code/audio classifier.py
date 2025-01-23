import numpy as np
from scipy.io import wavfile
from mediapipe.tasks import python
from mediapipe.tasks.python import audio
from mediapipe.tasks.python.components import containers


# Lista de classes suspeitas
audio_set_classes = [
    "Glass breaking",
    "Alarm",
    "Explosion",
    "Gunshot",
    "Screaming",
    "Car alarm",
    "Dog bark",
    "Door slam",
    "Footsteps",
    "Siren",
    "Glass",
    "Shatter",
    "Breaking",
    "Silence"
]

# Função para classificar o áudio
def classify_audio(audio_file_name, classifier):
    sample_rate, wav_data = wavfile.read(audio_file_name)

    # Normalizar os dados para float
    audio_clip = containers.AudioData.create_from_array(
        wav_data.astype(float) / np.iinfo(np.int16).max, sample_rate
    )

    # Classificar o áudio
    classification_result_list = classifier.classify(audio_clip)

    for classification_result in classification_result_list:
        if classification_result.classifications:
            top_category = classification_result.classifications[0].categories[0]
            category_name = top_category.category_name
            print(f"Detected sound: {category_name} ({top_category.score:.2f})")

            # Verificar se a classe está na lista de sons suspeitos
            if category_name in audio_set_classes:
                print("Suspicious sound detected!")
                return audio_file_name, category_name
    return None, None