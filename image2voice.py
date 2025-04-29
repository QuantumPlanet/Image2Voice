from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import requests
from transformers import pipeline
from datasets import load_dataset
import soundfile as sf
import torch

def generate_caption(image_url):
    """
    Generate a caption for the given image using a pre-trained BLIP model.
    :param image_url: URL of the image to be captioned
    :return: Description of the image
    """
    # Load the BLIP model and processor
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    # Load and process the image
    image = Image.open(requests.get(image_url, stream=True).raw).convert('RGB')
    #another way to read image
    # image = Image.open(image_path).convert('RGB')
    inputs = processor(images=image, return_tensors="pt")

    # Generate caption
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    
    return caption

def text2voice(text):
    """
    Convert text to voice using a pre-trained TTS model.
    
    :param text: The text to convert to speech.
    :return: None
    """
    # Load the TTS model
    synthesiser = pipeline("text-to-speech", "microsoft/speecht5_tts")

    # Load the speaker embedding dataset
    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
    
    # Select a specific speaker embedding
    speaker_embedding = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
    
    # Generate speech
    speech = synthesiser(text, forward_params={"speaker_embeddings": speaker_embedding})
    
    # Save the generated speech to a file
    sf.write("speech.wav", speech["audio"], samplerate=speech["sampling_rate"])

def image2voice(image_url):
    """
    Generate a caption for the image and convert it to voice.
    
    :param image_url: URL of the image to be captioned
    :return: None
    """
    caption = generate_caption(image_url)
    print("Generated Caption:", caption)
    text2voice(caption)
    print("Speech generated and saved as 'speech.wav'.")

if __name__ == "__main__":
    image_url = "https://storage.googleapis.com/sfr-vision-language-research/BLIP/demo.jpg"
    image2voice(image_url)